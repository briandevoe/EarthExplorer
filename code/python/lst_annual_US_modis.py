import ee, time
ee.Initialize(project="ee-testing-458522")

# Define CONUS geometry
states = ee.FeatureCollection("TIGER/2018/States")
conus = states.filter(ee.Filter.notEquals("NAME", "Alaska")) \
              .filter(ee.Filter.notEquals("NAME", "Hawaii")) \
              .geometry()

# MODIS LST (Terra, daily)
lst = ee.ImageCollection("MODIS/061/MOD11A1") \
    .filterDate("2021-01-01", "2021-12-31") \
    .select("LST_Day_1km") \
    .filterBounds(conus)

# Scale by factor 0.02 and convert to Celsius
def scale_lst(img):
    return img.multiply(0.02).subtract(273.15).rename("LST_C")

lst_celsius = lst.map(scale_lst)
lst_mean = lst_celsius.mean().clip(conus)

# Export to Drive
task = ee.batch.Export.image.toDrive(
    image=lst_mean,
    description="MODIS_LST_CONUS_2021",
    folder="LST_MODIS_CONUS_20250609_1830",
    fileNamePrefix="modis_lst_conus_2021",
    region=conus.bounds().getInfo()["coordinates"],
    scale=1000,  # 1 km resolution
    maxPixels=1e13
)

task.start()
print("🌡️ Exporting MODIS LST (2021)...")
while task.active():
    print("⏳ Waiting...")
    time.sleep(30)
print("✅ Done:", task.status()['state'])
