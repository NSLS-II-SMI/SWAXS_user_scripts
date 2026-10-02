"""Use the library's simulated beamline, with an explicit source-checkout dependency."""

import importlib.util
import os
import sys
from pathlib import Path

import pytest


_checkout = Path(os.environ.get(
    "SMI_PLANS_CHECKOUT", Path(__file__).resolve().parents[4] / "smi-plans",
)).expanduser().resolve()
_fixtures = _checkout / "tests" / "conftest.py"
if not _fixtures.is_file():
    raise pytest.UsageError("Set SMI_PLANS_CHECKOUT to a smi-plans source checkout with tests/conftest.py")
sys.path.insert(0, str(_checkout / "src"))
_spec = importlib.util.spec_from_file_location("_smi_script_simulation", _fixtures)
_module = importlib.util.module_from_spec(_spec)
sys.modules[_spec.name] = _module
_spec.loader.exec_module(_module)
sim = _module.sim


@pytest.fixture
def inject(sim, monkeypatch):
    """Inject library simulation globals and restore them after each script test."""
    import importlib

    def apply(module_name):
        for name in (module_name, "smi_plans._core", "smi_plans._compose", "smi_plans._preprocessors"):
            importlib.import_module(name)
        for name, module in list(sys.modules.items()):
            if name.startswith("smi_plans") and module is not None:
                for key, value in sim.globals_dict().items():
                    monkeypatch.setattr(module, key, value, raising=False)
        return importlib.import_module(module_name)

    return apply
