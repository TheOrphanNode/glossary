import sys
import re
from pathlib import Path
import yaml

REQUIRED_FIELDS = ["id", "term_tr", "term_en", "definition"]
KEBAB_CASE_REGEX = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")

def validate_yaml_files():
    root_dir = Path(__file__).resolve().parent.parent
    data_dir = root_dir / "data" / "domains"

    yaml_files = list(data_dir.glob("*.yaml")) + list(data_dir.glob("*.yml"))
    if not yaml_files:
        print("[!] Hata: Doğrulanacak YAML dosyası bulunamadı.")
        return False

    has_errors = False
    seen_ids = set()
    total_terms = 0

    for file_path in yaml_files:
        rel_file = file_path.relative_to(root_dir)
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                data = yaml.safe_load(f)
        except Exception as e:
            print(f"[x] YAML Sözdizimi Hatası ({rel_file}): {e}")
            has_errors = True
            continue

        if not isinstance(data, dict):
            print(f"[x] Format Hatası ({rel_file}): Dosya ana yapısı bir sözlük (key-value) olmalıdır.")
            has_errors = True
            continue

        if "domain" not in data:
            print(f"[x] Eksik Üst Alan ({rel_file}): 'domain' anahtarı zorunludur.")
            has_errors = True

        terms = data.get("terms", [])
        if not isinstance(terms, list):
            print(f"[x] Format Hatası ({rel_file}): 'terms' alanı bir liste olmalıdır.")
            has_errors = True
            continue

        for idx, item in enumerate(terms, start=1):
            total_terms += 1
            term_id = item.get("id")

            # Zorunlu alan kontrolü
            for field in REQUIRED_FIELDS:
                if not item.get(field):
                    print(f"[x] Eksik Alan ({rel_file} -> #{idx}. Terim): '{field}' alanı eksik veya boş.")
                    has_errors = True

            if term_id:
                # Kebab-case format kontrolü
                if not KEBAB_CASE_REGEX.match(term_id):
                    print(f"[x] Geçersiz ID Biçimi ({rel_file} -> '{term_id}'): Sadece küçük harf, rakam ve tire (-) kullanılmalıdır.")
                    has_errors = True

                # Tekillik (Unique) kontrolü
                if term_id in seen_ids:
                    print(f"[x] Çift ID Tanımı ({rel_file}): '{term_id}' ID'si birden fazla terimde kullanılmış.")
                    has_errors = True
                seen_ids.add(term_id)

    if has_errors:
        print("\n[!] Doğrulama başarısız oldu. Lütfen yukarıdaki hataları giderin.")
        return False

    print(f"[✓] Doğrulama başarılı: {len(yaml_files)} dosyada toplam {total_terms} terim kontrol edildi.")
    return True

if __name__ == "__main__":
    success = validate_yaml_files()
    sys.exit(0 if success else 1)
