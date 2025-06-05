import ee
import time

# ---------------------------------------------------------------------
# Initialize Earth Engine
# ---------------------------------------------------------------------
ee.Initialize(project="ee-testing-458522")

# ---------------------------------------------------------------------
# Settings
# ---------------------------------------------------------------------
years = list(range(2008, 2024))
states = ["California", "Texas", "New York", "Florida", "Illinois"]
output_folder = "earthengine_exports"

# ---------------------------------------------------------------------
# Loop over states and years
# ---------------------------------------------------------------------
for state_name in states:
    for year in years:
        filename = f"aod_raster_{state_name.lower().replace(' ', '_')}_{year}"

        # Load state geometry
        state_geom = ee.FeatureCollection("TIGER/2018/States") \
            .filter(ee.Filter.eq("NAME", state_name)) \
            .geometry()

        # Load and average MODIS AOD monthly data for the year
        aod_annual = ee.ImageCollection("MODIS/061/MOD08_M3") \
            .filterDate(f"{year}-01-01", f"{year}-12-31") \
            .select("Aerosol_Optical_Depth_Land_Ocean_Mean_Mean") \
            .mean() \
            .clip(state_geom) \
            .rename("AOD")

        # Export AOD image to Google Drive as GeoTIFF
        task = ee.batch.Export.image.toDrive(
            image=aod_annual,
            description=filename,
            folder=output_folder,
            fileNamePrefix=filename,
            scale=1000,
            region=state_geom,
            crs="EPSG:4326",
            maxPixels=1e13
        )

        task.start()
        print(f"\U0001F30E Export started: {filename}.tif → Google Drive → '{output_folder}/'")

        # Optional: Wait for export to initialize before launching next
        time.sleep(10)

print("✅ All export tasks started. Check your Google Drive for results.")
