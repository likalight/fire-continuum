"""Preserve NASA's separate-instrument published observation and its provenance."""
import json,hashlib
from pathlib import Path
from datetime import datetime,timezone
import requests
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'web/public/data'
URL='https://science.nasa.gov/wp-content/uploads/2025/10/indonesia_oli_2019258.jpg'
def main():
    session=requests.Session();session.trust_env=False;r=session.get(URL,timeout=60);r.raise_for_status()
    assert r.content[:2]==b'\xff\xd8','Expected JPEG'
    (OUT/'borneo-landsat-2019-09-15.jpg').write_bytes(r.content)
    manifest={'title':'Smoke Blankets Borneo','publisher':'NASA Earth Observatory','article_date':'2019-09-18','observation_date':'2019-09-15','instrument':'Landsat 8 Operational Land Imager (OLI)','source_url':'https://science.nasa.gov/earth/earth-observatory/smoke-blankets-borneo-145614/','image_url':URL,'local_image':'borneo-landsat-2019-09-15.jpg','sha256':hashlib.sha256(r.content).hexdigest(),'retrieved_utc':datetime.now(timezone.utc).isoformat(),'credit':'NASA Earth Observatory / Joshua Stevens; Landsat data from the U.S. Geological Survey. Article by Adam Voiland.','interpretation':'NASA describes active fires in southern Borneo, highlighted with shortwave-infrared bands 7-6-2 over natural-color bands 4-3-2.','supports':['An actual fire episode in southern Borneo during September 2019','A separate instrument observes active fires during the calendar episode'],'does_not_support':['Independent accuracy of our regional count or adjusted magnitude','A georeferenced fire perimeter or burned-area estimate','Proof that every hotspot is vegetation fire','Fire-free conditions in the comparison year'],'date_note':'The article download list labels the Landsat image September 15; the filename day-of-year 258 also corresponds to September 15. The 2025 upload path is a website migration date, not the observation date.'}
    (OUT/'case-evidence.json').write_text(json.dumps(manifest,indent=2));(ROOT/'reports/case-evidence.json').write_text(json.dumps(manifest,indent=2))
    print(json.dumps(manifest,indent=2))
if __name__=='__main__':main()
