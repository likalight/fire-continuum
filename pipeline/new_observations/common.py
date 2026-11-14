from pathlib import Path
import json,hashlib,shutil
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
OUT=ROOT/'data/raw/new-observations'
REPORTS=ROOT/'reports/new-observations'
OUT.mkdir(parents=True,exist_ok=True);REPORTS.mkdir(parents=True,exist_ok=True)
for name in ['protocol.json','october-transfer-protocol.json']:
 if not (OUT/name).exists():shutil.copyfile(HERE/name,OUT/name)
PINS=json.loads((HERE/'pinned-sha256.json').read_text(encoding='utf-8'))
def verify_input(name,data):
 expected=PINS.get(Path(name).name)
 if expected is None:raise ValueError('Unexpected input: '+Path(name).name)
 if hashlib.sha256(data).hexdigest()!=expected:raise ValueError('Pinned input changed: '+Path(name).name)
