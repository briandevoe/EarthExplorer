import ee
import time
#import os

# ---------------------------------------------------------------------
# 0. Initialize Earth Engine
# ---------------------------------------------------------------------
ee.Initialize(project="ee-testing-458522")  

# ---------------------------------------------------------------------
# 1. Define New Orleans AOI
# ---------------------------------------------------------------------
nola = ee.Geometry.Rectangle([-90.14, 29.87, -89.62, 30.13])

# ---------------------------------------------------------------------
# 2. Index calculator for Landsat 5
# ---------------------------------------------------------------------
def add_indices(image):
    ndvi = image.normalizedDifference(['SR_B4', 'SR_B3']).rename('NDVI')   # NIR, Red
    ndwi = image.normalizedDifference(['SR_B2', 'SR_B4']).rename('NDWI')   # Green, NIR
    ndbi = image.normalizedDifference(['SR_B5', 'SR_B4']).rename('NDBI')   # SWIR1, NIR
    return image.addBands([ndvi, ndwi, ndbi])

# ---------------------------------------------------------------------
# 3. Load & preprocess Landsat 5 image
# ---------------------------------------------------------------------
def get_landsat5_image(start, end):
    return (ee.ImageCollection('LANDSAT/LT05/C02/T1_L2')
            .filterBounds(nola)
            .filterDate(start, end)
            .filter(ee.Filter.lt('CLOUD_COVER', 20))
            .map(lambda img: img.multiply(0.0000275).add(-0.2).copyProperties(img, ["system:time_start"]))
            .map(add_indices)
            .median()
            .clip(nola))

# ---------------------------------------------------------------------
# 4. Before and After Katrina (August–September 2005)
# ---------------------------------------------------------------------
before = get_landsat5_image('2005-08-01', '2005-08-28')   # Katrina landfall: Aug 29
after  = get_landsat5_image('2005-09-01', '2005-09-30')

# ---------------------------------------------------------------------
# 5. Compute Change Layers
# ---------------------------------------------------------------------
ndvi_diff = after.select('NDVI').subtract(before.select('NDVI')).rename('NDVI_Change')
ndwi_diff = after.select('NDWI').subtract(before.select('NDWI')).rename('NDWI_Change')
ndbi_diff = after.select('NDBI').subtract(before.select('NDBI')).rename('NDBI_Change')

# ---------------------------------------------------------------------
# 6. True Color RGB from 'after' image
# ---------------------------------------------------------------------
true_color = after.select(['SR_B3', 'SR_B2', 'SR_B1']).rename(['Red', 'Green', 'Blue'])

# ---------------------------------------------------------------------
# 7. Export function
# ---------------------------------------------------------------------
def export_to_drive(image, name):
    task = ee.batch.Export.image.toDrive(
        image=image,
        description=f"{name}_NOLA_2005",
        folder="earthengine_exports",
        fileNamePrefix=f"{name.lower()}_nola_2005",
        region=nola,
        scale=30,
        crs="EPSG:4326",
        maxPixels=1e13
    )
    task.start()
    return task

# ---------------------------------------------------------------------
# 8. Start Export Tasks
# ---------------------------------------------------------------------
tasks = {
    "NDVI": export_to_drive(ndvi_diff, "NDVI_Change"),
    "NDWI": export_to_drive(ndwi_diff, "NDWI_Change"),
    "NDBI": export_to_drive(ndbi_diff, "NDBI_Change"),
    "TrueColor": export_to_drive(true_color, "TrueColor_RGB")
}

# ---------------------------------------------------------------------
# 9. Monitor Progress
# ---------------------------------------------------------------------
print("🛰️ Katrina 2005 exports started...")
while any(task.active() for task in tasks.values()):
    for name, task in tasks.items():
        print(f"⏳ {name} status: {task.status()['state']}")
    time.sleep(10)

# Final status
for name, task in tasks.items():
    status = task.status()
    print(f"✅ {name} final status: {status['state']}")
    if 'error_message' in status:
        print(f"❌ {name} failed with error: {status['error_message']}")
