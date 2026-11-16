"""
Fetch the photograph chosen for each element (build/photos.tsv, picked by hand from each element's Wikidata picture
and the one Periodic-Table-JSON names, looking at every one) from Wikimedia Commons, at most 480 pixels on a side,
as media/<symbol>.jpg, and write who made each and under what licence to media/credits.tsv.

  python3 photos.py          (needs pillow)

A photograph was left out where the candidates were an illustration, a diagram, a museum display or apparatus, a
compound or solution rather than the element, or showed the element's symbol (a labelled sample would give the
answer away).
"""
import csv, io, json, re, sys, time, html, urllib.parse, urllib.request
from pathlib import Path
from PIL import Image

HERE = Path(__file__).resolve().parent
MEDIA = HERE.parent / 'media'
UA = {'User-Agent': 'knack-elements-build/1.0 (https://github.com/lorien-danger/knack-elements)'}
SIDE = 480

def get(url):
    for k in range(6):
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=120) as r: return r.read()
        except Exception as e:
            print('  retry:', e, file=sys.stderr); time.sleep(10 * (k + 1))
    raise RuntimeError(url)

def text(s):
    """Commons metadata is HTML: keep the words"""
    t = re.sub(r'\s+', ' ', html.unescape(re.sub(r'<[^>]+>', '', s or ''))).strip()
    return re.sub(r'(Unknown author)\1', r'\1', t)

def info(name):
    q = urllib.parse.urlencode({'action': 'query', 'titles': 'File:' + name, 'prop': 'imageinfo',
                                'iiprop': 'url|extmetadata|size', 'iiurlwidth': SIDE, 'iiurlheight': SIDE, 'format': 'json'})
    page = next(iter(json.loads(get('https://commons.wikimedia.org/w/api.php?' + q))['query']['pages'].values()))
    ii = page['imageinfo'][0]
    m = {k: v.get('value', '') for k, v in ii.get('extmetadata', {}).items()}
    return ii, m

if __name__ == '__main__':
    MEDIA.mkdir(exist_ok=True)
    rows = list(csv.reader(open(HERE / 'photos.tsv'), delimiter='\t'))[1:]
    credits = [['symbol', 'file', 'commons page', 'author', 'licence', 'licence link', 'description']]
    for z, sym, name in rows:
        if not name: continue
        ii, m = info(name)
        img = Image.open(io.BytesIO(get(ii.get('thumburl') or ii['url'])))
        if img.mode in ('RGBA', 'LA', 'P'):
            img = img.convert('RGBA'); bg = Image.new('RGBA', img.size, 'white'); bg.alpha_composite(img); img = bg
        img = img.convert('RGB')
        img.thumbnail((SIDE, SIDE), Image.LANCZOS)
        img.save(MEDIA / f'{sym}.jpg', quality=82, optimize=True, progressive=True)
        lic = text(m.get('LicenseShortName'))
        if not lic or re.search(r'non-?commercial|fair use|all rights', lic, re.I): raise SystemExit(f'{sym}: licence {lic!r}')
        credits.append([sym, f'media/{sym}.jpg', ii['descriptionurl'], text(m.get('Artist')) or text(m.get('Credit')),
                        lic, m.get('LicenseUrl', ''), text(m.get('ImageDescription'))[:300]])
        print(z, sym, img.size, lic, flush=True)
        time.sleep(1)
    with open(MEDIA / 'credits.tsv', 'w', newline='') as f:
        csv.writer(f, delimiter='\t', lineterminator='\n').writerows(credits)
