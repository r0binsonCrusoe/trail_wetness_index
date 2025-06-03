import xarray as xr
from soils import ds
import s3fs


# ----- Pull in NCEI CFS data for Precipitation, surface runoff, subsurface runoff, potential evaporation -----

# 1. Point s3fs at the public bucket (no credentials needed)
fs = s3fs.S3FileSystem(anon=True)

# 2. List a directory (e.g. daily time_series files for soil moisture)
path = "noaa-cfs-pds/cfs.20250530/06/"  # adjust to your year/month dynamically
files = fs.glob(
    path + "6hrly_grib_01/flxf2025053012.01.2025053006.grb2"
)  # sm0to10cm = soil moisture 0–10 cm

# 3. Open as a single concatenated Dataset
ds_cfs = xr.open_mfdataset(
    ["s3://" + f for f in files],
    engine="cfgrib2",  # or "netcdf4", depending on format
    combine="by_coords",
    backend_kwargs={"fs": fs},
)

precipitation = ds_cfs["prate"]
evaporation = ds_cfs["pevap"]
surface_runoff = ds_cfs["runoff"]
subsurface_runoff = ds_cfs["baseflow"]

# 4. Inspect variables
print(precipitation)


# -----soil moisture functions--------


def update_soil_moisture(S_prev, P, ET, R=None, D=None, FC=None, WP=None):
    # Optional terms default to zero if not provided
    R = R if R is not None else 0
    D = D if D is not None else 0

    # Update soil moisture
    S_new = S_prev + P - ET - R - D

    # Cap at field capacity (or porosity, if you model it explicitly)
    if FC is not None:
        S_new = xr.where(S_new > FC, FC, S_new)

    # Bound to wilting point
    if WP is not None:
        S_new = xr.where(S_new < WP, WP, S_new)

    return S_new


def compute_trail_wetness_index(S, WP, FC):
    """Paramaters: S: Soil moisture. WP: wilting point. FC: Field Capacity"""
    wi = (S - WP) / (FC - WP)
    wi = wi.clip(0, 1)  # Bound between 0 and 1
    return wi


# Use actual observed data where posible,
wi_obs = smops / FC
wi_obs = wi_obs.clip(0, 1)

# 1. Create a Dataset of static soil properties - On soils.py - imported ds (dataset containing porosity, field capacity, etc)


# 2. Initialize S₀ (could be field_capacity or SMOPS from yesterday)
S = ds["field_capacity"].copy(deep=True)


# 3. Loop over time, update soil moisture
# I don't think I would need to do this if I am just saving it to the django model and storing in PostGIS
soil_moisture_list = []
wetness_index_list = []

threshold_mm = 5.0  # You can tune this (see below)
alpha = 0.2  # Wetness bump if recent rain

for t in range(n_days):
    P_t = precip[t]  # DataArray for day t
    ET_t = evap[t]  # DataArray for day t
    # Optional: calculate runoff & drainage
    S = update_soil_moisture(
        S, P_t, ET_t, FC=ds["field_capacity"], WP=ds["wilting_point"]
    )
    rain_flag = xr.where(P_t > threshold_mm, 1.0, 0.0)
    w_index = compute_trail_wetness_index(S, ds["wilting_point"], ds["field_capacity"])
    w_index_augmented = (w_index + alpha * rain_flag).clip(0, 1)

    # Save to DB/django model instead of list that will be used for DataArrays?
    soil_moisture_list.append(S)
    wetness_index_list.append(w_index)


# 4. Stack into time-series DataArrays
soil_moisture_ts = xr.concat(soil_moisture_list, dim="time")
trail_wetness_ts = xr.concat(wetness_index_list, dim="time")
