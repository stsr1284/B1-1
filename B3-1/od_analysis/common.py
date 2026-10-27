from pathlib import Path
import hashlib
import json

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / 'data/raw'
OUT = ROOT / 'data/processed/transit_od'
AUDIT = ROOT / 'outputs/od_validation'
FIG = ROOT / 'outputs/od_figures'
META = ROOT / 'data/metadata/transit_hourly_od'
HOURS = [f'h{h:02}' for h in range(24)]
COLS = ['date', 'origin', 'destination'] + HOURS
VERSION = 'od-v1'

def write_json(path, obj):
    path.parent.mkdir(parents=True, exist_ok=True)
    part = path.with_suffix(path.suffix + '.tmp')
    part.write_text(json.dumps(obj, ensure_ascii=False, indent=2, allow_nan=False) + '\n')
    part.replace(path)

def sha(path):
    with path.open('rb') as f:
        return hashlib.file_digest(f, 'sha256').hexdigest()
