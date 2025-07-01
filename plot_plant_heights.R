#!/usr/bin/env Rscript
# Plot zur Visualisierung der geschätzten Pflanzenhöhen im Vergleich zur wahren Höhe von 32cm

library(yaml)
library(ggplot2)
library(dplyr)

# Funktion zum Laden der Pflanzenhöhen-Daten aus der YAML-Datei
load_plant_data <- function(yaml_file) {
  # Lade YAML-Daten
  data <- yaml.load_file(yaml_file)
  
  # Extrahiere plant_height_cm und mean_depth_cm Werte
  heights <- c()
  depths <- c()
  
  for(i in seq_along(data)) {
    measurement <- data[[i]]
    if(!is.null(measurement)) {
      # Plant heights
      if("plant_height_cm" %in% names(measurement)) {
        height <- measurement$plant_height_cm
        if(!is.na(height) && !is.null(height) && height != ".nan") {
          heights <- c(heights, as.numeric(height))
        }
      }
      
      # Mean depths
      if("mean_depth_cm" %in% names(measurement)) {
        depth <- measurement$mean_depth_cm
        if(!is.na(depth) && !is.null(depth) && depth != ".nan") {
          depths <- c(depths, as.numeric(depth))
        }
      }
    }
  }
  
  return(list(heights = heights, depths = depths))
}

# Funktion zur Erstellung der Plant Height Plots
create_plant_height_plot <- function(heights, true_height = 32) {
  
  # Erstelle DataFrame
  df <- data.frame(
    measurement = seq_along(heights),
    height = heights
  )
  
  # Berechne Statistiken
  mean_height <- mean(heights)
  std_height <- sd(heights)
  median_height <- median(heights)
  deviation <- abs(mean_height - true_height)
  
  # Plot: Scatter plot of measurements
  p1 <- ggplot(df, aes(x = measurement, y = height)) +
    geom_point(alpha = 0.6, size = 2, color = "blue") +
    geom_hline(yintercept = true_height, color = "red", linetype = "dashed", size = 1) +
    labs(
      x = "Measurement Number",
      y = "Plant Height (cm)",
      title = "Estimated Plant Heights vs. True Height (32 cm)"
    ) +
    theme_minimal() +
    theme(plot.title = element_text(hjust = 0.5)) +
    scale_y_continuous(breaks = scales::pretty_breaks(n = 10))
  
  # Print statistics separately
  cat("\n--- Plant Height Statistics ---\n")
  cat("Mean:", round(mean_height, 2), "cm\n")
  cat("Standard Deviation:", round(std_height, 2), "cm\n")
  cat("Median:", round(median_height, 2), "cm\n")
  cat("Deviation from true value:", round(deviation, 2), "cm\n")
  cat("-------------------------------\n\n")
  
  return(p1)
}

# Funktion zur Erstellung der Depth Plots
create_depth_plot <- function(depths, true_depth = 100) {
  
  # Erstelle DataFrame
  df <- data.frame(
    measurement = seq_along(depths),
    depth = depths
  )
  
  # Berechne Statistiken
  mean_depth <- mean(depths)
  std_depth <- sd(depths)
  median_depth <- median(depths)
  deviation <- abs(mean_depth - true_depth)
  
  # Plot: Scatter plot of measurements
  p1 <- ggplot(df, aes(x = measurement, y = depth)) +
    geom_point(alpha = 0.6, size = 2, color = "green") +
    geom_hline(yintercept = true_depth, color = "red", linetype = "dashed", size = 1) +
    labs(
      x = "Measurement Number",
      y = "Mean Depth (cm)",
      title = "Estimated Mean Depths vs. True Depth (100 cm)"
    ) +
    theme_minimal() +
    theme(plot.title = element_text(hjust = 0.5)) +
    scale_y_continuous(breaks = scales::pretty_breaks(n = 10))
  
  # Print statistics separately
  cat("\n--- Mean Depth Statistics ---\n")
  cat("Mean:", round(mean_depth, 2), "cm\n")
  cat("Standard Deviation:", round(std_depth, 2), "cm\n")
  cat("Median:", round(median_depth, 2), "cm\n")
  cat("Deviation from true value:", round(deviation, 2), "cm\n")
  cat("-----------------------------\n\n")
  
  return(p1)
}

# Hauptfunktion
main <- function() {
  yaml_file <- "results/tiefenberechnung_results.yaml"
  
  tryCatch({
    # Lade die Daten
    data <- load_plant_data(yaml_file)
    heights <- data$heights
    depths <- data$depths
    
    cat("Number of valid height measurements:", length(heights), "\n")
    cat("Number of valid depth measurements:", length(depths), "\n")
    
    # Plant Height Analysis
    cat("\n=== PLANT HEIGHT ANALYSIS ===\n")
    cat("Min height:", round(min(heights), 2), "cm\n")
    cat("Max height:", round(max(heights), 2), "cm\n")
    cat("Mean:", round(mean(heights), 2), "cm\n")
    cat("Standard deviation:", round(sd(heights), 2), "cm\n")
    
    # Identify outliers for heights
    reasonable_heights <- heights[heights < 100]
    height_outliers <- heights[heights >= 100]
    
    if(length(height_outliers) > 0) {
      cat("\nHeight outliers found (>= 100cm):", length(height_outliers), "measurements\n")
      
      # Create and save height plots
      plot_height_filtered <- create_plant_height_plot(reasonable_heights, true_height = 32)
      plot_height_all <- create_plant_height_plot(heights, true_height = 32)
      
      png("results/plant_heights_filtered.png", width = 12, height = 8, units = "in", res = 300)
      print(plot_height_filtered)
      dev.off()
      
      png("results/plant_heights_all.png", width = 12, height = 8, units = "in", res = 300)
      print(plot_height_all)
      dev.off()
      
      cat("Height plots saved: plant_heights_filtered.png, plant_heights_all.png\n")
    } else {
      plot_height <- create_plant_height_plot(heights, true_height = 32)
      png("results/plant_heights_analysis.png", width = 12, height = 8, units = "in", res = 300)
      print(plot_height)
      dev.off()
      cat("Height plot saved: plant_heights_analysis.png\n")
    }
    
    # Depth Analysis
    cat("\n=== MEAN DEPTH ANALYSIS ===\n")
    cat("Min depth:", round(min(depths), 2), "cm\n")
    cat("Max depth:", round(max(depths), 2), "cm\n")
    cat("Mean:", round(mean(depths), 2), "cm\n")
    cat("Standard deviation:", round(sd(depths), 2), "cm\n")
    
    # Identify outliers for depths (values very far from 100cm)
    reasonable_depths <- depths[depths > 50 & depths < 200]  # Keep values within reasonable range
    depth_outliers <- depths[depths <= 50 | depths >= 200]
    
    if(length(depth_outliers) > 0) {
      cat("\nDepth outliers found (< 50cm or >= 200cm):", length(depth_outliers), "measurements\n")
      
      # Create and save depth plots
      plot_depth_filtered <- create_depth_plot(reasonable_depths, true_depth = 100)
      plot_depth_all <- create_depth_plot(depths, true_depth = 100)
      
      png("results/mean_depths_filtered.png", width = 12, height = 8, units = "in", res = 300)
      print(plot_depth_filtered)
      dev.off()
      
      png("results/mean_depths_all.png", width = 12, height = 8, units = "in", res = 300)
      print(plot_depth_all)
      dev.off()
      
      cat("Depth plots saved: mean_depths_filtered.png, mean_depths_all.png\n")
    } else {
      plot_depth <- create_depth_plot(depths, true_depth = 100)
      png("results/mean_depths_analysis.png", width = 12, height = 8, units = "in", res = 300)
      print(plot_depth)
      dev.off()
      cat("Depth plot saved: mean_depths_analysis.png\n")
    }
    
  }, error = function(e) {
    if(grepl("cannot open the connection", e$message)) {
      cat("Error: File", yaml_file, "not found!\n")
    } else {
      cat("Error processing data:", e$message, "\n")
    }
  })
}

# Führe Hauptfunktion aus
main()
