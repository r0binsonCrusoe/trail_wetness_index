from owslib.wcs import WebCoverageService
import xarray as xr
import rioxarray as rxr


# bulk density
bdod_wcs = WebCoverageService("https://maps.isric.org/mapserv?map=/map/bdod.map")

bdod_0_5_mean = bdod_wcs.contents["bdod_0-5cm_mean"]

# bdod_0_5_mean.supportedCRS
# bdod_0_5_mean.supportedFormats
# bdod_0_5_mean.boundingboxes

bbox = [("X", -1784000.0, -1140000.0), ("Y", 1356000.0, 1863000.0)]
crs = "http://www.opengis.net/def/crs/EPSG/0/152160"

response = bdod_wcs.getCoverage(
    identifier="bdod_0-5cm_mean",
    crs=crs,
    bbox=bbox,
    resx=250,
    resy=250,
    format="image/tiff",
)

with open("./data/bulk_density_0_5_mean.tif", "wb") as file:
    file.write(response.read())


# Clay content
clay_wcs = WebCoverageService("https://maps.isric.org/mapserv?map=/map/clay.map")

# print(clay_wcs.contents.keys())

# Sand content
sand_wcs = WebCoverageService("https://maps.isric.org/mapserv?map=/map/sand.map")

# Soil Organic Carbon content
soc_wcs = WebCoverageService("https://maps.isric.org/mapserv?map=/map/soc.map")


# use sand = sand.rio.reproject_match(bulk_density) to reproject to difference CRS if needed. All input geotifs should be in the same CRS, resolution, and extent.


def compute_soil_properties_xr(bd, sand, clay, soc):
    # Add coarse fragments later to adjust awc in rocky soils. Usually awc * (1 - (cf/100))
    """
    Compute porosity, field capacity, wilting point, and available water capacity using xarray DataArrays.
    All parameters are xarray DataArrays with aligned dimensions and spatial coordinates.
    """
    om = soc * 1.724

    # Particle density of mineral soil in g/cm³
    particle_density = 2.65

    # Porosity
    porosity = 1 - (bd / particle_density)

    # Field Capacity (volumetric water content at -33 kPa)
    fc = (
        -0.251 * sand
        + 0.195 * clay
        + 0.011 * om
        + 0.006 * sand * om
        - 0.027 * clay * om
        + 0.452
    )

    # Wilting Point (volumetric water content at -1500 kPa)
    wp = (
        -0.024 * sand
        + 0.487 * clay
        + 0.006 * om
        + 0.005 * sand * om
        - 0.013 * clay * om
        + 0.068
    )

    # Available Water Capacity
    awc = fc - wp

    return porosity.clip(0, 1), fc.clip(0, 1), wp.clip(0, 1), awc.clip(0, 1)


# === Load SoilGrids Layers ===
bulk_density = rxr.open_rasterio(
    "bulk_bulk_density_0_5_mean.tif", masked=True
).squeeze()
sand = rxr.open_rasterio("sand.tif", masked=True).squeeze()
clay = rxr.open_rasterio("clay.tif", masked=True).squeeze()
soc = rxr.open_rasterio("soil_organic_carbon.tif", masked=True).squeeze()

# Optional: scale or adjust units if needed
# e.g., SoilGrids data may use g/cm³ * 100, or % in 0–100 range — check your data

# === Compute Soil Properties ===
ds = xr.Dataset(
    {"bulk_density": bulk_density, "sand": sand, "clay": clay, "soc": soc}
)  # xarray DataSet

ds["porosity"], ds["field_capacity"], ds["wilting_point"], ds["awc"] = (
    compute_soil_properties_xr(ds["bulk_density"], ds["sand"], ds["clay"], ds["soc"])
)
