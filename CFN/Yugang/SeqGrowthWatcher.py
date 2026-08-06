#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Beamline-side watcher for Sequential Growth startX/tempX/stopX windows.

Standalone by design: run with ``python SeqGrowthWatcher.py --dry`` or
``%run -i SeqGrowthWatcher.py`` in the CMS profile environment.  No project
imports are required.  The producer/consumer contract is that the side which
consumes a marker deletes it.

Three markers, all lab -> beamline.  StartX OPENS a window, StopX CLOSES it, and
TempX does neither: it arrives inside an open window whenever the block reaches a
new set-point, so the temperature can be stamped into the file names.

Profile hooks (optional; ``--dry`` just prints instead)::

    seqgrowth_start_collection(filename, marker)
    seqgrowth_stop_collection(filename, marker)
    seqgrowth_temperature(temp_c, marker)        # called on every TempX

At SMI the bluesky file ``SMI_SeqGrowth.py`` does all three itself (``DR.run_auto()``),
so this script is used there for bench tests and for ``--monitor``.
"""
from __future__ import print_function

import argparse
import io
import os
import time

import numpy as np

# TRANSPORT -- default is the LOCAL relay folder, which is how CMS actually runs:
#   sys76   Dropbox_Comm/Dropbox_Com.ipynb  : folder A -> Dropbox (and deletes the local copy)
#   beamline xf11bm_relay.py                : Dropbox  -> folder B (and deletes it on Dropbox)
#   THIS script watches folder B. It never talks to Dropbox, so it runs inside the bluesky
#   profile with no dropbox package and no network egress.
# Set USE_DROPBOX = True only to bypass the relay and poll Dropbox directly (needs `dropbox`).
USE_DROPBOX = False


def _env(name, default=None):
    """``DC_<name>``, falling back to the legacy ``SY_<name>``, then ``default``.

    DC_ = Droplet Controls, i.e. the software, not a person: the rig is shared. The old
    SY_* names keep working so a session that was started before the rename does not
    silently end up on a different beamline than its partner process.
    """
    return os.environ.get('DC_' + name, os.environ.get('SY_' + name, default))


# Which beamline? Same switch, same defaults as xf11bm_relay.py and the lab-side
# protocols/config/auto_flow.py -- one `export DC_BEAMLINE=smi` moves the relay, this
# watcher and the bluesky script together. DC_COMM_DIR / DC_DROPBOX_DIR still override
# either folder on its own.
BEAMLINE = _env('BEAMLINE', 'cms').strip().lower()
_PROFILES = {
    'cms': {'local': '/nsls2/auto-storage/cms/legacy/xf11bm/data/2025_2/YZhang/SY_Comm/',
            'dropbox': '/CFN/CMS/AutoFlow_Com/'},
    'smi': {'local': '/nsls2/data/smi/legacy/results/data/2024_3/313765_Zhang/Dropbox_Com/',
            'dropbox': '/CFN/SMI/SeqGrowth_Com/'},
}
_PROFILE = _PROFILES.get(BEAMLINE, _PROFILES['cms'])
DROPBOX_COMM_DIR = _env('DROPBOX_DIR', _PROFILE['dropbox'])
# folder B -- MUST match LOCAL_DIR in xf11bm_relay.py, or the relay downloads markers
# into a folder nobody reads and every window silently times out at the cap.
COMM_DIR = _env('COMM_DIR', _PROFILE['local'])


def use_beamline(name):
    """Repoint this module at a beamline profile (the ``--beamline`` flag uses it).

    The module constants are read at import, so a plain ``os.environ`` change afterwards
    would do nothing -- that silence is exactly how the two sides end up on different
    Dropbox folders. DC_COMM_DIR / DC_DROPBOX_DIR still win, as everywhere else.
    """
    global BEAMLINE, DROPBOX_COMM_DIR, COMM_DIR
    BEAMLINE = str(name).strip().lower()
    profile = _PROFILES.get(BEAMLINE, _PROFILES['cms'])
    DROPBOX_COMM_DIR = _env('DROPBOX_DIR', profile['dropbox'])
    COMM_DIR = _env('COMM_DIR', profile['local'])
    return {'beamline': BEAMLINE, 'comm_dir': COMM_DIR, 'dropbox': DROPBOX_COMM_DIR}

STARTX_NAME = 'StartX.npy'
STOPX_NAME = 'StopX.npy'
TEMPX_NAME = 'TempX.npy'          # inside an open window: the block reached a new set-point.
                                  #   It opens and closes NOTHING -- it only tells the
                                  #   beamline which temperature to stamp into the names.
FASTPUSH_NAME = 'Start_Push.npy'


def _now_stamp():
    return time.strftime('%Y-%m-%d_%H:%M:%S', time.localtime())


def _encode_marker(name='', signal='', payload=None):
    marker = {'method': str(name), 'signal': str(signal), 'ts': _now_stamp()}
    if payload is not None:
        marker['payload'] = payload
    buf = io.BytesIO()
    np.save(buf, marker, allow_pickle=True)
    return buf.getvalue()


def _decode_marker(data):
    try:
        obj = np.load(io.BytesIO(data), allow_pickle=True)
        value = obj.item() if hasattr(obj, 'item') else obj
        return dict(value) if isinstance(value, dict) else {'raw': value}
    except Exception as exc:
        print('SeqGrowthWatcher: decode failed:', exc)
        return {}


class _SharedDir(object):
    def __init__(self, directory):
        self.dir = os.path.abspath(os.path.expanduser(directory))
        if not os.path.isdir(self.dir):
            os.makedirs(self.dir)
    def _path(self, name):
        return os.path.join(self.dir, name)
    def exists(self, name):
        return os.path.exists(self._path(name))
    def get(self, name):
        try:
            with open(self._path(name), 'rb') as handle:
                return handle.read()
        except (IOError, OSError):
            return None
    def put(self, name, data):
        path = self._path(name)
        tmp = path + '.tmp-%d' % os.getpid()
        try:
            with open(tmp, 'wb') as handle:
                handle.write(data)
            os.replace(tmp, path)
            return True
        except (IOError, OSError) as exc:
            print('SeqGrowthWatcher: shared put failed:', exc)
            try:
                os.remove(tmp)
            except OSError:
                pass
            return False
    def delete(self, name):
        try:
            os.remove(self._path(name))
        except OSError:
            pass
        return True


class _DropboxDir(object):
    def __init__(self, directory):
        import dropbox
        token = (os.environ.get('DROPBOX_ACCESS_TOKEN') or
                 os.environ.get('DROPBOX_TOKEN'))
        if not token:
            try:
                import Dropbox as legacy
                token = getattr(legacy, 'access_token', None)
            except Exception:
                token = None
        if not token:
            raise RuntimeError('set DROPBOX_ACCESS_TOKEN (or load Dropbox.py first)')
        self.dbx = dropbox.Dropbox(token)
        self.dir = '/' + directory.strip('/') + '/'
    def exists(self, name):
        try:
            self.dbx.files_get_metadata(self.dir + name)
            return True
        except Exception:
            return False
    def get(self, name):
        try:
            return self.dbx.files_download(self.dir + name)[1].content
        except Exception as exc:
            print('SeqGrowthWatcher: dropbox get failed:', exc)
            return None
    def put(self, name, data):
        import dropbox
        try:
            self.dbx.files_upload(data, self.dir + name,
                                  mode=dropbox.files.WriteMode.overwrite, mute=True)
            return True
        except Exception as exc:
            print('SeqGrowthWatcher: dropbox put failed:', exc)
            return False
    def delete(self, name):
        try:
            self.dbx.files_delete_v2(self.dir + name)
        except Exception:
            pass
        return True


def _filename(marker):
    payload = marker.get('payload') or {}
    return str(payload.get('filename') or marker.get('method') or 'seq-growth')


def _temp(marker):
    """The set-point (deg C) a marker carries, or None. StartX brings the opening one,
    TempX every later one; both keep it in ``payload['temp_c']``."""
    if not marker:
        return None
    payload = marker.get('payload') or {}
    for value in (payload.get('temp_c'), marker.get('temp_c')):
        if value is None:
            continue
        try:
            value = float(value)
        except (TypeError, ValueError):
            continue
        if value == value:
            return value
    return None


class SeqGrowthWatcher(object):
    """Consume one startX/stopX pair per batch and bound every collection."""
    def __init__(self, poll_s=5.0, max_collect_min=120.0, dry=False,
                 comm_dir=None, use_dropbox=None, send_ack=False, channel=None):
        self.poll_s = float(poll_s)
        self.max_collect_min = float(max_collect_min)
        self.dry = bool(dry)
        # OFF by default: in sequential growth the LAB owns the window (it sends both
        # StartX and StopX) and waits for nothing back, so the beamline must create
        # nothing. Turn it on only for an older lab script that still blocks on the ack.
        self.send_ack = bool(send_ack)
        use_db = USE_DROPBOX if use_dropbox is None else bool(use_dropbox)
        self.ch = channel or (_DropboxDir(DROPBOX_COMM_DIR) if use_db else
                              _SharedDir(comm_dir or COMM_DIR))
        # Last set-point the lab reported (StartX payload, then every TempX). The bluesky
        # side stamps it into the file names; here it is passed to the hooks and printed.
        self.temp_c = None
        print('SeqGrowthWatcher: beamline=%s transport=%s poll=%.1fs cap=%.1fmin dry=%s ack=%s' %
              (BEAMLINE, 'dropbox' if use_db and channel is None else 'shared/test',
               self.poll_s, self.max_collect_min, self.dry, self.send_ack))

    def _consume(self, name):
        if not self.ch.exists(name):
            return None
        data = self.ch.get(name)
        if data is None:
            return None
        self.ch.delete(name)
        marker = _decode_marker(data)
        print('SeqGrowthWatcher: consumed %s ts=%s filename=%s' %
              (name, marker.get('ts', '?'), _filename(marker)))
        return marker

    def take_temperature(self, announce=True):
        """Consume a TempX if one is waiting and remember the new set-point.

        Returns the temperature, or None when there was no marker. It never opens or
        closes a window -- StartX and StopX still own that.
        """
        marker = self._consume(TEMPX_NAME)
        if marker is None:
            return None
        temp_c = _temp(marker)
        if temp_c is None:
            print('SeqGrowthWatcher: %s carried no temp_c -- ignored.' % TEMPX_NAME)
            return None
        old, self.temp_c = self.temp_c, temp_c
        if announce:
            print('SeqGrowthWatcher: temperature %s -> %.1f C' % (old, temp_c))
        hook = globals().get('seqgrowth_temperature')
        if hook is not None and not self.dry:
            hook(temp_c, marker)
        return temp_c

    def wait_for_start(self, stop_check=None):
        print('SeqGrowthWatcher: waiting for %s ...' % STARTX_NAME)
        while not (stop_check and stop_check()):
            marker = self._consume(STARTX_NAME)
            if marker is not None:
                return marker
            # A StopX with no window open is stale (we restarted mid-batch, or the relay
            # delivered start+stop in the same poll). If it survived it would close the
            # NEXT window before a single frame -- silently losing that batch.
            if self._consume(STOPX_NAME) is not None:
                print('SeqGrowthWatcher: stale %s with no window open -- discarded.'
                      % STOPX_NAME)
            # A TempX while idle is NOT stale: it is the block's current set-point, and
            # remembering it means the next window starts at the right temperature.
            self.take_temperature()
            time.sleep(self.poll_s)
        return None

    def start_collection(self, filename, marker):
        if self.dry:
            print('SeqGrowthWatcher: DRY start collection filename=%s' % filename)
            return
        hook = globals().get('seqgrowth_start_collection')
        if hook is None:
            raise RuntimeError('define seqgrowth_start_collection(filename, marker) in the '
                               'beamline profile, or run dry=True')
        hook(filename, marker)

    def stop_collection(self, filename, marker=None, timed_out=False):
        if self.dry:
            print('SeqGrowthWatcher: DRY stop collection filename=%s timed_out=%s' %
                  (filename, timed_out))
            return
        hook = globals().get('seqgrowth_stop_collection')
        if hook is None:
            raise RuntimeError('define seqgrowth_stop_collection(filename, marker) in the '
                               'beamline profile, or run dry=True')
        hook(filename, marker)

    def send_fast_push(self, filename):
        ok = self.ch.put(FASTPUSH_NAME, _encode_marker(
            filename, 'start_fast_push', {'filename': filename}))
        print('SeqGrowthWatcher: ack %s filename=%s -> %s' %
              (FASTPUSH_NAME, filename, ok))
        return ok

    def serve_once(self, stop_check=None):
        start = self.wait_for_start(stop_check=stop_check)
        if start is None:
            return None
        filename = _filename(start)
        # StartX is authoritative about the opening temperature: a window opened without
        # one clears the last value, so an old campaign's T cannot leak into this batch.
        self.temp_c = _temp(start)
        self.start_collection(filename, start)
        began = time.monotonic()
        stop = None
        timed_out = False
        try:
            while not (stop_check and stop_check()):
                self.take_temperature()          # renames the frames, ends nothing
                candidate = self._consume(STOPX_NAME)
                if candidate is not None:
                    stop_name = _filename(candidate)
                    if stop_name != filename:
                        print('SeqGrowthWatcher: WARNING stop filename=%s does not match start=%s'
                              % (stop_name, filename))
                    stop = candidate
                    break
                if time.monotonic() - began >= self.max_collect_min * 60.0:
                    timed_out = True
                    print('SeqGrowthWatcher: ERROR collection cap reached for filename=%s' %
                          filename)
                    break
                time.sleep(self.poll_s)
        finally:
            self.stop_collection(filename, stop, timed_out=timed_out)
        if self.send_ack:
            self.send_fast_push(filename)
        return {'filename': filename, 'start': start, 'stop': stop,
                'timed_out': timed_out, 'temp_c': self.temp_c}

    def run(self, stop_check=None, max_pairs=None):
        count = 0
        try:
            while not (stop_check and stop_check()):
                result = self.serve_once(stop_check=stop_check)
                if result is None:
                    break
                count += 1
                if max_pairs is not None and count >= int(max_pairs):
                    break
        except KeyboardInterrupt:
            print('\nSeqGrowthWatcher: stopped by operator.')
        return count


def _peek_label(cdir, name):
    """``'TempX.npy (T=40.0)'`` -- read WITHOUT deleting, and silent about anything it
    cannot parse (a marker being written by the relay is half there for a moment)."""
    label = name
    try:
        with open(os.path.join(cdir, name), 'rb') as handle:
            obj = np.load(io.BytesIO(handle.read()), allow_pickle=True)
        marker = obj.item() if hasattr(obj, 'item') else obj
        marker = dict(marker) if isinstance(marker, dict) else {}
        temp_c = _temp(marker)
        bits = [b for b in (_filename(marker) if marker else None,
                            'T=%.1f' % temp_c if temp_c is not None else None) if b]
        if bits:
            label = '%s (%s)' % (name, ', '.join(bits))
    except Exception:
        pass
    return label


def monitor(comm_dir=None, poll_s=5.0, hours=14.0):
    """Print folder B whenever it CHANGES, consuming nothing.

    Safe to leave running in a second terminal next to the bluesky session -- unlike the
    watcher itself, which eats the markers the run loop is waiting for. Empty is the
    healthy state; a marker that SITS here means the next hop is not running. Each marker
    is shown with the filename (and, for TempX, the temperature) it carries.
    """
    cdir = os.path.abspath(os.path.expanduser(comm_dir or COMM_DIR))
    print('SeqGrowthWatcher: monitoring %s (read only, Ctrl-C to stop)' % cdir)
    t_end = time.time() + float(hours) * 3600.0
    last = None
    try:
        while time.time() < t_end:
            try:
                now = sorted(n for n in os.listdir(cdir) if not n.endswith('.tmp'))
            except OSError as exc:
                now = ['<unreadable: %s>' % exc]
            if now != last:
                print('%s  %s' % (_now_stamp(),
                                  ', '.join(_peek_label(cdir, n) for n in now)
                                  if now else 'empty'))
                last = now
            time.sleep(float(poll_s))
    except KeyboardInterrupt:
        print('\nSeqGrowthWatcher: monitor stopped.')
    return last


def _main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--beamline', default=None, choices=['cms', 'smi'],
                        help='pick folder B + the Dropbox folder (default: DC_BEAMLINE)')
    parser.add_argument('--dry', action='store_true', help='print instead of running bluesky hooks')
    parser.add_argument('--poll', type=float, default=5.0, help='poll interval in seconds')
    parser.add_argument('--max-collect-min', type=float, default=120.0)
    parser.add_argument('--shared-dir', default=None,
                        help='use a shared directory instead of Dropbox')
    parser.add_argument('--ack', action='store_true',
                        help='write a dummy Start_Push after each window '
                             '(off by default: sequential growth needs no reply)')
    parser.add_argument('--no-ack', action='store_true', help='(default; kept for old scripts)')
    parser.add_argument('--once', action='store_true')
    parser.add_argument('--monitor', action='store_true',
                        help='just watch folder B and print what is in it -- consumes '
                             'NOTHING, so it is safe next to a running acquisition')
    parser.add_argument('--hours', type=float, default=14.0, help='how long --monitor runs')
    args = parser.parse_args()
    if args.beamline:
        print('SeqGrowthWatcher: %s' % use_beamline(args.beamline))
    if args.monitor:
        monitor(comm_dir=args.shared_dir, poll_s=args.poll, hours=args.hours)
        return
    watcher = SeqGrowthWatcher(poll_s=args.poll,
                               max_collect_min=args.max_collect_min,
                               dry=args.dry, comm_dir=args.shared_dir,
                               use_dropbox=False if args.shared_dir else None,
                               send_ack=args.ack and not args.no_ack)
    watcher.run(max_pairs=1 if args.once else None)


if __name__ == '__main__':
    _main()
