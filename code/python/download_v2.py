# ------------------------------------------------------------------------------
# Script: GEE Quarterly Environmental Indices Export for Continental U.S.
# Purpose:
#   - Export quarterly mean composites for:
#       - NDVI (vegetation health)      | 250m | MODIS MOD13Q1
#       - NDBI (urban index, approx.)   | 500m | MODIS MOD09A1
#       - OZONE (air quality)           | ~7–28km | Sentinel-5P
#       - AOD (PM2.5 proxy, air quality)| ~1km  | MODIS MCD19A2
#   - For 2024, over the continental U.S. (excluding AK and HI)
# ------------------------------------------------------------------------------

import ee
import time
import os
from datetime import datetime
from pydrive2.auth import GoogleAuth
from pydrive2.drive import GoogleDrive

# ---------------------------------------------------------------------
# 0. Initialize Earth Engine
# ---------------------------------------------------------------------
ee.Initialize(project="ee-testing-458522")

# ---------------------------------------------------------------------
# 1. Date Ranges - Quarterly in 2024
# ---------------------------------------------------------------------
quarters = [
    ("2024-01-01", "2024-03-31"),
    ("2024-04-01", "2024-06-30"),
    ("2024-07-01", "2024-09-30"),
    ("2024-10-01", "2024-12-31"),
]

# ---------------------------------------------------------------------
# 2. Region - Continental U.S.
# ---------------------------------------------------------------------
region = ee.FeatureCollection("TIGER/2018/States") \
    .filter(ee.Filter.neq('NAME', 'Alaska')) \
    .filter(ee.Filter.neq('NAME', 'Hawaii')) \
    .geometry()

# ---------------------------------------------------------------------
# 3. Google Drive Authentication
# ---------------------------------------------------------------------
gauth = GoogleAuth()
if os.path.exists("credentials.json"):
    gauth.LoadCredentialsFile("credentials.json")
    if gauth.access_token_expired:
        gauth.Refresh()
    else:
        gauth.Authorize()
else:
    gauth.LoadClientConfigFile("client_secrets.json")
    gauth.GetFlow()
    gauth.flow.params.update({'access_type': 'offline', 'approval_prompt': 'force'})
    gauth.LocalWebserverAuth()
    gauth.SaveCredentialsFile("credentials.json")
drive = GoogleDrive(gauth)

# ---------------------------------------------------------------------
# 4. Loop Over Each Quarter
# ---------------------------------------------------------------------
export_folder_id = "189FkFs8JpDqyLdkH97ACoHojQgHiE6vp"

for start_date, end_date in quarters:
    output_prefix = f"continental_us_{start_date}_to_{end_date}"
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    download_folder = os.path.join("C:/Users/bdevoe/Desktop/git/EarthExplorer/data/raw/", f"{output_prefix}_{timestamp}")
    os.makedirs(download_folder, exist_ok=True)

    # -----------------------------------------------------------------
    # 4a. NDVI (MOD13Q1, 250m)
    # -----------------------------------------------------------------
    ndvi = ee.ImageCollection("MODIS/006/MOD13Q1") \
        .filterDate(start_date, end_date) \
        .select("NDVI") \
        .mean() \
        .clip(region) \
        .rename("NDVI")

    # -----------------------------------------------------------------
    # 4b. NDBI (approx. using MOD09A1 bands: SWIR = B6, NIR = B2)
    #      MODIS 500m resolution
    # -----------------------------------------------------------------
    modis_bands = ee.ImageCollection("MODIS/006/MOD09A1") \
        .filterDate(start_date, end_date) \
        .select(["sur_refl_b6", "sur_refl_b2"]) \
        .mean() \
        .clip(region)

    ndbi = modis_bands.normalizedDifference(["sur_refl_b6", "sur_refl_b2"]).rename("NDBI")

    # -----------------------------------------------------------------
    # 4c. OZONE (Sentinel-5P, S5P O3 column, ~7–28 km resolution)
    # -----------------------------------------------------------------
    ozone = ee.ImageCollection("COPERNICUS/S5P/OFFL/L3_O3") \
        .filterDate(start_date, end_date) \
        .select("O3_column_number_density") \
        .mean() \
        .clip(region) \
        .rename("OZONE")

    # -----------------------------------------------------------------
    # 4d. AOD (MODIS, Optical Depth 047, ~1 km resolution)
    # -----------------------------------------------------------------
    aod = ee.ImageCollection("MODIS/006/MCD19A2_GRANULES") \
        .filterDate(start_date, end_date) \
        .select("Optical_Depth_047") \
        .mean() \
        .clip(region) \
        .rename("AOD")

    # -----------------------------------------------------------------
    # 5. Export Function
    # -----------------------------------------------------------------
    def export_to_drive(image, name, scale):
        task = ee.batch.Export.image.toDrive(
            image=image,
            description=f"{name}_{output_prefix}",
            folder="earthengine_exports",
            fileNamePrefix=f"{name.lower()}_{output_prefix}",
            region=region,
            scale=scale,
            crs="EPSG:4326",
            maxPixels=1e13
        )
        task.start()
        return task

    # -----------------------------------------------------------------
    # 6. Launch Exports
    # -----------------------------------------------------------------
    tasks = {
        "NDVI": export_to_drive(ndvi, "NDVI", 250),
        "NDBI": export_to_drive(ndbi, "NDBI", 500),
        "OZONE": export_to_drive(ozone, "OZONE", 1000),  # 1km is reasonable for coarse resolution
        "AOD": export_to_drive(aod, "AOD", 1000)
    }

    print(f"\n🛰️ Export started for {start_date} to {end_date}...")
    while any(task.active() for task in tasks.values()):
        for name, task in tasks.items():
            print(f"⏳ {name} status: {task.status()['state']}")
        time.sleep(10)

    # -----------------------------------------------------------------
    # 7. Print Final Task Status
    # -----------------------------------------------------------------
    for name, task in tasks.items():
        status = task.status()
        print(f"✅ {name} final status: {status['state']}")
        if 'error_message' in status:
            print(f"❌ {name} failed with error: {status['error_message']}")

    # -----------------------------------------------------------------
    # 8. Download from Google Drive
    # -----------------------------------------------------------------
    file_list = drive.ListFile({'q': f"'{export_folder_id}' in parents and trashed=false"}).GetList()
    print(f"📁 Downloading files to {download_folder}...")
    for file in file_list:
        if file['title'].lower().startswith(("ndvi", "ndbi", "ozone", "aod")) and output_prefix in file['title']:
            print(f"⬇️ Downloading {file['title']}...")
            file.GetContentFile(os.path.join(download_folder, file['title']))
            print(f"🗑️ Deleting {file['title']} from Drive...")
            drive.auth.service.files().delete(fileId=file['id']).execute()

    print(f"✅ Completed: {start_date} to {end_date}\n")
