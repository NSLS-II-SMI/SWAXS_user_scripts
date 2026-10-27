# Kapton experiment logs

The default `LOG_DIRECTORY` points here. Use `LOG_DIRECTORY / "kapton_air_holder_01_bpm2_bpm3_waxs_oav.sqlite"`
for this specimen; `resume=True` reopens the same database after a process restart.
Runtime SQLite files, journals and lock files are ignored by git.

SQLite WAL requires a local filesystem with working locks. If this checkout is
on NFS on the beamline host, place the live database on local disk and use the
SQLite backup API to write snapshots here instead.
