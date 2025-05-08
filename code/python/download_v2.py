# -----------------------------------------------------------------------------
# Script: download_ma_satellite.py
# Purpose: Dynamically download NDVI, NDBI, OZONE data using correct satellite
# and bands per year/month defined in `satellite_config.xlsx`
# -----------------------------------------------------------------------------

import ee
import os
import time
import calendar
import pandas as pd
from datetime import datetime
from pydrive2.auth import GoogleAuth
from pydrive2.drive import GoogleDrive

# ---------------------------------------------------------------------
# 1. Initialization and Configuration
# ---------------------------------------------------------------------
ee.Initialize(project="ee-testing-458522")

state_name = "Massachusetts"
region = ee.FeatureCollection("TIGER/2018/States") \
    .filter(ee.Filter.eq('NAME', state_name)) \
    .geometry()
state_clean = state_name.lower().replace(" ", "_")

# Load Excel configuration
config_path = "satellite_config.xlsx"
satellites = pd.read_excel(config_path, sheet_name="satellites")
indicators = pd.read_excel(config_path, sheet_name="indicators")
bands = pd.read_excel(config_path, sheet_name="bands")

# Time periods: Jan-Jul for both 2008 and 2023
def get_months(year):
    return [(f"{year}-{m:02d}-01", f"{year}-{m:02d}-{calendar.monthrange(year, m)[1]}") for m in range(1, 8)]

months = get_months(2008) + get_months(2023)

# Google Drive Auth
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
export_folder_id = "189FkFs8JpDqyLdkH97ACoHojQgHiE6vp"

# ---------------------------------------------------------------------
# 2. Utility to get satellite config and band codes
# ---------------------------------------------------------------------
def get_satellite_and_bands(year, indicator):
    for _, row in indicators[indicators.indicator == indicator].iterrows():
        sat_id = row['satellite_id']
        sat_row = satellites[satellites.satellite_id == sat_id]
        if not sat_row.empty:
            if sat_row.iloc[0]['start_year'] <= year <= sat_row.iloc[0]['end_year']:
                band1 = bands.query("satellite_id == @sat_id and band_name == @row['band_1']")
                band2 = bands.query("satellite_id == @sat_id and band_name == @row['band_2']") if pd.notna(row['band_2']) else None
                return {
                    'dataset': sat_row.iloc[0]['dataset'],
                    'scale': sat_row.iloc[0]['resolution_m'],
                    'formula': row['formula_type'],
                    'band_1': band1['band_code'].values[0] if not band1.empty else row['band_1'],
                    'band_2': band2['band_code'].values[0] if band2 is not None and not band2.empty else row['band_2'],
                    'satellite_id': sat_id
                }
    return None

# ---------------------------------------------------------------------
# 3. Main Loop
# ---------------------------------------------------------------------
for start_date, end_date in months:
    year = int(start_date[:4])
    output_prefix = f"{state_clean}_{start_date}_to_{end_date}"
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    download_folder = os.path.join("C:/Users/bdevoe/Desktop/git/EarthExplorer/data/raw", f"{output_prefix}_{timestamp}")
    os.makedirs(download_folder, exist_ok=True)
    tasks = {}

    for indicator in ["NDVI", "NDBI", "OZONE"]:
        config = get_satellite_and_bands(year, indicator)
        if not config:
            print(f"⚠️ No config for {indicator} in {year}")
            continue

        ic = ee.ImageCollection(config['dataset']) \
            .filterDate(start_date, end_date) \
            .filterBounds(region)

        if 'LANDSAT' in config['dataset']:
            ic = ic.filter(ee.Filter.lt("CLOUD_COVER", 20))
            ic = ic.map(lambda img: img.multiply(0.0000275).add(-0.2))

        if ic.size().getInfo() == 0:
            print(f"⚠️ No images for {indicator} in {start_date}")
            continue

        if config['formula'] == 'normalized_diff':
            image = ic.median().normalizedDifference([config['band_1'], config['band_2']])
        elif config['formula'] == 'mean':
            image = ic.select(config['band_1']).reduce(ee.Reducer.mean())
        else:
            continue

        image = image.toFloat().rename(indicator).clip(region)

        task = ee.batch.Export.image.toDrive(
            image=image,
            description=f"{indicator}_{output_prefix}",
            folder="earthengine_exports",
            fileNamePrefix=f"{indicator.lower()}_{output_prefix}",
            region=region,
            scale=config['scale'],
            crs="EPSG:4326",
            maxPixels=1e13
        )
        task.start()
        tasks[indicator] = task

    print(f"\n🛰️ Export started for {state_name} {start_date} to {end_date}...")
    while any(task.active() for task in tasks.values()):
        for name, task in tasks.items():
            print(f"⏳ {name} status: {task.status()['state']}")
        time.sleep(10)

    for name, task in tasks.items():
        status = task.status()
        print(f"✅ {name} final status: {status['state']}")
        if 'error_message' in status:
            print(f"❌ {name} failed with error: {status['error_message']}")

    # Download results
    file_list = drive.ListFile({'q': f"'{export_folder_id}' in parents and trashed=false"}).GetList()
    for file in file_list:
        if file['title'].lower().startswith(tuple(ind.lower() for ind in tasks)) and output_prefix in file['title']:
            file.GetContentFile(os.path.join(download_folder, file['title']))
            drive.auth.service.files().delete(fileId=file['id']).execute()

    print(f"✅ Completed: {state_name} {start_date} to {end_date}\n")
