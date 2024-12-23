import subprocess
import json
import csv

# Test dosyalarının yollarını belirtin
test_files = [
    "color_palette_app.tests.test_algorithm",
    "color_palette_app.tests.test_models",
    "color_palette_app.tests.test_utils",
    "color_palette_app.tests.test_views",
]

def run_tests_and_collect_results(output_format="csv"):
    """
    Django testlerini çalıştırır ve her bir dosyanın sonuçlarını belirtilen formatta kaydeder.
    """
    all_results = []

    for test_file in test_files:
        print(f"Running tests in: {test_file}")
        # Her bir test dosyasını çalıştır
        result = subprocess.run(
            ["python3", "manage.py", "test", test_file, "--verbosity=2"],
            capture_output=True,
            text=True
        )

        # Test sonucu metni
        test_output = result.stdout
        errors = result.stderr

        # Test sonuçlarını ayrıştır
        for line in test_output.splitlines():
            if "FAIL" in line or "ERROR" in line or "OK" in line:
                all_results.append({"test_file": test_file, "result": line})

    # Sonuçları kaydet
    if output_format == "csv":
        with open("test_results.csv", "w", newline="") as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=["test_file", "result"])
            writer.writeheader()
            writer.writerows(all_results)
    elif output_format == "json":
        with open("test_results.json", "w") as jsonfile:
            json.dump(all_results, jsonfile, indent=4)

    print(f"Test sonuçları 'test_results.{output_format}' dosyasına kaydedildi.")

# Örnek kullanım
run_tests_and_collect_results(output_format="csv")
