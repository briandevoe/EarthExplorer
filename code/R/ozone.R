# Load required packages
library(terra)
library(ggplot2)
library(viridis)

# Set file path to the exported ozone GeoTIFF
ozone_path <- "C:/Users/bdevoe/Desktop/Remote Sensing/data and scripts/ozone/OZONE_S5P_MA_2021/ozone_s5p_massachusetts_2021.tif"

# Load the raster
r <- rast(ozone_path)

# Downsample for plotting (if needed)
r_small <- aggregate(r, fact = 2, fun = mean, na.rm = TRUE)  # Adjust 'fact' as needed

# Convert to data.frame
r_df <- as.data.frame(r_small, xy = TRUE, na.rm = TRUE)
names(r_df)[3] <- "Ozone"

# Plot
ggplot(r_df, aes(x = x, y = y, fill = Ozone)) +
  geom_raster() +
  scale_fill_viridis(name = "O₃ (mol/m²)", na.value = "transparent") +
  coord_equal() +
  labs(
    title = "Annual Mean Tropospheric Ozone (Sentinel-5P)",
    subtitle = "Massachusetts, 2021",
    x = "Longitude", y = "Latitude"
  ) +
  theme_minimal()
