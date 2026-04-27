#!/bin/bash
# Regenerate GeoJSON from KEM sources for docs/ map.

set -e
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

cd "$PROJECT_ROOT"
if ! python3 scripts/convert_gpkg_to_geojson.py; then
  echo "Python converter unavailable, falling back to GDAL converter..."
  scripts/convert_gpkg_to_geojson.sh
fi
echo "docs/ is ready for commit."
