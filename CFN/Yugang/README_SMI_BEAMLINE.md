# SMI 12-ID — sequential growth / droplet reactors (2026C2)

The card for the beamline machine. Everything here is typed **in the SMI bluesky session**
unless it says "terminal". The full two-machine procedure is `docs/SMI_SEQ_GROWTH_RUNBOOK.md`
in the sys76 repo.

Files in this folder (`/nsls2/data/smi/proposals/2026-2/pass-317378/projects/controls/`):

| File | What it is |
|---|---|
| `SMI_SeqGrowth.py` | the acquisition loop — `DR` (three modes, below) |
| `SeqGrowthWatcher.py` | folder-B monitor + bench test (consumes nothing in `--monitor`) |
| `xf11bm_relay.py` | Dropbox ⇄ folder B relay — **must be running for auto mode** |
| `2026C2_Flow.py` | snapshot of the run-book file (live copy: `~xf12id/SWAXS_user_scripts/CFN/Yugang/`) |

---

## 1. Load it

```python
proposal_swap(317378)
%run -i /home/xf12id/SWAXS_user_scripts/CFN/Yugang/YZhang_SMI_Base.py
project_set('Digestive Ripening')
%run -i /home/xf12id/SWAXS_user_scripts/CFN/Yugang/2026C2_Flow.py          # alignment of the day
%run -i /nsls2/data/smi/proposals/2026-2/pass-317378/projects/controls/SMI_SeqGrowth.py
DR.check()
```

`proposal_swap` + `project_set` decide where frames land
(`…/2026-2/pass-317378/projects/Digestive_Ripening`) — do them first.

Order matters: `%run -i` shares **one** namespace, and `SMI_SeqGrowth.py` borrows `RE`, `bp`,
`bps`, `MDrive`, `stage`, `pil2M`, `pil900KW`, `pil2M_pos`, `det_exposure_time`, `sample_id`,
`save_ova`, `setup_ova`, `move_waxs`, `waxs` and `user_name` from the base. It defines no name
the base already owns, so loading it cannot rename files for the rest of your session.

`DR.check()` prints the motors, the reactor positions, the tweak window and folder B, and
measures nothing. If it says `motorX is not bound`, the MDrive IOC came up after the file
loaded: `set_motors(MDrive.m3, stage.y)`.

## 2. Geometry — MDrive3 is the only motor that moves

```
R0 = 50 mm (48-53)     R1 = 85 mm (82-88)     R2 = 120 mm (117-123)      on MDrive.m3
Huber stage: X -28, Y -30, Z 2 — set by hand, never driven by this file.
```

```python
DR.pos_dict                        # read it back
DR.set_reactor_x('R1', 86.2)       # after aligning one reactor
DR.calibrate(x0=50.0, pitch=35.0)  # or the whole evenly spaced row
DR.set_reactors(2)                 # 1, 2, 3 — or ['R0','R2'], or 'R0,R2'
```

**This changed from 2025:** X used to be `MDrive.m5` with `m3` as the read-only height. Now
**`m3` is X** and the height is `stage.y` (read for the file name, never driven). An old
`set_motors(MDrive.m5, MDrive.m3)` would drive the wrong axis.

## 3. Beam-damage tweak (long runs)

Each full sweep steps every reactor to the next spot in a ±2 mm window at 0.2 mm — 20 spots
— then wraps:

```
R0@p00 → R1@p00 → R2@p00 → R0@p01 → R1@p01 → R2@p01 → … → p19 → p00 → …
```

```python
DR.set_tweak(radius=2.0, step=0.2)   # the default: 20 spots
DR.set_tweak(on=False)               # pin every frame to the reactor centre
DR.reset_positions()                 # start the walk again at p00
```

The spot index **and** the true motor read-back are both in the file name, so a spot can
never be guessed wrong: `…_R0_p07_2026_07_30_01_14_02_x051.40_y77.60_det05.00m_waxs16.00_expt10s`.

## 3b. Temperature in the file name (`TempX`)

In auto mode the lab tells us its set-point: `StartX` carries the opening one, and a
`TempX.npy` arrives **every time the block reaches a new one**. From that frame on the name
carries a single `T<value>` token:

```
DR_AuC8C12_b01_R0_T25.0_p03_2026_07_30_21_10_44_x049.60_…      RT hold
DR_AuC8C12_b01_R0_T40.0_p04_2026_07_30_22_11_02_x049.80_…      after TempX(40)
```

The token is **rebuilt** for every frame, never appended — a frame can only ever carry one
temperature. `TempX` opens and closes nothing; `StartX`/`StopX` still own the window, and a
`TempX` seen while idle is remembered for the window that follows. `StartX` is authoritative:
a window opened without a temperature (temperature control off in that case) clears the token.

```python
DR.temp_c                 # what the lab last said, or None
DR.set_temp(100)          # by hand, e.g. for a manual run at a known T
DR.set_temp(None)         # take the temperature back out of the names
DR.collect_once('DR_pristine', temp_c=25)     # one sweep, stamped T25.0
```

Manual mode reads **no** `TempX` (it would steal the auto loop's marker) — `run_manual` prints
the temperature it will stamp in its banner.

## 3c. Email during the run

Window opened, window closed, every temperature change and any frame that raises are emailed:

```bash
export DC_MAIL_TO=yuzhang@bnl.gov,wliu1@bnl.gov     # before starting bluesky
export DC_MAIL=0                                    # or turn it off entirely
```

```python
mail_test()               # send one now — do this ONCE at the start of the beamtime
```

Best effort in a daemon thread with a 20 s timeout: three failures in a row (a host with no
SMTP route) switch mailing off for the session and the run is untouched.

## 4. The three ways to run

### a. One sweep, now — `collect_once`

```python
DR.collect_once('AgBH')                        # one frame per selected reactor
DR.collect_once('DR_align', rxn_pos=1)         # only R0
DR.collect_once('DR_check', rxn_pos=['R0','R2'], exp_time=2)
```

Pinned to the reactor centres (`tweak=False`) so two check frames are comparable.

### b. Timed run, no handshake — `run_manual`

```python
DR.run_manual('DR_run7_100C', run_time=3*3600, exp_time=1)
DR.run_manual('DR_R0_only', run_time=1800, rxn_pos=1, interval=20)
```

You name it, you time it. **Nothing is read from or written to folder B** — the lab GUI plays
no part. Ctrl-C stops it cleanly between frames (if the RunEngine is left paused, `RE.abort()`
before the next acquisition).

### c. Automated windows — `run_auto`

The lab owns the collection window: it sends `StartX.npy` to open, `TempX.npy` at every
temperature it reaches, and `StopX.npy` to close. The sample name comes from the marker, so no
batch number has to stay in sync.

```python
DR.run_auto(exp_time=10, run_time=60*60*14)
```

Needs `xf11bm_relay.py` running in its own terminal (`export DC_BEAMLINE=smi; python
~/xf11bm_relay.py --hours 14`). It prints `waiting for StartX.npy …` while idle, then one
`WINDOW n OPEN … / WINDOW n CLOSED …` pair per batch.

| argument | default | for |
|---|---|---|
| `exp_time` | `10` | seconds per frame |
| `run_time` | `60*60*10` | how long to keep serving windows |
| `rxn_pos` | `None` | reactors (None = whatever `set_reactors` chose) |
| `tweak` | `True` | walk the ±2 mm spots |
| `interval` | `0` | minimum seconds between frame starts (0 = back-to-back) |
| `sleep_time` | `0` | extra pause after each frame |
| `max_collect_min` | `180` | safety cap if `StopX` is lost — raised automatically to fit the window the lab declared in `expected_s` |
| `extra` | `''` | prefix in front of the StartX filename |
| `name_note` | `False` | append the lab's per-reactor note to the name |
| `waxs_angle` | `None` | move WAXS here first (default `WAXS_ANGLE = 16`) |
| `comm_dir` | `None` | override folder B for one run |

Or name the mode: `DR.run('once', 'AgBH')` / `DR.run('manual', 'DR_run7', run_time=3600)` /
`DR.run('auto')`.

## 5. Looking at folder B without breaking anything

```python
peek_markers()          # list folder B, consume NOTHING — safe mid-run
consume_marker('StartX.npy')    # read + DELETE (preflight only, never mid-run)
```

In a terminal, a live view that also consumes nothing:

```bash
export DC_BEAMLINE=smi
python SeqGrowthWatcher.py --beamline smi --monitor --hours 14
```

**Never run `SeqGrowthWatcher.py` without `--monitor` while `DR.run_auto()` is serving** — the
two would race for the same markers and each would eat half the windows.

`--monitor` shows what each waiting marker carries, e.g.
`TempX.npy (dr_b01, T=40.0)` — a marker that *sits* there means the next hop is not running.

## 6. Warnings that mean the files are not what you think

* `WARNING StopX filename=… does not match StartX=…` — two windows crossed; the frames in that
  window are named after the *first* filename.
* `WARNING cap of … min reached … closing the window without a StopX` — the stop marker was
  lost. Nothing is collected after that until the next `StartX`.
* `FRAME FAILED (n/5)` — that exposure was lost; the loop backs off 2 s and carries on. **Five
  in a row** stop the run (`ACQUISITION STOPPED`), because by then something is broken. Fix it
  and start `DR.run_auto()` again — the lab's window is still open, so collection resumes.
* `no T in the names` — check `DR.temp_c`. Either the lab's case has
  `beamline_temp_marker_SeqGrowth = False`, or its `StartX` carried no `temp_c`.

## 7. Bench test, no beam and no Dropbox

```bash
mkdir -p /tmp/sg_comm
python SeqGrowthWatcher.py --dry --shared-dir /tmp/sg_comm --once --poll 0.2
```

Then, from the sys76 repo, drop markers into the same folder to drive it:

```python
from droplet_core.beamline_comm import SharedDirComm, BeamlineHandshake
hs = BeamlineHandshake(SharedDirComm('/tmp/sg_comm'), startx_name='StartX.npy',
                       stopx_name='StopX.npy', tempx_name='TempX.npy')
hs.send_startX('bench_b01', payload={'filename': 'bench_b01', 'temp_c': 25.0})
hs.send_tempX('bench_b01', temp_c=40.0, payload={'filename': 'bench_b01'})
hs.send_stopX('bench_b01', payload={'filename': 'bench_b01'})
```
