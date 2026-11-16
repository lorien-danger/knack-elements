# Elements

The 118 chemical elements: name, symbol, a photograph of the element itself, atomic number, what kind of element it
is, group, period and block, its state at room temperature, when it was discovered, atomic weight, density, melting
point, whether it occurs in nature, and where its name comes from. There are also two embeddings: how the photograph
looks (DINOv2) and how the name sounds (a ByT5 pronunciation model). A dataset for
[Knack](https://github.com/lorien-danger/knack). Add it by this repo's link.

Suggested decks: **Symbols** (name, symbol), **Where it sits** (name, atomic number, group, kind) and **What it
looks like** (photo, name).

## Columns

| column | what it is | source |
| --- | --- | --- |
| name, symbol | the IUPAC name (British spelling, as Wikipedia uses: aluminium, caesium) and symbol | Wikipedia, [List of chemical elements](https://en.wikipedia.org/wiki/List_of_chemical_elements) |
| photo | a photograph of the element, at most 480 pixels on a side, in `media/` (95 elements) | Wikimedia Commons; each file's author and licence are in [`media/credits.tsv`](media/credits.tsv) |
| atomic number | 1 to 118 | Wikipedia, List of chemical elements |
| kind | a tree: metal › alkali metal, alkaline earth metal, transition metal, post-transition metal, lanthanide or actinide; metalloid; nonmetal › diatomic nonmetal, polyatomic nonmetal or noble gas | the `category` of [Periodic-Table-JSON](https://github.com/Bowserinator/Periodic-Table-JSON), which is compiled from Wikipedia |
| group, period | where it sits in the table. There is no group for the f-block elements (La to Yb, Ac to No), as Wikipedia gives none | Wikipedia, List of chemical elements |
| block | s-, p-, d- or f-block | Wikipedia, List of chemical elements |
| state at 25 °C | solid, liquid or gas | Wikipedia, List of chemical elements ("phase at standard state") |
| discovered | the year it was first observed or recognised as a new element: the "Observed" year in Wikipedia's [Timeline of chemical element discoveries](https://en.wikipedia.org/wiki/Timeline_of_chemical_element_discoveries). It is empty for the 14 elements in its pre-modern table (carbon, sulfur, iron, copper, zinc, arsenic, silver, tin, antimony, platinum, gold, mercury, lead, bismuth), which have no agreed year. For nihonium the source gives "2003–2004" and 2003 is used | Wikipedia, Timeline of chemical element discoveries |
| atomic weight | the standard atomic weight. It is empty where there is none, which Wikipedia shows as a mass number in brackets | Wikipedia, List of chemical elements |
| density (kg/m³) | Wikipedia's g/cm³ × 1000 (the app shows a gas's 0.00009 g/cm³ as 0, so kg/m³ is used) | Wikipedia, List of chemical elements |
| melting point (°C) | Wikipedia's kelvin − 273.15, shown to 3 significant digits | Wikipedia, List of chemical elements |
| occurrence | primordial, from decay, or synthetic | Wikipedia, List of chemical elements |
| name origin | where the name comes from, word for word as Wikipedia's footnote has it ("Greek líthos 'stone'") | Wikipedia, List of chemical elements |
| photo look | an embedding of the photograph: DINOv2 (`facebook/dinov2-base`), 64 numbers, in `photo-look.npy`. The full 768-number vectors are in `build/photo-look-full.npy`. Elements without a photo are NaN rows | made by `build/embed.py` |
| name sound | an embedding of how the name is said: a ByT5 pronunciation model, 64 numbers, in `name-sound.npy` | made by the Knack app's `npm run describe` |

Wikipedia gives some values only as predictions, shown in parentheses (the density of a superheavy element, say).
Those are left empty, and so is carbon's melting point (">4000 K"). Kind is empty for elements 109 to 118 except
copernicium and flerovium, which the source marks only as "unknown, probably …".

### Photographs

A photograph is included only where one shows the element itself. For 23 elements there is none: polonium, radon,
francium, curium, and fermium onwards. Their candidates were illustrations, diagrams, museum displays, apparatus, a
solution of a compound (curium), or an alloy (fermium), so those elements have no photo. Each photo was chosen by
looking at the element's Wikidata image and the one Periodic-Table-JSON names. Photos that show the element's symbol
(labelled samples, neon-sign letters) were passed over, since they would give the answer away. Some photos of very
radioactive elements show their glow (actinium, astatine, einsteinium).

The files were downloaded from Wikimedia Commons and scaled down. Their licences: CC BY 3.0 (43), Free Art License
(21), public domain (12), CC BY-SA 3.0 (13, two of them the German port), CC BY-SA 4.0 (3), CC BY 4.0 (1),
CC BY 2.0 (1), and attribution only (1). Most are by Jurii ([images-of-elements.com](https://images-of-elements.com))
and Alchemist-hp ([pse-mendelejew.de](https://www.pse-mendelejew.de)). Author, licence, Commons page and description
for every file are in [`media/credits.tsv`](media/credits.tsv).

## Licence

The data (`columns.json`, `rows.jsonl`, the `.npy` files) is drawn from Wikipedia (CC BY-SA 4.0) and
Periodic-Table-JSON (CC BY-SA 3.0), so it is shared under
[Creative Commons Attribution-ShareAlike 4.0](https://creativecommons.org/licenses/by-sa/4.0/) (`LICENSE`).
Attribution: Wikipedia contributors, "List of chemical elements" (revision 1384916014) and "Timeline of chemical
element discoveries" (revision 1386015288); Bowserinator and contributors, Periodic-Table-JSON.

Each photograph in `media/` keeps its own licence, listed in `media/credits.tsv`. The build scripts in `build/` may
be used freely.

## Checked by hand

- The photos, one by one, against their element. Each file name also matches its element.
- Every row against [PubChem's periodic table](https://pubchem.ncbi.nlm.nih.gov/periodic-table/) (an independent
  source):
  - Symbols, names, states, atomic weights and kinds agree, apart from known differences of convention. PubChem
    spells aluminum and cesium. It calls astatine a halogen and polonium a metalloid, where the source used here
    says metalloid and post-transition metal.
  - Densities and melting points agree within a few percent, except for some radioactive elements (Fr, Ra, Th, Am,
    Bk), where references disagree.
  - Discovery years differ for about 45 elements, because references date "discovery" differently: first observed,
    or first isolated. Hydrogen is 1671 here (Boyle first made it) but often 1766 (Cavendish identified it).
    Fluorine is 1771 here (Scheele) but often 1886 (Moissan isolated it).
- A sample of whole rows, read one by one against PubChem and the usual reference values: H, Li, Fe, Hg, Au, Ho,
  Md and Og. They are right, with one small error in the source: Wikipedia's list gives mercury's melting point as
  234.43 K (−38.7 °C), where its article and PubChem give 234.32 K (−38.8 °C).

## Building it

`build/` makes the dataset. It needs Python 3; `embed.py` and `photos.py` also need pillow, and `embed.py` needs
numpy, torch and transformers.

    cd build
    python3 fetch.py      # download the sources into build/sources/ (already there: the copies used)
    python3 photos.py     # the photographs chosen in photos.tsv -> media/, with media/credits.tsv
    python3 build.py      # columns.json and rows.jsonl
    python3 embed.py      # photo look (DINOv2): photo-look.npy and its column
    # name sound: from a checkout of the Knack app,  npm run describe -- <this folder> name

`build.py` keeps the embedding columns already in `columns.json`, so it can be rerun on its own.
