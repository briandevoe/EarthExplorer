import ee
import time

# ---------------------------------------------------------------------
# Initialize Earth Engine
# ---------------------------------------------------------------------
ee.Initialize(project="ee-testing-458522")

# ---------------------------------------------------------------------
# Settings
# ---------------------------------------------------------------------
years = list(range(2015, 2024))  # Extended to more years
output_folder = "earthengine_exports"

# ---------------------------------------------------------------------
# Load all U.S. state names (excluding nulls)
# ---------------------------------------------------------------------
all_states_fc = ee.FeatureCollection("TIGER/2018/States")
valid_states_fc = all_states_fc.filter(ee.Filter.notNull(["NAME"]))
state_names = valid_states_fc.aggregate_array("NAME").getInfo()

# ---------------------------------------------------------------------
# Loop through states and years to export AI composites
# ---------------------------------------------------------------------
for state_name in state_names:
    state_geom = ee.FeatureCollection("TIGER/2018/States") \
        .filter(ee.Filter.eq("NAME", state_name)) \
        .geometry()

    for year in years:
        safe_name = state_name.lower().replace(' ', '_').replace('.', '').replace(',', '')
        filename = f"aerosol_index_{safe_name}_{year}_sentinel5p"

        # Load and process Sentinel-5P AI data
        ai_ic = ee.ImageCollection("COPERNICUS/S5P/NRTI/L3_AER_AI") \
            .filterDate(f"{year}-01-01", f"{year}-12-31") \
            .filterBounds(state_geom) \
            .select("absorbing_aerosol_index")

        mean_ai = ai_ic.mean().clip(state_geom).rename("Aerosol_Index")

        # Export as GeoTIFF
        task = ee.batch.Export.image.toDrive(
            image=mean_ai,
            description=filename,
            folder=output_folder,
            fileNamePrefix=filename,
            scale=7000,
            region=state_geom,
            crs="EPSG:4326",
            maxPixels=1e13
        )

        task.start()
        print(f"🛰️ Export started: {filename}.tif → Google Drive → '{output_folder}/'")

        # Optional: Delay to avoid GEE throttling
        time.sleep(10)

print("✅ All export tasks started. Check your Google Drive.")




