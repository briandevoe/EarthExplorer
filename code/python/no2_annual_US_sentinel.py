import ee
import time

# ---------------------------------------------------------------------
# Initialize Earth Engine
# ---------------------------------------------------------------------
ee.Initialize(project="ee-testing-458522")

# ---------------------------------------------------------------------
# Parameters
# ---------------------------------------------------------------------
YEAR = 2021
START_DATE = f"{YEAR}-01-01"
END_DATE = f"{YEAR}-12-31"
SCALE = 7000  # Native resolution for Sentinel-5P NO2
MAX_PIXELS = 1e13
FOLDER = "NO2_S5P_CONUS_2021"
FILENAME = "no2_s5p_conus_2021"

# ---------------------------------------------------------------------
# Define contiguous U.S. geometry
# ---------------------------------------------------------------------
states = ee.FeatureCollection("TIGER/2018/States")
conus = states.filter(ee.Filter.notEquals("NAME", "Alaska")) \
              .filter(ee.Filter.notEquals("NAME", "Hawaii")) \
              .geometry()

# ---------------------------------------------------------------------
# Load Sentinel-5P NO2 and compute mean
# ---------------------------------------------------------------------
no2 = ee.ImageCollection("COPERNICUS/S5P/NRTI/L3_NO2") \
    .filterDate(START_DATE, END_DATE) \
    .filterBounds(conus) \
    .select("NO2_column_number_density")

no2_mean = no2.mean().clip(conus)

# ---------------------------------------------------------------------
# Export to Google Drive
# ---------------------------------------------------------------------
task = ee.batch.Export.image.toDrive(
    image=no2_mean,
    description=FILENAME,
    folder=FOLDER,
    fileNamePrefix=FILENAME,
    region=conus.bounds().getInfo()['coordinates'],
    scale=SCALE,
    crs="EPSG:4326",
    maxPixels=MAX_PIXELS
)

print("🌀 Submitting NO₂ export task for CONUS...")
task.start()

# Monitor
while task.active():
    print("⏳ Waiting for task to complete...")
    time.sleep(30)

print(f"✅ Export task completed with status: {task.status()['state']}")
