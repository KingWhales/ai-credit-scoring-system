import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
MODELS = ROOT / "ml-service" / "models"
MIN_AUC = 0.75


def _metrics():
    path = MODELS / "metrics.json"
    assert path.exists(), "metrics.json missing: run ml-service/src/train.py and commit the result"
    return json.loads(path.read_text())


def test_auc_meets_threshold():
    m = _metrics()
    assert m["auc_roc"] >= MIN_AUC, f"Model AUC {m['auc_roc']} is below the required {MIN_AUC}"


def test_metrics_match_committed_model():
    m = _metrics()
    sha = hashlib.sha256((MODELS / "xgb_credit_model.pkl").read_bytes()).hexdigest()
    assert sha == m["model_sha256"], "Model file changed without re-recording its metrics: rerun train.py"
