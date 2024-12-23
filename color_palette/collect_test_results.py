import subprocess  # sistem komutlarını çalıştırmak için gerekli modül
import json  # json formatında dosya yazma ve okuma işlemleri için modül
import csv  # csv formatında dosya yazma ve okuma işlemleri için modül

# test dosyalarının yollarını liste olarak tanımlıyoruz
# bu dosyalar django projelerinde yazılmış testleri içeriyor
test_files = [
    "color_palette_app.tests.test_algorithm",  # algoritma testleri
    "color_palette_app.tests.test_models",  # model testleri
    "color_palette_app.tests.test_utils",  # yardımcı fonksiyon testleri
    "color_palette_app.tests.test_views",  # view fonksiyonlarının testleri
]

def run_tests_and_collect_results(output_format="csv"):
    """
    belirtilen test dosyalarını çalıştırır ve sonuçları toplar. sonuçları belirtilen formatta (csv veya json) kaydeder.

    parametreler:
        output_format (str): "csv" veya "json" olarak test sonuçlarının kaydedilmesini belirler.
    """
    all_results = []  # tüm test sonuçlarını tutmak için boş bir liste

    # listedeki her bir test dosyası için işlemleri gerçekleştiriyoruz
    for test_file in test_files:
        print(f"Running tests in: {test_file}")  # hangi test dosyasının çalıştırıldığını gösterir
        
        # subprocess ile django'nun test komutunu çalıştırıyoruz
        result = subprocess.run(
            ["python3", "manage.py", "test", test_file, "--verbosity=2"],  # detaylı test çıktısı burada windows kullanıyorsanız "python" olarak değiştirin
            capture_output=True,  # komut çıktısını yakalar
            text=True  # çıktıyı metin olarak işler
        )

        # test çıktısını ve hata mesajlarını alıyoruz
        test_output = result.stdout  # testin standart çıktısı
        errors = result.stderr  # test sırasında oluşabilecek hatalar

        # test çıktısını satır satır dolaşıyoruz
        for line in test_output.splitlines():
            # satırda "FAIL", "ERROR" veya "OK" varsa, bu satırı sonuçlara ekliyoruz
            if "FAIL" in line or "ERROR" in line or "OK" in line:
                all_results.append({"test_file": test_file, "result": line})

    # sonuçları belirtilen formata göre kaydediyoruz
    if output_format == "csv":
        with open("test_results.csv", "w", newline="") as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=["test_file", "result"])
            writer.writeheader()  # csv dosyasına başlık ekler
            writer.writerows(all_results)  # sonuçları csv formatında yazar
    elif output_format == "json":
        with open("test_results.json", "w") as jsonfile:
            json.dump(all_results, jsonfile, indent=4)  # json formatında yazar ve okunabilir hale getirir

    print(f"Test sonuçları 'test_results.{output_format}' dosyasına kaydedildi.")  # işlem tamamlanınca bilgi verir

# örnek kullanım: test sonuçlarını csv formatında kaydetmek
run_tests_and_collect_results(output_format="csv")