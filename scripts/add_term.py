import re
import sys
from pathlib import Path
import unicodedata
import yaml

def slugify(text: str) -> str:
    """Metni kebab-case formata dönüştürür."""
    text = text.replace("ı", "i").replace("İ", "i")
    text = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode("utf-8")
    text = re.sub(r"[^\w\s-]", "", text).strip().lower()
    return re.sub(r"[-\s]+", "-", text)

def prompt_required(prompt_text: str) -> str:
    while True:
        value = input(prompt_text).strip()
        if value:
            return value
        print("  [!] Bu alan zorunludur, boş bırakılamaz.")

def select_or_create_domain(domains_dir: Path) -> Path:
    yaml_files = sorted(list(domains_dir.glob("*.yaml")) + list(domains_dir.glob("*.yml")))
    
    print("\n--- 📁 Alan (Domain) Seçimi ---")
    for idx, f in enumerate(yaml_files, start=1):
        print(f"[{idx}] {f.stem}")
    print(f"[{len(yaml_files) + 1}] + Yeni Domain Dosyası Oluştur")

    while True:
        choice = input(f"\nBir alan seçin (1-{len(yaml_files) + 1}): ").strip()
        if choice.isdigit():
            choice_num = int(choice)
            if 1 <= choice_num <= len(yaml_files):
                return yaml_files[choice_num - 1]
            elif choice_num == len(yaml_files) + 1:
                new_domain_name = prompt_required("Yeni domain adı (örn. computer-science): ")
                domain_slug = slugify(new_domain_name)
                new_file = domains_dir / f"{domain_slug}.yaml"
                
                title_tr = input("Alan Başlığı (TR) [Opsiyonel]: ").strip()
                desc_tr = input("Alan Açıklaması (TR) [Opsiyonel]: ").strip()
                
                initial_data = {
                    "domain": domain_slug,
                    "title_tr": title_tr or domain_slug,
                    "description_tr": desc_tr or "",
                    "terms": []
                }
                with open(new_file, "w", encoding="utf-8") as f:
                    yaml.dump(initial_data, f, allow_unicode=True, sort_keys=False)
                return new_file
        print("  [!] Geçersiz seçim, lütfen listedeki rakamlardan birini girin.")

def main():
    root_dir = Path(__file__).resolve().parent.parent
    domains_dir = root_dir / "data" / "domains"
    domains_dir.mkdir(parents=True, exist_ok=True)

    print("═════════════════════════════════════════════")
    print("        🚀 Yeni Terim Ekleme Sihirbazı        ")
    print("═════════════════════════════════════════════")

    target_file = select_or_create_domain(domains_dir)

    with open(target_file, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f) or {}

    if "terms" not in data or not isinstance(data["terms"], list):
        data["terms"] = []

    existing_ids = {t.get("id") for t in data["terms"] if isinstance(t, dict)}

    print("\n--- ✍️  Terim Bilgileri ---")
    term_tr = prompt_required("Terim (Türkçe): ")
    term_en = prompt_required("İngilizce Karşılık: ")

    default_id = slugify(term_en if term_en else term_tr)
    while True:
        term_id_input = input(f"ID [Varsayılan: '{default_id}']: ").strip()
        term_id = slugify(term_id_input) if term_id_input else default_id

        if term_id in existing_ids:
            print(f"  [!] '{term_id}' ID'si bu alanda zaten kayıtlı. Farklı bir ID belirleyin.")
        else:
            break

    category = input("Kategori (örn: financial-evaluation, telos-framework) [Opsiyonel]: ").strip()
    definition = prompt_required("Tanım: ")
    formula = input("Formül (Varsa, örn: (Gelir - Gider) / Gider) [Opsiyonel]: ").strip()
    
    tags_input = input("Etiketler (Virgülle ayırın, örn: finance, metric) [Opsiyonel]: ").strip()
    tags = [slugify(t) for t in tags_input.split(",") if t.strip()] if tags_input else []

    new_term = {
        "id": term_id,
        "term_en": term_en,
        "term_tr": term_tr,
        "category": slugify(category) if category else "",
        "definition": definition,
    }

    if formula:
        new_term["formula"] = formula
    if tags:
        new_term["tags"] = tags

    data["terms"].append(new_term)

    with open(target_file, "w", encoding="utf-8") as f:
        yaml.dump(data, f, allow_unicode=True, sort_keys=False, default_flow_style=False)

    print(f"\n[✓] '{term_tr}' terimi başarıyla {target_file.name} dosyasına eklendi.")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n[!] İşlem iptal edildi.")
        sys.exit(0)
