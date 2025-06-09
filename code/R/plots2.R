# Load required packages
library(terra)
library(ggplot2)
library(ggspatial)
library(stringr)

# Define folder containing exported GeoTIFFs
folder_path <- "C:/Users/bdevoe/Desktop/Remote Sensing/data and scripts/ndvi/sentinel/NDVI_S2_MA_2021/"

# List all GeoTIFF files
file_list <- list.files(folder_path, full.names = TRUE)

# Extract state and year from filenames
extract_metadata <- function(file_path) {
  fname <- basename(file_path)
  matches <- str_match(fname, "aod_raster_([a-z_]+)_(//d{4})//.tif")
  list(state = str_to_title(gsub("_", " ", matches[2])), year = as.integer(matches[3]))
}

metadata <- lapply(file_list, extract_metadata)

# Loop through each file and plot
for (i in seq_along(file_list)) {
  file <- file_list[i]
  state <- metadata[[i]]$state
  year <- metadata[[i]]$year

  # Load raster
  r <- rast(file)

  # Convert raster to data frame for ggplot
  r_df <- as.data.frame(r, xy = TRUE, na.rm = TRUE)
  colnames(r_df)[3] <- "AOD"

  # Plot
  p <- ggplot(r_df, aes(x = x, y = y, fill = AOD)) +
    geom_raster() +
    scale_fill_viridis_c(option = "C", na.value = "transparent") +
    coord_equal() +
    labs(title = paste("Annual Average AOD -", state, year),
         fill = "AOD",
         x = NULL,
         y = NULL) +
    theme_minimal()

  print(p)

  # Optionally save the plot
  # ggsave(sprintf("C:/Users/bdevoe/Desktop/aod_exports2/plots/aod_%s_%d.png", tolower(gsub(' ', '_', state)), year), plot = p, width = 6, height = 5)
}



