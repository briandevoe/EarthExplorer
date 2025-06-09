import ee
import time

# Authenticate and initialize
ee.Authenticate()
ee.Initialize()

# Define year and date range
year = 2021
start_date = f'{year}-01-01'
end_date = f'{year}-12-31'

# Load NO₂ data (Sentinel-5P TROPOMI)
no2_collection = ee.ImageCollection('COPERNICUS/S5P/NRTI/L3_NO2') \
    .filterDate(start_date, end_date) \
    .select('NO2_column_number_density')

# Compute annual mean NO₂
no2_mean = no2_collection.mean()

# Define CONUS bounding box
conus = ee.Geometry.BBox(-125, 24, -66.5, 50)

# Scale factor (to convert from mol/m² to more readable values if needed)
scale_factor = 1e-5  # optional scaling, can remove if not needed
no2_scaled = no2_mean.multiply(scale_factor)

# Export to Google Drive
task = ee.batch.Export.image.toDrive(
    image=no2_scaled,
    description='NO2_Annual_2021_CONUS',
    folder='EarthEngine_NO2',
    fileNamePrefix='no2_2021_conus',
    region=conus,
    scale=1113.2,  # ~7km native resolution of TROPOMI
    crs='EPSG:4326',
    maxPixels=1e13
)

print("🌀 Submitting NO₂ export task for CONUS...")
task.start()

# Wait until done
while task.active():
    print("⏳ Waiting for task to complete...")
    time.sleep(30)

print(f"✅ Export task completed with status: {task.status()['state']}")

