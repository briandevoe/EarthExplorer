# -----------------------------------------------------------------------------
# Script: plot_modis_ndvi_ndbi.R
# Purpose: Plot monthly NDVI and NDBI GeoTIFFs exported by the MODIS Python script
# -----------------------------------------------------------------------------

library(raster)
library(ggplot2)
library(ggpubr)
library(patchwork)
library(stringr)

# -----------------------------------------------------------------------------
# 1. SET FILE PATH
# -----------------------------------------------------------------------------
base_path <- "C:/Users/bdevoe/Desktop/git/EarthExplorer/data/raw"
all_dirs <- list.dirs(base_path, full.names = TRUE, recursive = FALSE)

# -----------------------------------------------------------------------------
# 2. FIND TIFF FILES FOR EACH MONTH
# -----------------------------------------------------------------------------
ndvi_files <- list.files(all_dirs, pattern = "ndvi_us_2023-\\d{2}-\\d{2}\\.tif$", full.names = TRUE, recursive = TRUE)
ndbi_files <- list.files(all_dirs, pattern = "ndbi_us_2023-\\d{2}-\\d{2}\\.tif$", full.names = TRUE, recursive = TRUE)

# Sort chronologically
ndvi_files <- ndvi_files[order(ndvi_files)]
ndbi_files <- ndbi_files[order(ndbi_files)]

# -----------------------------------------------------------------------------
# 3. PLOT EACH PAIR OF NDVI + NDBI
# -----------------------------------------------------------------------------
plot_ndvi_ndbi <- function(ndvi_path, ndbi_path) {
  ndvi <- raster(ndvi_path)
  ndbi <- raster(ndbi_path)
  date_str <- str_extract(ndvi_path, "2023-\\d{2}-\\d{2}")

  p1 <- as.data.frame(rasterToPoints(ndvi)) |>
    ggplot(aes(x = x, y = y, fill = layer)) +
    geom_raster() +
    scale_fill_viridis_c(na.value = "transparent", name = "NDVI") +
    coord_equal() +
    theme_minimal() +
    ggtitle(paste("NDVI -", date_str))

  p2 <- as.data.frame(rasterToPoints(ndbi)) |>
    ggplot(aes(x = x, y = y, fill = layer)) +
    geom_raster() +
    scale_fill_viridis_c(na.value = "transparent", name = "NDBI") +
    coord_equal() +
    theme_minimal() +
    ggtitle(paste("NDBI -", date_str))

  return(p1 + p2)
}

# -----------------------------------------------------------------------------
# 4. LOOP THROUGH MONTHLY IMAGES AND DISPLAY
# -----------------------------------------------------------------------------
for (i in seq_along(ndvi_files)) {
  cat("📅 Plotting", ndvi_files[i], "\n")
  print(plot_ndvi_ndbi(ndvi_files[i], ndbi_files[i]))
  # Sys.sleep(1)  # Pause to view before next plot
}
