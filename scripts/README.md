# Scripts

| Script | Purpose |
|---|---|
| `convert_gpkg_to_geojson.py` | Convert KEM GeoPackage layers to GeoJSON for the web map |
| `update_docs_for_github_pages.sh` | Regenerate map data in `docs/data/` |

Sources are read from:
- `KEM/results/grids/`
- `KEM/data/networks/`
- `KEM/destinations/`
- `KEM/boundaries/`

Outputs are written to:
- `docs/data/*.geojson`
