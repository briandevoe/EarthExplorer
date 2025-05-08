# -----------------------------------------------------------------------------
# Script: download_SR.py
# Purpose: Download NDVI, NDBI, LST (or other surface reflectance indicators)
# using dynamic satellite + band info from satellite_config.xlsx
# -----------------------------------------------------------------------------

import ee
import os
import time
import calendar
import pandas as pd
from datetime import datetime
from pydrive2.auth import GoogleAuth
from pydrive2.drive import GoogleDrive

# -----------------------------------------------------------------------------
# 1. USER CONFIGURATION SECTION (EDIT ONLY THIS SECTION)
#
# Define your region and what indicators to download. The date ranges
# are generated using `get_months()` for specific years.
# -----------------------------------------------------------------------------
region_name = "California"
measurement_list = ["NDVI", "NDBI"]
def get_months(year):
    return [(f"{year}-{m:02d}-01", f"{year}-{m:02d}-{calendar.monthrange(year, m)[1]}") for m in range(1, 8)]
months = get_months(2008) + get_months(2023)


# -----------------------------------------------------------------------------
# 2. Initialization & Load Config
#
# Initialize Earth Engine, load state geometry, and read config Excel
# containing satellite metadata, indicator formulas, and band mappings.
# -----------------------------------------------------------------------------
ee.Initialize(project="ee-testing-458522")
region = ee.FeatureCollection("TIGER/2018/States").filter(ee.Filter.eq('NAME', region_name)).geometry()
region_clean = region_name.lower().replace(" ", "_")

config_path = "satellite_config_modis_lst.xlsx"
satellites = pd.read_excel(config_path, sheet_name="satellites")
indicators = pd.read_excel(config_path, sheet_name="indicators")
bands = pd.read_excel(config_path, sheet_name="bands")

# Drive auth
# Authorize and connect to Google Drive to download exported images.
creds_path = "credentials.json"
gauth = GoogleAuth()
if os.path.exists(creds_path):
    gauth.LoadCredentialsFile(creds_path)
    if gauth.access_token_expired: gauth.Refresh()
    else: gauth.Authorize()
else:
    gauth.LoadClientConfigFile("client_secrets.json")
    gauth.GetFlow(); gauth.flow.params.update({'access_type': 'offline', 'approval_prompt': 'force'})
    gauth.LocalWebserverAuth(); gauth.SaveCredentialsFile(creds_path)
drive = GoogleDrive(gauth)
export_folder_id = "189FkFs8JpDqyLdkH97ACoHojQgHiE6vp"


# -----------------------------------------------------------------------------
# 3. Get satellite + bands info for indicator
#
# This function matches the given indicator and year to a satellite,
# retrieves its dataset, scale, formula, and required bands.
# -----------------------------------------------------------------------------
def get_satellite_config(year, indicator):
    for _, row in indicators[indicators.indicator == indicator].iterrows():
        sid = row['satellite_id']
        meta = satellites[satellites.satellite_id == sid]
        if not meta.empty and meta.iloc[0].start_year <= year <= meta.iloc[0].end_year:
            def get_band(bn):
                if pd.isna(bn): return None
                match = bands.query("satellite_id == @sid and band_name == @bn", local_dict={'sid': sid, 'bn': bn})
                return match['band_code'].values[0] if not match.empty else bn
            return {
                'satellite_id': sid,
                'dataset': meta.iloc[0].dataset,
                'scale': int(meta.iloc[0].resolution_m),
                'formula': row['formula_type'],
                'bands': [get_band(row.get(f'band_{i}')) for i in range(1, 5) if f'band_{i}' in row and pd.notna(row[f'band_{i}'])]
            }
    return None


# -----------------------------------------------------------------------------
# 4. Main Loop
#
# Pseudocode Overview:
# For each date range:
#   - Get year and generate output folder
#   - For each indicator (NDVI, NDBI, LST, etc.):
#       - Lookup appropriate satellite and bands
#       - Fetch ImageCollection, apply filters and algebra
#       - Export image to Google Drive and monitor task
#   - After all tasks complete, download files locally

# -----------------------------------------------------------------------------
# Loop through each month range
default_export_region = region
for start_date, end_date in months:
    year = int(start_date[:4])
    prefix = f"{region_clean}_{start_date}_to_{end_date}"
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    out_dir = os.path.join("C:/Users/bdevoe/Desktop/git/EarthExplorer/data/raw", f"{prefix}_{timestamp}")
    os.makedirs(out_dir, exist_ok=True)
    tasks = {}

    # Loop through each selected measurement type (NDVI, NDBI, etc.)
    for ind in measurement_list:
        cfg = get_satellite_config(year, ind)
        if not cfg:
            print(f"⚠️ Skipping {ind}: no config for {year}"); continue

        ic = ee.ImageCollection(cfg['dataset']).filterDate(start_date, end_date).filterBounds(region)
        if 'LANDSAT' in cfg['dataset']: ic = ic.filter(ee.Filter.lt("CLOUD_COVER", 20)).map(lambda img: img.multiply(0.0000275).add(-0.2))
        if ic.size().getInfo() == 0:
            print(f"⚠️ No images for {ind} in {start_date}"); continue

        # Try to compute image with correct formula
        try:
            if cfg['formula'] == 'normalized_diff':
                image = ic.median().normalizedDifference(cfg['bands'][:2])
            elif cfg['formula'] == 'mean':
                image = ic.select(cfg['bands'][0]).reduce(ee.Reducer.mean())
            elif cfg['formula'] == 'evi':
                image = ic.median()
                nir, red, blue = cfg['bands'][:3]
                image = image.expression(
                    '2.5 * ((NIR - RED) / (NIR + 6 * RED - 7.5 * BLUE + 1))',
                    {'NIR': image.select(nir), 'RED': image.select(red), 'BLUE': image.select(blue)}
                )
            else:
                print(f"⚠️ Unsupported formula {cfg['formula']} for {ind}"); continue
            image = image.toFloat().rename(ind).clip(region)
        except Exception as e:
            print(f"❌ Failed {ind} on {start_date}: {e}"); continue

        task = ee.batch.Export.image.toDrive(
            image=image,
            description=f"{ind}_{prefix}",
            folder="earthengine_exports",
            fileNamePrefix=f"{ind.lower()}_{prefix}",
            region=region,
            scale=cfg['scale'],
            crs="EPSG:4326",
            maxPixels=1e13
        )
        task.start(); tasks[ind] = task

    print(f"\n🛰️ Export started for {region_name} {start_date} to {end_date}...")
    # Wait for all tasks to complete before proceeding to download
    while any(task.active() for task in tasks.values()):
        # Print final status for each export task
        for name, task in tasks.items():
            print(f"⏳ {name} status: {task.status()['state']}")
        time.sleep(10)

    for name, task in tasks.items():
        status = task.status()
        print(f"✅ {name} final status: {status['state']}")
        if 'error_message' in status:
            print(f"❌ {name} failed with error: {status['error_message']}")

    # Download finished files from Google Drive and clean up
    for f in drive.ListFile({'q': f"'{export_folder_id}' in parents and trashed=false"}).GetList():
        if f['title'].lower().startswith(tuple(ind.lower() for ind in tasks)) and prefix in f['title']:
            f.GetContentFile(os.path.join(out_dir, f['title']))
            drive.auth.service.files().delete(fileId=f['id']).execute()

    print(f"✅ Completed: {region_name} {start_date} to {end_date}\n")

