library(terra)
library(ggplot2)
library(cowplot)

# ----------------------------
# Inputs
# ----------------------------
base_dir <- "C:/Users/bdevoe/Desktop/git/EarthExplorer/data/raw"
target_month <- "2023-02-01_to_2023-02-28"
state <- "new_jersey"
output_file <- file.path(base_dir, paste0("plot_", target_month, "_", state, ".png"))

# ----------------------------
# Helper: Find raster file
# ----------------------------
get_file <- function(indicator) {
  folder <- list.dirs(base_dir, recursive = FALSE, full.names = TRUE)
  folder <- folder[grepl(target_month, folder)]
  if (length(folder) == 0) return(NULL)
  tif_file <- list.files(folder, pattern = paste0(indicator, "_", state, "_", target_month, ".*\\.tif$"), full.names = TRUE)
  if (length(tif_file) > 0) return(tif_file[1]) else return(NULL)
}

# ----------------------------
# Load rasters
# ----------------------------
ndvi_r <- rast(get_file("ndvi"))
ndbi_r <- rast(get_file("ndbi"))
ozone_r <- rast(get_file("ozone"))

# ----------------------------
# Resample to NDVI grid (reference)
# ----------------------------
if (!is.null(ndbi_r)) {
  ndbi_r <- resample(ndbi_r, ndvi_r, method = "bilinear")
}
if (!is.null(ozone_r)) {
  ozone_r <- resample(ozone_r, ndvi_r, method = "bilinear")
}

# ----------------------------
# Convert to data.frames
# ----------------------------
to_df <- function(r, name) {
  if (is.null(r)) return(NULL)
  df <- as.data.frame(r, xy = TRUE, na.rm = TRUE)
  colnames(df)[3] <- "value"
  df$indicator <- name
  return(df)
}

ndvi_df <- to_df(ndvi_r, "NDVI")
ndbi_df <- to_df(ndbi_r, "NDBI")
ozone_df <- to_df(ozone_r, "OZONE")

# ----------------------------
# Plotting
# ----------------------------
plot_map <- function(df, title) {
  if (is.null(df)) {
    return(ggplot() + theme_void() + ggtitle(paste(title, "(missing)")))
  }
  ggplot(df, aes(x = x, y = y, fill = value)) +
    geom_raster() +
    coord_sf(expand = FALSE) +
    scale_fill_viridis_c(option = "C", name = NULL) +
    theme_minimal(base_size = 12) +
    theme(
      axis.text = element_blank(),
      axis.title = element_blank(),
      axis.ticks = element_blank(),
      panel.grid = element_blank(),
      legend.title = element_text(size = 10),
      legend.text = element_text(size = 8),
      plot.title = element_text(size = 14, hjust = 0.5)
    ) +
    labs(title = title)
}

# ----------------------------
# Final plot and save
# ----------------------------
p1 <- plot_map(ndvi_df, "NDVI")
p2 <- plot_map(ndbi_df, "NDBI")
p3 <- plot_map(ozone_df, "OZONE")

print(plot_grid(p1, p3, ncol = 2, rel_widths = c(1, 1)))


cat("✅ High-resolution aligned plot saved to:\n", output_file, "\n")
