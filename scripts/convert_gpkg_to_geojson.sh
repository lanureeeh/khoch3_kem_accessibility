#!/bin/bash
# Convert KEM source datasets to docs/data/*.geojson using GDAL.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
KEM_ROOT="$(cd "$PROJECT_ROOT/../.." && pwd)"
OUT_DIR="$PROJECT_ROOT/docs/data"
CLIP_BOUNDARY="$PROJECT_ROOT/KEM_merged_dissolved.geojson"

# Avoid mixed PROJ installs (e.g. conda vs homebrew GDAL)
if [ -d "/opt/homebrew/share/proj" ]; then
  export PROJ_DATA="/opt/homebrew/share/proj"
  export PROJ_LIB="/opt/homebrew/share/proj"
fi

mkdir -p "$OUT_DIR"

convert() {
  local src="$1"
  local layer="$2"
  local out="$3"
  local clip="${4:-0}"
  if [ ! -f "$src" ]; then
    echo "Skip: missing $src"
    return 0
  fi
  rm -f "$OUT_DIR/$out"
  if [ "$clip" = "1" ] && [ -f "$CLIP_BOUNDARY" ]; then
    ogr2ogr -f GeoJSON "$OUT_DIR/$out" "$src" "$layer" -t_srs EPSG:4326 -clipsrc "$CLIP_BOUNDARY"
    echo "OK: $(basename "$src") -> $out (clipped)"
    return 0
  fi
  ogr2ogr -f GeoJSON "$OUT_DIR/$out" "$src" "$layer" -t_srs EPSG:4326
  echo "OK: $(basename "$src") -> $out"
}

convert "$KEM_ROOT/results/grids/kem_walk_charing_stations.gpkg" "kem_walk_charing_stations" "walk_charging_stations.geojson" "1"
convert "$KEM_ROOT/results/grids/kem_walk_pt_stops.gpkg" "kem_walk_pt_stops" "walk_pt_stops.geojson" "1"
convert "$KEM_ROOT/results/grids/kem_walk_schools.gpkg" "kem_walk_schools" "walk_schools.geojson" "1"
convert "$KEM_ROOT/results/grids/kem_walk_kindergartens.gpkg" "kem_walk_kindergartens" "walk_kindergartens.geojson" "1"
convert "$KEM_ROOT/results/grids/kem_bike_charging_stations.gpkg" "kem_bike_charging_stations" "bike_charging_stations.geojson" "1"
convert "$KEM_ROOT/results/grids/kem_bike_pt_stops.gpkg" "kem_bike_pt_stops" "bike_pt_stops.geojson" "1"
convert "$KEM_ROOT/results/grids/kem_bike_schools.gpkg" "kem_bike_schools" "bike_schools.geojson" "1"
convert "$KEM_ROOT/results/grids/kem_bike_kindergartens.gpkg" "kem_bike_kindergartens" "bike_kindergartens.geojson" "1"

convert "$KEM_ROOT/data/networks/walk_network_kem.gpkg" "edges" "walk_network.geojson" "1"
convert "$KEM_ROOT/data/networks/bike_network_kem.gpkg" "edges" "bike_network.geojson" "1"

convert "$KEM_ROOT/destinations/charging_stations.gpkg" "charging_points_austria" "charging_stations.geojson" "1"
convert "$KEM_ROOT/destinations/pt_stops.gpkg" "pt_stops" "pt_stops.geojson" "1"
convert "$KEM_ROOT/destinations/schools.gpkg" "schools" "schools.geojson" "1"
convert "$KEM_ROOT/destinations/kindergartens.gpkg" "kindergartens" "kindergartens.geojson" "1"

if [ -f "$CLIP_BOUNDARY" ]; then
  rm -f "$OUT_DIR/kem_boundaries.geojson"
  ogr2ogr -f GeoJSON "$OUT_DIR/kem_boundaries.geojson" "$CLIP_BOUNDARY" -t_srs EPSG:4326
  echo "OK: repo boundary -> kem_boundaries.geojson"
fi

if [ -f "$KEM_ROOT/boundaries/KEM_merged_dissolved.geojson" ]; then
  rm -f "$OUT_DIR/boundary.geojson"
  ogr2ogr -f GeoJSON "$OUT_DIR/boundary.geojson" "$KEM_ROOT/boundaries/KEM_merged_dissolved.geojson" -t_srs EPSG:4326
  echo "OK: boundary -> boundary.geojson"
fi

echo "Done. Files written to $OUT_DIR"
