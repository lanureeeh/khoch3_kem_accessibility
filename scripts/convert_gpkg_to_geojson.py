#!/usr/bin/env python3
"""
Convert KEM GeoPackage layers to GeoJSON for the accessibility web map.
Run from this repo root: python scripts/convert_gpkg_to_geojson.py
"""

from pathlib import Path

try:
    import geopandas as gpd
except ImportError:
    print("Error: geopandas required. Install with: pip install geopandas")
    raise SystemExit(1)


PROJECT_ROOT = Path(__file__).resolve().parent.parent
KEM_ROOT = PROJECT_ROOT.parent.parent
OUT_DIR = PROJECT_ROOT / "docs" / "data"
OUT_DIR.mkdir(parents=True, exist_ok=True)
CLIP_BOUNDARY_PATH = PROJECT_ROOT / "KEM_merged_dissolved.geojson"


def to_geojson(gdf: "gpd.GeoDataFrame", out_path: Path) -> None:
    """Write GeoDataFrame to WGS84 GeoJSON."""
    gdf = gdf.to_crs(epsg=4326)
    for col in gdf.columns:
        if gdf[col].dtype == object and gdf[col].apply(lambda x: isinstance(x, (list, dict))).any():
            gdf = gdf.drop(columns=[col], errors="ignore")
    gdf.to_file(out_path, driver="GeoJSON")


def clip_to_boundary_if_available(gdf: "gpd.GeoDataFrame") -> "gpd.GeoDataFrame":
    """Clip geometries to repo boundary if present."""
    if not CLIP_BOUNDARY_PATH.exists():
        return gdf
    try:
        boundary = gpd.read_file(CLIP_BOUNDARY_PATH).to_crs(gdf.crs)
        clipped = gpd.clip(gdf, boundary)
        if clipped.empty:
            return gdf.iloc[0:0].copy()
        return clipped
    except Exception as exc:
        print(f"  WARN: clip failed, using uncut geometry: {exc}")
        return gdf


def convert_gridded() -> None:
    """Convert KEM gridded accessibility layers."""
    grids_dir = KEM_ROOT / "results" / "grids"
    if not grids_dir.exists():
        print("Skipping gridded: KEM/results/grids not found")
        return

    file_map = [
        ("kem_walk_charing_stations.gpkg", "walk_charging_stations.geojson"),
        ("kem_walk_pt_stops.gpkg", "walk_pt_stops.geojson"),
        ("kem_walk_schools.gpkg", "walk_schools.geojson"),
        ("kem_walk_kindergartens.gpkg", "walk_kindergartens.geojson"),
        ("kem_bike_charging_stations.gpkg", "bike_charging_stations.geojson"),
        ("kem_bike_pt_stops.gpkg", "bike_pt_stops.geojson"),
        ("kem_bike_schools.gpkg", "bike_schools.geojson"),
        ("kem_bike_kindergartens.gpkg", "bike_kindergartens.geojson"),
    ]

    for src_name, out_name in file_map:
        src_path = grids_dir / src_name
        if not src_path.exists():
            print(f"  Skip: {src_name} not found")
            continue
        try:
            gdf = gpd.read_file(src_path)
            if "travel_time_min" not in gdf.columns and "travel_time" in gdf.columns:
                gdf["travel_time_min"] = gdf["travel_time"]
            gdf = clip_to_boundary_if_available(gdf)
            to_geojson(gdf, OUT_DIR / out_name)
            print(f"  OK: {src_name} -> {out_name}")
        except Exception as exc:
            print(f"  FAIL: {src_name}: {exc}")


def convert_networks() -> None:
    """Convert KEM walk and bike network layers."""
    networks_dir = KEM_ROOT / "data" / "networks"
    network_files = [
        ("walk_network_kem.gpkg", "walk_network.geojson"),
        ("bike_network_kem.gpkg", "bike_network.geojson"),
    ]

    for src_name, out_name in network_files:
        src_path = networks_dir / src_name
        if not src_path.exists():
            print(f"  Skip: {src_name} not found")
            continue
        try:
            layers = gpd.list_layers(src_path)
            layer_name = None
            if hasattr(layers, "columns") and "name" in layers.columns:
                for ln in layers["name"]:
                    if str(ln).lower() == "edges":
                        layer_name = str(ln)
                        break
                if layer_name is None and len(layers) > 0:
                    layer_name = str(layers["name"].iloc[0])
            gdf = gpd.read_file(src_path, layer=layer_name)
            gdf = gdf[gdf.geometry.notna()]
            if gdf.geometry.is_empty.any():
                gdf = gdf[~gdf.geometry.is_empty]
            gdf = clip_to_boundary_if_available(gdf)
            to_geojson(gdf, OUT_DIR / out_name)
            print(f"  OK: {src_name} -> {out_name}")
        except Exception as exc:
            print(f"  FAIL: {src_name}: {exc}")


def convert_destinations() -> None:
    """Convert KEM destination point layers."""
    destination_dir = KEM_ROOT / "destinations"
    destination_files = [
        ("charging_stations.gpkg", "charging_stations.geojson"),
        ("pt_stops.gpkg", "pt_stops.geojson"),
        ("schools.gpkg", "schools.geojson"),
        ("kindergartens.gpkg", "kindergartens.geojson"),
    ]

    for src_name, out_name in destination_files:
        src_path = destination_dir / src_name
        if not src_path.exists():
            print(f"  Skip: {src_name} not found")
            continue
        try:
            gdf = gpd.read_file(src_path)
            gdf = clip_to_boundary_if_available(gdf)
            to_geojson(gdf, OUT_DIR / out_name)
            print(f"  OK: {src_name} -> {out_name}")
        except Exception as exc:
            print(f"  FAIL: {src_name}: {exc}")


def convert_boundary() -> None:
    """Convert KEM study area boundary."""
    boundary_candidates = [
        KEM_ROOT / "boundaries" / "KEM_merged_dissolved.geojson",
        KEM_ROOT / "boundaries" / "KEM_merged_dissolved_buffered.geojson",
        KEM_ROOT / "boundaries" / "KEM_meged_dissolved_buffered_31287.geojson",
    ]
    for path in boundary_candidates:
        if not path.exists():
            continue
        try:
            gdf = gpd.read_file(path)
            to_geojson(gdf, OUT_DIR / "kem_boundaries.geojson")
            print(f"  OK: {path.name} -> kem_boundaries.geojson")
            return
        except Exception as exc:
            print(f"  FAIL boundary from {path.name}: {exc}")
    print("  Skip: no boundary file found")


def main() -> None:
    print("Converting KEM GeoPackage layers to GeoJSON for web map...")
    print(f"KEM root: {KEM_ROOT}")
    print(f"Output directory: {OUT_DIR}")
    if CLIP_BOUNDARY_PATH.exists():
        print(f"Clip boundary: {CLIP_BOUNDARY_PATH}")
    else:
        print("Clip boundary: not found, exporting uncut geometries")
    print("\nGridded layers:")
    convert_gridded()
    print("\nNetworks:")
    convert_networks()
    print("\nDestinations:")
    convert_destinations()
    print("\nBoundary:")
    convert_boundary()
    print("\nDone. GeoJSON files written to docs/data/")


if __name__ == "__main__":
    main()
