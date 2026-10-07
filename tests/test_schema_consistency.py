"""Guards the contract between backend (ml_client) and ml-service (ApplicantInput).

The ML service silently ignores unknown fields, so a naming mismatch does not
raise an error. It just scores every applicant on empty input.
"""
import ast
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "backend"))

from ml_client import FIELD_NAME_MAP  # noqa: E402

# ML-service fields the backend deliberately or temporarily does not send.
# Remove an entry once it is fixed; the test then enforces it.
KNOWN_GAPS = {
    "CODE_GENDER": "Not collected on purpose: gender should not drive credit decisions. Retrain without it.",
}


def ml_service_fields():
    tree = ast.parse((ROOT / "ml-service" / "api.py").read_text())
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef) and node.name == "ApplicantInput":
            return {n.target.id for n in node.body if isinstance(n, ast.AnnAssign)}
    raise AssertionError("ApplicantInput class not found in ml-service/api.py")


def test_every_mapped_name_exists_in_ml_service():
    unknown = set(FIELD_NAME_MAP.values()) - ml_service_fields()
    assert not unknown, f"backend sends fields the ML service does not accept: {sorted(unknown)}"


def test_every_ml_field_is_sent_by_backend():
    missing = ml_service_fields() - set(FIELD_NAME_MAP.values()) - set(KNOWN_GAPS)
    assert not missing, f"ML service fields the backend never sends: {sorted(missing)}"
