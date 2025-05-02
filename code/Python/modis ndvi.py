import ee
import time

# Initialize Earth Engine
ee.Initialize(project="ee-testing-458522")

# ---------------------------------------------------------------------
# 1. Define Bounding Box for the Continental US (CONUS)
# ---------------------------------------------------------------------
conus = ee.Geometry.Rectangle([-125, 24.5, -66.5, 49.5])

# ---------------------------------------------------------------------
# 2. Load MODIS NDVI for July 2023
# MOD13Q1 is 16-day NDVI at 250m, scaled by 0.0001
# ---------------------------------------------------------------------
ndvi = (ee.ImageCollection("MODIS/061/MOD13Q1")
        .filterDate("2023-07-01", "2023-07-31")
        .select("NDVI")
        .mean()
        .clip(conus)
        .multiply(0.0001)
        .rename("NDVI"))

# ---------------------------------------------------------------------
# 3. Export to Google Drive (500m resolution)
# ---------------------------------------------------------------------
task = ee.batch.Export.image.toDrive(
    image=ndvi,
    description="NDVI_CONUS_MODIS_July2023",
    folder="earthengine_exports",
    fileNamePrefix="ndvi_conus_july2023",
    region=conus,
    scale=500,
    crs="EPSG:4326",
    maxPixels=1e13
)

task.start()
print("🛰️ MODIS NDVI export started...")

# ---------------------------------------------------------------------
# 4. Monitor Export Status
# ---------------------------------------------------------------------
while task.active():
    print(f"⏳ Export status: {task.status()['state']}")
    time.sleep(10)

final_status = task.status()
print(f"✅ Final status: {final_status['state']}")

if 'error_message' in final_status:
    print("❌ Export failed with error:")
    print(final_status['error_message'])
else:
    print("📁 Export complete. Check Google Drive → 'earthengine_exports'")
