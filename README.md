
---

## 🌎 Variables and Descriptions

### Vegetation and Land Use Indices

**1. NDVI (Normalized Difference Vegetation Index)**
**Source:** Landsat 9 (Bands 5 and 4)
**Formula:** `(NIR - Red) / (NIR + NIR)`
**Description:** Measures vegetation health and greenness. Values near +1 indicate healthy vegetation; values near 0 or negative indicate urban/barren areas.

**2. NDWI (Normalized Difference Water Index)**
**Source:** Landsat 9 (Bands 3 and 5)
**Formula:** `(Green - NIR) / (Green + NIR)`
**Description:** Highlights surface water features and moisture presence.

**3. NDBI (Normalized Difference Built-up Index)**
**Source:** Landsat 9 (Bands 6 and 5)
**Formula:** `(SWIR - NIR) / (SWIR + NIR)`
**Description:** Identifies urban and built-up areas.

**4. LST (Land Surface Temperature)**
**Source:** Landsat 9 Thermal Band 10
**Formula:** `ST_B10 * 0.00341802 + 149.0`
**Description:** Estimates surface temperature in Kelvin.

**5. Turbidity Index**
**Source:** Landsat 9 Green Band (SR\_B3)
**Description:** Proxy for water turbidity based on reflectance; not a direct pollution measure.

---

### Air Quality and Atmospheric Variables

**6. CO (Carbon Monoxide)**
**Source:** Sentinel-5P (`COPERNICUS/S5P/OFFL/L3_CO`)
**Description:** Indicates air pollution from fires, cars, industry.

**7. NO₂ (Nitrogen Dioxide)**
**Source:** Sentinel-5P (`COPERNICUS/S5P/OFFL/L3_NO2`)
**Description:** A major urban pollutant linked to traffic and respiratory health impacts.

**8. OZONE (O₃ Column)**
**Source:** Sentinel-5P (`COPERNICUS/S5P/OFFL/L3_O3`)
**Description:** Measures ozone concentration; ground-level ozone is a health hazard.

**9. AOD (Aerosol Optical Depth)**
**Source:** MODIS (`MODIS/006/MCD19A2_Optical_Depth_Land`)
**Description:** Indicates the level of aerosols (airborne particles) in the atmosphere. **Acts as a proxy for PM2.5**, although it is not a direct measurement. Often used in modeling fine particulate pollution.

---

### Infrastructure and Activity

**10. Nighttime Lights (Radiance)**
**Source:** VIIRS-DNB (`NOAA/VIIRS/DNB/MONTHLY_V1/VCMSLCFG`)
**Variable:** `avg_rad`
**Description:** Reflects human infrastructure, activity, and electrification.

---

### Notes on Data

* **Temporal Scope:** All data are monthly means/medians.
* **Spatial Scope:** 30m (Landsat); 1km+ (MODIS, Sentinel-5P).
* **Caveats:** Cloud cover, data quality, and atmospheric conditions may introduce gaps or biases. QA masks are recommended during analysis.



## 🌱 Potential Indicators for Expansion

These are additional spatial indicators under consideration to enhance linkage with the Child Opportunity Index (COI). Most are available from public satellite data via Google Earth Engine and can be computed monthly and at high resolution.

### 🌊 Hydrologic & Environmental Hazards

| Indicator         | Description                                              | GEE Source(s)                                   |
|------------------|----------------------------------------------------------|-------------------------------------------------|
| **Flood Risk**    | Persistent surface water changes or flood-prone zones    | `JRC/GSW1_3/MonthlyHistory`, Sentinel-1 SAR     |
| **Fire Risk**     | Burned areas and active fire events                      | `MODIS/MCD64A1`, `FIRMS`, `VIIRS`               |
| **Drought Index** | Evapotranspiration or soil moisture anomalies            | `MOD16A2`, `NASA/SMAP/SPL3SMP`                  |

---

### 🌡️ Climate Stressors

| Indicator              | Description                                                  | Method / Source                            |
|------------------------|--------------------------------------------------------------|--------------------------------------------|
| **Temperature Anomaly**| Monthly LST deviation from 10-year climatology               | MODIS LST (`MOD11A2`) or Landsat LST       |
| **Urban Heat Index**   | Combine high LST + low albedo to flag heat vulnerability     | `MODIS/MCD43A3` + LST                      |

---

### 🌫️ Atmospheric Pollution & Exposure

| Indicator   | Description                                   | GEE Source                                |
|-------------|-----------------------------------------------|-------------------------------------------|
| **UV Index**| Potential UV exposure at surface              | `COPERNICUS/S5P/OFFL/L3_UVAI`             |
| **SO₂**     | Sulfur dioxide, linked to industrial activity | `COPERNICUS/S5P/OFFL/L3_SO2`              |
| **CH₄**     | Methane, from landfills, agriculture, etc.    | `COPERNICUS/S5P/OFFL/L3_CH4`              |

---

### 🏔️ Terrain & Elevation

| Indicator     | Description                                    | GEE Source / Method               |
|---------------|------------------------------------------------|-----------------------------------|
| **Elevation** | Absolute elevation in meters above sea level   | `USGS/SRTMGL1_003`, `MERIT DEM`   |
| **Slope**     | Degree of terrain steepness                    | Derived from DEM with `terrain()` |
| **Sea Level Risk** | Tracts below flood-prone elevation threshold | Elevation mask + flood layers     |

---

> These metrics support analyses of environmental injustice, child health disparities, urban heat vulnerability, and disaster resilience across U.S. census tracts. Future development phases will test and integrate select indicators into the broader COI framework.

