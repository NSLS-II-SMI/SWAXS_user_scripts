# Sequential Growth at SMI (12-ID) — step-by-step setup

How to bring up a sequential-growth run in which the synthesis machine (**sys76**) in the lab
drives the reactors and the **SMI** bluesky session collects SAXS/WAXS. Every command below is
meant to be typed in the order it appears.

`docs/SEQ_GROWTH_BEAMLINE.md` is the *policy* runbook (what a good run looks like, abort rules,
wiring surface). **This** file is the *procedure*: which terminal, which export, which line, and
how to tell it worked. `Beamline_Control/README_SMI_BEAMLINE.md` is the short card that ships
next to the code at the beamline. For CMS (11-BM) the same procedure applies with
`DC_BEAMLINE=cms` and `NanoSyn.py` in place of `SMI_SeqGrowth.py`.

**Not every run needs the handshake.** Two of the three acquisition modes (§B5a/b) are
beamline-only: no GUI, no relays, no Dropbox. Parts A3–A4, B6 and C apply to the automated mode
only. Read §B5 first and pick a mode before setting anything up.

---

## 0. The shape of it (read once)

```
   sys76 (lab)                       cloud                    beamline (SMI 12-ID)
 ┌──────────────┐              ┌──────────────┐        ┌──────────────┬───────────┐
 │ Web GUI      │  np.save     │              │        │              │  bluesky  │
 │ Seq. Growth  │─────────────▶│   Dropbox    │───────▶│   folder B   │──────────▶│
 │  :5641       │   folder A   │              │        │              │  measures │
 └──────────────┘              └──────────────┘        └──────────────┴───────────┘
              Dropbox_Com.ipynb (jupyter :5642)      xf11bm_relay.py    SMI_SeqGrowth.py
```

Five hops. sys76 cannot see `/nsls2` and the beamline cannot see sys76, so **the Dropbox hop is
mandatory** and the two relays are the only processes that ever touch Dropbox. (Yes, sys76 can
sshfs-mount `/nsls2/data/smi/legacy/...`, but that mount is *not* the route — it is read-only
convenience for looking at data. The handshake goes through Dropbox.)

Three facts that explain nearly every failure:

1. **Whoever CONSUMES a marker DELETES it.** An empty folder is the healthy state. A marker that
   *sits* somewhere means the next hop is not running.
2. **The lab owns the collection window.** sys76 sends one `StartX.npy` at the start of a batch
   and one `StopX.npy` at the end, plus a `TempX.npy` each time the block *reaches* a new
   set-point. The beamline creates nothing and decides nothing. The batch filename travels
   *inside* the marker, so no batch number has to stay in sync. `TempX` opens and closes
   nothing — it only changes the temperature stamped in the file names (§C2).
3. **`DC_BEAMLINE` picks all three folders at once**, it is read at **import** time, and it must
   be the same on both machines. Mismatched profiles are silent: the relays meet on different
   Dropbox folders and every marker vanishes.

| `DC_BEAMLINE` | folder A (sys76) | Dropbox | folder B (beamline) |
|---|---|---|---|
| `smi` | `~/NSLS_II_Link/smi_remote/2026-2/pass-319371/Dropbox_Com` | `/CFN/SMI/SeqGrowth_Com/` | `/nsls2/data/smi/legacy/results/data/2024_3/313765_Zhang/Dropbox_Com/` |
| `cms` | `~/NSLS_II_Link/cms_remote/2026-2/pass-316987/Dropbox_Com` | `/CFN/CMS/AutoFlow_Com/` | `/nsls2/auto-storage/cms/legacy/xf11bm/data/2025_2/YZhang/SY_Comm/` |

Two different SMI passes are in play and that is deliberate: **pass-319371** is the handshake
staging folder (folder A), **pass-317378** is where the code lives (§A1). New proposal/cycle
mid-run? Override one folder alone with `DC_SHARED_DIR_LOCAL` (A), `DC_DROPBOX_DIR` (cloud),
`DC_COMM_DIR` (B) instead of editing `protocols/config/auto_flow.py`.

---

## PART A — sys76 (the lab machine)

### A1. Put the beamline code where the beamline can read it

No `scp`. `~/NSLS_II_Link/smi_remote/…` is an sshfs mount of the NSLS-II proposal tree, so this
one folder is the same folder on both machines:

| on sys76 | at the beamline |
|---|---|
| `~/NSLS_II_Link/smi_remote/2026-2/pass-317378/projects/controls/` | `/nsls2/data/smi/proposals/2026-2/pass-317378/projects/controls/` |

```bash
cd ~/NSLS_II_Link && mount_bl smi          # only if the mount is not up; it mounts ./smi_remote
cd ~/Repos/Droplet_Controls_Update
./Beamline_Control/sync_to_smi.sh --diff   # what differs, copies nothing
./Beamline_Control/sync_to_smi.sh          # push repo -> beamline
```

`mount_bl` is relative to the current directory — run it from `~/NSLS_II_Link` or the mount lands
somewhere else. For the **auto mode**, folder A lives under this same mount, and sshfs's default
20 s directory cache is longer than a marker poll; if markers show up late or a deleted one keeps
listing, remount with `-o dcache_timeout=1 -o entry_timeout=1 -o attr_timeout=1`.

It pushes `SMI_SeqGrowth.py`, `SeqGrowthWatcher.py`, `xf11bm_relay.py` and
`README_SMI_BEAMLINE.md`. It **pulls** `2026C2_Flow.py` (`--pull`), because that file is edited
at the beamline — it holds the alignment of the day. Pull it and commit it at the end of the run
so the alignment is versioned with the data.

`xf11bm_relay.py` needs the `dropbox` package; `SMI_SeqGrowth.py` needs nothing but `numpy` (it
never touches the network).

> Doing only a manual or single-shot run (§B5a/b)? You are done with Part A — go to Part B.

### A2. Export the profile, then start the GUI

`DC_BEAMLINE` is read at **import**, so it must be set *before* the process starts. Exporting it
in another terminal afterwards does nothing, and a GUI already running without it is in `cms`
mode no matter what the folders on screen suggest.

```bash
cd ~/Repos/Droplet_Controls_Update
export DC_BEAMLINE=smi
./run 5641                      # ./run 5641 <password> to gate it
```

Open the **Sequential Growth** page → **📡 Beamline handshake** tab. The route picture at the
top must say `DC_BEAMLINE=smi` and show the three SMI folders. If it says `cms`, stop and
restart the GUI with the export.

Check what is actually running before trusting it:

```bash
pgrep -af "streamlit|jupyter"
tr '\0' '\n' < /proc/<pid>/environ | grep DC_BEAMLINE     # <unset> means cms
```

### A3. Start the Dropbox relay — jupyter on :5642 (auto mode only)

The relay comes up **before** the GUI campaign, so the first `StartX` has somewhere to go.

```bash
cd ~/Repos/Droplet_Controls_Update
export DC_BEAMLINE=smi
jupyter-lab --port 5642
```

Open `Dropbox_Comm/Dropbox_Com.ipynb` and run:

* **cell 1** — imports + config. It prints `DC_BEAMLINE : smi` and the three folders. **If it
  prints `cms`, the kernel did not inherit the export**: the config module resolves the profile
  at import, so restart the kernel *and* jupyter with `DC_BEAMLINE=smi` exported (or put
  `os.environ['DC_BEAMLINE']='smi'` as the very first line of that cell, above the imports).
* **cell 2** — `bc.make_relay(confs, side='sys76')`. Fails fast on a bad Dropbox token.
* **cell 4** — lists Dropbox and folder A. Both should be empty before a run.
* **cell 8** — `relay.run(hours=144, poll_s=5)`. This blocks; leave the tab open.

Same relay as a plain terminal process, if you prefer no notebook:

```bash
export DC_BEAMLINE=smi
python Dropbox_Comm/sys76_relay.py --list      # prints both folders + what is in them
python Dropbox_Comm/sys76_relay.py --hours 14
```

The banner must show folder A, the Dropbox folder, `outbound: StartX.npy, StopX.npy, TempX.npy`
and `inbound: Start_Push.npy`.

### A4. Pick the case and check the method (auto mode only)

In the **▶ Campaign** tab, load the case study (e.g. `014_20260730_dr_au_c8c12_tramp`) and
confirm:

* **Detector = `xray`**, `beamline_handshake = True`, `beamline_per_batch = True`,
  `beamline_temp_marker = True` (the last one is what sends `TempX` at every rung).
* Every recipe volume, wait and temperature is a real number — cases 011–013 ship with
  placeholder zeroes, and case 014 has five `<<< EDIT` numbers at the top of the file
  (`T_LIST`, `HOLD_RT_H`, `HOLD_T_H`, `C8_UL`, `C12_UL`).
* Pump addresses, liquid valve ports, gas M-Switch ports and stir channels match the physical
  labels. Trace every liquid and gas line to waste by hand before connecting.

Run a **dry run** and scrub the digital twin. Each batch must contain exactly one ordered
`beamline_start` → `beamline_stop`; windows must not overlap. Every `temperature` step inside
the window shows a `beamline_temp` op right after it — that is the `TempX` that renames the
frames.

Note the filename the GUI shows: `Next batch filename: <campaign>_b01`. That exact string is what
the beamline will name its frames after.

#### Today's case: `014_20260730_dr_au_c8c12_tramp` (Au NP + C8/C12/C16, RT then T ramp)

By hand, **before** ▶ Start — the script does not do these and does not check them:

* **A0** load pristine Au NP solution into R0/R1/R2, collect a by-hand frame of each at the
  beamline (`DR.collect_once('DR_pristine', temp_c=25)`), start the stir bars and **leave them
  on for the whole experiment**.
* **A1** add C16SH (a solid) to R2 by hand.

Then ▶ Start runs, in one long window: `beamline_start` at RT → inject C8SH→R0 (NE 1) and
C12SH→R1 (NE 2) → hold `HOLD_RT_H` h at RT → each rung of `T_LIST` heating then
`T_LIST[:-1]` cooling, `HOLD_T_H` h each, one `TempX` per rung → `beamline_stop` → stir off.
As configured now — `T_LIST=[40,60,80,100,110]`, `HOLD_RT_H=HOLD_T_H=1` — that is 9 rungs + the
1 h RT hold ≈ **10.4 h in one window**, which is what the GUI shows next to ▶ Start and what
`StartX` carries as `expected_s`; see the `max_collect_min` note in §B5c, the beamline raises its
own cap (to 653 min here) to fit. Change `T_LIST` or the holds and that number moves — re-read it
from the GUI before choosing `run_time` in C1.

Rehearse it first: 📡 tab → **🎬 Simulate the whole campaign** sends the same 11 markers in about
a minute (§B6).

---

## PART B — the SMI beamline machine

### B1. Export the profile

In **every** terminal you open on the beamline machine, before anything else:

```bash
export DC_BEAMLINE=smi
```

It must match sys76 (A2/A3). `xf11bm_relay.py` and `SeqGrowthWatcher.py` both read it.
`SMI_SeqGrowth.py` defaults to the SMI folder B regardless, so manual modes work without it.

### B2. Start the beamline relay (auto mode only — its own terminal, leave it up)

```bash
export DC_BEAMLINE=smi
cd /nsls2/data/smi/proposals/2026-2/pass-317378/projects/controls
python xf11bm_relay.py --once      # single pump — proves the token + both folders work
python xf11bm_relay.py --hours 14  # then leave this running
```

The startup print must name folder B
(`/nsls2/data/smi/legacy/results/data/2024_3/313765_Zhang/Dropbox_Com/`) and the Dropbox folder
(`/CFN/SMI/SeqGrowth_Com/`). If folder B does not exist, create it — the relay downloads into it
and the bluesky loop reads out of it.

### B3. Load the acquisition code into the bluesky session

```python
proposal_swap(317378)
%run -i /home/xf12id/SWAXS_user_scripts/CFN/Yugang/YZhang_SMI_Base.py
project_set('Digestive Ripening')
%run -i /nsls2/data/smi/proposals/2026-2/pass-317378/projects/controls/SMI_SeqGrowth.py
DR.check()
```

`proposal_swap` + `project_set` decide **where the frames land**
(`/nsls2/users/yuzhang/smi_proposals_link/2026-2/pass-317378/projects/Digestive_Ripening`) — do
them first or the data goes to the previous proposal. `2026C2_Flow.py` is `%run` from its live
home, `/home/xf12id/SWAXS_user_scripts/CFN/Yugang/`; the copy in the controls folder is the
versioned snapshot that `sync_to_smi.sh --pull` brings back to the repo.

Order matters. `%run -i` shares **one** namespace, so `SMI_SeqGrowth.py` borrows `RE`, `bp`,
`bps`, `MDrive`, `stage`, `pil2M`, `pil900KW`, `pil2M_pos`, `det_exposure_time`, `sample_id`,
`save_ova`, `setup_ova`, `move_waxs`, `waxs` and `user_name` from the base file. It deliberately
defines **no** name the base already owns, so loading it cannot rename files for the rest of your
session.

`DR.check()` prints the motors, the reactor positions, the tweak window and folder B, and
measures nothing. Run it after every reload. `DR.setup_beamline()` is the version that also moves
WAXS and arms the OAV camera (the auto/manual modes call it for you).

### B4. Calibrate — the part that is NOT done for you

**2026C2 geometry — this changed from 2025.** X is now `MDrive.m3` (MDrive3), the three reactors
sit in one row along it, and the Huber `stage` is set by hand and never driven:

```
R0 = 50 mm (48-53)     R1 = 85 mm (82-88)     R2 = 120 mm (117-123)     on MDrive.m3
Huber stage: X -28, Y -30, Z 2       stage.y is READ for the file name, never moved.
```

An old `set_motors(MDrive.m5, MDrive.m3)` line would now drive the wrong axis. The correct
binding, if the IOC came up late, is `set_motors(MDrive.m3, stage.y)`.

Two numbers decide whether the data is usable — **do both before the first window**:

1. **Reactor X positions.** Align each reactor in the beam by eye, then:

   ```python
   DR.set_reactor_x('R1', 86.2)          # one reactor at a time
   DR.calibrate(x0=50.0, pitch=35.0)     # or the whole evenly spaced row (ascending X)
   DR.pos_dict                           # read it back and write it in the logbook
   ```

2. **WAXS angle.** `setup_beamline()` moves the real `waxs` motor and the file name uses the
   motor's own read-back, so the two cannot disagree. Change it with either:

   ```python
   WAXS_ANGLE = 20                  # module default for the whole run
   DR.run_auto(waxs_angle=20)       # or per run
   ```

Also confirm the detector distance (`pil2M_pos` goes into every file name) and that the
shutter/measurement mode is set — SMI has no `cms.modeMeasurement()`, so that part is manual.

### B5. Pick a mode

Reactor selection is the same in all three: `rxn_pos` takes a **count** (`1`, `2`, `3` → the
first N of R0,R1,R2), a **name list** (`['R0','R2']`), or a **string** (`'R0,R2'`). `None` means
"whatever `DR.set_reactors()` was last set to" (default all three).

#### a. `collect_once` — one sweep, right now

```python
DR.collect_once('AgBH')                              # one frame per selected reactor
DR.collect_once('DR_align', rxn_pos=1)               # only R0
DR.collect_once('DR_check', rxn_pos=['R0','R2'], exp_time=2)
```

Pinned to the reactor centres (tweak off) so two check frames are comparable. This is the
alignment/standards tool.

#### b. `run_manual` — timed run, no handshake

```python
DR.run_manual('DR_run7_100C', run_time=3*3600, exp_time=1)
DR.run_manual('DR_R0_only', run_time=1800, rxn_pos=1, interval=20)
```

You name it, you time it. **Nothing is read from or written to folder B** — no relays, no GUI,
no Dropbox. The beam-damage tweak is **on** by default here. `Ctrl-C` stops it cleanly between
frames (if the RunEngine is left paused, `RE.abort()` before the next acquisition).

#### c. `run_auto` — automated windows from the lab

```python
DR.run_auto(exp_time=10, run_time=60*60*14)
```

Needs both relays (A3, B2) and the preflight (B6). Per window it:

1. consumes `StartX.npy`, takes `payload['filename']` as the sample name and `payload['temp_c']`
   as the opening temperature;
2. sweeps the selected reactors, moving **X only**, exposing `exp_time` at each, stepping the
   tweak after every full sweep;
3. consumes any `TempX.npy` *between* frames and re-stamps the name from there on (§C2);
4. closes the instant `StopX.npy` arrives (checked *between* exposures — a `bp.count` cannot be
   interrupted, so the window closes within about one exposure).

A frame that raises is emailed, the RunEngine is nudged back to idle, and the loop carries on
after a 2 s backoff; **five failures in a row** end the window with `ACQUISITION STOPPED` (§C3).

| argument | default | what it is for |
|---|---|---|
| `exp_time` | `10` | seconds per frame (what `det_exposure_time` is set to) |
| `run_time` | `60*60*10` | how long to keep serving windows before returning |
| `rxn_pos` | `None` | which reactors (see above) |
| `tweak` | `True` | walk the ±2 mm spots |
| `interval` | `0` | minimum seconds between frame *starts*; 0 = back-to-back |
| `sleep_time` | `0` | extra pause after each frame |
| `max_collect_min` | `180` | safety cap: close the window if `StopX` never arrives. **Raised automatically** to `payload['expected_s']` + 30 min, so a declared 8 h ramp is not cut off at 3 h |
| `extra` | `''` | prefix in front of the StartX filename |
| `name_note` | `False` | append the per-reactor note from the payload (long names) |
| `waxs_angle` | `None` | move WAXS here first (default: `WAXS_ANGLE = 16`) |
| `comm_dir` | `None` | override folder B for one run |

Or name the mode: `DR.run('once', 'AgBH')` / `DR.run('manual', 'DR_run7', run_time=3600)` /
`DR.run('auto')`.

#### The beam-damage tweak (b and c)

Every full sweep moves each reactor to the next spot in a ±2 mm window at 0.2 mm — 20 spots —
then wraps back to the first:

```
R0@p00 → R1@p00 → R2@p00 → R0@p01 → R1@p01 → R2@p01 → … → p19 → p00 → …
```

```python
DR.set_tweak(radius=2.0, step=0.2)   # the default: 20 spots over 4 mm
DR.set_tweak(on=False)               # pin every frame to the reactor centre
DR.reset_positions()                 # start the walk again at p00
```

The spot index **and** the true motor read-back are both in the name, so a spot can never be
guessed wrong:

```
<startX filename>_R0_p07_2026_07_30_01_14_02_x051.40_y77.60_det05.00m_waxs16.00_expt10s
```

— name, reactor, spot index, timestamp, X, stage height, detector distance, WAXS angle,
exposure. The OAV camera frame is saved under `<user_name>_<same name>id_<scan_id>`. In auto
mode a `T<value>` token sits between the reactor and the spot index (§C2).

#### Email alerts (all three modes)

Window open, window closed, every temperature change and every failed frame are emailed. Set
the recipients **before** starting the bluesky session, and prove the route once per beamtime:

```bash
export DC_MAIL_TO=yuzhang@bnl.gov,someone.else@bnl.gov     # default: yuzhang@bnl.gov
export DC_MAIL=0                                           # or switch it off entirely
```

```python
mail_test()        # sends one now — do it ONCE, at the start
```

Best effort only: a daemon thread with a 20 s timeout, throttled per message kind, and three
failures in a row (a machine with no SMTP route) switch mailing off for the rest of the session.
Mail never delays or stops acquisition. sys76 also texts/emails through its own `notify()` at
each temperature step and on campaign failure — the two paths are independent on purpose, so a
dead beamline network still leaves you the lab's messages.

### B6. Handshake preflight (auto mode only — both machines, ~2 minutes)

Both relays running, bluesky loaded, nothing collecting yet:

1. **On sys76**, 📡 Beamline handshake tab → **🧹 Clear markers**. Never start on top of a stale
   `StartX`/`StopX` — a stale `StopX` closes the next window before the first frame.
2. → **🔁 Round-trip test**. It must report put/read/delete OK.
3. → **📤 Send startX**. Watch it move: it disappears from the route picture within a poll, the
   sys76 relay logs an upload, the beamline relay logs a download, and folder B gets `StartX.npy`.
4. **On the beamline**, look without consuming, then consume it by hand so the run starts clean:

   ```python
   peek_markers()                     # lists folder B, deletes NOTHING
   consume_marker('StartX.npy')       # prints ts + filename, then DELETES it
   ```

5. **On sys76**, set **tempX temperature** to something unmistakable (e.g. `77`) → **🌡 Send
   tempX**, and repeat step 4 with `'TempX.npy'`. The print must show `temp_c=77.0`; that number
   is the whole reason the marker exists. Below the buttons the tab states, in words, whether the
   markers it just decoded carry `temp_c` and what the frames will therefore be called
   (`…_T77.0_…`). If it warns **carries no `temp_c`**, stop: the ramp will collect the whole night
   under one temperature.
6. **On sys76**, → **📤 Send stopX** and repeat step 4 with `'StopX.npy'`.
7. **On sys76**, → **🧹 Clear markers** once more. The route picture must read **"empty ✓
   (nothing stuck)"** on both machines before you go on.

**Rehearsing the whole night in a minute.** 📡 tab → **🎬 Simulate the whole campaign** replays the
markers the loaded case *will* send — `startX` → one `tempX` per rung → `stopX` — at a few seconds
per step instead of hours. The rungs are read from the case's own script, so what you rehearse is
what will run. With `DR.run_auto(...)` up at the beamline you should watch the file names change T
nine times and stop by themselves; then **🧹 Clear markers** and `peek_markers()` empty on both
sides. It sends real markers, so run it *before* the campaign, never during one.

Do **not** use **🎭 Simulate reply** during a real run — it is a GUI bench tool. Same for 🎬.

---

## PART C — running (auto mode)

### C1. Start it, in this order

1. **On the beamline**: `mail_test()` once, then
   `DR.run_auto(exp_time=10, run_time=60*60*14)`. It prints its configuration, then blocks with
   `waiting for StartX.npy ...` about once a minute. `run_time` must outlast the campaign — case
   014 as configured (RT + 5 rungs up + 4 down, 1 h each) is **≈10.4 h**, so use `60*60*14`, not
   the 10 h default. The GUI prints the campaign's own estimate next to ▶ Start; take that number,
   add margin, and don't reuse a number from a previous night.
2. **On sys76**: Campaign tab → **Start (hardware)**. Only after B6 passed.
3. Keep four things visible: the GUI campaign panel, the jupyter relay tab, the beamline relay
   terminal, and the bluesky session.
4. Every window prints `WINDOW n OPEN — filename=… batch=i/N T=…°C` with the per-reactor recipe,
   and `WINDOW n CLOSED — … (m min, k frames total)`. Both are emailed.
5. Never create a marker by hand while a campaign is running.

To watch folder B from a second beamline terminal without stealing markers:

```bash
python SeqGrowthWatcher.py --beamline smi --monitor --hours 14
```

`--monitor` consumes nothing and shows what each waiting marker carries — e.g.
`TempX.npy (DR_AuC8C12_b01, T=40.0)`. **Never run `SeqGrowthWatcher.py` without `--monitor`
while `run_auto` is serving** — the two would race for the same markers and each would eat half
the windows.

### C2. The temperature in the file name

sys76 sends a `TempX.npy` the moment the block **settles** at each new set-point (after the
tolerance/stability gate, not when the ramp is commanded). The beamline reads it between frames
and rebuilds the name from there on:

```
DR_AuC8C12_b01_R0_T25.0_p03_2026_07_30_21_10_44_x049.60_y77.60_det05.00m_waxs16.00_expt10s
DR_AuC8C12_b01_R0_T40.0_p04_2026_07_30_22_11_02_x049.80_y77.60_det05.00m_waxs16.00_expt10s
```

Four rules, in the order they matter:

1. **The token is rebuilt, never appended.** One frame can only ever carry one `T…`; even a lab
   filename that already contains a `T<number>` token has it stripped first.
2. **`StartX` is authoritative.** The opening `temp_c` in its payload sets the token, and a
   window opened *without* one clears it — an earlier campaign's temperature cannot leak into a
   new batch.
3. **`TempX` opens and closes nothing.** One seen while idle is remembered for the window that
   follows; it never starts or ends a collection.
4. **At most one frame lags.** The marker is applied between exposures, so the frame already in
   flight when the block settles still carries the previous T. Expected, not a fault.

By hand at the beamline, when there is no lab window (manual/one-shot modes read **no** `TempX`):

```python
DR.temp_c                                     # what the lab last said, or None
DR.set_temp(100)                              # stamp T100.0 by hand
DR.set_temp(None)                             # take T back out of the names
DR.collect_once('DR_pristine', temp_c=25)     # the A0 by-hand pristine frames
```

### C3. Warnings that mean the files are not what you think

The run is still producing files, but not the ones you assume:

* `WARNING StopX filename=… does not match StartX=…` — two windows crossed. The frames in that
  window are named after the *first* filename.
* `WARNING cap of … min reached … closing the window without a StopX` — the stop marker was
  lost. Everything after that point is uncollected until the next `StartX`.
* `FRAME FAILED (n/5)` — that one exposure was lost; the loop mails, backs off 2 s and carries
  on. **Five in a row** print `ACQUISITION STOPPED` and end the window. The lab's window is
  still open, so fixing the fault and re-running `DR.run_auto()` resumes collection.
* **No `T…` in the names** — check `DR.temp_c`. Either the case has
  `beamline_temp_marker_SeqGrowth = False`, or its `StartX` carried no `temp_c`, or the sys76
  relay is down and `TempX` is stuck in folder A.

### Abort

1. **GUI → Stop.** The sequencer stops between safe operations, turns stirring off, and sends
   `stopX` if a window is open.
2. If comms are down, stop acquisition at the beamline first (`Ctrl-C` in the bluesky loop, then
   `RE.abort()` if the RunEngine is left paused), then stop the GUI campaign.
3. Physical faults (misrouted pump/valve/heater/gas) → hardware E-stop and pressure isolation.
   Software cleanup is not a substitute.
4. Before retrying: stop both programs, note the last filename, **clear all markers on both
   sides**, fix the fault, redo B6, start a new campaign.

### Post-run

1. One closed collection per batch, each with its own filename.
2. No marker left on either side (`sys76_relay.py --list`; `peek_markers()`).
3. `./Beamline_Control/sync_to_smi.sh --pull` and commit — that versions the day's
   `2026C2_Flow.py` with the data.
4. Keep the case files, both relay logs, the GUI log and the beamline files together.
5. Log every manual intervention, timeout, filename mismatch and aborted batch.
6. Write the calibrated `DR.pos_dict` and WAXS angle into the logbook — they are the two things
   nobody can reconstruct afterwards.

---

## Troubleshooting

| Symptom | Where to look |
|---|---|
| GUI route picture says **`cms`** at SMI | `DC_BEAMLINE` was not exported before `./run`. Check with `tr '\0' '\n' < /proc/<pid>/environ \| grep DC_BEAMLINE`, then restart the GUI. |
| Notebook cell 1 prints `DC_BEAMLINE : cms` | jupyter itself was started without the export; the profile resolves at import. Restart the kernel *and* jupyter, or set `os.environ['DC_BEAMLINE']='smi'` above the imports. |
| Marker chip stuck under **folder A** | The sys76 relay is not running (A3), or its cell/terminal died. |
| GUI: *"comm folder did not respond within 2 s"* | Folder A's mount is hung/unmounted. `ls` it in a terminal. Nothing can be sent until it is back. |
| Marker leaves folder A but never reaches folder B | The two relays are on different Dropbox folders — compare the `DC_BEAMLINE` line in both banners. Or the beamline relay is not running (B2). |
| Markers appear late, or a deleted marker still lists | sshfs directory caching. Mount with `-o dcache_timeout=1 -o entry_timeout=1 -o attr_timeout=1` (the default 20 s cache is longer than a poll). |
| bluesky prints `waiting for StartX.npy` forever | Compare its `comm dir` line with the beamline relay's `LOCAL_DIR`. They must be the *same string*. `exists=False` means the folder is not there at all. |
| A window opens and closes with 0 frames | A stale `StopX` was sitting in folder B. The loop discards a stale StopX when no window is open — but clear both sides before starting (B6.6). |
| Windows are served but half are missed | A second `SeqGrowthWatcher.py` is running without `--monitor` and eating markers. |
| Every frame has the same exposure regardless of `exp_time` | `det_exposure_time` is a *plan* in the current profile; the loop runs it via `RE(...)`. If you copied `measure_one` elsewhere, a bare `det_exposure_time(t,t)` is a silent no-op. |
| File names say a WAXS angle the detector is not at | `setup_beamline()` was skipped. Names use the motor read-back, so this only happens if the motor is absent. |
| `NA` in a file name where a number belongs | That motor/device did not read back (e.g. `pil2M_pos` absent). The frame is still collected; `NA` is used instead of `nan` so a name can never contain a space. |
| Every frame lands on the same spot | The tweak is off (`DR.set_tweak(on=True)`), or you are in `collect_once`, which is centre-pinned by design. |
| No `T…` token in any file name | `DR.temp_c` is `None`: the case has `beamline_temp_marker_SeqGrowth = False`, or `StartX` carried no `temp_c` (temperature control off), or `TempX` is stuck upstream — check the route picture. |
| The names show the *previous* T for one frame after a step | By design: `TempX` is applied between exposures, so the frame in flight finishes under the old stamp. |
| Names carry a T but the GUI never reached it | `DR.set_temp()` was typed by hand earlier in the session and is still latched. `DR.set_temp(None)`, or open a fresh window — `StartX` overwrites it. |
| Two `T…` tokens in one name | Cannot happen from this code (the token is rebuilt each frame). If you see it, the *lab* filename contains something like `_T5_` that is not a temperature — rename the campaign. |
| No emails at all | `mail_test()` in the bluesky session. Empty `DC_MAIL_TO`, `DC_MAIL=0`, or three consecutive send failures switched mailing off for the session — restart the session to re-enable. |
| Emails stop partway through a run | Same three-strike rule. It is deliberate: mail failures must never block acquisition. The run itself is unaffected. |
| No OAV frames | `setup_ova()` did not run — it arms the JPEG plugin and sets the write path. `DR.setup_beamline()` calls it. |
| `motorX is not bound` | The MDrive IOC came up after the file loaded: `set_motors(MDrive.m3, stage.y)`. |
| X moves to a position nothing is at | An old `set_motors(MDrive.m5, MDrive.m3)` from 2025 is in the session. In 2026C2, `m3` **is** X. |
| Hardware Control shows a Flow EZ at `0.00 mbar` and setting pressure does nothing | Look for the red `Underpressure` chip next to the channel: the SDK is reporting *no supply gas*, not zero pressure. Check the cylinder, the regulator (≈2–3 bar), and the line into the LineUP. Valves (M-Switch) keep working without gas, so the rest of the tab looks healthy. |

### Bench test with no beamline and no Dropbox

Point both sides at one private folder and drive the markers by hand:

```bash
python Beamline_Control/SeqGrowthWatcher.py --dry --shared-dir runtime_data/sg_comm --once --poll 0.2
```

The watcher must consume/delete all three markers and print one bounded start/stop pair with the
temperature it saw (`RESULT {'filename': …, 'timed_out': False, 'temp_c': 40.0}`). Drive it from
the sys76 repo:

```python
from droplet_core.beamline_comm import SharedDirComm, BeamlineHandshake
hs = BeamlineHandshake(SharedDirComm('runtime_data/sg_comm'), startx_name='StartX.npy',
                       stopx_name='StopX.npy', tempx_name='TempX.npy')
hs.send_startX('bench_b01', payload={'filename': 'bench_b01', 'temp_c': 25.0})
hs.send_tempX('bench_b01', temp_c=40.0, payload={'filename': 'bench_b01'})
hs.send_stopX('bench_b01', payload={'filename': 'bench_b01'})
```

```bash
python -m pytest tests/test_smi_seqgrowth.py tests/test_beamline_comm.py -q   # no hardware
```

---

## File map

| File | Machine | What it is |
|---|---|---|
| `streamlit_gui/sequential_growth_page.py` | sys76 | the GUI (Campaign + 📡 Beamline handshake tabs) |
| `streamlit_gui/sequential_growth_twin.py` | sys76 | the rig twin and the marker-route picture |
| `protocols/sequential_growth.py` | sys76 | the campaign engine that sends startX/tempX/stopX |
| `protocols/config/014_20260730_dr_au_c8c12_tramp_config.py` | sys76 | today's case — Au NP + C8/C12/C16, RT hold then T ramp |
| `protocols/config/auto_flow.py` | sys76 | `DC_BEAMLINE` profiles — folder A / B / Dropbox |
| `droplet_core/beamline_comm.py` | sys76 | marker encode/decode, transports, `make_relay` |
| `Dropbox_Comm/Dropbox_Com.ipynb` | sys76 | the relay as run in jupyter (:5642) |
| `Dropbox_Comm/sys76_relay.py` | sys76 | the same relay as a CLI process |
| `Beamline_Control/sync_to_smi.sh` | sys76 | push/pull between this repo and the controls folder |
| `Beamline_Control/xf11bm_relay.py` | beamline | Dropbox ⇄ folder B relay |
| `Beamline_Control/SMI_SeqGrowth.py` | beamline | SMI acquisition loop (`DR`) — the three modes |
| `Beamline_Control/README_SMI_BEAMLINE.md` | beamline | the short card, ships next to the code |
| `Beamline_Control/2026C2_Flow.py` | beamline | the run-book file (edited at the beamline, `--pull`ed back) |
| `Beamline_Control/SeqGrowthWatcher.py` | beamline | folder-B monitor + bench test |
| `Beamline_Control/NanoSyn.py` | beamline | the equivalent loop for CMS |
