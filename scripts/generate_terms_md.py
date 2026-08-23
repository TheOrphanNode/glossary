import os
import glob
from pathlib import Path
import yaml

def get_initial_letter(text: str) -> str:
    """Türkçe karakterleri ve baş harfi normalize ederek klasör harfini döner."""
    mapping = {
        'ç': 'c', 'Ç': 'c',
        'ğ': 'g', 'Ğ': 'g',
        'ı': 'i', 'I': 'i', 'İ': 'i', 'i': 'i',
        'ö': 'o', 'Ö': 'o',
        'ş': 's', 'Ş': 's',
        'ü': 'u', 'Ü': 'u',
    }
    cleaned = text.strip()
    if not cleaned:
        return 'other'
    first_char = cleaned[0]
    normalized = mapping.get(first_char, first_char.lower())
    return normalized if normalized.isalpha() else 'other'

def main():
    root_dir = Path(__file__).resolve().parent.parent
    data_dir = root_dir / "data" / "domains"
    terms_tr_dir = root_dir / "terms" / "tr"

    yaml_files = list(data_dir.glob("*.yaml")) + list(data_dir.glob("*.yml"))
    if not yaml_files:
        print(f"[!] Hata: {data_dir} dizininde YAML dosyası bulunamadı.")
        return

    generated_count = 0

    for file_path in yaml_files:
        with open(file_path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)

        if not data or "terms" not in data:
            continue

        domain = data.get("domain", file_path.stem)
        terms = data.get("terms", [])

        for item in terms:
            term_id = item.get("id")
            term_tr = item.get("term_tr", "")
            term_en = item.get("term_en", "")
            definition = item.get("definition", "")
            category = item.get("category", "")
            formula = item.get("formula", "")
            tags = item.get("tags", [])

            if not term_id or not term_tr:
                continue

            letter_dir = terms_tr_dir / get_initial_letter(term_tr)
            letter_dir.mkdir(parents=True, exist_ok=True)

            target_md_path = letter_dir / f"{term_id}.md"

            # YAML Frontmatter ve Markdown gövdesi
            tags_formatted = ", ".join(f'"{tag}"' for tag in tags)
            tags_badges = ", ".join(f"`{t}`" for t in tags) if tags else "-"

            content_lines = [
                "---",
                f'id: "{term_id}"',
                f'term_tr: "{term_tr}"',
                f'term_en: "{term_en}"',
                f'domain: "{domain}"',
                f'category: "{category}"',
                f'tags: [{tags_formatted}]',
                "---",
                "",
                f"# {term_tr}",
                f"> **İngilizce Karşılık:** {term_en}",
                "",
                "## Tanım",
                f"{definition}",
                ""
            ]

            if formula:
                content_lines.extend([
                    "## Formül",
                    f"> `{formula}`",
                    ""
                ])

            content_lines.extend([
                "## Detaylar & Metadata",
                f"- **Alan (Domain):** {domain}",
                f"- **Kategori:** {category}",
                f"- **Etiketler:** {tags_badges}",
                ""
            ])

            with open(target_md_path, "w", encoding="utf-8") as md_file:
                md_file.write("\n".join(content_lines))

            generated_count += 1

    print(f"[✓] Toplam {generated_count} adet Markdown terim dosyası başarıyla üretildi.")

if __name__ == "__main__":
    main()
