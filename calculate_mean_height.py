import yaml

with open("tiefenberechnung_results.yaml", "r") as f:
    results = yaml.safe_load(f)

heights = []
for entry in results:
    h = entry.get("plant_height_cm")
    if h is not None and isinstance(h, (int, float)) and h == h:  # check for NaN
        heights.append(h)

if heights:
    mean_height = sum(heights) / len(heights)
    print(f"Anzahl Messungen: {len(heights)}")
    print(f"Mittlere Pflanzenhöhe: {mean_height:.2f} cm")
else:
    print("Keine gültigen Pflanzenhöhen gefunden.")