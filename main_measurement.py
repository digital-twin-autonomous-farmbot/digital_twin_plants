import subprocess

def run_script(cmd, shell=False):
    print(f"Running: {cmd}")
    result = subprocess.run(cmd, shell=shell)
    if result.returncode != 0:
        print(f"Fehler beim Ausführen von: {cmd}")
        exit(result.returncode)

if __name__ == "__main__":
    # 1. Bilder aufnehmen
    run_script(["picture_taking_scripts/take_plant_picture.sh"])

    # 2. Tiefenberechnung für alle Bildpaare
    run_script(["python", "death_calculation/tiefenberechnung_schleife.py"])

    # 3. Mittelwert berechnen
    run_script(["python", "death_calculation/sorte_results.py"])