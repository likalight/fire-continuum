"""Run pinned acquisition and analyses; does not modify production models or publish."""
import subprocess,sys
from pathlib import Path
HERE=Path(__file__).resolve().parent
for name in ['discover.py','acquire.py','geolocation.py','download_geolocation.py','october.py','evaluate.py','mask_audit.py']:
 subprocess.run([sys.executable,str(HERE/name)],check=True)
