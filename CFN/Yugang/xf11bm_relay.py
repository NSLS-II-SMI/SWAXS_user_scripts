#!/usr/bin/python
# -*- coding: utf-8 -*-
# vi: ts=4 sw=4
################################################################################
# xf11bm_relay.py -- the BEAMLINE-side Dropbox relay for the MultiAutoFlow handshake.
#
# Run this on the beamline machine, logged in as yourself (so you have your env + the
# dropbox package + can read/write folder B). It is the mirror image of the sys76
# notebook relay (Dropbox_Comm/Dropbox_Com.ipynb): it bridges the xf11bm-accessible
# LOCAL folder (folder B) to the SAME Dropbox folder, so ConFlow_SY2 never touches
# Dropbox -- it only reads/writes folder B.
#
# Loop, both directions:
#   * INBOUND (StartX, sys76 -> beamline): if StartX.npy is on Dropbox, DOWNLOAD it into
#     folder B and DELETE it from Dropbox. ConFlow_SY2 then sees it, deletes it, measures.
#   * OUTBOUND (Start_Push, beamline -> sys76): if ConFlow_SY2 wrote Start_Push.npy into
#     folder B (after the DAQ scan), UPLOAD it to Dropbox and DELETE the local copy.
#
# Self-contained: talks to the dropbox SDK directly (token matches sys76's account),
# no repo import, no /nsls2 legacy path other than folder B. Needs only `dropbox`.
#
# Usage (plain terminal or ipython in your beamline env):
#     python xf11bm_relay.py                 # loops for 144 h
#     python xf11bm_relay.py --hours 12      # or a shorter window
#     python xf11bm_relay.py --once          # single pump (for a quick test)
################################################################################

import argparse
import os
import time
#dd
###test
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
# Which beamline is this? Folder B and the Dropbox folder ALWAYS move together, so pick
# both with one variable and keep them in step with the lab side
# (protocols/config/auto_flow.py, same names):
#
#     export DC_BEAMLINE=smi     # then just: python xf11bm_relay.py
#
# Override either one on its own with DC_COMM_DIR / DC_DROPBOX_DIR when a new proposal
# starts mid-cycle. NanoSyn.py, SMI_SeqGrowth.py and SeqGrowthWatcher.py read the SAME
# DC_COMM_DIR, so one export points every beamline-side process at the new folder.
#BEAMLINE = _env('BEAMLINE', 'cms').strip().lower()
bl = 'smi'
BEAMLINE = _env('BEAMLINE', bl).strip().lower()
_PROFILES = {
    'cms': {'local': '/nsls2/auto-storage/cms/legacy/xf11bm/data/2025_2/YZhang/SY_Comm/',
            'dropbox': '/CFN/CMS/AutoFlow_Com/'},
    'smi': {'local': '/nsls2/data/smi/legacy/results/data/2024_3/313765_Zhang/Dropbox_Com/',
            'dropbox': '/CFN/SMI/SeqGrowth_Com/'},
}
_PROFILE = _PROFILES.get(BEAMLINE, _PROFILES[bl])
 

# folder B: the beamline-accessible local comm folder (relay + the bluesky script share it).
LOCAL_DIR = _env('COMM_DIR', _PROFILE['local'])
# the Dropbox folder both relays bridge to (separate per beamline, so a CMS relay can
# never swallow an SMI marker if the two runs overlap).
DROPBOX_DIR = _env('DROPBOX_DIR', _PROFILE['dropbox'])
# Dropbox app token -- SAME account as sys76 (droplet_core/Config.py TOKEN_Dropbox).
DROPBOX_TOKEN = 'R_fvHVzYH3sAAAAAAAAAAX03Z7-QVDJ4zSDF_zf5YV7V0KEwwiY9so95zLRU8Rcx'

STARTX_NAME = 'StartX.npy'          # sys76 -> beamline (INBOUND here)
STOPX_NAME = 'StopX.npy'            # sys76 -> beamline (INBOUND here) -- sequential growth:
                                    #   the LAB owns the collection window, so it sends BOTH
                                    #   the start and the stop; the beamline never makes StopX.
FASTPUSH_NAME = 'Start_Push.npy'    # beamline -> sys76 (OUTBOUND here)

POLL_S = 5.0
HOURS = 144.0


def _now():
    return time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())


class Relay:
    def __init__(self, local_dir=LOCAL_DIR, dropbox_dir=DROPBOX_DIR, token=DROPBOX_TOKEN):
        import dropbox
        self.local_dir = local_dir
        os.makedirs(self.local_dir, exist_ok=True)
        self.dropbox_dir = dropbox_dir if dropbox_dir.endswith('/') else dropbox_dir + '/'
        self.dbx = dropbox.Dropbox(token)
        self.dbx.users_get_current_account()            # fail fast on a bad token
        print('%s beamline relay [%s]: local=%s dropbox=%s'
              % (_now(), BEAMLINE, self.local_dir, self.dropbox_dir))

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
    def pump_inbound(self, name=STARTX_NAME, note='ConFlow_SY2 will pick it up'):
        """A sys76 marker on Dropbox -> folder B, then delete it from Dropbox."""
        data = self._cloud_get(name)
        if data is None:
            return False
        self._local_put(name, data)
        self._cloud_delete(name)
        print('%s relay: %s downloaded cloud->B (%s)' % (_now(), name, note))
        return True

    def pump_inbound_stopx(self):
        """StopX on Dropbox -> folder B. Sequential growth ends its collection window from
        the LAB, so the stop marker travels the same direction as the start; without this
        the beamline would keep collecting until its own safety cap fired."""
        return self.pump_inbound(STOPX_NAME, note='SeqGrowthWatcher will stop collecting')

    def pump_outbound(self):
        """Start_Push in folder B -> Dropbox, then delete the local copy."""
        data = self._local_get(FASTPUSH_NAME)
        if data is None:
            return False
        try:
            self._cloud_put(FASTPUSH_NAME, data)
        except Exception as e:
            print('%s relay: Start_Push upload FAILED (%s); keeping local copy' % (_now(), e))
            return False
        self._local_delete(FASTPUSH_NAME)
        print('%s relay: Start_Push uploaded B->cloud (sys76 will fast-push)' % _now())
        return True

    def pump_once(self):
        inb = stop = out = False
        try:
            inb = self.pump_inbound()
        except Exception as e:
            print('%s relay inbound error: %s' % (_now(), e))
        try:
            stop = self.pump_inbound_stopx()
        except Exception as e:
            print('%s relay stopX error: %s' % (_now(), e))
        try:
            out = self.pump_outbound()
        except Exception as e:
            print('%s relay outbound error: %s' % (_now(), e))
        return {'inbound': inb, 'stopx': stop, 'outbound': out}

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
    ap = argparse.ArgumentParser(description='xf11bm-side Dropbox relay for MultiAutoFlow.')
    ap.add_argument('--hours', type=float, default=HOURS)
    ap.add_argument('--poll', type=float, default=POLL_S)
    ap.add_argument('--once', action='store_true', help='single pump then exit (test)')
    args = ap.parse_args()
    r = Relay()
    if args.once:
        print(r.pump_once())
    else:
        r.run(hours=args.hours, poll_s=args.poll)
