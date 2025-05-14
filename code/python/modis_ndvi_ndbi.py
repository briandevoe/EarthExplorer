# -----------------------------------------------------------------------------
# Script: modis_export_annual_all_years.py
# Purpose: Export annual average NDVI and NDBI from MODIS 2000–2023
# -----------------------------------------------------------------------------

import ee
import time
from datetime import datetime
from pydrive2.auth import GoogleAuth
from pydrive2.drive import GoogleDrive

# -----------------------------------------------------------------------------
# 1. SETUP
# -----------------------------------------------------------------------------
ee.Initialize(project="ee-testing-458522")
region = ee.FeatureCollection("TIGER/2018/States").geometry()

gauth = GoogleAuth()
gauth.LoadClientConfigFile("client_secrets.json")
gauth.LocalWebserverAuth()
drive = GoogleDrive(gauth)

# -----------------------------------------------------------------------------
# 2. CONFIG
# -----------------------------------------------------------------------------
modis_dataset = "MODIS/061/MOD09GA"
export_folder = "earthengine_exports"
export_scale = 1000
max_pixels = 1e13
start_year = 2000
end_year = 2023

# -----------------------------------------------------------------------------
# 3. FUNCTIONS
# -----------------------------------------------------------------------------
def mask_clouds(image):
    qa = image.select('state_1km').unmask()
    return image.updateMask(
        qa.bitwiseAnd(2**10).eq(0).And(qa.bitwiseAnd(2**11).eq(0))
    )

def compute_ndvi(img): return img.normalizedDifference(['sur_refl_b02', 'sur_refl_b01']).rename('NDVI')
def compute_ndbi(img): return img.normalizedDifference(['sur_refl_b06', 'sur_refl_b02']).rename('NDBI')

def export_image(image, band_name, year):
    desc = f"{band_name}_US_annual_{year}"
    task = ee.batch.Export.image.toDrive(
        image=image.toFloat().clip(region),
        description=desc,
        folder=export_folder,
        fileNamePrefix=desc.lower(),
        region=region,
        scale=export_scale,
        crs="EPSG:4326",
        maxPixels=max_pixels
    )
    task.start()
    print(f"🛰️ Export started: {desc}")
    return task

# -----------------------------------------------------------------------------
# 4. MAIN LOOP — YEARS 2000 TO 2023
# -----------------------------------------------------------------------------
tasks = []

for year in range(start_year, end_year + 1):
    start_date = f"{year}-01-01"
    end_date = f"{year + 1}-01-01"
    print(f"\n📆 Processing year: {year}")

    try:
        collection = ee.ImageCollection(modis_dataset) \
            .filterDate(start_date, end_date) \
            .filterBounds(region) \
            .map(mask_clouds)

        ndvi_collection = collection.map(compute_ndvi)
        ndbi_collection = collection.map(compute_ndbi)

        ndvi_mean = ndvi_collection.mean().rename("NDVI_AnnualMean")
        ndbi_mean = ndbi_collection.mean().rename("NDBI_AnnualMean")

        tasks.append(export_image(ndvi_mean, "NDVI", year))
        tasks.append(export_image(ndbi_mean, "NDBI", year))

    except Exception as e:
        print(f"❌ Error processing {year}: {e}")

# -----------------------------------------------------------------------------
# 5. OPTIONAL: Monitor a few exports
# -----------------------------------------------------------------------------
print("\n📦 Monitoring first 5 export tasks (optional):")
for task in tasks[:5]:
    while task.active():
        print(f"⏳ {task.config['description']} status: {task.status()['state']}")
        time.sleep(10)
    print(f"✅ {task.config['description']} export complete: {task.status()['state']}")
    if 'error_message' in task.status():
        print(f"❌ {task.config['description']} error: {task.status()['error_message']}")
