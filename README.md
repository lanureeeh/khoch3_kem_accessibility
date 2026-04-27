# KEM Accessibility Leaflet Map

Interactive Leaflet web map for accessibility analysis in the KEM region, published via GitHub Pages.

## Live map

[https://lanureeeh.github.io/KEM_accessibility/](https://lanureeeh.github.io/KEM_accessibility/)

## Project structure

```text
khoch3_kem_accessibility/
├── docs/
│   ├── index.html          # Leaflet application entry point (GitHub Pages)
│   ├── data/               # GeoJSON layers used by the map
│   └── README.md           # docs-specific notes
├── scripts/
│   ├── convert_gpkg_to_geojson.py
│   ├── convert_gpkg_to_geojson.sh
│   └── update_docs_for_github_pages.sh
└── README.md
```

## Publish-ready setup

- GitHub Pages source should be set to `docs/` on the `main` branch.
- `docs/index.html` loads all map layers from `docs/data/`.
- Regenerate `docs/data/*.geojson` before publishing if source data changes.

## Local preview

From the project root:

```bash
python -m http.server 8000
```

Open:

- <http://localhost:8000/docs/>

## Data update workflow

Use the scripts in `scripts/` to regenerate GeoJSON files from the source GPKG/network/destination data, then commit updates in `docs/data/`.
