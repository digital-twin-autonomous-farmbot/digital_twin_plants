# Load required libraries
library(yaml)
library(ggplot2)
library(stats)
library(tidyverse)

# Read the YAML file
results <- yaml::read_yaml("results/tiefenberechnung_results.yaml")

# Convert to dataframe
df <- data.frame(
  plant_height = sapply(results, function(x) x$plant_height_cm),
  mean_depth = sapply(results, function(x) x$mean_depth)
)

# Remove any NA values
df_clean <- na.omit(df)

# Perform correlation test
cor_test <- cor.test(df_clean$plant_height, df_clean$mean_depth, 
                     method="pearson",
                     conf.level = 0.95)

# Create scatter plot
plot <- ggplot(df_clean, aes(x=mean_depth, y=plant_height)) +
  geom_point() +
  geom_smooth(method=lm, se=TRUE) +
  labs(
    title = "Plant Height vs Mean Depth",
    x = "Mean Depth (cm)",
    y = "Plant Height (cm)",
    caption = paste("Correlation coefficient:", round(cor_test$estimate, 3),
                   "\np-value:", round(cor_test$p.value, 4))
  ) +
  theme_minimal()

# Save the plot
ggsave("results/height_depth_correlation.png", plot, width=8, height=6)

# Print statistical results
cat("\nCorrelation Analysis Results:\n")
cat("-----------------------------\n")
cat("Pearson correlation coefficient:", round(cor_test$estimate, 3), "\n")
cat("95% Confidence Interval:", 
    round(cor_test$conf.int[1], 3), "to", 
    round(cor_test$conf.int[2], 3), "\n")
cat("p-value:", round(cor_test$p.value, 4), "\n")

# Save statistical results
sink("results/statistical_analysis.txt")
cat("Statistical Analysis Results\n")
cat("==========================\n\n")
cat("Correlation Analysis:\n")
cat("--------------------\n")
cat("Method: Pearson's product-moment correlation\n\n")
cat("Correlation coefficient:", round(cor_test$estimate, 3), "\n")
cat("95% Confidence Interval:", 
    round(cor_test$conf.int[1], 3), "to", 
    round(cor_test$conf.int[2], 3), "\n")
cat("p-value:", round(cor_test$p.value, 4), "\n\n")
cat("Interpretation:\n")
cat("-------------\n")
if (cor_test$p.value < 0.05) {
  cat("There is a significant correlation between plant height and mean depth\n")
  if (cor_test$estimate > 0) {
    cat("The correlation is positive, indicating that plant height tends to increase with depth\n")
  } else {
    cat("The correlation is negative, indicating that plant height tends to decrease with depth\n")
  }
} else {
  cat("There is no significant correlation between plant height and mean depth\n")
}
sink()

# Create multiple visualizations for thesis

# 1. Scatter plot with regression line and confidence interval
scatter_plot <- ggplot(df_clean, aes(x=mean_depth, y=plant_height)) +
  geom_point(color="darkblue", size=3, alpha=0.6) +
  geom_smooth(method=lm, se=TRUE, color="red") +
  labs(
    title = "Plant Height vs Mean Depth",
    subtitle = paste("Pearson correlation =", round(cor_test$estimate, 3)),
    x = "Mean Depth (cm)",
    y = "Plant Height (cm)"
  ) +
  theme_minimal() +
  theme(
    text = element_text(size=12),
    plot.title = element_text(size=14, face="bold"),
    plot.subtitle = element_text(size=12, face="italic")
  )

# 2. Residual plot
model <- lm(plant_height ~ mean_depth, data=df_clean)
df_clean$residuals <- residuals(model)
df_clean$fitted <- fitted(model)

residual_plot <- ggplot(df_clean, aes(x=fitted, y=residuals)) +
  geom_point(color="darkblue", size=3, alpha=0.6) +
  geom_hline(yintercept=0, linetype="dashed", color="red") +
  labs(
    title = "Residual Plot",
    subtitle = "Check for homoscedasticity",
    x = "Fitted Values (cm)",
    y = "Residuals (cm)"
  ) +
  theme_minimal() +
  theme(
    text = element_text(size=12),
    plot.title = element_text(size=14, face="bold"),
    plot.subtitle = element_text(size=12, face="italic")
  )

# 3. Q-Q plot for normality check
qq_plot <- ggplot(df_clean, aes(sample=residuals)) +
  stat_qq(color="darkblue", size=3) +
  stat_qq_line(color="red") +
  labs(
    title = "Normal Q-Q Plot",
    subtitle = "Check for normality of residuals",
    x = "Theoretical Quantiles",
    y = "Sample Quantiles"
  ) +
  theme_minimal() +
  theme(
    text = element_text(size=12),
    plot.title = element_text(size=14, face="bold"),
    plot.subtitle = element_text(size=12, face="italic")
  )

# Get current date in DD_MM_YYYY format
current_date <- format(Sys.Date(), "%d_%m_%Y")

# Save all plots with date in filenames
ggsave(sprintf("results/scatter_plot_%s.pdf", current_date), scatter_plot, width=8, height=6)
ggsave(sprintf("results/residual_plot_%s.pdf", current_date), residual_plot, width=8, height=6)
ggsave(sprintf("results/qq_plot_%s.pdf", current_date), qq_plot, width=8, height=6)

# Add regression statistics to the analysis file
sink("results/statistical_analysis.txt", append=TRUE)
cat("\nRegression Analysis:\n")
cat("-------------------\n")
cat("Linear model summary:\n")
print(summary(model))
cat("\nModel diagnostics:\n")
cat("R-squared:", round(summary(model)$r.squared, 3), "\n")
cat("Adjusted R-squared:", round(summary(model)$adj.r.squared, 3), "\n")
cat("F-statistic p-value:", format.pval(summary(model)$fstatistic[1], digits=4), "\n")
sink()