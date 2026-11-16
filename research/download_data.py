from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
import hashlib, json, urllib.request, zipfile

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / 'data' / 'raw'
RAW.mkdir(parents=True, exist_ok=True)
BASE = 'https://raw.githubusercontent.com/bradleyboehmke/completejourney/master/'
FILES = {'online_retail.zip': 'https://archive.ics.uci.edu/static/public/352/online%2Bretail.zip'}
for name in ['transactions.rds','products.rda','demographics.rda','campaigns.rda','campaign_descriptions.rda','coupons.rda','coupon_redemptions.rda']:
    FILES[name] = BASE + 'data/' + name
FILES['completejourney_DESCRIPTION.txt'] = BASE + 'DESCRIPTION'
def download(pair):
    name, url = pair
    path = RAW / name
    if not path.exists():
        req = urllib.request.Request(url, headers={'User-Agent':'retail-research/1.0'})
        with urllib.request.urlopen(req, timeout=120) as response:
            path.write_bytes(response.read())
    return {'file': name, 'url':url, 'bytes':path.stat().st_size, 'sha256':hashlib.sha256(path.read_bytes()).hexdigest(), 'download_date':'2026-11-01'}
with ThreadPoolExecutor(max_workers=4) as pool:
    manifest = list(pool.map(download, FILES.items()))
(RAW.parent / 'manifest.json').write_text(json.dumps(manifest,indent=2),encoding='utf-8')
with zipfile.ZipFile(RAW / 'online_retail.zip') as archive:
    for name in archive.namelist():
        if name.endswith('.xlsx'):
            (RAW / Path(name).name).write_bytes(archive.read(name))
print(json.dumps(manifest,indent=2))
