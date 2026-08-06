#!/usr/bin/python
# -*- coding: utf-8 -*-
# vi: ts=4 sw=4
################################################################################
# bl_relay.py -- the BEAMLINE-side Dropbox relay for the startX/tempX/stopX
# handshake. One file for every beamline (was xf11bm_relay.py, which read as
# CMS-only): it runs at CMS (xf11bm) and at SMI (xf12id) unchanged. Pick the
# beamline with --beamline, DC_BEAMLINE, or let it autodetect from which /nsls2
# tree exists on this machine.
#
# Run this on the beamline machine, logged in as yourself (so you have your env + the
# dropbox package + can read/write folder B). It is the mirror image of the sys76
# relay (Dropbox_Comm/sys76_relay.py, or the same thing in Dropbox_Com.ipynb): it
# bridges the beamline-accessible LOCAL folder (folder B) to the SAME Dropbox folder,
# so the bluesky script never touches Dropbox -- it only reads/writes folder B.
#
#     sys76  folder A  <--sys76_relay-->  Dropbox  <--THIS SCRIPT-->  folder B  bluesky
#
# Loop, both directions:
#   * INBOUND (lab -> beamline): StartX / TempX / StopX on Dropbox are DOWNLOADED into
#     folder B and DELETED from Dropbox. The bluesky side then consumes and deletes them.
#     The LAB owns the collection window, so all three ride this way: StartX opens it,
#     StopX closes it, and TempX carries a new set-point mid-window so the temperature
#     lands in the file name.
#   * OUTBOUND (beamline -> lab): Start_Push.npy written into folder B (the optional
#     ack after a DAQ scan) is UPLOADED to Dropbox and the local copy deleted.
#
# Whoever CONSUMES a marker DELETES it -- that is the whole contract.
#
# Self-contained: talks to the dropbox SDK directly (token matches sys76's account),
# no repo import, no /nsls2 path other than folder B. Needs only `dropbox`.
#
# Usage (plain terminal or ipython in your beamline env):
#     python bl_relay.py                     # autodetect beamline, loop for 144 h
#     python bl_relay.py --beamline smi      # or say it outright
#     python bl_relay.py --hours 14          # one night
#     python bl_relay.py --list              # show both folders, then exit
#     python bl_relay.py --once              # single pump (for a quick test)
################################################################################

import argparse
import os
import time


def _env(name, default=None):
    """``DC_<name>``, falling back to the legacy ``SY_<name>``, then ``default``.

    DC_ = Droplet Controls, i.e. the software, not a person: the rig is shared. The old
    SY_* names keep working so a session that was started before the rename does not
    silently end up on a different beamline than its partner process.
    """
    return os.environ.get('DC_' + name, os.environ.get('SY_' + name, default))


# --------------------------------------------------------------------------- #
# CONFIG -- must match droplet_core/Config.py *_Comm on sys76.
# --------------------------------------------------------------------------- #
# Folder B and the Dropbox folder ALWAYS move together, so one profile picks both and
# keeps them in step with the lab side (protocols/config/auto_flow.py, same names).
# Override either one on its own with DC_COMM_DIR / DC_DROPBOX_DIR when a new proposal
# starts mid-cycle. NanoSyn.py, SMI_SeqGrowth.py and SeqGrowthWatcher.py read the SAME
# DC_COMM_DIR, so one export points every beamline-side process at the new folder.
_PROFILES = {
    'cms': {'local': '/nsls2/auto-storage/cms/legacy/xf11bm/data/2025_2/YZhang/SY_Comm/',
            'dropbox': '/CFN/CMS/AutoFlow_Com/',
            # a directory that exists ONLY on this beamline's machines -- used to
            # autodetect where we are when nobody said.
            'marker_dir': '/nsls2/auto-storage/cms'},
    'smi': {'local': '/nsls2/data/smi/legacy/results/data/2024_3/313765_Zhang/Dropbox_Com/',
            'dropbox': '/CFN/SMI/SeqGrowth_Com/',
            'marker_dir': '/nsls2/data/smi'},
}
DEFAULT_BEAMLINE = 'cms'        # last resort only; autodetect normally answers first


def detect_beamline():
    """Which beamline's filesystem are we sitting on? ``None`` if it is not obvious.

    Looking at the disk beats hardcoding a default: the same file is checked out at
    both beamlines, and a wrong guess sends every marker to the wrong Dropbox folder
    where the other beamline's relay may swallow it.
    """
    hits = [name for name, prof in sorted(_PROFILES.items())
            if os.path.isdir(prof['marker_dir'])]
    return hits[0] if len(hits) == 1 else None


def resolve_beamline(explicit=None):
    """``(name, why)`` -- --beamline wins, then DC_BEAMLINE, then the filesystem."""
    if explicit:
        return str(explicit).strip().lower(), 'command line'
    env = _env('BEAMLINE')
    if env:
        return str(env).strip().lower(), 'DC_BEAMLINE'
    found = detect_beamline()
    if found:
        return found, 'autodetected from %s' % _PROFILES[found]['marker_dir']
    return DEFAULT_BEAMLINE, 'fallback default -- pass --beamline to be sure'


def profile_for(beamline):
    """Folder B + Dropbox folder for one beamline, with the DC_ overrides applied."""
    prof = _PROFILES.get(beamline, _PROFILES[DEFAULT_BEAMLINE])
    return (_env('COMM_DIR', prof['local']), _env('DROPBOX_DIR', prof['dropbox']))


BEAMLINE, _WHY = resolve_beamline()
# folder B: the beamline-accessible local comm folder (relay + the bluesky script share it).
# the Dropbox folder both relays bridge to (separate per beamline, so a CMS relay can
# never swallow an SMI marker if the two runs overlap).
LOCAL_DIR, DROPBOX_DIR = profile_for(BEAMLINE)
# Dropbox app token -- SAME account as sys76 (droplet_core/Config.py TOKEN_Dropbox).
DROPBOX_TOKEN = 'R_fvHVzYH3sAAAAAAAAAAX03Z7-QVDJ4zSDF_zf5YV7V0KEwwiY9so95zLRU8Rcx'

STARTX_NAME = 'StartX.npy'          # lab -> beamline: OPEN the collection window
TEMPX_NAME = 'TempX.npy'            # lab -> beamline: new set-point INSIDE an open window
STOPX_NAME = 'StopX.npy'            # lab -> beamline: CLOSE the window. Sequential growth
                                    #   has the LAB own the window, so it sends the stop
                                    #   too; the beamline never makes StopX itself.
FASTPUSH_NAME = 'Start_Push.npy'    # beamline -> lab (OUTBOUND here)

# All three lab-side markers ride the same way. Adding one here is all it takes -- a
# marker that is not in this list sits on Dropbox forever and the beamline never sees it.
INBOUND_NAMES = (STARTX_NAME, TEMPX_NAME, STOPX_NAME)
OUTBOUND_NAMES = (FASTPUSH_NAME,)
_INBOUND_NOTE = {
    STARTX_NAME: 'bluesky will open the collection window',
    TEMPX_NAME: 'bluesky will stamp the new temperature into the file name',
    STOPX_NAME: 'bluesky will stop collecting',
}

POLL_S = 5.0
HOURS = 144.0


def _now():
    return time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())


class Relay:
    def __init__(self, local_dir=None, dropbox_dir=None, token=DROPBOX_TOKEN,
                 beamline=None):
        import dropbox
        self.beamline = beamline or BEAMLINE
        if local_dir is None or dropbox_dir is None:
            _local, _cloud = profile_for(self.beamline)
            local_dir = local_dir or _local
            dropbox_dir = dropbox_dir or _cloud
        self.local_dir = local_dir
        os.makedirs(self.local_dir, exist_ok=True)
        self.dropbox_dir = dropbox_dir if dropbox_dir.endswith('/') else dropbox_dir + '/'
        self.dbx = dropbox.Dropbox(token)
        self.dbx.users_get_current_account()            # fail fast on a bad token
        print('%s beamline relay [%s]: local=%s dropbox=%s'
              % (_now(), self.beamline, self.local_dir, self.dropbox_dir))
        print('%s   inbound  (lab -> here) : %s' % (_now(), ', '.join(INBOUND_NAMES)))
        print('%s   outbound (here -> lab) : %s' % (_now(), ', '.join(OUTBOUND_NAMES)))

    # -- Dropbox helpers ----------------------------------------------------- #
    def _cloud_list(self):
        try:
            return [e.name for e in self.dbx.files_list_folder(self.dropbox_dir.rstrip('/')).entries]
        except Exception:
            return []

    def _cloud_get(self, name):
        try:
            _md, resp = self.dbx.files_download(self.dropbox_dir + name)
            return resp.content
        except Exception:
            return None

    def _cloud_put(self, name, data):
        import dropbox
        self.dbx.files_upload(data, self.dropbox_dir + name,
                              mode=dropbox.files.WriteMode.overwrite, mute=True)
        return True

    def _cloud_delete(self, name):
        try:
            self.dbx.files_delete_v2(self.dropbox_dir + name)
        except Exception:
            pass
        return True

    # -- local helpers ------------------------------------------------------- #
    def _local_path(self, name):
        return os.path.join(self.local_dir, name)

    def _local_list(self):
        try:
            return sorted(os.listdir(self.local_dir))
        except Exception:
            return []

    def _local_get(self, name):
        try:
            with open(self._local_path(name), 'rb') as f:
                return f.read()
        except Exception:
            return None

    def _local_put(self, name, data):
        tmp = self._local_path(name) + '.tmp'
        with open(tmp, 'wb') as f:
            f.write(data)
        os.replace(tmp, self._local_path(name))         # atomic
        return True

    def _local_delete(self, name):
        try:
            os.remove(self._local_path(name))
        except FileNotFoundError:
            pass
        return True

    # -- pumps --------------------------------------------------------------- #
    def pump_inbound(self, name=STARTX_NAME, note=None):
        """One lab marker on Dropbox -> folder B, then delete it from Dropbox."""
        data = self._cloud_get(name)
        if data is None:
            return False
        self._local_put(name, data)
        self._cloud_delete(name)
        print('%s relay: %s downloaded cloud->B (%s)'
              % (_now(), name, note or _INBOUND_NOTE.get(name, 'bluesky will pick it up')))
        return True

    def pump_inbound_tempx(self):
        """TempX -> folder B. Carries the block's new set-point INSIDE an open window; it
        opens and closes nothing, but without it every file of the run is named at the
        temperature the run started at."""
        return self.pump_inbound(TEMPX_NAME)

    def pump_inbound_stopx(self):
        """StopX -> folder B. Sequential growth ends its collection window from the LAB, so
        the stop marker travels the same direction as the start; without this the beamline
        would keep collecting until its own safety cap fired."""
        return self.pump_inbound(STOPX_NAME)

    def pump_outbound(self, name=FASTPUSH_NAME):
        """Start_Push in folder B -> Dropbox, then delete the local copy."""
        data = self._local_get(name)
        if data is None:
            return False
        try:
            self._cloud_put(name, data)
        except Exception as e:
            print('%s relay: %s upload FAILED (%s); keeping local copy' % (_now(), name, e))
            return False
        self._local_delete(name)
        print('%s relay: %s uploaded B->cloud (sys76 will fast-push)' % (_now(), name))
        return True

    def pump_once(self):
        """One sweep of every marker, both directions. Never raises: a Dropbox hiccup on
        one marker must not stop the others -- a dropped StopX means a run that never ends."""
        moved = {}
        for name in INBOUND_NAMES:
            try:
                moved[name] = self.pump_inbound(name)
            except Exception as e:
                print('%s relay inbound error (%s): %s' % (_now(), name, e))
                moved[name] = False
        for name in OUTBOUND_NAMES:
            try:
                moved[name] = self.pump_outbound(name)
            except Exception as e:
                print('%s relay outbound error (%s): %s' % (_now(), name, e))
                moved[name] = False
        # legacy keys, so an old notebook cell that reads ['inbound'] keeps working
        moved['inbound'] = moved.get(STARTX_NAME, False)
        moved['tempx'] = moved.get(TEMPX_NAME, False)
        moved['stopx'] = moved.get(STOPX_NAME, False)
        moved['outbound'] = moved.get(FASTPUSH_NAME, False)
        return moved

    def show(self):
        """Print both ends without moving anything -- the first thing to run when a marker
        seems stuck: it says which side is holding it."""
        print('%s folder B : %s' % (_now(), self._local_list()))
        print('%s Dropbox  : %s' % (_now(), self._cloud_list()))

    def run(self, hours=HOURS, poll_s=POLL_S):
        t_end = time.time() + float(hours) * 3600.0
        print('%s relay loop: %.0f h, poll %.0f s. Ctrl-C to stop.' % (_now(), hours, poll_s))
        try:
            while time.time() < t_end:
                self.pump_once()
                time.sleep(poll_s)
        except KeyboardInterrupt:
            print('%s relay stopped by operator.' % _now())
        print('%s relay window elapsed.' % _now())


if __name__ == '__main__':
    ap = argparse.ArgumentParser(
        description='Beamline-side Dropbox relay for the startX/tempX/stopX handshake.')
    ap.add_argument('--beamline', default=None, choices=sorted(_PROFILES),
                    help='which beamline (default: DC_BEAMLINE, else autodetect)')
    ap.add_argument('--comm-dir', default=None,
                    help='folder B override (default: the beamline profile / DC_COMM_DIR)')
    ap.add_argument('--dropbox-dir', default=None,
                    help='Dropbox folder override (default: profile / DC_DROPBOX_DIR)')
    ap.add_argument('--hours', type=float, default=HOURS)
    ap.add_argument('--poll', type=float, default=POLL_S)
    ap.add_argument('--once', action='store_true', help='single pump then exit (test)')
    ap.add_argument('--list', action='store_true', dest='do_list',
                    help='print folder B and the Dropbox folder, then exit')
    args = ap.parse_args()

    BEAMLINE, _WHY = resolve_beamline(args.beamline)
    LOCAL_DIR, DROPBOX_DIR = profile_for(BEAMLINE)
    print('=' * 72)
    print('beamline relay   %s   (%s)' % (BEAMLINE, _WHY))
    print('=' * 72)
    r = Relay(local_dir=args.comm_dir or LOCAL_DIR,
              dropbox_dir=args.dropbox_dir or DROPBOX_DIR,
              beamline=BEAMLINE)
    if args.do_list:
        r.show()
    elif args.once:
        print(r.pump_once())
    else:
        r.run(hours=args.hours, poll_s=args.poll)
