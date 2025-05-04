EarthExplorer is a research tool for extracting and analyzing satellite-derived environmental indicators using Google Earth Engine and Python. This project generates monthly, high-resolution geospatial datasets across the U.S. — including NDVI, surface temperature, air pollution, flood risk, and more — and links them to census tracts for integration with social indices like the Child Opportunity Index (COI), Social Vulnerability Index (SVI), and Opportunity Atlas (OA). The goal is to support environmental justice, public health research, and data-driven policymaking by bridging remote sensing and social science.

---

## 🚀 Getting Started

### Prerequisites

To run this project locally, you need:

* Python 3.10 or higher
* A Google Cloud project with Earth Engine and Drive APIs enabled
* `client_secrets.json` from your Google Cloud OAuth credentials
* The following Python packages:

  ```bash
  pip install earthengine-api pydrive2 rasterio numpy
  ```

### Setup Instructions

1. Clone this repository:

   ```bash
   git clone https://github.com/your-username/EarthExplorer.git
   cd EarthExplorer
   ```
2. Place your `client_secrets.json` file in the root folder.
3. Run the main script to authenticate and begin downloading:

   ```bash
   python 1_download.py
   ```
4. Downloaded `.tif` files will be saved in the `data/` folder (ignored by Git).


## 🤝 How to Contribute

Contributions are welcome! If you'd like to improve the codebase or expand the analysis:

1. Fork the repository
2. Create a new branch:

   ```bash
   git checkout -b feature/your-feature-name
   ```
3. Commit your changes:

   ```bash
   git commit -m "Add your message here"
   ```
4. Push to the branch:

   ```bash
   git push origin feature/your-feature-name
   ```
5. Open a pull request describing what you changed and why

If you’re working with new environmental indicators, please update the `README.md` with the source and purpose of the metric.

---

## 🌎 Variables and Descriptions

### Vegetation and Land Use Indices

| Indicator                                         | Description                                                                                                   | Source                    |
| ------------------------------------------------- | ------------------------------------------------------------------------------------------------------------- | ------------------------- |
| **NDVI (Normalized Difference Vegetation Index)** | Measures vegetation health using `(NIR - Red) / (NIR + Red)`. Values near +1 indicate healthy vegetation.     | Landsat 9 (Bands 5 and 4) |
| **NDWI (Normalized Difference Water Index)**      | Detects surface water using `(Green - NIR) / (Green + NIR)`. Useful for wetland and water mapping.            | Landsat 9 (Bands 3 and 5) |
| **NDBI (Normalized Difference Built-up Index)**   | Identifies built-up areas using `(SWIR - NIR) / (SWIR + NIR)`. Higher values imply more urban infrastructure. | Landsat 9 (Bands 6 and 5) |
| **LST (Land Surface Temperature)**                | Estimates land temperature in Kelvin using `ST_B10 * 0.00341802 + 149.0`.                                     | Landsat 9 Thermal Band 10 |
| **Turbidity Index**                               | A proxy for water turbidity using green reflectance. Higher values may imply suspended solids or algal bloom. | Landsat 9 (Band SR\_B3)   |

---

### Air Quality and Atmospheric Variables

| Indicator                       | Description                                                               | Source                                         |
| ------------------------------- | ------------------------------------------------------------------------- | ---------------------------------------------- |
| **CO (Carbon Monoxide)**        | Indicates combustion-related pollution from vehicles, fires, or industry. | Sentinel-5P (`COPERNICUS/S5P/OFFL/L3_CO`)      |
| **NO₂ (Nitrogen Dioxide)**      | Major urban pollutant linked to traffic and respiratory health concerns.  | Sentinel-5P (`COPERNICUS/S5P/OFFL/L3_NO2`)     |
| **OZONE (O₃ Column)**           | Measures tropospheric ozone; ground-level ozone is harmful to health.     | Sentinel-5P (`COPERNICUS/S5P/OFFL/L3_O3`)      |
| **AOD (Aerosol Optical Depth)** | Indicates airborne particulate concentration; used as a proxy for PM2.5.  | MODIS (`MODIS/006/MCD19A2_Optical_Depth_Land`) |

---

### Infrastructure and Activity

| Indicator                       | Description                                                                                  | Source                                           |
| ------------------------------- | -------------------------------------------------------------------------------------------- | ------------------------------------------------ |
| **Nighttime Lights (Radiance)** | Reflects infrastructure, human presence, and economic activity using visible light at night. | VIIRS-DNB (`NOAA/VIIRS/DNB/MONTHLY_V1/VCMSLCFG`) |

---

### Notes on Data

* **Temporal Scope:** All variables are monthly means or medians.
* **Spatial Resolution:** 30m (Landsat); 1–7km (MODIS, Sentinel-5P).
* **Caveats:** Cloud cover, atmospheric conditions, and sensor differences can introduce bias. Use QA masks when possible.

## 🌱 Potential Indicators for Expansion

This section outlines additional environmental and social indicators that can be integrated into the EarthExplorer project. Many of these are available through Google Earth Engine or public datasets and align well with measures like the Child Opportunity Index (COI), Social Vulnerability Index (SVI), and Opportunity Atlas (OA).

These are additional spatial indicators under consideration to enhance linkage with the Child Opportunity Index (COI). Most are available from public satellite data via Google Earth Engine and can be computed monthly and at high resolution.

### 🌊 Hydrologic & Environmental Hazards

| Indicator         | Description                                           | GEE Source(s)                               |
| ----------------- | ----------------------------------------------------- | ------------------------------------------- |
| **Flood Risk**    | Persistent surface water changes or flood-prone zones | `JRC/GSW1_3/MonthlyHistory`, Sentinel-1 SAR |
| **Fire Risk**     | Burned areas and active fire events                   | `MODIS/MCD64A1`, `FIRMS`, `VIIRS`           |
| **Drought Index** | Evapotranspiration or soil moisture anomalies         | `MOD16A2`, `NASA/SMAP/SPL3SMP`              |

---

### 🌡️ Climate Stressors

| Indicator               | Description                                              | Method / Source                      |
| ----------------------- | -------------------------------------------------------- | ------------------------------------ |
| **Temperature Anomaly** | Monthly LST deviation from 10-year climatology           | MODIS LST (`MOD11A2`) or Landsat LST |
| **Urban Heat Index**    | Combine high LST + low albedo to flag heat vulnerability | `MODIS/MCD43A3` + LST                |

---

### 🌫️ Atmospheric Pollution & Exposure

| Indicator    | Description                                   | GEE Source                    |
| ------------ | --------------------------------------------- | ----------------------------- |
| **UV Index** | Potential UV exposure at surface              | `COPERNICUS/S5P/OFFL/L3_UVAI` |
| **SO₂**      | Sulfur dioxide, linked to industrial activity | `COPERNICUS/S5P/OFFL/L3_SO2`  |
| **CH₄**      | Methane, from landfills, agriculture, etc.    | `COPERNICUS/S5P/OFFL/L3_CH4`  |

---

### 🧭 Urban & Land Use Patterns

| Indicator                   | Description                                              | Source                                  |
| --------------------------- | -------------------------------------------------------- | --------------------------------------- |
| **Impervious Surface Area** | Maps urban sprawl and infrastructure coverage            | `USGS/NLCD`, `Global Urban Footprint`   |
| **Green Space Access**      | Analyzes distance to nearest public parks/vegetated land | Derived from NDVI or land cover rasters |
| **Zoning Classification**   | Differentiates residential, commercial, and mixed zones  | National Zoning Atlas (in progress)     |

### 🌬️ Additional Atmospheric & Air Quality Metrics

| Indicator                       | Description                                                | GEE Source / Status                       |
| ------------------------------- | ---------------------------------------------------------- | ----------------------------------------- |
| **PM10**                        | Larger particulates that impact respiratory health         | Proxy via AOD or modeled datasets         |
| **VOCs**                        | Volatile organic compounds contributing to ozone formation | Under research; limited availability      |
| **Surface-Level PM Estimation** | Blend AOD with weather reanalysis to model exposure        | Modeled from Sentinel/MODIS + meteorology |

### 📊 Social Indicators and Public Datasets

FEMA and other federal agencies publish a wide array of disaster-related datasets that are relevant to socioeconomic and environmental justice research. These datasets can be joined to census tracts or ZIP codes and used to examine disaster resilience, recovery inequality, and infrastructure disparities.

#### 🚨 FEMA and Disaster Claims Datasets

| Indicator                      | Description                                                                | Geography Level | Source                                                                                            |
| ------------------------------ | -------------------------------------------------------------------------- | --------------- | -------------------------------------------------------------- |
| **Flood Insurance Claims**     | Historical NFIP claims and payouts by ZIP or county                        | ZIP, County     | [FEMA datasets](https://www.fema.gov/about/openfema/data-sets) |
| **Disaster Declarations**      | Official FEMA disaster declarations including event type, region, and date | County          | [FEMA datasets](https://www.fema.gov/about/openfema/data-sets) |
| **Hazard Mitigation Grants**   | Grants for rebuilding and resilience efforts by project and location       | County          | [FEMA datasets](https://www.fema.gov/about/openfema/data-sets) |
| **Fire Management Assistance** | Declarations and assistance for wildfire suppression and damage            | County          | [FEMA datasets](https://www.fema.gov/about/openfema/data-sets) |
| **Individual Assistance Data** | Data on federal housing, repair, and disaster assistance                   | County          | [FEMA datasets](https://www.fema.gov/about/openfema/data-sets) |

| Indicator                                       | Description                                                            | Geography Level      | Source                                                     |
| ----------------------------------------------- | ---------------------------------------------------------------------- | -------------------- | ---------------------------------------------------------- |
| **Child Opportunity Index (COI)**               | Composite measure of neighborhood-level opportunity for children       | Tract                | diversitydatakids.org                                      |
| **Social Vulnerability Index (SVI)**            | CDC’s metric of community resilience to disasters and hardship         | Tract, County        | CDC/ATSDR                                                  |
| **Opportunity Atlas (OA)**                      | Economic mobility measures by childhood neighborhood                   | Tract                | opportunityatlas.org                                       |
| **Zoning Restrictions (National Zoning Atlas)** | Classifies local zoning codes by land use and restrictiveness          | Municipality         | [https://www.zoningatlas.org](https://www.zoningatlas.org) |
| **Healthcare Access Scores**                    | Distance to hospitals, emergency care, or clinics                      | Tract/ZIP            | HRSA, ACS-derived                                          |
| **Redlining Maps (HOLC Grades)**                | Historical neighborhood risk grades (A–D) from HOLC                    | Neighborhood / Tract | [Mapping Inequality Project](https://dsl.richmond.edu/panorama/redlining) |

| Indicator          | Description                                  | GEE Source / Method               |
| ------------------ | -------------------------------------------- | --------------------------------- |
| **Elevation**      | Absolute elevation in meters above sea level | `USGS/SRTMGL1_003`, `MERIT DEM`   |
| **Slope**          | Degree of terrain steepness                  | Derived from DEM with `terrain()` |
| **Sea Level Risk** | Tracts below flood-prone elevation threshold | Elevation mask + flood layers     |

---

### 🛰️ Satellite-Derived Proxies

| Proxy                    | Description                                             | Source                             |
|--------------------------|---------------------------------------------------------|------------------------------------|
| **Intersection Density** | High street and node density correlates with walkability| Derived from OpenStreetMap (OSM)   |
| **Land Use Diversity**   | Presence of mixed-use (residential + commercial) zoning | OSM, zoning data                   |
| **Impervious Surface**   | Maps roads, sidewalks, and buildings                    | USGS/NLCD, MODIS, NDBI             |
| **Green Space Proximity**| Distance to parks and recreational areas                | Landsat NDVI, OSM parks            |
| **Nighttime Lights**     | Indicates commercial corridors active at night          | VIIRS/DNB                          |

### 🚌 Transit Accessibility Datasets (Non-Satellite)

| Dataset / Tool                     | Description                                             | Source                             |
|------------------------------------|---------------------------------------------------------|------------------------------------|
| **AllTransit Metrics**             | Transit frequency, access, and walkability scores       | [alltransit.cnt.org](https://alltransit.cnt.org/) |
| **EPA Smart Location Database**    | Tract-level walk and transit scores, built env. metrics | U.S. EPA                           |
| **Walk Score API**                 | Popular walk/transit score (limited free access)        | [walkscore.com](https://www.walkscore.com/) |
| **OpenStreetMap (OSM)**            | Global map of streets, sidewalks, paths, and transit    | Open source                        |
| **GTFS Feeds**                     | Transit agency route and schedule data                  | Local agencies / transit.land      |
| **LEHD LODES Data**                | Home-to-work commute flows by block                     | U.S. Census Bureau                 |



