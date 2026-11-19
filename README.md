# scopeREPAIR – Website-Prototyp

Statischer Prototyp (Python + Jinja2), deployed auf Vercel aus `site/`.

```
pip install jinja2 pillow
python3 build.py          # baut site/ (Hub, v1, v2, Bilder, Foto-ZIP)
python3 -m http.server -d site 8765
python3 tools/qa.py v1 de # Screenshots 1440/390, Overflow, verdeckte Klicks
python3 tools/flows.py v1 de  # Interaktionstests
```

- `content.py` – einzige Quelle für Texte (DE/EN von scoperepair.de, FR/RU übersetzt) und Katalogdaten (`data/`).
- `templates/v1`, `templates/v2` – Varianten; `templates/shared` – Wizards und Formular-Makros.
- `static/js/proto.js` – gemeinsames Verhalten (Menüs, Dropdowns, Wizards, Fake-Formulare, Galerie, Filter).
- `assets/photos/` – alle Fotos von scoperepair.de, nach Seiten/Hersteller/Typ/Modell sortiert, mit `manifest.csv` (Quelle je Datei). Als ZIP unter `/downloads/scoperepair-fotos.zip`.
