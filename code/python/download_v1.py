# Nationwide GEE Export and Download Script

import ee
import time
import os
from datetime import datetime
from pydrive2.auth import GoogleAuth
from pydrive2.drive import GoogleDrive

# ---------------------------------------------------------------------
# 0. Initialize Earth Engine
# ---------------------------------------------------------------------
ee.Initialize(project="ee-testing-458522")  # replace with your GCP project ID

# ---------------------------------------------------------------------
# 1. Settings: States and Monthly Ranges
# ---------------------------------------------------------------------
states = [
    "Ohio"
]  # New England states

# Generate all months in 2024
months = [(f"2024-{str(m).zfill(2)}-01", f"2024-{str(m).zfill(2)}-{str((datetime(2024, m % 12 + 1, 1) - datetime(2024, m, 1)).days)}") for m in range(1, 13)]

satellite = 'LANDSAT/LC09/C02/T1_L2'
export_folder_id = "189FkFs8JpDqyLdkH97ACoHojQgHiE6vp"

# ---------------------------------------------------------------------
# 2. Earth Engine Index Calculator
# ---------------------------------------------------------------------
def add_indices(image):
    ndvi = image.normalizedDifference(['SR_B5', 'SR_B4']).rename('NDVI')
    ndwi = image.normalizedDifference(['SR_B3', 'SR_B5']).rename('NDWI')
    ndbi = image.normalizedDifference(['SR_B6', 'SR_B5']).rename('NDBI')
    lst = image.select('ST_B10').multiply(0.00341802).add(149.0).rename('LST')
    turbidity = image.select('SR_B3').rename('TurbidityIndex')  # Green band as a proxy
    return image.addBands([ndvi, ndwi, ndbi, lst, turbidity])

# ---------------------------------------------------------------------
# 3. Google Drive Auth with Credential Persistence
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
    gauth.GetFlow()  # set up the OAuth2 flow
    gauth.flow.params.update({'access_type': 'offline', 'approval_prompt': 'force'})
    gauth.LocalWebserverAuth()
    gauth.SaveCredentialsFile("credentials.json")
    gauth.SaveCredentialsFile("credentials.json")
drive = GoogleDrive(gauth)

# ---------------------------------------------------------------------
# 4. Main Loop Over States and Months
# ---------------------------------------------------------------------
for state in states:
    for start_date, end_date in months:

        region = ee.FeatureCollection("TIGER/2018/States").filter(ee.Filter.eq('NAME', state)).geometry()
        output_prefix = f"{state.lower().replace(' ', '_')}_{start_date}_to_{end_date}"

        # Folder for local download
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        download_folder = os.path.join("C:/Users/bdevoe/Desktop/git/EarthExplorer/data/raw/", f"{output_prefix}_{timestamp}")
        os.makedirs(download_folder, exist_ok=True)

        # Get Image
        def get_landsat_snapshot(start, end):
            return (ee.ImageCollection(satellite)
                    .filterBounds(region)
                    .filterDate(start, end)
                    .filter(ee.Filter.lt('CLOUD_COVER', 20))
                    .map(lambda img: img.multiply(0.0000275).add(-0.2).copyProperties(img, ["system:time_start"]))
                    .map(add_indices)
                    .median()
                    .clip(region))

        image = get_landsat_snapshot(start_date, end_date)

        # Select bands
        ndvi = image.select('NDVI')
        ndwi = image.select('NDWI')
        ndbi = image.select('NDBI')
        lst  = image.select('LST')
        true_color = image.select(['SR_B4', 'SR_B3', 'SR_B2']).rename(['Red', 'Green', 'Blue'])
        turbidity = image.select('TurbidityIndex')

        # Additional environmental indicators
        co = ee.ImageCollection("COPERNICUS/S5P/OFFL/L3_CO").filterDate(start_date, end_date).select("CO_column_number_density").mean().clip(region).rename("CO")
        no2 = ee.ImageCollection("COPERNICUS/S5P/OFFL/L3_NO2").filterDate(start_date, end_date).select("NO2_column_number_density").mean().clip(region).rename("NO2")
        ozone = ee.ImageCollection("COPERNICUS/S5P/OFFL/L3_O3").filterDate(start_date, end_date).select("O3_column_number_density").mean().clip(region).rename("OZONE")
        aod = ee.ImageCollection("MODIS/006/MCD19A2_GRANULES").filterDate(start_date, end_date).select("Optical_Depth_047").mean().clip(region).rename("AOD")
        lights = ee.ImageCollection("NOAA/VIIRS/DNB/MONTHLY_V1/VCMSLCFG").filterDate(start_date, end_date).select("avg_rad").mean().clip(region).rename("NightLights")

        # Export Function
        def export_to_drive(image, name):
            task = ee.batch.Export.image.toDrive(
                image=image,
                description=f"{name}_{output_prefix}",
                folder="earthengine_exports",
                fileNamePrefix=f"{name.lower()}_{output_prefix}",
                region=region,
                scale=30,
                crs="EPSG:4326",
                maxPixels=1e13
            )
            task.start()
            return task

        # Launch exports
        tasks = {
            "NDVI": export_to_drive(ndvi, "NDVI"),
            #"NDWI": export_to_drive(ndwi, "NDWI"),
            "NDBI": export_to_drive(ndbi, "NDBI"),
            #"LST": export_to_drive(lst, "LST"),
            #"TrueColor": export_to_drive(true_color, "TrueColor_RGB"),
            #"Turbidity": export_to_drive(turbidity, "Turbidity"),
            "CO": export_to_drive(co, "CO"),
            "NO2": export_to_drive(no2, "NO2"),
            "OZONE": export_to_drive(ozone, "OZONE"),
            #"AOD": export_to_drive(aod, "AOD"),
            "NightLights": export_to_drive(lights, "NightLights")
        }

        # Monitor tasks
        print(f"\n🛰️ Export started for {state} {start_date} to {end_date}...")
        while any(task.active() for task in tasks.values()):
            for name, task in tasks.items():
                print(f"⏳ {state} {start_date} {name} status: {task.status()['state']}")
            time.sleep(10)

        for name, task in tasks.items():
            status = task.status()
            print(f"✅ {state} {start_date} {name} final status: {status['state']}")
            if 'error_message' in status:
                print(f"❌ {name} failed with error: {status['error_message']}")

        # Download from Google Drive
        file_list = drive.ListFile({'q': f"'{export_folder_id}' in parents and trashed=false"}).GetList()
        print(f"📁 Downloading files to {download_folder}...")
        for file in file_list:
            if file['title'].lower().startswith(("ndvi", "ndwi", "ndbi", "lst", "truecolor", "turbidity", "co", "no2", "ozone", "aod", "nightlights")) and output_prefix in file['title']:
                print(f"⬇️ Downloading {file['title']}...")
                file.GetContentFile(os.path.join(download_folder, file['title']))
                print(f"🗑️ Deleting {file['title']} from Drive...")
                drive.auth.service.files().delete(fileId=file['id']).execute()
                #file.Delete()

        print(f"✅ Completed: {state}, {start_date} to {end_date}\n")
