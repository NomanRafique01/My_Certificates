import os
import shutil
from pathlib import Path
from PIL import Image
from pdf2image import convert_from_path

BASE_DIR = Path(r"C:\Users\pc\Desktop\Certifcates")
POPPLER_PATH = r"C:\Program Files\Calibre2\app\bin"

# Target directories
CATEGORIES = {
    "Internship": BASE_DIR / "Internship",
    "IBM_Cert": BASE_DIR / "IBM_Cert",
    "Anthropic_Academy": BASE_DIR / "Anthropic_Academy",
    "OpenAI": BASE_DIR / "OpenAI",
    "AI_Ethics_and_Career": BASE_DIR / "AI_Ethics_and_Career",
    "Extra_Crricular_Cert": BASE_DIR / "Extra_Crricular_Cert",
    "Misc": BASE_DIR / "Misc",
}

for folder in CATEGORIES.values():
    folder.mkdir(parents=True, exist_ok=True)

def image_to_pdf(image_path: Path, output_pdf_path: Path):
    with Image.open(image_path) as img:
        rgb_img = img.convert("RGB")
        rgb_img.save(output_pdf_path, "PDF", resolution=150.0)
    print(f"Created PDF from image: {output_pdf_path.name}")

def image_to_png(image_path: Path, output_png_path: Path):
    with Image.open(image_path) as img:
        img.save(output_png_path, "PNG")
    print(f"Created PNG from image: {output_png_path.name}")

def pdf_first_page_to_png(pdf_path: Path, output_png_path: Path):
    pages = convert_from_path(str(pdf_path), first_page=1, last_page=1, dpi=150, poppler_path=POPPLER_PATH)
    if pages:
        pages[0].save(str(output_png_path), "PNG")
        print(f"Rendered PNG from PDF: {output_png_path.name}")
    else:
        print(f"Warning: No pages found in {pdf_path}")

def classify_root_file(filename: str) -> str:
    name_lower = filename.lower()
    if "flyrank" in name_lower:
        return "Internship"
    elif "openai" in name_lower or "gpts" in name_lower:
        return "OpenAI"
    elif "agentic" in name_lower or "ibm" in name_lower:
        return "IBM_Cert"
    elif "numl" in name_lower:
        return "Extra_Crricular_Cert"
    elif "ethics" in name_lower or "career" in name_lower:
        return "AI_Ethics_and_Career"
    else:
        return "Misc"

def process_all():
    # 1. Process Anthropic Academy PDFs
    old_anthropic_dir = BASE_DIR / "Anthrophic Accademy"
    anthropic_target_dir = CATEGORIES["Anthropic_Academy"]
    
    if old_anthropic_dir.exists() and old_anthropic_dir.is_dir():
        for item in sorted(old_anthropic_dir.iterdir()):
            if item.is_file() and item.suffix.lower() == ".pdf":
                dest_pdf = anthropic_target_dir / item.name
                shutil.copy2(item, dest_pdf)
                # Convert PDF to PNG
                dest_png = anthropic_target_dir / f"{item.stem}.png"
                pdf_first_page_to_png(dest_pdf, dest_png)
        # We can remove old_anthropic_dir or keep as backup
        try:
            shutil.rmtree(old_anthropic_dir)
            print("Successfully migrated 'Anthrophic Accademy' to 'Anthropic_Academy'")
        except Exception as e:
            print(f"Notice: Could not remove old directory: {e}")

    # 2. Process Root Files
    for file_path in sorted(BASE_DIR.iterdir()):
        if not file_path.is_file():
            continue
        if file_path.name in ["process_certificates.py", "organize_certificates.py", "README.md"]:
            continue
        
        category = classify_root_file(file_path.name)
        target_dir = CATEGORIES[category]
        stem = file_path.stem
        ext = file_path.suffix.lower()
        
        print(f"\nProcessing {file_path.name} -> Category: {category}")
        
        if ext in [".jpg", ".jpeg", ".png"]:
            dest_pdf = target_dir / f"{stem}.pdf"
            dest_png = target_dir / f"{stem}.png"
            # Convert image to PDF
            image_to_pdf(file_path, dest_pdf)
            # Ensure PNG exists
            image_to_png(file_path, dest_png)
            # Remove original from root so root stays clean
            file_path.unlink()
        elif ext == ".pdf":
            dest_pdf = target_dir / file_path.name
            dest_png = target_dir / f"{stem}.png"
            shutil.move(str(file_path), str(dest_pdf))
            pdf_first_page_to_png(dest_pdf, dest_png)

    # 3. Generate README.md
    generate_readme()

def generate_readme():
    readme_path = BASE_DIR / "README.md"
    import urllib.parse
    
    category_titles = {
        "Internship": "💼 Internship Certificate",
        "IBM_Cert": "🔷 IBM Certifications",
        "Anthropic_Academy": "🎓 Anthropic Academy Certificates",
        "OpenAI": "🤖 OpenAI & Custom GPTs",
        "AI_Ethics_and_Career": "⚖️ AI Ethics & Career Empowerment",
        "Extra_Crricular_Cert": "🏅 Extra-Curricular Certificates",
        "Misc": "📜 Miscellaneous & Other Certifications",
    }
    
    category_descriptions = {
        "Internship": "Verified industry completion certificate for professional backend AI engineering internship experience.",
        "IBM_Cert": "Industry credentials and digital badges awarded by IBM SkillsBuild for Agentic AI architecture and workflows.",
        "Anthropic_Academy": "Comprehensive 20-course certification series from Anthropic covering Claude architecture, prompt engineering, agentic skills, subagents, and Model Context Protocol (MCP).",
        "OpenAI": "Specialized certifications in OpenAI technologies, GPT customization, and prompt engineering workflows.",
        "AI_Ethics_and_Career": "Foundational certifications in artificial intelligence ethics, governance, and professional career development.",
        "Extra_Crricular_Cert": "Honors, competitive achievements, and inter-college quiz competition awards.",
        "Misc": "Additional awards and professional development courses from HP Foundation and UNITAR.",
    }

    lines = []
    lines.append("# 🏆 Certificates & Professional Credentials\n")
    lines.append("A curated showcase of verified certifications, professional courses, and industry credentials in Artificial Intelligence, Prompt Engineering, and Autonomous Systems Development.\n")
    
    # Calculate stats
    total_certs = 0
    cat_counts = {}
    for cat_key, cat_folder in CATEGORIES.items():
        pdfs = list(cat_folder.glob("*.pdf"))
        cat_counts[cat_key] = len(pdfs)
        total_certs += len(pdfs)
        
    lines.append("## 📊 Overview\n")
    lines.append(f"- **Total Certificates:** {total_certs}")
    for cat_key, title in category_titles.items():
        count = cat_counts.get(cat_key, 0)
        lines.append(f"- [{title}](#{cat_key.lower()}): **{count}** {'certificate' if count == 1 else 'certificates'}")
    lines.append("\n---\n")

    for cat_key, cat_folder in CATEGORIES.items():
        title = category_titles[cat_key]
        desc = category_descriptions[cat_key]
        lines.append(f"<a id=\"{cat_key.lower()}\"></a>")
        lines.append(f"## {title}\n")
        lines.append(f"> {desc}\n")
        
        png_files = sorted(cat_folder.glob("*.png"), key=lambda p: p.name.lower())
        
        if not png_files:
            lines.append("_No certificates in this category yet._\n")
            continue
            
        if cat_key == "Anthropic_Academy":
            lines.append("<table>")
            for i in range(0, len(png_files), 4):
                chunk = png_files[i:i + 4]
                lines.append("  <tr>")
                for png_file in chunk:
                    pdf_file = png_file.with_suffix(".pdf")
                    stem = png_file.stem
                    display_name = stem.replace("_", " ")
                    encoded_png = f"{cat_key}/{urllib.parse.quote(png_file.name)}"
                    encoded_pdf = f"{cat_key}/{urllib.parse.quote(pdf_file.name)}"

                    lines.append('    <td width="25%" align="center" valign="top">')
                    lines.append(f'      <a href="{encoded_pdf}">')
                    lines.append(f'        <img src="{encoded_png}" alt="{display_name}" width="100%" style="border-radius: 6px; box-shadow: 0 4px 10px rgba(0,0,0,0.12); border: 1px solid #e1e4e8;" />')
                    lines.append('      </a>')
                    lines.append('      <br />')
                    lines.append(f'      <strong>{display_name}</strong>')
                    lines.append('    </td>')
                if len(chunk) < 4:
                    for _ in range(4 - len(chunk)):
                        lines.append('    <td width="25%"></td>')
                lines.append("  </tr>")
            lines.append("</table>\n")
            lines.append("\n---\n")
            continue

        for png_file in png_files:
            pdf_file = png_file.with_suffix(".pdf")
            stem = png_file.stem
            
            # Special friendly labels for known IDs
            if "82aeeb73" in stem:
                display_name = "HP LIFE – AI for Beginners"
            elif "Certificate_of_Completion-images-0" in stem:
                display_name = "UNITAR UN CC:Learn – Climate Change: From Learning to Action"
            elif "Numl certificate" in stem:
                display_name = "NUML – 1st Position Inter-Colleges Quiz Competition (Certificate of Appreciation)"
            elif "MakeAgenticAIWorkforYou" in stem:
                display_name = "IBM SkillsBuild – Make Agentic AI Work for You"
            elif "flyrank" in stem:
                display_name = "FlyRank – Backend AI Engineering Internship (Certificate of Completion)"
            elif "ai-and-career-empowerment" in stem:
                display_name = "AI and Career Empowerment – Noman Rafique"
            elif "OpenAI GPTs" in stem:
                display_name = "OpenAI – Certificate in OpenAI GPTs: Creating Your Own Custom AI"
            elif "Certificate of Ethics" in stem:
                display_name = "Certificate of Ethics of Artificial Intelligence"
            else:
                display_name = stem.replace("_", " ")

            encoded_png = f"{cat_key}/{urllib.parse.quote(png_file.name)}"
            encoded_pdf = f"{cat_key}/{urllib.parse.quote(pdf_file.name)}"
            
            lines.append(f"### {display_name}\n")
            if pdf_file.exists():
                lines.append(f"<p align=\"center\">\n  <a href=\"{encoded_pdf}\">\n    <img src=\"{encoded_png}\" alt=\"{display_name}\" width=\"720\" style=\"border-radius: 8px; box-shadow: 0 4px 14px rgba(0,0,0,0.12);\" />\n  </a>\n</p>\n")
            else:
                lines.append(f"<p align=\"center\">\n  <img src=\"{encoded_png}\" alt=\"{display_name}\" width=\"720\" style=\"border-radius: 8px; box-shadow: 0 4px 14px rgba(0,0,0,0.12);\" />\n</p>\n")
            lines.append("\n---\n")

    readme_path.write_text("\n".join(lines), encoding="utf-8")
    print("README.md regenerated successfully!")

if __name__ == "__main__":
    process_all()
