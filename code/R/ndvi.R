library(raster)
library(sf)
library(ggplot2)
library(viridis)
library(RColorBrewer)

# Set working directory where the TIFFs are saved
setwd("C:/Users/bdevoe/Downloads/")

# Load individual TIFFs
ndvi <- raster("ndvi_change_nola_2005.tif")
ndwi <- raster("ndwi_change_nola_2005.tif")
ndbi <- raster("ndbi_change_nola_2005.tif")
rgb  <- stack("truecolor_rgb_nola_2005.tif")

# Plot flood-relevant indices
par(mfrow = c(2, 2))
plot(ndvi, main = "NDVI Change (2005)")
plot(ndwi, main = "NDWI Change (2005)")
plot(ndbi, main = "NDBI Change (2005)")

# Plot RGB true color
plotRGB(rgb, r = 1, g = 2, b = 3, scale = 1, stretch = "lin", main = "True Color (Post-Flood)")
