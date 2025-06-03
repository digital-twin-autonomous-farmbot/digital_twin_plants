import yaml

with open("results/tiefenberechnung_results.yaml", "r") as f:
    results = yaml.safe_load(f)

# Define bins: (label, lower_bound, upper_bound)
bins = [
    ("< 5 cm", 0, 5),
    ("5–15 cm", 5, 15),
    ("15–30 cm", 15, 30),
    ("30–50 cm", 30, 50),
    (">= 50 cm", 50, float("inf")),
]


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