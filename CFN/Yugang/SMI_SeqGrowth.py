#!/usr/bin/python
# -*- coding: utf-8 -*-
# vi: ts=4 sw=4
"""SMI (12-ID) beamline acquisition for the three-reactor droplet block.

Run it inside the SMI bluesky profile, AFTER the usual base file::

    %run -i /home/xf12id/SWAXS_user_scripts/CFN/Yugang/YZhang_SMI_Base.py
    %run -i /home/xf12id/SWAXS_user_scripts/CFN/Yugang/SMI_SeqGrowth.py
    # ...or straight from the proposal folder sync_to_smi.sh pushes to:
    # /nsls2/data/smi/proposals/2026-2/pass-317378/projects/controls/SMI_SeqGrowth.py

    DR.check()                       # preflight: motors, positions, folder B
    DR.collect_once('AgBH')          # ONE sweep, right now
    DR.run_manual('DR_run7', run_time=3*3600)      # timed run, no handshake
    DR.run_auto(run_time=14*3600)                  # StartX/StopX windows from the lab

TWO ACQUISITION MODES, one measuring loop
-----------------------------------------
* **manual**  (``collect_once`` / ``run_manual``) — you name the run and you say how long.
  Nothing is read from the comm folder; the lab GUI is not involved. This is the mode for
  alignment, a calibrant, or any run you drive by hand.
* **auto**    (``run_auto``) — the lab owns the window. The loop
  waits for ``StartX.npy``, measures under the filename carried in it, and stops on
  ``StopX.npy``. See HANDSHAKE below.

Both modes share ``_collect_loop`` — same naming, same reactor cycling, same beam-damage
tweak — so a frame taken by hand and a frame taken in a window are named the same way.

GEOMETRY (2026C2)
-----------------
Three reactors in a horizontal row, selected by **MDrive3 (``MDrive.m3``) = X**. The Huber
stage (X -28, Y -30, Z 2) is still set by hand; ``stage.y`` is then driven only within the
beam-damage raster below, never to change the alignment::

    R0 = 50 mm   (48-53)      R1 = 85 mm   (82-88)      R2 = 120 mm  (117-123)

BEAM-DAMAGE TWEAK (long runs) -- a raster
-----------------------------------------
Re-exposing one spot for hours cooks it. Each sweep steps every reactor to the NEXT spot
of a raster: X +/-1.2 mm at 0.2 mm = **12 columns**, and (when the height is switched on)
Y +/-1.0 mm at 0.2 mm = 10 rows crossed with them, filling a row of X before dropping
0.2 mm in height::

    R0@p00 -> R1@p00 -> R2@p00 -> R0@p01 -> ... -> p11 (row done, y steps) -> p12 -> ...

**THE HEIGHT IS OFF BY DEFAULT (2026-08-01).** ``TWEAK_Y_RADIUS_MM`` is 0.0, so ``stage.y``
is never commanded: X-only stepping, 12 spots, revisited every ~35 min at 3 min a sweep.
The 08-01 collection stopped dead part-way through the night with ``stage.y`` stuck, and a
blocking move on a stuck axis hangs the loop forever (see ACQUISITION SAFETY below). Turn
the height back on for one session with ``DR.set_tweak(y_radius=1.0)`` -- ONLY after the
axis has been proven to move by hand.

When it is on, the height raster is centred on the CONFIGURED alignment
``TWEAK_Y_CENTER_MM`` (-30.0, the Huber Y above), not on a motor read-back -- a read-back
that came back empty is why the 07-31 night ran with the height never moving at all.
``DR.park_y()`` returns the stage to that centre. Re-aligned? Set ``TWEAK_Y_CENTER_MM`` (or
call ``DR.set_y_center(<new>)`` for one session); ``setup_beamline`` compares the constant
with the live read-back and refuses to drive Y if they differ by more than
``TWEAK_Y_SAFE_MM``. ``DR.y_is_driven()`` is the one place that answers "will this run
touch the height?" -- preflight, the moves and the parking all ask it, so what ``DR.check()``
prints is what the loop does.

The spot index is in the file name (``_p07_``) and so are both true motor read-backs
(``_x051.40_y77.40_``). ``tweak=False`` pins every frame to the reactor centre and touches
the height not at all.

ACQUISITION SAFETY
------------------
Two things were wrong on the 08-01 night and both are fixed here:

* every move is bounded by ``MOVE_TIMEOUT_S`` (180 s). ``RE(bps.mv(...))`` waits on the
  move status with no timeout, so an axis that never gets there blocks the loop forever --
  no deadline check, no ``StopX``, no mail, just silence;
* the move happens INSIDE the frame's ``try``. It used to sit outside, so a move that
  raised walked straight out of the run loop: collection stopped with no frame-error
  count, no page and no "ACQUISITION STOPPED" mail. Now a bad move is a frame error like
  any other -- counted, mailed, backed off, and after ``max_frame_errors`` it stops the
  run loudly.

TEMPERATURE IN THE FILE NAME (auto mode)
----------------------------------------
The block's set-point is not measured here -- it is *told* to us. Every time the lab
reaches a new set-point it drops **TempX.npy** into folder B, and from that frame on the
name carries ONE ``_T<value>_`` token::

    DR_AuC8C12_b01_R0_T25.0_p03_...        <- RT hold
    DR_AuC8C12_b01_R0_T40.0_p04_...        <- after TempX(40),  heating
    DR_AuC8C12_b01_R0_TC40.0_p09_...       <- after TempX(40),  COOLING

``TC`` marks the cool-down leg. A heat/cool ramp visits every set-point twice and the two
passes are not the same sample -- the second has been through the top of the ramp -- so
they must not share a file family. The lab decides which leg a rung is on and says so in
``payload['temp_leg']`` ('heat' / 'cool'); a marker without one means heating, which is
what every name meant before this field existed.

The token is REBUILT for every frame, never appended, so a name can never end up with two
temperatures in it. The opening T comes from StartX's ``payload['temp_c']``.

################################################################################
# HANDSHAKE -- StartX / TempX / StopX (auto mode).
#
# The synthesis machine (sys76) owns the collection window ENTIRELY:
#
#   sys76 GUI  --writes StartX/TempX/StopX.npy-->  folder A
#   sys76      Dropbox relay        : folder A  -> Dropbox   (uploads, deletes local)
#   beamline   bl_relay.py      : Dropbox   -> folder B  (downloads, deletes on Dropbox)
#   beamline   THIS FILE (bluesky)  : watches folder B, measures between Start and Stop
#
# The beamline creates NOTHING. It does not make StopX, and it does not have to reply --
# Start_Push is optional and off by default (send_ack=True writes a dummy one if some
# older lab-side script still waits for it).
#
# The sample name comes from the StartX marker: payload['filename'] (the lab's batch
# filename, e.g. DR_AsPrepAu_C8C12C16_b01), so the beamline files and the
# synthesis log line up without anyone typing a batch number.
#
# StartX OPENS the window, StopX CLOSES it. TempX does NEITHER: it arrives inside an open
# window, only updates the temperature that goes into the name, and is consumed between
# frames like StopX. A TempX seen while idle still updates T -- it is the current
# set-point of the block, whether or not we are collecting.
#
# The marker file is a pickled dict saved with np.save:
#   {'method': <filename>, 'signal': 'startX'|'stopX'|'tempX', 'ts': '...',
#    'payload': {'filename', 'case_id', 'batch', 'n_batches', 'reactors',
#                'recipes': {reactor: {reagent: uL}}, 'notes': {reactor: str},
#                'temp_c', 'procedure', 'expected_s'}}
# Whoever CONSUMES a marker deletes it -- that is the whole protocol.
################################################################################

EMAIL / SMS DURING THE RUN
--------------------------
Window opened, window closed, every temperature change and any frame that raises are
mailed to ``MAIL_TO`` (see the mail block below). It is best effort in a daemon thread:
if the beamline cannot reach the SMTP server, it says so ONCE and the run carries on.
``SMI_SeqGrowth.MAIL_ENABLED = False`` (or ``export DC_MAIL=0``) turns it off.

Everything it borrows from the session -- ``RE``, ``bp``, ``bps``, ``MDrive``, ``stage``,
``pil2M``, ``pil900KW``, ``pil2M_pos``, ``det_exposure_time``, ``sample_id``, ``save_ova``,
``setup_ova``, ``move_waxs``, ``waxs``, ``user_name`` -- comes from YZhang_SMI_Base.py.
It defines no name the base already owns (see the note above ``_sg_time``).
"""

import os
import threading
import time
# `import datetime`, NOT `from datetime import datetime`. `%run -i` shares ONE namespace
# with the profile, and something in it binds the name `datetime` to the MODULE -- with the
# `from` form, whichever file loads last wins and the other one's calls raise. Importing
# the module and spelling out `datetime.datetime` is the form that survives either order.
import datetime

import numpy as np


# --------------------------------------------------------------------------- #
# where things live at SMI
# --------------------------------------------------------------------------- #


def _env(name, default=None):
    """``DC_<name>``, falling back to the legacy ``SY_<name>``, then ``default``.

    DC_ = Droplet Controls, i.e. the software, not a person: the rig is shared. The old
    SY_* names keep working so a session that was started before the rename does not
    silently end up on a different beamline than its partner process.
    """
    return os.environ.get('DC_' + name, os.environ.get('SY_' + name, default))


# folder B -- MUST match LOCAL_DIR in the relay running on THIS machine.
#   SMI : '/nsls2/data/smi/legacy/results/data/2024_1/313765_Zhang/Dropbox_Com/'
#   CMS : '/nsls2/auto-storage/cms/legacy/xf11bm/data/2025_2/YZhang/SY_Comm/'  (NanoSyn.py)
# Change it without editing this file in any of three ways:
#     export DC_COMM_DIR=/nsls2/.../Dropbox_Com/     (before starting bluesky)
#     set_comm_dir('/nsls2/.../Dropbox_Com/')        (in the running session)
#     DR.run_auto(comm_dir='/nsls2/.../Dropbox_Com/')            (one run only)
#
# The cycle is 2024_1 here and 2024_3 in `self.base` below, and that is NOT a typo: the
# comm folder is the one the bluesky session can actually reach, the data root is where
# the cycle's results live. They were once made to agree, and the run looked healthy on
# both consoles while the relay wrote every marker into a folder nobody was watching.
# bl_relay.py, SeqGrowthWatcher.py and protocols/config/auto_flow.py all spell this same
# string; a test pins all four together.
COMM_DIR = _env(
    'COMM_DIR',
    '/nsls2/data/smi/legacy/results/data/2024_1/313765_Zhang/Dropbox_Com/')

STARTX_NAME = 'StartX.npy'        # lab -> beamline: START collecting under payload['filename']
STOPX_NAME = 'StopX.npy'          # lab -> beamline: STOP collecting (the lab owns the window)
TEMPX_NAME = 'TempX.npy'          # lab -> beamline: the block reached a new set-point. Opens
                                  #   and closes NOTHING -- it only changes the _T<value>_
                                  #   token in the file name from the next frame on.
FASTPUSH_NAME = 'Start_Push.npy'  # beamline -> lab: optional dummy ack, off by default

# WAXS detector angle for the run. setup_beamline() MOVES the waxs motor here, and the file
# name then uses the motor's own read-back -- so the name can never disagree with the optic.
# Set it before starting: SMI_SeqGrowth.WAXS_ANGLE = 20 (or pass waxs_angle= to the run).
WAXS_ANGLE = 16

# ---- reactor geometry, 2026C2 -------------------------------------------------------
# MDrive3 X (mm) of each reactor, from the alignment written into 2026C2_Flow.py:
#     Reactor 1: 50 (48-53)   Reactor 2: 85 (82-88)   Reactor 3: 120 (117-123)
# The bracketed ranges are the width of each reactor -- that is why the tweak window below
# stays small: it has to remain inside the reactor with a margin at both ends.
#POS_DICT = {'R0': 50.0, 'R1': 85.0, 'R2': 120.0}
#POS_DICT = {'R0': 50.6, 'R1': 85.6, 'R2': 120.6}
#POS_DICT = {'R0': 40.5, 'R1': 90, 'R2': 130} #Cu 600uL
#POS_DICT = {'R0': 48.1, 'R1': 89.8, 'R2': 130} #Cu 3000uL 
POS_DICT = {'R0': 42, 'R1': 91, 'R2': 132} #Cu 600uL

REACTORS = ['R0', 'R1', 'R2']            # default order; DR.set_reactors(1|2|3|[...]) narrows it

'''
08/02/26 2026C2 SMI
Cu2O Synthesis Stage (600 uL): 

Huber Stage: X: 9, Y:-29.9 , Z:4.5
Reactor M3(hard limit) = 40-135

R0: 37(40 limit)-47 (center: 42)
R1: 82.5-92.5 (center: 87.5)
R2: 127.5-137.5(135 limit) (center: 132.5)



08/03/26 2026C2 SMI
Cu2O Synthesis Stage (3000 uL): 

Huber Stage: X: 9, Y: -39.9, Z:12
Reactor M3(hard limit) = 40-135

R0: 41.7 (40 limit)-47 (center: 41.7)
R1: 82.5-92.5 (center: 87.5)
R2: 127.5-137.5(135 limit) (center: 132.5)
'''


##

# ---- beam-damage tweak: a 2-D raster ------------------------------------------------
# X (MDrive3) +/-1.2 mm at 0.2 mm = 12 columns; Y (stage.y) +/-1.0 mm at 0.2 mm = 10 rows.
# 0.2 mm is about the beam width, so neighbouring spots do not overlap.
#
# The 07-30 overnight moved in X ONLY -- 12 spots, revisited every ~35 min at 3 min a
# sweep, and the damage was visible anyway. Adding the height turns 12 spots into 120:
# the walk fills a row of X, drops 0.2 mm, and fills the next one, so a spot is not
# revisited for ~6 h. Change either axis with DR.set_tweak(radius, step, y_radius, y_step).
#
# TWEAK_Y_RADIUS_MM IS 0.0 -- THE HEIGHT IS OFF (2026-08-01). stage.y stuck part-way
# through the 08-01 night and the collection stopped there. Radius 0 means ONE row, and
# one row now means the axis is not commanded at all (DR.y_is_driven() -> False): not by
# goto_Pos, not by park_y. It used to mean "one row, still driven to the centre on every
# single frame" while DR.check() printed 'Y raster off' -- the preflight said one thing
# and the loop did another. Put the height back with DR.set_tweak(y_radius=1.0) once the
# axis has been moved by hand and comes back.
#
# The centre is a NUMBER IN THIS FILE, not a read-back. The first version recorded
# whatever stage.y happened to read at setup_beamline() and refused to move if it could
# not read one -- which is how the 07-31 night ran with the height never moving at all
# and nothing but one printed line to say so. A configured centre cannot fail that way:
# TWEAK_Y_CENTER_MM is the Huber height this rig is aligned at (X -28, Y -30, Z 2), so
# the raster is always +/-TWEAK_Y_RADIUS_MM around -30 whether or not the motor answers.
#
# If you re-align the height, change this constant (or call DR.set_y_center(<new>) for
# one session). setup_beamline() compares it against the live read-back and shouts if
# they disagree by more than TWEAK_Y_SAFE_MM -- that guard is what stops a stale constant
# from turning the first frame into a 100 mm blind move.
TWEAK_RADIUS_MM = .4#1.2
TWEAK_STEP_MM = 0.2
TWEAK_Y_CENTER_MM = -26 #-30.0
TWEAK_Y_RADIUS_MM = 0.0      # 0 = the height is NOT driven (08-01: stage.y stuck)
TWEAK_Y_STEP_MM = 0.2
TWEAK_Y_SAFE_MM = 5.0        # refuse to drive Y if the stage is further than this away

# How long ONE move may take before it is called a failure, in seconds. This exists
# because RE(bps.mv(...)) waits on the move status with NO timeout: a stuck axis does not
# raise, it blocks -- and the loop's deadline / StopX / max_collect_min checks all live
# after the move, so none of them can fire while it is hung. That is exactly how the
# 08-01 night ended: collection simply stopped, with no error and no mail.
# A timed-out move stops the axis, raises, and is then counted as a frame error.
# Generous on purpose -- a long MDrive3 traverse is seconds, not minutes.
# Set to 0 (or None) to go back to an unbounded RE(bps.mv(...)).
MOVE_TIMEOUT_S = 180.0

# How long to wait after a frame RAISES before trying the next one. Long enough that a
# detector re-arming is given a chance, short enough that a flaky night still collects.
FRAME_ERROR_BACKOFF_S = 2.0

# ---- who gets paged from the beamline -------------------------------------------------
# Same gmail relay the lab side uses (droplet_core/Message.py). Everything here can be
# overridden from the environment before bluesky starts, so nothing has to be edited at
# 3 a.m.:
#     export DC_MAIL=0                        # no mail at all from the beamline
#     export DC_MAIL_TO=yuzhang@bnl.gov,wliu1@bnl.gov
#     export DC_MAIL_USER=... DC_MAIL_PASS=... DC_MAIL_HOST=... DC_MAIL_PORT=587
# NSLS-II hosts do not always have outbound SMTP. That is fine: the first failure prints
# once, mailing switches itself off, and the run is untouched.
MAIL_ENABLED = _env('MAIL', '1').strip().lower() not in ('0', 'no', 'off', 'false')
MAIL_TO = [a.strip() for a in _env(
    'MAIL_TO', 'yuzhang@bnl.gov').replace(';', ',').split(',') if a.strip()]
MAIL_HOST = _env('MAIL_HOST', 'smtp.gmail.com')
MAIL_PORT = int(_env('MAIL_PORT', '587'))
MAIL_USER = _env('MAIL_USER', 'dropletcfnuser@gmail.com')
MAIL_PASS = _env('MAIL_PASS', 'ymjv efds hbrc dqfq')   # gmail app password
MAIL_TIMEOUT_S = 20.0        # never let a dead SMTP server hold a thread forever
MAIL_MIN_INTERVAL_S = 30.0   # per-subject throttle, so an error loop cannot spam the phone

# This file is loaded with `%run -i` INTO the same namespace as YZhang_SMI_Base.py, so any
# module-level name it defines OVERWRITES the base's. Two things are deliberately not
# defined here for that reason:
#   * ``user_name`` -- the base sets it ('YZ'); measure_one() reads whatever is in the
#     namespace at measure time, so changing it in the session just works.
#   * ``get_current_time`` -- the base's takes no arguments and returns '%Y-%m-%d-%H-%M-%S';
#     redefining it would silently change file names everywhere else in the session. The
#     private ``_sg_time`` below is used instead.


def _sg_time(pattern='%Y_%m_%d_%H_%M_%S'):
    """Timestamp for sample names. Private: do NOT name it get_current_time -- that name
    belongs to YZhang_SMI_Base.py and the whole session shares one namespace."""
    return datetime.datetime.today().strftime(pattern)


def _sg_user_name():
    """The base file's ``user_name`` (read at call time, so the session can change it)."""
    return str(globals().get('user_name', 'YZ'))


# --------------------------------------------------------------------------- #
# paging -- best effort, in a daemon thread, NEVER in the way of a frame
# --------------------------------------------------------------------------- #

_MAIL_LAST = {}          # subject/dedup key -> time of the last send
_MAIL_FAILS = [0]        # consecutive failures; 3 in a row switches mailing off


def mail(subject, body='', key=None, min_interval_s=None, sync=False):
    """Email the operators about something that happened during the run.

    Called for: window opened, window closed, every temperature change, and any frame
    that raised. It NEVER raises and it never blocks the acquisition -- the SMTP
    conversation happens in a daemon thread with a hard timeout, so a beamline host with
    no route to the internet costs one log line, not a night of data.

    ``key`` (default = subject) is throttled to one message per ``min_interval_s``.
    ``sync=True`` waits for the send -- only used by ``mail_test()``.
    """
    if not MAIL_ENABLED or not MAIL_TO:
        return False
    if _MAIL_FAILS[0] >= 3:
        return False
    gap = MAIL_MIN_INTERVAL_S if min_interval_s is None else float(min_interval_s)
    dedup = key or subject
    now = time.time()
    if gap and (now - _MAIL_LAST.get(dedup, 0.0)) < gap:
        return False
    _MAIL_LAST[dedup] = now

    text = '%s\n\n%s\nSMI_SeqGrowth on %s at %s' % (
        body or subject, '-' * 40, os.uname()[1] if hasattr(os, 'uname') else '?',
        _sg_time('%Y-%m-%d %H:%M:%S'))

    def _send():
        import smtplib
        from email.mime.text import MIMEText
        try:
            msg = MIMEText(text)
            msg['Subject'] = str(subject)
            msg['From'] = MAIL_USER
            msg['To'] = ', '.join(MAIL_TO)
            with smtplib.SMTP(MAIL_HOST, MAIL_PORT, timeout=MAIL_TIMEOUT_S) as server:
                server.starttls()
                server.login(MAIL_USER, MAIL_PASS)
                server.send_message(msg)
            _MAIL_FAILS[0] = 0
        except Exception as exc:
            _MAIL_FAILS[0] += 1
            print('SMI_SeqGrowth: mail failed (%d/3): %s' % (_MAIL_FAILS[0], exc))
            if _MAIL_FAILS[0] >= 3:
                print('SMI_SeqGrowth: mail switched OFF for this session '
                      '(SMI_SeqGrowth.MAIL_ENABLED / _MAIL_FAILS to re-arm). '
                      'The run is NOT affected.')

    if sync:
        _send()
        return _MAIL_FAILS[0] == 0
    threading.Thread(target=_send, name='sg_mail', daemon=True).start()
    return True


def mail_test(subject='SMI_SeqGrowth: mail test'):
    """Send one mail NOW and say whether it worked. Run it once at the start of a beamtime
    -- it is the only way to find out that the host has no SMTP route before you need it."""
    _MAIL_FAILS[0] = 0
    _MAIL_LAST.pop(subject, None)
    ok = mail(subject, 'If you are reading this, beamline paging works.',
              min_interval_s=0.0, sync=True)
    print('SMI_SeqGrowth: mail to %s -> %s' % (MAIL_TO, 'OK' if ok else 'FAILED'))
    return ok


# --------------------------------------------------------------------------- #
# marker plumbing -- byte-identical protocol to NanoSyn.py (CMS) and to the lab's
# droplet_core/beamline_comm.py encoder. Do not "improve" one side alone.
# --------------------------------------------------------------------------- #

def _marker_path(name, comm_dir=None):
    return os.path.join(comm_dir or COMM_DIR, name)


def _decode_marker(data):
    """Marker .npy bytes -> dict (best effort; {} if it cannot be read)."""
    import io
    try:
        obj = np.load(io.BytesIO(data), allow_pickle=True)
        value = obj.item() if hasattr(obj, 'item') else obj
        return dict(value) if isinstance(value, dict) else {'raw': value}
    except Exception as exc:
        print('SMI_SeqGrowth: marker decode failed: %s' % exc)
        return {}


def consume_marker(name, comm_dir=None, n_loop=3, sleep_time=0.05):
    """Read + DELETE one marker, or return None if it is not there.

    Retries the read a few times: the relay writes the file in another process, so a
    zero-length/partial read is possible for a moment. Deleting is what tells the lab
    side (and this loop) that the marker has been acted on -- never leave it in place.
    """
    path = _marker_path(name, comm_dir)
    if not os.path.exists(path):
        return None
    data = None
    for _ in range(int(n_loop)):
        try:
            with open(path, 'rb') as handle:
                data = handle.read()
            if data:
                break
        except (IOError, OSError):
            pass
        time.sleep(sleep_time)
    try:
        os.remove(path)
    except OSError:
        pass
    if not data:
        print('SMI_SeqGrowth: %s was empty/unreadable -- discarded.' % name)
        return None
    marker = _decode_marker(data)
    print('SMI_SeqGrowth: consumed %s  ts=%s  filename=%s' %
          (name, marker.get('ts', '?'), marker_filename(marker)))
    return marker


def peek_markers(comm_dir=None):
    """What is sitting in folder B right now, WITHOUT consuming anything.

    Safe to call while a run is serving windows -- unlike consume_marker(), which would
    eat the marker the run loop is waiting for. An empty list is the healthy state.
    """
    cdir = comm_dir or COMM_DIR
    try:
        names = sorted(n for n in os.listdir(cdir) if not n.endswith('.tmp'))
    except OSError as exc:
        print('SMI_SeqGrowth: cannot list %s: %s' % (cdir, exc))
        return []
    print('SMI_SeqGrowth: folder B %s -> %s' % (cdir, names or 'empty (nothing stuck)'))
    return names


def marker_filename(marker, default='seq_growth'):
    """The lab's batch filename carried by a marker -- what the samples get named after."""
    payload = (marker or {}).get('payload') or {}
    return str(payload.get('filename') or (marker or {}).get('method') or default)


def marker_temp(marker):
    """The set-point (deg C) a marker carries, or None if it carries none.

    StartX brings the opening temperature, TempX brings every later one. Both keep it in
    ``payload['temp_c']``; the top level is checked too so a hand-made marker also works.
    """
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
        if value == value:                       # not nan
            return value
    return None


def marker_temp_leg(marker, default='heat'):
    """Which pass of the ramp a marker belongs to: ``'heat'`` or ``'cool'``.

    A heat/cool ramp visits the same set-points TWICE. The lab decides which pass a rung is
    on (it owns the ladder) and says so in ``payload['temp_leg']``; anything unrecognised,
    or a marker from an older lab build that carries no leg at all, means heating -- which
    is what every name meant before this field existed.
    """
    if not marker:
        return default
    payload = marker.get('payload') or {}
    for value in (payload.get('temp_leg'), marker.get('temp_leg')):
        if value is None:
            continue
        text = str(value).strip().lower()
        if text.startswith('c'):                  # 'cool', 'cooling', 'cool_down'
            return 'cool'
        if text.startswith('h'):
            return 'heat'
    return default


def temp_token(temp_c, leg='heat'):
    """'T40.0' on the way up, 'TC40.0' on the way down, '' when T is unknown.

    ONE decimal, always: 40 and 40.0 and 40.04 all name the same file family, and
    'T40.5' stays as short as the lab writes it.

    The ``C`` matters. 014's ramp goes 40 -> 110 and then 110 -> 25, so every set-point is
    visited twice, and the frames from both passes used to land in one ``_T40.0_`` family.
    They are not the same sample -- the second has been through 110 C -- and nothing in the
    name said so. Cooling frames are now ``_TC40.0_``.
    """
    if temp_c is None:
        return ''
    try:
        temp_c = float(temp_c)
    except (TypeError, ValueError):
        return ''
    if temp_c != temp_c:
        return ''
    return ('TC%.1f' if str(leg).lower().startswith('c') else 'T%.1f') % temp_c


def strip_temp_token(text):
    """Remove any ``T<number>`` / ``TC<number>`` token from a name.

    The name is rebuilt from the base every frame, so the temperature is REPLACED rather
    than appended. This also protects against a lab-side filename that already carries a
    temperature -- without it, ``..._T25.0_b01`` would grow a second one at 40 C.

    Both spellings are stripped, and by BOTH: a heating frame must not keep the ``TC`` of
    the cool-down rung before it, and vice versa.
    """
    parts = str(text).split('_')
    kept = []
    for part in parts:
        for prefix in ('TC', 'T'):
            if len(part) > len(prefix) and part.startswith(prefix):
                try:
                    float(part[len(prefix):])
                except ValueError:
                    continue
                break                             # it is a temperature token -- drop it
        else:
            kept.append(part)
    return '_'.join(p for p in kept if p != '')


def _safe_name(text):
    """Keep sample names filesystem-safe (they become file names on the detector)."""
    out = []
    for ch in str(text):
        out.append(ch if (ch.isalnum() or ch in '-_.') else '_')
    return ''.join(out).strip('_') or 'x'


def set_comm_dir(path):
    """Point the handshake at a different folder B. It must be the same folder the
    SMI-side relay downloads into."""
    global COMM_DIR
    COMM_DIR = str(path)
    print('SMI_SeqGrowth: COMM_DIR -> %s  (exists=%s)' % (COMM_DIR, os.path.isdir(COMM_DIR)))
    return COMM_DIR


def send_dummy_ack(filename, comm_dir=None):
    """Optional Start_Push reply. The sequential-growth flow does NOT need it -- the lab
    sends both StartX and StopX -- so this is only for an older lab script that waits."""
    import io
    marker = {'method': str(filename), 'signal': 'start_fast_push',
              'ts': _sg_time('%Y-%m-%d_%H:%M:%S'),
              'payload': {'filename': str(filename), 'dummy': True}}
    buf = io.BytesIO()
    np.save(buf, marker, allow_pickle=True)
    path = _marker_path(FASTPUSH_NAME, comm_dir)
    tmp = path + '.tmp'
    try:
        with open(tmp, 'wb') as handle:
            handle.write(buf.getvalue())
        os.replace(tmp, path)
        print('SMI_SeqGrowth: wrote dummy %s for %s' % (FASTPUSH_NAME, filename))
        return True
    except (IOError, OSError) as exc:
        print('SMI_SeqGrowth: dummy ack failed: %s' % exc)
        return False


# --------------------------------------------------------------------------- #
# motors -- 2026C2: MDrive3 (MDrive.m3) is X and is the ONLY axis this file drives.
# --------------------------------------------------------------------------- #
#   X (motorX): MDrive.m3  -- reactor-to-reactor AND the beam-damage raster. DRIVEN.
#   Y (motorY): stage.y    -- droplet height. Set by hand with the Huber stage, and from
#                             07-31 also DRIVEN, but only +/-1 mm around that hand setting
#                             as the second axis of the raster. It never selects a reactor.
# NOTE the change from the 2025 block, where X was MDrive.m5 and m3 was the read-only
# height. m3 is now the horizontal axis -- an old set_motors(MDrive.m5, MDrive.m3) would
# drive the wrong axis.
# Resolved lazily so this file can be read/parsed before the MDrive IOC is up (and so it
# can be tested off-site). Call set_motors() if the profile names them differently.
try:
    motorX = MDrive.m3      # noqa: F821  (injected by the SMI bluesky profile)
except NameError:
    motorX = None
    print('SMI_SeqGrowth: MDrive not in the namespace yet -- '
          'run the SMI base profile, then set_motors().')
try:
    motorY = stage.y        # noqa: F821  height: read for the file name, rastered +/-1 mm
except NameError:
    motorY = None


def set_motors(x=None, y=None):
    """Bind the horizontal axis (x) and the height (y).

        set_motors(MDrive.m3, stage.y)      # 2026C2 default

    X is always driven. Binding Y does NOT by itself make the height move -- with
    ``TWEAK_Y_RADIUS_MM = 0`` (the 08-01 default) it is bound so it can be READ into the
    file name, and nothing commands it. ``DR.set_tweak(y_radius=1.0)`` switches it on.
    """
    global motorX, motorY
    if x is not None:
        motorX = x
    if y is not None:
        motorY = y
    print('SMI_SeqGrowth: motorX=%s (reactor + raster X)  motorY=%s (raster Y %s)'
          % (getattr(motorX, 'name', motorX), getattr(motorY, 'name', motorY),
             ('+/-%.1f mm' % TWEAK_Y_RADIUS_MM) if TWEAK_Y_RADIUS_MM > 0
             else 'OFF -- read only'))
    return motorX, motorY


def _axis_position(motor):
    """motor.position, or nan when the motor is not bound (so naming never raises)."""
    try:
        return float(motor.position)
    except Exception:
        return float('nan')


class MoveTimeout(RuntimeError):
    """An axis did not reach its target inside ``MOVE_TIMEOUT_S``."""


def _move_axes(pairs, timeout=None):
    """Move ``[(motor, target), ...]`` together, and give up after ``timeout`` seconds.

    ``RE(bps.mv(motor, x))`` waits on the move status forever. A motor that will not move
    therefore does not raise -- it HANGS, holding the run loop at the move, so the
    deadline, the ``StopX`` check and the frame-error counter (all of which come later in
    the loop) can never run. On 2026-08-01 ``stage.y`` stuck and the night's collection
    stopped right there: no exception, no mail, no frames.

    So: start both axes without waiting, poll their statuses, and if the clock runs out
    stop the motors and raise ``MoveTimeout`` -- which the run loop counts as a frame
    error, mails, and eventually stops the run with a page.

    The status path needs ``motor.move(target, wait=False)`` (ophyd). Anything that does
    not offer it -- and ``timeout`` of 0/None -- falls back to the original
    ``RE(bps.mv(...))``. Falling back after a partial start is safe: these are ABSOLUTE
    moves to the same targets, so re-commanding them is a no-op.
    """
    pairs = [(m, float(x)) for m, x in pairs if m is not None]
    if not pairs:
        return None
    statuses = None
    if timeout:
        try:
            statuses = [m.move(x, wait=False) for m, x in pairs]
            if any(not hasattr(s, 'done') for s in statuses):
                statuses = None                      # not an ophyd status -- cannot poll
        except Exception as exc:                     # older/other API: no wait= kwarg
            print('SMI_SeqGrowth: %s has no timed move (%s) -- falling back to '
                  'RE(bps.mv(...)), which cannot time out.'
                  % (getattr(pairs[0][0], 'name', pairs[0][0]), exc))
            statuses = None
    if statuses is None:
        flat = []
        for m, x in pairs:
            flat += [m, x]
        RE(bps.mv(*flat))                            # noqa: F821  (RE/bps from the profile)
        return None
    deadline = time.time() + float(timeout)
    while not all(getattr(s, 'done', True) for s in statuses):
        if time.time() >= deadline:
            for m, _ in pairs:
                try:
                    m.stop()
                except Exception:
                    pass                             # best effort -- the raise is the point
            raise MoveTimeout(
                '%s did not arrive within %.0f s (targets %s, now %s)'
                % (', '.join(str(getattr(m, 'name', m)) for m, _ in pairs), float(timeout),
                   [x for _, x in pairs],
                   [_num(_axis_position(m)) for m, _ in pairs]))
        time.sleep(0.05)
    for s in statuses:                               # a status can finish UNhappily
        try:
            exc = s.exception()
        except Exception:
            exc = None
        if exc is not None:
            raise exc
        if getattr(s, 'success', True) is False:
            raise RuntimeError('move failed: %s' % (s,))
    return None


def _idle_run_engine():
    """Best-effort: put the RunEngine back to idle after a frame raised.

    A plan that blew up can leave RE paused, and then EVERY later ``RE(...)`` raises
    'The RunEngine is paused' -- one bad exposure would poison the rest of the night.
    Never raises: if there is no RE, or it will not abort, we say so and carry on.
    """
    engine = globals().get('RE')
    state = getattr(engine, 'state', None)
    if engine is None or state in (None, 'idle'):
        return False
    for method in ('abort', 'stop', 'halt'):
        call = getattr(engine, method, None)
        if not callable(call):
            continue
        try:
            call()
            print('SMI_SeqGrowth: RunEngine was %r -- RE.%s() -> %r'
                  % (state, method, getattr(engine, 'state', '?')))
            return True
        except Exception as exc:
            print('SMI_SeqGrowth: RE.%s() failed: %s' % (method, exc))
    return False


def _num(value, width=6, prec=2):
    """Zero-padded number for a file name, or 'NA' when the axis is not bound.

    '%05.2f' % nan is '  nan' -- SPACES, in a name that becomes a file name on the
    detector. Never let a formatted number reach the name unfiltered.
    """
    try:
        value = float(value)
    except (TypeError, ValueError):
        return 'NA'
    if value != value or value in (float('inf'), float('-inf')):
        return 'NA'
    return ('%0*.*f' % (width, prec, value))


def _waxs_angle():
    """The WAXS angle that goes into the file name.

    Read back from the real ``waxs`` motor whenever the session has one (that is what
    ``move_waxs()`` in YZhang_SMI_Base.py drives), so the name can never disagree with
    where the detector actually is. Falls back to the ``WAXS_ANGLE`` constant off-line.
    """
    motor = globals().get('waxs')
    try:
        return float(motor.position)
    except Exception:
        return float(WAXS_ANGLE)


def _saxs_distance():
    """SAXS detector distance for the file name.

    The profile has spelled this ``pil2M_pos`` and ``pil2m_pos`` in different years and
    both spellings appear in 2026C2_Flow.py. Try both, then give up quietly -- a naming
    detail must never abort a frame at 3 a.m.
    """
    for name in ('pil2M_pos', 'pil2m_pos'):
        holder = globals().get(name)
        try:
            return float(holder.z.position)
        except Exception:
            continue
    return float('nan')


def tweak_offsets(radius=None, step=None):
    """The beam-damage spot list along ONE axis: offsets (mm) from the centre.

    Default +/-1.2 mm at 0.2 mm = **12 spots**, from -1.2 to +1.0. The +1.2 end is left
    out on purpose so wrapping from the last spot to the first is one full step, not a
    double exposure of the same place.
    """
    radius = TWEAK_RADIUS_MM if radius is None else float(radius)
    step = TWEAK_STEP_MM if step is None else float(step)
    if step <= 0 or radius <= 0:
        return [0.0]
    n = int(round(2.0 * radius / step)) or 1
    return [round(-radius + i * step, 4) for i in range(n)]


def tweak_offsets_y(radius=None, step=None):
    """The HEIGHT half of the raster: offsets (mm) from the hand-set stage height.

    Default +/-1.0 mm at 0.2 mm = **10 rows**. Pass ``radius=0`` for the old behaviour --
    X-only stepping, with the height left exactly where the alignment put it.
    """
    radius = TWEAK_Y_RADIUS_MM if radius is None else float(radius)
    step = TWEAK_Y_STEP_MM if step is None else float(step)
    if step <= 0 or radius <= 0:
        return [0.0]
    n = int(round(2.0 * radius / step)) or 1
    return [round(-radius + i * step, 4) for i in range(n)]


# --------------------------------------------------------------------------- #

class DropletReactor(object):
    """Three-reactor droplet block for in-situ SAXS/WAXS of nanoparticle synthesis.

    R0/R1/R2 sit in a horizontal row, so a reactor is ONE number: its MDrive3-X position.
    One measuring loop serves every mode:

        DR.check()                                  preflight, measures nothing
        DR.collect_once('AgBH')                     one sweep of the selected reactors
        DR.run_manual('DR_run7', run_time=3*3600)   timed, no handshake
        DR.run_auto(run_time=14*3600)               StartX/StopX windows from the lab
    """

    pos_dict = dict(POS_DICT)

    def __init__(self, name='seq_growth', base=None, comm_dir=None, pos_dict=None,
                 reactors=None, tweak=True, **kwargs):
        self.name = name
        self.sample_pref = name
        self.sample_name = name
        # SMI data root (only used for messages -- the DAQ writes where the profile says).
        self.base = base or '/nsls2/data/smi/legacy/results/data/2024_3/313765_Zhang/'
        # folder B for the StartX/StopX handshake (see COMM_DIR at the top of this file).
        self.comm_dir = comm_dir or COMM_DIR
        self.pos_dict = dict(pos_dict) if pos_dict else dict(DropletReactor.pos_dict)
        self.reactors = self._as_reactors(reactors) if reactors else list(REACTORS)
        self.tweak = bool(tweak)
        self.offsets = tweak_offsets()          # X columns, mm from the reactor centre
        self.offsets_y = tweak_offsets_y()      # Y rows, mm from the configured height
        # The height the raster is centred on -- CONFIGURED, not measured (see
        # TWEAK_Y_CENTER_MM). A number here means Y moves; only an explicit
        # set_y_center(None) turns the height off.
        self.y_center = TWEAK_Y_CENTER_MM
        # Where in the spot list the next sweep starts. It KEEPS COUNTING across windows
        # and across runs, so batch 2 does not land back on batch 1's burnt spots.
        self.pos_index = 0
        # Last set-point the lab told us about (StartX payload, then every TempX). None
        # means "unknown" and simply leaves the _T..._ token out of the names.
        self.temp_c = None
        # ...and which leg of the ramp it was on: 'heat' -> _T40.0_, 'cool' -> _TC40.0_.
        # A ramp visits every set-point twice and the two passes are different samples.
        self.temp_leg = 'heat'
        self.naming_scheme = ['name', 'extra', 'exposure_time']

    # ---- reactor selection and positions -----------------------------------

    def _as_reactors(self, spec):
        """Accept 1 / 2 / 3, 'R0', 'R0,R2', or ['R0','R2'] -- all mean the same thing."""
        if spec is None:
            return list(self.reactors)
        if isinstance(spec, int) and not isinstance(spec, bool):
            names = list(REACTORS)[:max(1, min(int(spec), len(REACTORS)))]
        elif isinstance(spec, str):
            names = [s.strip() for s in spec.replace(';', ',').split(',') if s.strip()]
        else:
            names = [str(s).strip() for s in spec]
        unknown = [r for r in names if r not in self.pos_dict]
        if unknown:
            raise KeyError('SMI_SeqGrowth: no X position for %s -- known: %s'
                           % (unknown, sorted(self.pos_dict)))
        if not names:
            raise ValueError('SMI_SeqGrowth: no reactors selected')
        return names

    def set_reactors(self, spec):
        """Choose which reactors a run cycles through, and in what order.

            DR.set_reactors(1)              # just R0
            DR.set_reactors(2)              # R0, R1
            DR.set_reactors(['R0', 'R2'])   # skip the middle one
        """
        self.reactors = self._as_reactors(spec)
        print('SMI_SeqGrowth: reactors %s  x=%s' %
              (self.reactors, [self.pos_dict[r] for r in self.reactors]))
        return self.reactors

    def set_reactor_x(self, pos_des, x):
        """Set ONE reactor's X (mm). Use after aligning that reactor by eye."""
        self.pos_dict[pos_des] = float(x)
        print('SMI_SeqGrowth: %s -> x=%.3f' % (pos_des, self.pos_dict[pos_des]))
        return self.pos_dict

    def calibrate(self, x0, pitch=35.0, reactors=('R0', 'R1', 'R2')):
        """Evenly spaced row: R0 at ``x0``, each next reactor ``pitch`` mm HIGHER in X.

        2026C2 is R0=50, R1=85, R2=120 -> ``DR.calibrate(50, 35)``. (The 2025 block ran
        the other way, R0 at the high-X end; the sign lives here so nothing else cares.)
        """
        self.pos_dict = dict((r, float(x0) + i * float(pitch))
                             for i, r in enumerate(reactors))
        print('SMI_SeqGrowth: positions %s' % (self.pos_dict,))
        return self.pos_dict

    def set_tweak(self, radius=None, step=None, on=True, y_radius=None, y_step=None):
        """Resize the beam-damage raster.

            DR.set_tweak(y_radius=0)                           # X only, Y NOT COMMANDED
            DR.set_tweak(1.2, 0.2, y_radius=1.0, y_step=0.2)   # the height back on
            DR.set_tweak(on=False)                             # pin the reactor centre

        ``y_radius=0`` really does leave ``stage.y`` alone now -- it is the 08-01 default
        and it is what ``y_is_driven()`` reports. Before, it only flattened the raster to
        one row: the height was still commanded to the centre on every frame while the
        preflight printed 'Y raster off'.

        Resetting the walk to spot 0 is deliberate: a resized raster is a different set of
        spots, so continuing the old count would land somewhere arbitrary.
        """
        self.offsets = tweak_offsets(radius, step)
        self.offsets_y = tweak_offsets_y(y_radius, y_step)
        self.tweak = bool(on)
        self.pos_index = 0
        print('SMI_SeqGrowth: tweak=%s  %d x %d = %d spot(s)   '
              'X %.2f .. %.2f  Y %.2f .. %.2f mm' %
              (self.tweak, len(self.offsets), len(self.offsets_y), self.n_spots(),
               self.offsets[0], self.offsets[-1],
               self.offsets_y[0], self.offsets_y[-1]))
        print('SMI_SeqGrowth: stage.y will %s'
              % ('be DRIVEN (centre %s)' % _num(self.y_center) if self.y_is_driven()
                 else 'NOT be commanded -- read only, for the file name'))
        return self.offsets, self.offsets_y

    def n_spots(self):
        """How many distinct places on a reactor the raster visits before it repeats."""
        return max(1, len(self.offsets or [0.0])) * max(1, len(self.offsets_y or [0.0]))

    def set_y_center(self, y='config'):
        """Pin the height the raster is centred on.

            DR.set_y_center()          # back to TWEAK_Y_CENTER_MM (-30.0)
            DR.set_y_center(-29.4)     # a different height, this session only
            DR.set_y_center('here')    # wherever stage.y reads RIGHT NOW
            DR.set_y_center(None)      # turn the Y axis off (X-only stepping)

        ``'here'`` is the old default and is now opt-in: reading the motor is the one
        mode that can fail quietly (an unreadable axis used to mean "never move Y"),
        so it has to be asked for.
        """
        if y == 'config':
            y = TWEAK_Y_CENTER_MM
        elif isinstance(y, str):                          # 'here' / 'now' / 'read'
            y = _axis_position(motorY)
        if y is None:
            self.y_center = None
            print('SMI_SeqGrowth: raster Y centre CLEARED -- the height will not move.')
            return None
        try:
            y = float(y)
        except (TypeError, ValueError):
            y = float('nan')
        if y != y:                                        # NaN: the read-back failed
            print('SMI_SeqGrowth: could not read stage.y -- keeping centre %s. '
                  'Pass a number to set it explicitly.' % _num(self.y_center))
            return self.y_center
        self.y_center = y
        print('SMI_SeqGrowth: raster Y centre = %.3f (+/-%.1f mm)'
              % (self.y_center, TWEAK_Y_RADIUS_MM))
        return self.y_center

    def y_is_driven(self):
        """Will this run command ``stage.y``? THE one answer -- ask it, do not re-derive it.

        Three ways to say no, and every one of them has to mean the same thing in the
        preflight, in ``goto_Pos`` and in ``park_y``:

          * ``motorY`` is not bound (``set_motors`` was never given a height),
          * the centre has been cleared -- ``set_y_center(None)``, or the safety veto in
            ``check_y_center`` when the constant and the read-back disagree,
          * the Y raster is one row (``y_radius=0``, the 08-01 default) -- "X-only
            stepping, the height left exactly where the alignment put it".

        The third used to be true of the raster only, not of the motion: with
        ``y_radius=0`` the offset was always 0.0 but ``goto_Pos`` still sent
        ``bps.mv(motorY, -30.0)`` on every frame, and ``DR.check()`` still said the raster
        was off. Two places disagreed about one fact, so this function is now the fact.
        """
        if motorY is None or self.y_center is None:
            return False
        return len(self.offsets_y or [0.0]) > 1

    def check_y_center(self):
        """Is the configured raster centre anywhere near where the stage actually is?

        Returns True when Y is safe to drive. The centre is a constant in this file, so
        the one thing that can go wrong is that the rig was re-aligned and the constant
        was not -- and the first frame would then be a 100 mm blind move. If the live
        read-back is further than ``TWEAK_Y_SAFE_MM`` away, the height is switched OFF
        for the session and the fix is printed in full.

        An axis that cannot be read at all is NOT a veto: unreadable means "cannot
        verify", and refusing to move on that is exactly the silent-no-motion failure
        the configured centre exists to end.
        """
        if not self.y_is_driven():
            return False
        here = _axis_position(motorY)
        if here != here:                                  # NaN -- no read-back available
            print('SMI_SeqGrowth: stage.y does not read back; trusting the configured '
                  'centre %.3f mm.' % float(self.y_center))
            return True
        gap = abs(float(here) - float(self.y_center))
        if gap <= TWEAK_Y_SAFE_MM:
            return True
        print('=' * 78)
        print('SMI_SeqGrowth: REFUSING to drive the height. stage.y reads %.3f but the'
              % float(here))
        print('  raster is configured for %.3f -- %.1f mm apart (limit %.1f).'
              % (float(self.y_center), gap, TWEAK_Y_SAFE_MM))
        print('  The run will step in X only. Fix it with ONE of:')
        print('     DR.set_y_center()          # -> the configured %.1f, if THAT is right'
              % TWEAK_Y_CENTER_MM)
        print("     DR.set_y_center('here')    # -> %.3f, if the stage is where you want it"
              % float(here))
        print('     SMI_SeqGrowth.TWEAK_Y_CENTER_MM = <new>   # permanent, for a re-align')
        print('=' * 78)
        self.y_center = None
        return False

    def park_y(self, force=False):
        """Put the height back on the alignment the raster is centred on.

        Does NOTHING when the height is not being driven -- there is nothing to undo, and
        a run that deliberately never touched ``stage.y`` must not touch it on the way out
        either (that was the last surviving Y move after ``y_radius=0``). ``force=True``
        moves it anyway, for putting a hand-nudged stage back on the alignment.
        """
        if motorY is None or self.y_center is None:
            print('SMI_SeqGrowth: no Y centre recorded -- height left where it is.')
            return None
        if not (force or self.y_is_driven()):
            print('SMI_SeqGrowth: the height was never driven -- leaving stage.y alone '
                  '(DR.park_y(force=True) to send it to %s anyway).' % _num(self.y_center))
            return None
        _move_axes([(motorY, float(self.y_center))], timeout=MOVE_TIMEOUT_S)
        print('SMI_SeqGrowth: motorY parked at %.3f' % float(self.y_center))
        return float(self.y_center)

    def reset_positions(self):
        """Start the spot walk again from the first spot (e.g. after reloading a sample)."""
        self.pos_index = 0
        return self.pos_index

    # ---- the temperature that goes into the name ---------------------------

    def set_temp(self, temp_c, why='set by hand', quiet=False, leg=None):
        """Set the temperature stamped into every following file name.

            DR.set_temp(100)                 # names become ..._T100.0_...
            DR.set_temp(100, leg='cool')     # names become ..._TC100.0_...  (cool-down)
            DR.set_temp(None)                # no temperature in the name at all

        In auto mode this is called for you: once from StartX and again for every TempX,
        and the LAB says which leg of the ramp it is on. Call it by hand for a manual run
        at a known temperature. It changes NOTHING on the block -- the beamline drives no
        heater; it only records what the lab said.
        """
        old, old_tag = self.temp_c, self.temp_tag()
        if leg is not None:
            self.temp_leg = 'cool' if str(leg).lower().startswith('c') else 'heat'
        if temp_c is None:
            self.temp_c = None
        else:
            try:
                self.temp_c = float(temp_c)
            except (TypeError, ValueError):
                print('SMI_SeqGrowth: ignoring a non-numeric temperature %r' % (temp_c,))
                return self.temp_c
        # the TAG is what lands in the file name, so a leg change alone is a real change:
        # 110 -> 110 on the way down is T110.0 -> TC110.0 and must be announced.
        if self.temp_tag() != old_tag and not quiet:
            print('SMI_SeqGrowth: T %s -> %s C  (%s) -- names now carry %r' %
                  (old, self.temp_c, why, self.temp_tag() or '(no T)'))
        return self.temp_c

    def temp_tag(self):
        """The ``T40.0`` / ``TC40.0`` token for the current temperature ('' if unknown)."""
        return temp_token(self.temp_c, getattr(self, 'temp_leg', 'heat'))

    def _consume_temp(self, comm_dir=None, announce=True):
        """Take a TempX marker if one is waiting and update the name temperature.

        Returns the new temperature, or None if there was no marker. Consuming it (read +
        delete) is what stops it from being applied twice.
        """
        marker = consume_marker(TEMPX_NAME, comm_dir or self.comm_dir or COMM_DIR)
        if marker is None:
            return None
        temp_c = marker_temp(marker)
        if temp_c is None:
            print('SMI_SeqGrowth: %s carried no temp_c -- name temperature unchanged.'
                  % TEMPX_NAME)
            return None
        old, old_tag = self.temp_c, self.temp_tag()
        self.set_temp(temp_c, why=TEMPX_NAME, leg=marker_temp_leg(marker))
        # compare TAGS, not temperatures: 110 -> 110 across the top of the ramp is a real
        # rename (T110.0 -> TC110.0) even though the set-point did not move.
        if announce and self.temp_tag() != old_tag:
            mail('SMI: T -> %.1f C %s (%s)'
                 % (self.temp_c, '(cooling)' if self.temp_leg == 'cool' else '(heating)',
                    self.sample_pref),
                 'The block reached %.1f C on the %s leg (was %s).\n'
                 'Frames are now named %s.\nReactors: %s   spot p%02d.'
                 % (self.temp_c, 'cool-down' if self.temp_leg == 'cool' else 'heat-up',
                    old, self.temp_tag(), self.reactors,
                    self.pos_index % self.n_spots()),
                 key='sg_temp', min_interval_s=0.0)
        return self.temp_c

    def _offset(self):
        """The (dx, dy) this sweep uses, in mm, and the flat spot index for the name.

        The walk fills a ROW of X and then drops one Y step, so consecutive sweeps are
        neighbours in X (the cheap move) and the height changes once per row.
        """
        if not self.tweak or not self.offsets:
            return 0.0, 0.0, 0
        xs = self.offsets
        ys = self.offsets_y or [0.0]
        index = int(self.pos_index) % (len(xs) * len(ys))
        return float(xs[index % len(xs)]), float(ys[index // len(xs)]), index

    def goto_Pos(self, pos_des, offset=0.0, offset_y=0.0):
        """Move to a reactor: MDrive3 X to its centre + the raster's X offset, and (only
        when the height is switched on) ``stage.y`` to its centre + the raster's Y offset.

        ``y_is_driven()`` decides -- NOT "is there a centre", which is what this used to
        ask. Under ``y_radius=0`` the offset was 0.0 but the axis was still commanded to
        the centre on every frame, which is not what "X-only stepping" means to anyone
        reading it, and not what ``DR.check()`` printed.

        Both axes go through ``_move_axes``, so a move that does not finish inside
        ``MOVE_TIMEOUT_S`` raises instead of hanging the night.
        """
        x = float(self.pos_dict[pos_des]) + float(offset)
        if self.y_is_driven():
            y = float(self.y_center) + float(offset_y)
            print('Reactor: %s --  motorX -> %.3f (centre %.3f, %+.2f)  '
                  'motorY -> %.3f (centre %.3f, %+.2f)'
                  % (pos_des, x, self.pos_dict[pos_des], offset,
                     y, float(self.y_center), offset_y))
            _move_axes([(motorX, x), (motorY, y)], timeout=MOVE_TIMEOUT_S)
        else:
            print('Reactor: %s --  motorX -> %.3f  (centre %.3f, offset %+.2f)'
                  % (pos_des, x, self.pos_dict[pos_des], offset))
            _move_axes([(motorX, x)], timeout=MOVE_TIMEOUT_S)

    # ---- beamline-specific hooks -------------------------------------------

    def setup_beamline(self, waxs_angle=None, take_camera=False):
        """Put the beamline where the run expects it, once, before the first frame.

        SMI has no ``cms.modeMeasurement()`` -- shutter/mode setup is done by hand. What
        this DOES do is the three things that silently ruin a night if they are skipped:

          * move the real WAXS motor (``move_waxs()`` in YZhang_SMI_Base.py) so the angle
            in every file name is the angle the detector is actually at,
          * arm the OAV camera (``setup_ova()``) so ``save_ova()`` has somewhere to write
            (``take_camera=False`` by default -- turn it on when the OAV is wanted), and
          * check the configured raster centre against where ``stage.y`` actually is.

        Then print the motors so an unbound axis is caught here, not after the night.
        """
        angle = WAXS_ANGLE if waxs_angle is None else float(waxs_angle)
        mover = globals().get('move_waxs')
        if callable(mover):
            print('SMI_SeqGrowth: move_waxs(%s)' % angle)
            mover(angle)
        else:
            print('SMI_SeqGrowth: no move_waxs() in the namespace -- '
                  'set the WAXS angle by hand; names will use WAXS_ANGLE=%s.' % angle)
        if take_camera:
            arm = globals().get('setup_ova')
            if callable(arm):
                arm()       # enables the JPEG plugin + sets the OAV write path
            else:
                print('SMI_SeqGrowth: no setup_ova() -- OAV frames may not be saved.')
        self.check_y_center()
        print('SMI_SeqGrowth: motorX=%s (x=%s)  motorY=%s (y=%s, centre %s, %s)  '
              'waxs=%.2f  det=%s m'
              % (getattr(motorX, 'name', motorX), _num(_axis_position(motorX)),
                 getattr(motorY, 'name', motorY), _num(_axis_position(motorY)),
                 _num(self.y_center), 'DRIVEN' if self.y_is_driven() else 'not commanded',
                 _waxs_angle(), _num(_saxs_distance(), 5, 2)))
        if motorX is None:
            print('SMI_SeqGrowth: WARNING motorX is not bound -- call set_motors() first.')
        if motorY is None and len(self.offsets_y or [0.0]) > 1:
            print('SMI_SeqGrowth: WARNING motorY is not bound -- the raster will step in X '
                  'only. set_motors(MDrive.m3, stage.y) to use the height too.')

    def measure_one(self, sample_name, exp_time, pos=None, marker=None, take_camera=False):
        """Take ONE exposure at the current position under ``sample_name``.

        Stamp the motor positions + detector distance into the name, register it with
        ``sample_id``, count both detectors, then save the OAV camera frame under the
        same scan id.
        """
        dets = [pil2M, pil900KW]                                    # noqa: F821
        # det_exposure_time() is a PLAN in the current profile -- calling it bare does
        # NOTHING (YZhang_SMI_Base.py carries the same FIXME). It has to be run, or every
        # frame silently keeps whatever exposure the previous user left behind.
        RE(det_exposure_time(exp_time, exp_time))                   # noqa: F821
        full_name = '%s_x%s_y%s_det%sm_waxs%s_expt%ss' % (
            sample_name,
            _num(_axis_position(motorX), 6, 2),
            _num(_axis_position(motorY), 5, 2),
            _num(_saxs_distance(), 5, 2),
            _num(_waxs_angle(), 5, 2),
            exp_time,
        )
        full_name = _safe_name(full_name)
        sample_id(user_name=_sg_user_name(), sample_name=full_name)  # noqa: F821
        print("\n\t=== Sample: %s ===\n" % full_name)
        RE(bp.count(dets))                                          # noqa: F821
        self.sample_name = full_name
        if take_camera:
            scan_id = RE.md["scan_id"]                              # noqa: F821
            save_ova(sample=_sg_user_name() + '_' + full_name + 'id_%s' % scan_id)  # noqa: F821
        return full_name

    # ---- preflight ----------------------------------------------------------

    def check(self, comm_dir=None, collect=False, exp_time=1, name='check'):
        """Print everything a run depends on, and (optionally) take one test frame.

        Run this before every campaign. It measures nothing unless ``collect=True``.
        """
        cdir = comm_dir or self.comm_dir or COMM_DIR
        offsets = self.offsets or [0.0]
        offsets_y = self.offsets_y or [0.0]
        print('=' * 72)
        print('SMI_SeqGrowth preflight   %s' % _sg_time('%Y-%m-%d %H:%M:%S'))
        print('  motorX     : %-10s x=%s   (DRIVEN: reactor + raster X)' %
              (getattr(motorX, 'name', motorX), _num(_axis_position(motorX))))
        if self.y_is_driven():
            _y_state = 'DRIVEN: raster Y, centre %s' % _num(self.y_center)
        elif motorY is None:
            _y_state = 'read only -- motorY unbound. set_motors(MDrive.m3, stage.y)'
        elif len(offsets_y) < 2:
            _y_state = 'read only -- NOT COMMANDED (y_radius=0, the 08-01 default)'
        else:
            _y_state = 'read only -- no centre. DR.set_y_center() to switch the height on'
        print('  motorY     : %-10s y=%s   (%s)' %
              (getattr(motorY, 'name', motorY), _num(_axis_position(motorY)), _y_state))
        print('  waxs       : %.2f deg     det: %s m' %
              (_waxs_angle(), _num(_saxs_distance(), 5, 2)))
        print('  reactors   : %s' % (self.reactors,))
        print('  positions  : %s' % (dict((r, self.pos_dict[r]) for r in self.reactors),))
        print('  tweak      : %s   %d x %d = %d spot(s)   X %+.2f .. %+.2f   '
              'Y %+.2f .. %+.2f mm  (next p%02d)' %
              (self.tweak, len(offsets), len(offsets_y), self.n_spots(),
               offsets[0], offsets[-1], offsets_y[0], offsets_y[-1],
               self.pos_index % self.n_spots()))
        print('  comm dir   : %s   (exists=%s)' % (cdir, os.path.isdir(cdir)))
        print('  name T     : %s   (StartX/%s set it in auto mode)' %
              (self.temp_tag() or 'none yet', TEMPX_NAME))
        print('  mail       : %s' %
              (', '.join(MAIL_TO) if (MAIL_ENABLED and MAIL_TO) else 'off -- DC_MAIL/MAIL_TO'))
        print('  user_name  : %s' % _sg_user_name())
        print('=' * 72)
        peek_markers(cdir)
        if motorX is None:
            print('SMI_SeqGrowth: WARNING motorX is not bound -- set_motors(MDrive.m3, stage.y)')
        if collect:
            self.collect_once(name, exp_time=exp_time)
        return {'reactors': list(self.reactors),
                'positions': dict((r, self.pos_dict[r]) for r in self.reactors),
                'comm_dir': cdir, 'comm_ok': os.path.isdir(cdir),
                'tweak': self.tweak, 'n_spots': self.n_spots(),
                'n_spots_x': len(offsets), 'n_spots_y': len(offsets_y),
                'y_center': self.y_center,
                'temp_c': self.temp_c, 'temp_tag': self.temp_tag(),
                'temp_leg': getattr(self, 'temp_leg', 'heat'),
                'mail_to': list(MAIL_TO) if MAIL_ENABLED else []}

    # ---- the one measuring loop --------------------------------------------

    def _collect_loop(self, base_name, exp_time, reactors, tweak=None, interval=0.0,
                      sleep_time=0.0, deadline=None, stop_check=None, max_sweeps=None,
                      note_by_reactor=None, temp_check=None, max_frame_errors=5,
                      take_camera=False, verbosity=3):
        """Cycle the reactors, measuring one frame each, until something says stop.

        Every mode funnels through here, so a manual frame and a handshake frame are
        named and positioned identically. Stopping conditions, checked BETWEEN frames
        (a ``bp.count`` cannot be interrupted, so the loop reacts within one exposure):

            stop_check()  returned something truthy   -> 'stop'  (+ the object)
            deadline      passed                      -> 'deadline'
            max_sweeps    complete sweeps done        -> 'sweeps'
            max_frame_errors consecutive failures     -> 'error'
            Ctrl-C                                    -> 'interrupt'

        ``temp_check`` is called in the same place as ``stop_check`` (auto mode passes the
        TempX consumer): it updates the temperature that goes into the name, and opens or
        closes nothing.

        A frame that RAISES does not end the run. It is mailed, the RunEngine is put back
        to idle, and the loop moves to the next reactor -- one bad exposure at 3 a.m. must
        not cost the remaining hours. ``max_frame_errors`` failures IN A ROW do stop it,
        because by then something is broken rather than flaky.

        Returns ``(n_frames, reason, stop_object)``.
        """
        was_tweak = self.tweak
        if tweak is not None:
            self.tweak = bool(tweak)
        notes = dict(note_by_reactor or {})
        base_name = strip_temp_token(base_name)     # our T token is the only one allowed
        n_frames = 0
        sweeps = 0
        errors = 0
        done = None
        stop_obj = None
        try:
            while done is None:
                if deadline is not None and time.time() >= deadline:
                    done = 'deadline'
                    break
                if max_sweeps is not None and sweeps >= int(max_sweeps):
                    done = 'sweeps'
                    break
                offset, offset_y, spot = self._offset()
                for pos in reactors:
                    if temp_check is not None:
                        temp_check()            # TempX -> self.temp_c (never stops a run)
                    if stop_check is not None:
                        stop_obj = stop_check()
                        if stop_obj:
                            done = 'stop'
                            break
                    if deadline is not None and time.time() >= deadline:
                        done = 'deadline'
                        break
                    frame_started = time.time()
                    note = notes.get(pos)
                    # The name is REBUILT here every frame -- base, reactor, note, T, spot,
                    # clock -- so a temperature change replaces the old token instead of
                    # appending to it, and one frame can only ever carry one T. Built
                    # BEFORE the move so a move that fails still has a name to put in the
                    # mail; the clock token is then frame-start, which is what it says.
                    tag = '%s_%s%s%s_p%02d_%s' % (base_name, pos,
                                                  ('_' + _safe_name(note)) if note else '',
                                                  ('_' + self.temp_tag()) if self.temp_tag() else '',
                                                  spot, _sg_time())
                    if verbosity >= 3:
                        print('SMI_SeqGrowth: measuring %s (%s s)' % (tag, exp_time))
                    try:
                        # The MOVE IS INSIDE THE TRY. It used to sit above this block, so a
                        # move that raised left the loop entirely: no error count, no mail,
                        # no 'ACQUISITION STOPPED' -- collection just ended mid-night.
                        self.goto_Pos(pos, offset, offset_y)
                        self.measure_one(tag, exp_time, pos=pos, take_camera=take_camera)
                        errors = 0
                    except Exception as exc:
                        errors += 1
                        print('SMI_SeqGrowth: FRAME FAILED (%d/%d) %s: %s'
                              % (errors, max_frame_errors, tag, exc))
                        mail('SMI: frame failed (%d/%d)' % (errors, max_frame_errors),
                             '%s\n\n%s: %s' % (tag, type(exc).__name__, exc),
                             key='sg_frame_error')
                        _idle_run_engine()
                        if errors >= int(max_frame_errors):
                            done = 'error'
                            stop_obj = stop_obj or {'error': str(exc)}
                            mail('SMI: ACQUISITION STOPPED after %d failures' % errors,
                                 'The last error was:\n%s: %s\n\nName: %s\n'
                                 'Nothing is being collected now.'
                                 % (type(exc).__name__, exc, tag),
                                 key='sg_stopped', min_interval_s=0.0)
                            break
                        time.sleep(FRAME_ERROR_BACKOFF_S)
                        continue
                    n_frames += 1
                    if sleep_time:
                        time.sleep(float(sleep_time))
                    if interval:
                        remaining = float(interval) - (time.time() - frame_started)
                        while remaining > 0:
                            time.sleep(min(0.2, remaining))
                            remaining = float(interval) - (time.time() - frame_started)
                if done is not None:
                    break
                # a full sweep finished -> step every reactor to the next spot. The counter
                # only moves while tweaking, so a pinned single-shot never shifts the walk.
                sweeps += 1
                if self.tweak:
                    self.pos_index += 1
        except KeyboardInterrupt:
            done = 'interrupt'
            print('\nSMI_SeqGrowth: Ctrl-C -- stopped after %d frame(s).' % n_frames)
            print('SMI_SeqGrowth: if the RunEngine is left paused, RE.abort() (or RE.stop()) '
                  'before the next acquisition.')
            if self.y_is_driven():
                print('SMI_SeqGrowth: the height is somewhere in the raster -- DR.park_y() '
                      'once the RunEngine is idle again.')
        finally:
            self.tweak = was_tweak
        # Leave the stage on its alignment, not on whatever row the raster stopped at, so
        # a by-hand frame taken next is at the height the alignment says. Skipped when the
        # height was never driven -- park_y() would then be the ONE move a y_radius=0 run
        # still made, on the axis we are avoiding. Skipped after a Ctrl-C too: the
        # RunEngine is probably paused and a move would only raise on top of it.
        if done != 'interrupt' and self.y_is_driven():
            try:
                self.park_y()
            except Exception as exc:
                print('SMI_SeqGrowth: could not park the height (%s) -- DR.park_y() by hand.'
                      % exc)
        return n_frames, done or 'deadline', stop_obj

    # ---- MANUAL mode: you name it, you time it ------------------------------

    def collect_once(self, name, exp_time=1, rxn_pos=None, tweak=False, sleep_time=0.0,
                     temp_c=False, take_camera=True, waxs_angle=None, setup=True,
                     verbosity=3, temp_leg=None):
        """ONE sweep: one frame at each selected reactor, right now.

            DR.collect_once('AgBH')                    # the reactors DR is set to
            DR.collect_once('DR_align', rxn_pos=1)     # only R0
            DR.collect_once('DR_check', rxn_pos=['R0', 'R2'])
            DR.collect_once('DR_pristine', temp_c=25)  # stamp _T25.0_ into the name
            DR.collect_once('DR_cooled', temp_c=40, temp_leg='cool')   # _TC40.0_

        ``tweak=False`` (the default here) keeps a single-shot on the reactor centre, so
        two check frames of the same reactor are comparable. Pass ``tweak=True`` to take
        the sweep at the next spot instead and advance the walk.

        ``temp_c`` unset leaves whatever DR already knows (see ``DR.set_temp``); pass a
        number to change it, or None to take the temperature out of the name.
        ``temp_leg='cool'`` names it TC… -- for a hand frame taken on the way down.
        """
        if temp_c is not False or temp_leg is not None:
            self.set_temp(self.temp_c if temp_c is False else temp_c,
                          why='collect_once()', leg=temp_leg)
        reactors = self._as_reactors(rxn_pos) if rxn_pos is not None else list(self.reactors)
        if setup:
            self.setup_beamline(waxs_angle=waxs_angle, take_camera=take_camera)
        base = _safe_name(name)
        print('SMI_SeqGrowth: single sweep %s%s -- %s'
              % (base, ('  [%s]' % self.temp_tag()) if self.temp_tag() else '', reactors))
        n, reason, _ = self._collect_loop(base, exp_time, reactors, tweak=tweak,
                                          sleep_time=sleep_time, max_sweeps=1,
                                          take_camera=take_camera, verbosity=verbosity)
        print('SMI_SeqGrowth: %d frame(s) (%s).' % (n, reason))
        return {'frames': n, 'reason': reason, 'name': base}

    def collect_multiple(self, name, exp_time=1, rxn_pos=None, tweak=False, sleep_time=0.0,
                     temp_c=False, take_camera=True, waxs_angle=None, setup=True,
                     verbosity=3, temp_leg=None, howmany=1, sleep_step=60*20):
        """ONE sweep: one frame at each selected reactor, right now.

            DR.collect_once('AgBH')                    # the reactors DR is set to
            DR.collect_once('DR_align', rxn_pos=1)     # only R0
            DR.collect_once('DR_check', rxn_pos=['R0', 'R2'])
            DR.collect_once('DR_pristine', temp_c=25)  # stamp _T25.0_ into the name
            DR.collect_once('DR_cooled', temp_c=40, temp_leg='cool')   # _TC40.0_

        ``tweak=False`` (the default here) keeps a single-shot on the reactor centre, so
        two check frames of the same reactor are comparable. Pass ``tweak=True`` to take
        the sweep at the next spot instead and advance the walk.
        ``temp_c`` unset leaves whatever DR already knows (see ``DR.set_temp``); pass a
        number to change it, or None to take the temperature out of the name.
        ``temp_leg='cool'`` names it TC… -- for a hand frame taken on the way down.
        """
        for i in range(howmany):
            if i == 0:
                tweak = False
            else:
                tweak = False
            print(' %s time measurement: tweak %s' %(i+1, tweak))
            if temp_c is not False or temp_leg is not None:
                self.set_temp(self.temp_c if temp_c is False else temp_c,
                            why='collect_once()', leg=temp_leg)
            reactors = self._as_reactors(rxn_pos) if rxn_pos is not None else list(self.reactors)
            if setup:
                self.setup_beamline(waxs_angle=waxs_angle, take_camera=take_camera)
            base = _safe_name(name)
            print('SMI_SeqGrowth: single sweep %s%s -- %s'
                % (base, ('  [%s]' % self.temp_tag()) if self.temp_tag() else '', reactors))
            n, reason, _ = self._collect_loop(base, exp_time, reactors, tweak=tweak,
                                            sleep_time=sleep_time, max_sweeps=1,
                                            take_camera=take_camera, verbosity=verbosity)
            print('SMI_SeqGrowth: %d frame(s) (%s).' % (n, reason))
            print('time sleep: %s (s).' % (sleep_step))
            time.sleep(sleep_step)
        return {'frames': n, 'reason': reason, 'name': base}

    def run_manual(self, name, exp_time=1, run_time=60 * 60, rxn_pos=None, tweak=True,
                   interval=0.0, sleep_time=0.0, temp_c=False, take_camera=False,
                   waxs_angle=None, setup=True, verbosity=3, temp_leg=None):
        """Timed run with NO handshake: measure for ``run_time`` seconds, then stop.

            DR.run_manual('DR_run7_100C', run_time=3*3600, exp_time=1)
            DR.run_manual('DR_R0_only', run_time=1800, rxn_pos=1, interval=20)
            DR.run_manual('DR_hold', run_time=3600, temp_c=None)   # no T in the name

        Ctrl-C stops it cleanly between frames. Nothing is read from or written to the
        comm folder -- the lab GUI plays no part in this mode, and NO TempX is read: the
        temperature in the name is whatever ``temp_c``/``DR.set_temp()`` last said, which
        is why the banner below prints it.
        """
        if temp_c is not False or temp_leg is not None:
            self.set_temp(self.temp_c if temp_c is False else temp_c,
                          why='run_manual()', leg=temp_leg)
        reactors = self._as_reactors(rxn_pos) if rxn_pos is not None else list(self.reactors)
        if setup:
            self.setup_beamline(waxs_angle=waxs_angle, take_camera=take_camera)
        base = _safe_name(name)
        print('=' * 72)
        print('SMI_SeqGrowth: MANUAL run %s' % base)
        print('  reactors   : %s   %s' %
              (reactors, dict((r, self.pos_dict[r]) for r in reactors)))
        print('  exposure   : %s s   interval: %s s   sleep: %s s' %
              (exp_time, interval, sleep_time))
        print('  tweak      : %s (%d spot(s), next p%02d)' %
              (tweak, self.n_spots(), self.pos_index % self.n_spots()))
        print('  name T     : %s   (no TempX is read in manual mode)' %
              (self.temp_tag() or 'none -- DR.set_temp(25) to add one'))
        print('  run time   : %.2f h   (Ctrl-C to stop early)' % (float(run_time) / 3600.0,))
        print('=' * 72)
        began = time.time()
        n, reason, _ = self._collect_loop(base, exp_time, reactors, tweak=tweak,
                                          interval=interval, sleep_time=sleep_time,
                                          deadline=began + float(run_time),
                                          take_camera=take_camera, verbosity=verbosity)
        print('SMI_SeqGrowth: MANUAL run %s done -- %d frame(s) in %.1f min (%s).' %
              (base, n, (time.time() - began) / 60.0, reason))
        return {'frames': n, 'reason': reason, 'name': base}

    # ---- AUTO mode: StartX -> measure -> StopX -------------------------------

    def run_auto(self, rxn_pos=None, sleep_time=12,
                 run_time=60 * 60 * 20, exp_time=1, extra='',
                 poll_s=5.0, max_collect_min=180.0, name_note=False,
                 send_ack=False, comm_dir=None, waxs_angle=None,
                 tweak=True, interval=0.0, take_camera=False,
                 verbosity=3, **md):
        """Measure ONLY inside the windows the synthesis machine opens.

            DR = DropletReactor('test')
            DR.run_auto()                          # names come from StartX
            DR.run_auto(extra='SMI_2026C2')        # optional prefix
            DR.run_auto(run_time=60*60*14, exp_time=1)

        One pass of the loop:

          1. wait for **StartX.npy** in ``comm_dir`` (folder B, filled by the relay),
             consume it (read + delete), take ``payload['filename']`` from it and
             ``payload['temp_c']`` as the opening temperature;
          2. cycle the selected reactors, measuring ``exp_time`` at each, stepping the
             beam-damage raster (X, then the height) after each full sweep, naming every
             frame after THAT filename and the CURRENT temperature;
          3. take any **TempX.npy** that arrives between frames -- the block reached a new
             set-point, so the ``_T<value>_`` token changes from the next frame on (the
             window is NOT disturbed);
          4. stop the instant **StopX.npy** shows up (consumed the same way), then go
             back to 1 for the next batch.

        The beamline creates nothing and decides nothing: the lab owns both ends of the
        window. The filename travels inside StartX, so the x-ray files and the synthesis
        log always match without a batch counter on two machines.

        StopX is checked BETWEEN exposures (a bp.count cannot be interrupted), so the
        window closes within about one exposure of the lab's stop -- and the same is true
        of a temperature change: at most one frame carries the previous T.

        Window opened, window closed, every T change and any failed frame are emailed
        (see ``mail`` / ``mail_test`` at the top of this file).

        Args:
            rxn_pos: reactors to cycle (None = whatever DR.set_reactors() chose; also
                accepts 1/2/3 or ['R0','R2']).
            sleep_time: extra pause after each exposure (s). 0 = measure back-to-back.
            run_time: total seconds to keep serving windows, then return.
            exp_time: exposure time per frame (s).
            extra: optional prefix in front of the StartX filename ('' = filename only).
            poll_s: how often to look for a marker while idle.
            max_collect_min: safety cap -- close the window if StopX never arrives, so a
                lost marker cannot collect for the rest of the night.
            name_note: append the per-reactor note from the StartX payload to the sample
                name (e.g. ..._R0_batch1_R0_CuCl2_76). Off by default: it makes long names.
            send_ack: write a dummy Start_Push after each window. NOT needed here.
            comm_dir: override folder B for this run.
            waxs_angle: WAXS angle to move to before the first window (default WAXS_ANGLE).
            tweak: walk the +/-2 mm beam-damage spots (True) or pin the centre (False).
            interval: minimum seconds between the start of consecutive frames (0 = as
                fast as the detector allows).
        """
        cdir = comm_dir or self.comm_dir or COMM_DIR
        reactors = self._as_reactors(rxn_pos) if rxn_pos is not None else list(self.reactors)
        self.setup_beamline(waxs_angle=waxs_angle, take_camera=take_camera)

        print('=' * 72)
        print('SMI_SeqGrowth: AUTO -- serving StartX/TempX/StopX windows')
        print('  comm dir   : %s   (exists=%s)' % (cdir, os.path.isdir(cdir)))
        print('  reactors   : %s' % (reactors,))
        print('  positions  : %s' % (dict((r, self.pos_dict.get(r)) for r in reactors),))
        print('  tweak      : %s (%d spot(s), next p%02d)' %
              (tweak, self.n_spots(), self.pos_index % self.n_spots()))
        print('  exposure   : %s s      poll: %s s     cap: %s min' %
              (exp_time, poll_s, max_collect_min))
        print('  run window : %.1f h' % (run_time / 3600.0,))
        print('  mail       : %s' % (', '.join(MAIL_TO) if (MAIL_ENABLED and MAIL_TO) else 'off'))
        print('=' * 72)
        mail('SMI: acquisition armed', 'Waiting for %s in %s.\nReactors %s, %s s/frame, '
             'up to %.1f h.' % (STARTX_NAME, cdir, reactors, exp_time, run_time / 3600.0),
             key='sg_armed', min_interval_s=0.0)

        t_end = time.time() + float(run_time)
        n_windows = 0
        n_frames = 0
        idle_ticks = 0

        while time.time() < t_end:
            # ---- 1. wait for StartX ---------------------------------------
            start = consume_marker(STARTX_NAME, cdir)
            if start is None:
                # A StopX with no window open is stale (e.g. we restarted mid-batch).
                # Drop it, or it would close the NEXT window the moment it opens.
                if consume_marker(STOPX_NAME, cdir) is not None:
                    print('SMI_SeqGrowth: stale StopX with no window open -- discarded.')
                # A TempX while idle is NOT stale: it is the block's current set-point, and
                # remembering it means the next window starts with the right T in its names.
                self._consume_temp(cdir)
                if idle_ticks % 12 == 0:
                    print('SMI_SeqGrowth: waiting for %s in %s ... (%s)' %
                          (STARTX_NAME, cdir, _sg_time()))
                idle_ticks += 1
                try:
                    time.sleep(poll_s)
                except KeyboardInterrupt:
                    print('\nSMI_SeqGrowth: Ctrl-C while idle -- leaving the loop.')
                    break
                continue

            idle_ticks = 0
            filename = marker_filename(start)
            payload = start.get('payload') or {}
            notes = payload.get('notes') or {}
            base_name = _safe_name('%s_%s' % (extra, filename)) if extra else _safe_name(filename)
            # the lab's per-reactor note ("batch1_R0 CuCl2 76") goes right after the
            # reactor tag when name_note=True -- off by default, it makes long names.
            window_notes = dict((r, notes[r]) for r in reactors
                                if name_note and notes.get(r))

            # The opening temperature rides in StartX; later ones arrive as TempX. StartX
            # is AUTHORITATIVE: a window opened without a temperature (temperature control
            # off in that case) clears the token, so a T left over from an earlier campaign
            # in the same bluesky session cannot leak into this batch's names.
            # The leg is reset with it: a window that opens while DR still remembers 'cool'
            # from the previous campaign would name its heat-up frames TC….
            self.set_temp(marker_temp(start), why='%s payload' % STARTX_NAME,
                          leg=marker_temp_leg(start))

            n_windows += 1
            print('-' * 72)
            print('SMI_SeqGrowth: WINDOW %d OPEN -- filename=%s  batch=%s/%s  T=%s C' %
                  (n_windows, filename, payload.get('batch'), payload.get('n_batches'),
                   payload.get('temp_c')))
            for reactor, vols in sorted((payload.get('recipes') or {}).items()):
                print('    %s: %s   %s' % (reactor, vols, notes.get(reactor, '')))

            # ---- 2. measure until StopX -----------------------------------
            began = time.time()
            # Two clocks bound a window: the run's own end (t_end) and the safety cap.
            # Whichever comes first closes it -- see the WARNING below for telling them apart.
            # The lab says how long its window will be (payload['expected_s']); a cap
            # SHORTER than that would cut an 8 h temperature ramp off after 3 h, so it is
            # raised to fit, with half an hour of slack. It is a runaway guard, not a timer.
            cap_min = float(max_collect_min)
            expected_s = payload.get('expected_s')
            try:
                expected_min = float(expected_s) / 60.0
            except (TypeError, ValueError):
                expected_min = 0.0
            if expected_min > cap_min:
                cap_min = expected_min + 30.0
                print('SMI_SeqGrowth: the lab expects %.0f min of collection -- raising the '
                      'safety cap %.0f -> %.0f min for this window.'
                      % (expected_min, float(max_collect_min), cap_min))
            capped_at = began + cap_min * 60.0
            window_end = min(t_end, capped_at)

            def _stop_check():
                return consume_marker(STOPX_NAME, cdir)

            def _temp_check():
                return self._consume_temp(cdir)

            mail('SMI: window OPEN -- %s' % filename,
                 'Collecting %s\nbatch %s/%s   T=%s C   reactors %s\n'
                 'exposure %s s, spot p%02d, cap %.0f min.'
                 % (base_name, payload.get('batch'), payload.get('n_batches'),
                    payload.get('temp_c'), reactors, exp_time,
                    self.pos_index % self.n_spots(), cap_min),
                 key='sg_window_open', min_interval_s=0.0)

            frames, reason, stop = self._collect_loop(
                base_name, exp_time, reactors, tweak=tweak, interval=interval,
                sleep_time=sleep_time, deadline=window_end, stop_check=_stop_check,
                note_by_reactor=window_notes, temp_check=_temp_check,
                take_camera=take_camera, verbosity=verbosity)
            n_frames += frames

            # ---- 3. window closed ------------------------------------------
            why = reason
            if stop is not None and reason == 'stop':
                stop_name = marker_filename(stop)
                why = 'StopX from the lab'
                if stop_name != filename:
                    print('SMI_SeqGrowth: WARNING StopX filename=%s does not match StartX=%s'
                          % (stop_name, filename))
            elif reason == 'error':
                why = 'REPEATED FRAME ERRORS -- see the log'
            elif reason == 'deadline' and window_end >= capped_at:
                why = 'safety cap of %.0f min, no StopX arrived' % cap_min
                print('SMI_SeqGrowth: WARNING cap of %.0f min reached for %s -- closing '
                      'the window without a StopX.' % (cap_min, filename))
            elif reason == 'deadline':
                why = "run_time reached (the lab's window is still open)"
                print('SMI_SeqGrowth: run_time reached -- leaving window %s open on '
                      'the lab side.' % filename)
            print('SMI_SeqGrowth: WINDOW %d CLOSED -- %s  (%.1f min, %d frames total, %s)' %
                  (n_windows, filename, (time.time() - began) / 60.0, n_frames, why))
            mail('SMI: window CLOSED -- %s' % filename,
                 '%d frame(s) in %.1f min (%d this run).\nReason: %s\nLast T: %s'
                 % (frames, (time.time() - began) / 60.0, n_frames, why,
                    self.temp_tag() or 'unknown'),
                 key='sg_window_close', min_interval_s=0.0)
            if send_ack:
                send_dummy_ack(filename, cdir)
            if reason == 'interrupt':
                print('SMI_SeqGrowth: interrupted -- not waiting for another window.')
                break
            if reason == 'error':
                print('SMI_SeqGrowth: stopping after repeated frame errors -- fix the '
                      'detector/motor, then start run_auto() again.')
                break

        print('=' * 72)
        print('SMI_SeqGrowth: done -- %d window(s), %d frame(s).' % (n_windows, n_frames))
        return {'windows': n_windows, 'frames': n_frames}

    # The one auto-mode entry point. It measures whatever the lab is making — the
    # chemistry rides in the marker, not in the method name — so there is no
    # per-system alias here; `Run_synthesis` is kept only for older beamline notes.
    Run_synthesis = run_auto

    # ---- one entry point, if you prefer naming the mode ---------------------

    def run(self, mode='auto', name=None, **kwargs):
        """``DR.run('auto')`` / ``DR.run('manual', 'DR_run7', run_time=3600)`` /
        ``DR.run('once', 'AgBH')`` -- thin dispatcher over the three above."""
        mode = str(mode).strip().lower()
        if mode in ('auto', 'handshake', 'startx'):
            return self.run_auto(**kwargs)
        if mode in ('manual', 'timed'):
            if not name:
                raise ValueError("manual mode needs a name: DR.run('manual', 'DR_run7')")
            return self.run_manual(name, **kwargs)
        if mode in ('once', 'single', 'check'):
            if not name:
                raise ValueError("single mode needs a name: DR.run('once', 'AgBH')")
            return self.collect_once(name, **kwargs)
        raise ValueError("mode must be 'auto', 'manual' or 'once' -- got %r" % (mode,))


#DR = DropletReactor('seq_growth')
DR = DropletReactor('Cu2O')