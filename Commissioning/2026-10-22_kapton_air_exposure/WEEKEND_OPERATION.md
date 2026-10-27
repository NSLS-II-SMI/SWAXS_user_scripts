# Weekend operation — updated after vacuum repair

Use [LOW_PRESSURE_CONTINUATION.md](LOW_PRESSURE_CONTINUATION.md) for the complete
current launch and live-test procedures. The earlier 0.05/0.10 Torr backup modes
are superseded. **All current pressure ceilings are 0.009 Torr.**

- Start with GV7 open, acquire SAXS + WAXS + OAV, log TetrAMM continuously.
- On trip close fast shutter/GV6/GV7, wait 30 s after boundary closure attempts,
  close pump IV1, disable turbo, then close cooling water.
- Continue pressure/current logging and periodic images after verified boundary
  isolation; never explicitly reopen the fast shutter or any gate valve.
- A failed boundary closure inhibits images; the pump shutdown is still attempted
  and the independent monitor continues. Shutdown is latched, not automatically reset.

The original overnight report is a historical record: its pressure ceiling was
0.05 Torr and its online counter was 4 h 57 min 26 s. The corrected beam estimate
is **4 h 59 min 22 s**, adding the accepted **116.03 s** early exposure. These
historical figures are not changed by the new configuration.

See `REPORT_AND_MOVIES.md` for the report, movies and reproducible Pixi tasks;
`SINGLE_RUN_ACCEPTANCE.md` for live hardware acceptance; and
`SINGLE_RUN_DESIGN.md` for the original architecture discussion.
