from pyrosm import OSM
import pandas as pd
import geopandas as gpd
from pathlib import Path

data_dir = Path("data/trails")
results = []
bboxes = [
    [-101.0000, 28.0000, -95.0000, 32.0000],
    [-101.0000, 32.0000, -95.0000, 37.0000],
    [-95, 25, -89, 31],
    [-95, 31, -89, 37],
]


trail_filter_mtb = {"route": ["mtb"]}

### Loop 1 MTB trails filter 1
for file in data_dir.glob("*.osm.pbf"):
    for box in bboxes:
        print(f"processing {file}, {box}")
        osm = OSM(str(file), bounding_box=box)

        trails_mtb = osm.get_data_by_custom_criteria(
            custom_filter=trail_filter_mtb,
            filter_type="keep",
        )

        if trails_mtb is not None and not trails_mtb.empty:
            results.append(trails_mtb)
            print(f"Appended results with mtb trails from {file}, {box}")

        ### Loop 2 MTB trails filter 2
        ##for file in data_dir.glob("*.osm.pbf"):
        print(f"processing filter 2 on {file}, {box}")

        # osm = OSM(str(file))

        trails_mtb_2 = osm.get_data_by_custom_criteria(
            custom_filter={},
            osm_keys_to_keep=["mtb:scale"],
            filter_type="keep",
        )

        if trails_mtb_2 is not None and not trails_mtb_2.empty:
            results.append(trails_mtb_2)
            print(f"Appended results of filter 2 with mtb trails from {file}, {box}")

        ### Loop 3 - Hiking trails filter 1
        # for file in data_dir.glob("*.osm.pbf"):
        print(f"processing filter 3 on {file}, {box}")
        # osm = OSM(str(file))

        trail_filter_hiking_1 = {}

        trails_hiking_1 = osm.get_data_by_custom_criteria(
            osm_keys_to_keep=["sac_scale", "osmc:symbol"],
            custom_filter=trail_filter_hiking_1,
            filter_type="keep",
        )

        if trails_hiking_1 is not None and not trails_hiking_1.empty:
            results.append(trails_hiking_1)
            print(f"Appended results of filter 3 with hiking trails from {file}, {box}")

        ### Loop 4 - Hiking trails filter 2
        # for file in data_dir.glob("*.osm.pbf"):
        print(f"processing filter 4 on {file}, {box}")

        # osm = OSM(str(file))

        trail_filter_hiking_2 = {"route": ["hiking"]}

        trails_hiking_2 = osm.get_data_by_custom_criteria(
            custom_filter=trail_filter_hiking_2,
            filter_type="keep",
        )

        if trails_hiking_2 is not None and not trails_hiking_2.empty:
            results.append(trails_hiking_2)
            print(f"Appended results of filter 4 with hiking trails from {file}, {box}")

all_trails = gpd.GeoDataFrame(pd.concat(results, ignore_index=True), crs="EPSG:4326")

all_trails.drop_duplicates()

all_trails_final = all_trails[["id", "tags", "osm_type", "geometry"]]

all_trails_final.to_file(
    "data/processed/us_trails.gpkg", driver="GPKG", mode="a"
)  # add mode='a' to next batches to append the file.
