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
SCALE = 7000  # Sentinel-5P NO2 native resolution
MAX_PIXELS = 1e13
FOLDER = "NO2_S5P_MA_2021"
FILENAME = "no2_s5p_massachusetts_2021"

# ---------------------------------------------------------------------
# Define Massachusetts geometry
# ---------------------------------------------------------------------
states = ee.FeatureCollection("TIGER/2018/States")
massachusetts = states.filter(ee.Filter.eq("NAME", "Massachusetts")).geometry()

# ---------------------------------------------------------------------
# Load and process NO2 data from Sentinel-5P
# ---------------------------------------------------------------------
no2 = ee.ImageCollection("COPERNICUS/S5P/NRTI/L3_NO2") \
    .filterDate(START_DATE, END_DATE) \
    .filterBounds(massachusetts) \
    .select("NO2_column_number_density")

# Optional: cloud filtering could be added here with 'cloud_fraction' if desired

# Compute annual mean NO2
no2_mean = no2.mean().clip(massachusetts)

# ---------------------------------------------------------------------
# Export to Google Drive
# ---------------------------------------------------------------------
task = ee.batch.Export.image.toDrive(
    image=no2_mean,
    description=FILENAME,
    folder=FOLDER,
    fileNamePrefix=FILENAME,
    region=massachusetts.bounds().getInfo()['coordinates'],
    scale=SCALE,
    crs="EPSG:4326",
    maxPixels=MAX_PIXELS
)

print("🌀 Submitting NO₂ export task for Massachusetts...")
task.start()

while task.active():
    print("⏳ Waiting for task to complete...")
    time.sleep(30)

print(f"✅ Export task completed with status: {task.status()['state']}")
