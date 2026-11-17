"""
Make the dataset (columns.json and rows.jsonl at the top of this repo) from the copies of the sources in
build/sources/ (fetch.py) and the photographs in media/ (photos.py). Every value is read from a source; nothing is
typed in here except how the sources' words are mapped onto columns (CATEGORY below).

  python3 build.py

Where each column comes from:
  name, symbol, atomic number, group, period, block, atomic weight, density (g/cm³ there, kg/m³ here),
  melting point (kelvin there, °C here), occurrence, state,
  name origin      Wikipedia, "List of chemical elements" (sources/list.html)
  kind             Periodic-Table-JSON's "category" (sources/ptj.json), arranged as a tree (CATEGORY)
  discovered       Wikipedia, "Timeline of chemical element discoveries" (sources/timeline.wiki): the year in the
                   "Observed" column of its modern-discoveries table; empty for elements in its pre-modern table
                   (known since antiquity or the Middle Ages, with no agreed year)
  photo            media/<symbol>.jpg where photos.py fetched one (credits in media/credits.tsv)

Values Wikipedia gives only as predictions (in parentheses), or as a mass number in brackets instead of a standard
atomic weight, are left empty, as is a melting point given as a bound (carbon's ">4000").
"""
import html, json, re
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
SRC = HERE / 'sources'

# Periodic-Table-JSON's categories, as a tree. Its "unknown, probably ..." (elements 109-118 but 112 and 114) are
# left empty: their chemistry has not been measured.
CATEGORY = {
    'alkali metal': ['metal', 'alkali metal'],
    'alkaline earth metal': ['metal', 'alkaline earth metal'],
    'transition metal': ['metal', 'transition metal'],
    'post-transition metal': ['metal', 'post-transition metal'],
    'lanthanide': ['metal', 'lanthanide'],
    'actinide': ['metal', 'actinide'],
    'metalloid': ['metalloid'],
    'diatomic nonmetal': ['nonmetal', 'diatomic nonmetal'],
    'polyatomic nonmetal': ['nonmetal', 'polyatomic nonmetal'],
    'noble gas': ['nonmetal', 'noble gas'],
}

# How the dataset looks and is asked in the Knack app. The embedding columns (photo look, name sound) are added by
# embed.py and the app's `npm run describe`; build.py keeps them if columns.json already has them.
META = {
    'name': 'Elements', 'item': 'element', 'items': 'elements', 'title': 'name',
    'practices': [
        {'name': 'Symbols', 'columns': ['name', 'symbol']},
        {'name': 'Where it sits', 'columns': ['name', 'atomic number', 'group', 'kind']},
        {'name': 'What it looks like', 'columns': ['photo', 'name']},
    ],
    'columns': [
        {'name': 'name', 'type': 'text'},
        # text, not plain: symbols that share letters (Hs, Hf, He) are near, so they are offered against each other
        {'name': 'symbol', 'type': 'text'},
        {'name': 'photo', 'type': 'plain', 'media': 'image'},
        {'name': 'atomic number', 'type': 'number'},
        {'name': 'kind', 'type': 'tree'},
        {'name': 'group', 'type': 'number'},
        {'name': 'period', 'type': 'number'},
        {'name': 'block', 'type': 'plain', 'order': ['s-block', 'p-block', 'd-block', 'f-block']},
        {'name': 'state', 'type': 'plain', 'label': 'State at 25 °C', 'order': ['solid', 'liquid', 'gas']},
        {'name': 'discovered', 'type': 'number'},
        {'name': 'atomic weight', 'type': 'number', 'digits': 4},
        {'name': 'density (kg/m³)', 'type': 'number', 'scale': 'log', 'label': 'Density', 'unit': 'kg/m³', 'digits': 3},
        {'name': 'melting point (°C)', 'type': 'number', 'label': 'Melting point', 'unit': '°C', 'digits': 3},
        {'name': 'occurrence', 'type': 'plain', 'order': ['primordial', 'from decay', 'synthetic']},
        {'name': 'name origin', 'type': 'plain', 'size': 'normal'},
    ],
}

def clean(s):
    s = re.sub(r'<sup.*?</sup>', '', s, flags=re.S)
    return re.sub(r'\s+', ' ', html.unescape(re.sub(r'<[^>]+>', '', s))).strip()

def number(s):
    """a plain number as Wikipedia writes it, or None for a prediction (…), a mass number […], a bound or a dash"""
    s = s.replace('−', '-').replace(',', '').replace(' ', '').replace(' ', '')
    return float(s) if re.fullmatch(r'-?\d+(\.\d+)?', s) else None

def wikipedia_list():
    t = (SRC / 'list.html').read_text()
    notes = {html.unescape(m.group(1)): clean(m.group(2)).lstrip('^ ')
             for m in re.finditer(r'<li id="([^"]+)">(.*?)</li>', t, re.S)}
    out = {}
    for r in re.findall(r'<tr[^>]*>(.*?)</tr>', t, re.S):
        cells = re.findall(r'<t[dh][^>]*>(.*?)</t[dh]>', r, re.S)
        if len(cells) != 16 or not clean(cells[0]).isdigit(): continue
        v = [clean(c) for c in cells]
        z = int(v[0])
        refs = [html.unescape(x) for x in re.findall(r'href="#([^"]+)"', cells[3])]
        origin = [notes[x] for x in refs if x in notes]
        out[z] = {
            'symbol': v[1], 'name': v[2], 'name origin': origin[0] if origin else None,
            'group': int(v[4]) if v[4].isdigit() else None, 'period': int(v[5]), 'block': v[6].split('-')[0],
            'atomic weight': number(v[7]), 'density': number(v[8]), 'melt K': number(v[9]),
            'occurrence': v[14], 'state': v[15] if v[15] in ('solid', 'liquid', 'gas') else None,
        }
    assert sorted(out) == list(range(1, 119)), sorted(set(range(1, 119)) - set(out))
    return out

def discoveries():
    t = (SRC / 'timeline.wiki').read_text()
    pre, modern = t.split('==Modern discoveries==')[0].split('== Pre-modern and early modern discoveries ==')[1], t.split('==Modern discoveries==')[1].split('==See also==')[0]
    ancient = set()
    for row in pre.split('\n|-')[1:]:
        m = re.match(r'\s*\|\s*(\d+)\s*\n', row)
        if m: ancient.add(int(m.group(1)))
    years = {}
    for row in modern.split('\n|-')[1:]:
        lines = [l for l in row.strip('\n').split('\n') if l.startswith('|')]
        if len(lines) < 3: continue
        z = re.match(r'\|\s*(\d+)', lines[0])
        if not z: continue
        y = re.search(r'\b(\d{4})\b', re.sub(r'<!--.*?-->', '', lines[2]))
        years[int(z.group(1))] = int(y.group(1)) if y else None
    return ancient, years

if __name__ == '__main__':
    wp = wikipedia_list()
    ptj = {e['number']: e for e in json.loads((SRC / 'ptj.json').read_text())['elements']}
    ancient, years = discoveries()
    missing = set(range(1, 119)) - ancient - set(years)
    assert not missing, f'no discovery row for {sorted(missing)}'
    assert not ancient & set(years), ancient & set(years)
    old = json.loads((ROOT / 'columns.json').read_text()) if (ROOT / 'columns.json').exists() else {'columns': []}
    META['columns'] += [c for c in old['columns'] if c['type'] == 'embedding']
    rows = []
    for z in range(1, 119):
        w, p = wp[z], ptj[z]
        assert p['symbol'] == w['symbol'], (z, p['symbol'], w['symbol'])
        photo = ROOT / 'media' / f"{w['symbol']}.jpg"
        row = {
            'id': w['symbol'].lower(),
            'name': w['name'],
            'symbol': w['symbol'],
            'photo': f'media/{photo.name}' if photo.exists() else None,
            'atomic number': z,
            'kind': CATEGORY.get(p['category']),
            'group': w['group'],
            'period': w['period'],
            'block': f"{w['block']}-block",
            'state': w['state'],
            'discovered': None if z in ancient else years[z],
            'atomic weight': w['atomic weight'],
            'density (kg/m³)': None if w['density'] is None else round(w['density'] * 1000, 6),  # Wikipedia gives g/cm³
            'melting point (°C)': None if w['melt K'] is None else round(w['melt K'] - 273.15, 2),
            'occurrence': w['occurrence'],
            'name origin': w['name origin'],
        }
        if p['category'] not in CATEGORY and not p['category'].startswith('unknown'): raise SystemExit(f"{z}: category {p['category']!r}")
        rows.append({k: v for k, v in row.items() if v is not None})
    with open(ROOT / 'columns.json', 'w') as f: f.write(json.dumps(META, indent=1, ensure_ascii=False) + '\n')
    with open(ROOT / 'rows.jsonl', 'w') as f:
        for r in rows: f.write(json.dumps(r, ensure_ascii=False) + '\n')
    print(len(rows), 'rows')
