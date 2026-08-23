import re
from pathlib import Path
import yaml

def turkish_sort_key(text: str):
    """Türkçe alfabetik sıralama ağırlıkları."""
    alphabet = "aâbcçdefgğhıiîjklmnoöprsştuûüvyz"
    order = {char: idx for idx, char in enumerate(alphabet)}
    return [order.get(c, ord(c)) for c in text.lower()]

def parse_term_file(file_path: Path, root_dir: Path):
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    metadata = {}
    frontmatter_match = re.match(r"^---\n(.*?)\n---", content, re.DOTALL)
    if frontmatter_match:
        try:
            metadata = yaml.safe_load(frontmatter_match.group(1)) or {}
        except Exception:
            pass

    rel_path = file_path.relative_to(root_dir).as_posix()
    term_tr = metadata.get("term_tr", file_path.stem)
    term_en = metadata.get("term_en", "-")
    domain = metadata.get("domain", "-")

    return {
        "term_tr": term_tr,
        "term_en": term_en,
        "domain": domain,
        "path": rel_path
    }

def main():
    root_dir = Path(__file__).resolve().parent.parent
    terms_dir = root_dir / "terms" / "tr"
    readme_path = root_dir / "README.md"

    md_files = list(terms_dir.glob("*/*.md"))
    if not md_files:
        print("[!] terms/tr/ dizini altında terim dosyası bulunamadı.")
        return

    # Terimleri ayrıştır ve sırala
    terms = [parse_term_file(p, root_dir) for p in md_files]
    terms.sort(key=lambda x: turkish_sort_key(x["term_tr"]))

    # Harf gruplaması
    grouped = {}
    for item in terms:
        first_letter = item["term_tr"][0].upper()
        grouped.setdefault(first_letter, []).append(item)

    letters = sorted(grouped.keys(), key=lambda l: turkish_sort_key(l))

    # README İçeriği İnşası
    lines = [
        "# 📚 Glossary",
        "",
        "Kişisel teknik terim sözlüğü ve kavram fihristi.",
        "",
        "## 🧭 Hızlı Erişim (Index)",
        "",
        " ".join([f"[{letter}](#{letter.lower()}) •" for letter in letters]).rstrip(" •"),
        "",
        "---",
        ""
    ]

    for letter in letters:
        lines.append(f"### {letter}")
        lines.append("")
        lines.append("| Terim (TR) | İngilizce Karşılık | Alan (Domain) |")
        lines.append("| :--- | :--- | :--- |")
        for term in grouped[letter]:
            lines.append(f"| [{term['term_tr']}]({term['path']}) | {term['term_en']} | `{term['domain']}` |")
        lines.append("")

    lines.extend([
        "---",
        "",
        "### 🛠 Bakım ve Otomasyon",
        "",
        "Yeni bir terim ekledikten sonra fihristi ve dosyaları güncellemek için:",
        "",
        "```bash",
        "# 1. YAML verilerinden Markdown dosyalarını üretin",
        "python3 scripts/generate_terms_md.py",
        "",
        "# 2. README fihrist tablosunu güncelleyin",
        "python3 scripts/generate_index.py",
        "```",
        ""
    ])

    with open(readme_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

    print(f"[✓] README.md dosyası {len(terms)} terim ile başarıyla güncellendi.")

if __name__ == "__main__":
    main()
