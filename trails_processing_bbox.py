from pyrosm import OSM
import pandas as pd
import geopandas as gpd
from pathlib import Path

# data_dir = Path("data/trails")
# results = []
file = "data/trails/socal-latest.osm.pbf"


### Loop 1 MTB trails filter 1
# for file in data_dir.glob("*.osm.pbf"):

# trail_filter_mtb = {"route": ["mtb"]}

# print(f"processing {file}")
# osm = OSM(str(file))

# trails_mtb = osm.get_data_by_custom_criteria(
#     custom_filter=trail_filter_mtb,
#     filter_type="keep",
# )

# if trails_mtb is not None and not trails_mtb.empty:
#     results.append(trails_mtb)
#     print(f"Appended results with mtb trails from {file}")

### Loop 2 MTB trails filter 2
# ##for file in data_dir.glob("*.osm.pbf"):
# print(f"processing filter 2 on {file}")

# osm = OSM(str(file))

# trails_mtb_2 = osm.get_data_by_custom_criteria(
#     custom_filter={},
#     osm_keys_to_keep=["mtb:scale"],
#     filter_type="keep",
# )

# if trails_mtb_2 is not None and not trails_mtb_2.empty:
#     results.append(trails_mtb_2)
#     print(f"Appended results of filter 2 with mtb trails from {file}")

### Loop 3 - Hiking trails filter 1
# for file in data_dir.glob("*.osm.pbf"):
# print(f"processing filter 3 on {file}")
# osm = OSM(str(file))

# trail_filter_hiking_1 = {}

# trails_hiking_1 = osm.get_data_by_custom_criteria(
#     osm_keys_to_keep=["sac_scale", "osmc:symbol"],
#     custom_filter=trail_filter_hiking_1,
#     filter_type="keep",
# )

# if trails_hiking_1 is not None and not trails_hiking_1.empty:
#     results.append(trails_hiking_1)
#     print(f"Appended results of filter 3 with hiking trails from {file}")

# ### Loop 4 - Hiking trails filter 2
# # for file in data_dir.glob("*.osm.pbf"):
print(f"processing filter 4 on {file}")

osm = OSM(str(file))

trail_filter_hiking_2 = {"route": ["hiking"]}

trails_hiking_2 = osm.get_data_by_custom_criteria(
    custom_filter=trail_filter_hiking_2,
    filter_type="keep",
)

# if trails_hiking_2 is not None and not trails_hiking_2.empty:
#     results.append(trails_hiking_2)
#     print(f"Appended results of filter 4 with hiking trails from {file}")

# all_trails = gpd.GeoDataFrame(results, ignore_index=True, crs="EPSG:4326")

# all_trails.drop_duplicates()
print("processing geodataframe and appending gpkg file")
alltrails = trails_hiking_2[["id", "tags", "osm_type", "geometry"]]

alltrails.to_file(
    "data/processed/alltrails.gpkg", driver="GPKG", mode="a"
)  # add mode='a' to next batches to append the file.
