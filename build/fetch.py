"""
Download the sources this dataset is made from into build/sources/, so build.py works from fixed copies (and anyone
can see exactly what it read). Run it again to take newer versions; the date is written to sources/FETCHED.

  python3 fetch.py

- list.html: Wikipedia, "List of chemical elements" (rendered table: group, period, block, atomic weight, density,
  melting point, origin, phase at room temperature, and footnotes on where each name comes from). CC BY-SA 4.0.
- timeline.wiki: Wikipedia, "Timeline of chemical element discoveries" (wikitext: the year each element was first
  observed, and which were known before modern times). CC BY-SA 4.0.
- ptj.json: Bowserinator/Periodic-Table-JSON (each element's category, compiled from Wikipedia). CC BY-SA 3.0.
- wikidata.csv: Wikidata (each element's main picture, P18, and its item id). CC0.
"""
import json, sys, urllib.parse, urllib.request, datetime
from pathlib import Path

HERE = Path(__file__).resolve().parent
OUT = HERE / 'sources'
UA = {'User-Agent': 'knack-elements-build/1.0 (https://github.com/lorien-danger/knack-elements)'}

def get(url, data=None, headers={}):
    req = urllib.request.Request(url, data=data, headers={**UA, **headers})
    with urllib.request.urlopen(req, timeout=120) as r: return r.read()

def wikipedia_html(title):
    q = urllib.parse.urlencode({'action': 'parse', 'page': title, 'prop': 'text|revid', 'format': 'json', 'formatversion': 2})
    j = json.loads(get(f'https://en.wikipedia.org/w/api.php?{q}'))['parse']
    return j['text'], j['revid']

def wikipedia_wikitext(title):
    q = urllib.parse.urlencode({'action': 'parse', 'page': title, 'prop': 'wikitext|revid', 'format': 'json', 'formatversion': 2})
    j = json.loads(get(f'https://en.wikipedia.org/w/api.php?{q}'))['parse']
    return j['wikitext'], j['revid']

SPARQL = '''
SELECT ?item ?z ?symbol ?image WHERE {
  ?item wdt:P31 wd:Q11344; wdt:P1086 ?z . FILTER(?z >= 1 && ?z <= 118)
  OPTIONAL { ?item wdt:P246 ?symbol }
  OPTIONAL { ?item wdt:P18 ?image }
} ORDER BY ?z
'''

if __name__ == '__main__':
    OUT.mkdir(exist_ok=True)
    revs = {}
    text, revs['List of chemical elements'] = wikipedia_html('List of chemical elements')
    (OUT / 'list.html').write_text(text)
    text, revs['Timeline of chemical element discoveries'] = wikipedia_wikitext('Timeline of chemical element discoveries')
    (OUT / 'timeline.wiki').write_text(text)
    (OUT / 'ptj.json').write_bytes(get('https://raw.githubusercontent.com/Bowserinator/Periodic-Table-JSON/master/PeriodicTableJSON.json'))
    q = urllib.parse.urlencode({'query': SPARQL})
    (OUT / 'wikidata.csv').write_bytes(get(f'https://query.wikidata.org/sparql?{q}', headers={'Accept': 'text/csv'}))
    stamp = {'date': datetime.date.today().isoformat(), 'wikipedia revisions': revs}
    (OUT / 'FETCHED').write_text(json.dumps(stamp, indent=1) + '\n')
    print(json.dumps(stamp))
