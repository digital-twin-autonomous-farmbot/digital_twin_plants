# mit R script ersetzten linesare coorelation ja oder nein

import yaml

with open("results/tiefenberechnung_results.yaml", "r") as f:
    results = yaml.safe_load(f)

# Define bins: (label, lower_bound, upper_bound)
bins = [
    ("< 5 cm", 0, 5),
    ("6–15 cm", 6, 15),
    ("16–30 cm", 16, 30),
    ("31–50 cm", 31, 50),
    (">= 51 cm", 51, float("inf")),
]

# histogram teifenberechnung_results.yaml
# Initialize counts for each bin
bins_depth = [
    ("< 50 cm", 0, 50),
    ("51-75 cm", 51, 75),
    ("75-100 cm", 76, 100),
    ("101-125 cm", 101, 125),
    ("126-150 cm", 126, 150),
    (">= 151 cm", 151, float("inf")),
]

# histogram plant height
  
# Initialize counters
counts = {label: 0 for (label, _, _) in bins}

for entry in results:
    h = entry.get("plant_height_cm")
    if h is not None and isinstance(h, (int, float)) and h == h:  # check for NaN
        for label, low, high in bins:
            if low <= h < high:
                counts[label] += 1
                break
        else:
            if h >= 50:
                counts[">= 50 cm"] += 1

print("Gruppierte Pflanzenhöhen:")
for label in counts:
    print(f"{label}: {counts[label]}")

# Initialize counters
counts = {label: 0 for (label, _, _) in bins_depth}

for entry in results:
    h = entry.get("mean_depth")
    if h is not None and isinstance(h, (int, float)) and h == h:  # check for NaN
        for label, low, high in bins:
            if low <= h < high:
                counts[label] += 1
                break
        else:
            if h >= 50:
                counts[">= 50 cm"] += 1

print("Gruppierte Pflanzenhöhen:")
for label in counts:
    print(f"{label}: {counts[label]}")