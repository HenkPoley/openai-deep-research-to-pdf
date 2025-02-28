import re
import os
import qrcode

# Configuration
input_file = "input.md"
output_file = "output.md"
qr_dir = "qr_codes"

os.makedirs(qr_dir, exist_ok=True)

# Data structures
link_to_footid = {}   # Maps (link_text, full_url) -> footnote_id
footid_to_data = {}   # Maps footnote_id -> (link_text, full_url)
url_to_ref     = {}   # Maps full_url -> QR code reference number

foot_counter = 1
ref_counter  = 1

def generate_qr(url, ref):
    """Generate a QR code for 'url' and save as 'qr_<ref>.png'."""
    img = qrcode.make(url)
    img_path = os.path.join(qr_dir, f"qr_{ref}.png")
    img.save(img_path)

def link_replacer(match):
    global foot_counter, ref_counter

    link_text = match.group(1)
    full_url  = match.group(2)

    # 1) Check if we've seen this exact (text, URL) pair
    if (link_text, full_url) not in link_to_footid:
        link_to_footid[(link_text, full_url)] = foot_counter
        footid_to_data[foot_counter] = (link_text, full_url)
        foot_counter += 1

    foot_id = link_to_footid[(link_text, full_url)]

    # 2) Check if we've generated a QR code reference for this URL
    if full_url not in url_to_ref:
        url_to_ref[full_url] = ref_counter
        generate_qr(full_url, ref_counter)
        ref_counter += 1

    # In the main text, replace the link with a footnote reference [^foot_id]
    return f"[^{foot_id}]"

# Read the input Markdown
with open(input_file, "r", encoding="utf-8") as f:
    content = f.read()

# Replace all Markdown links [text](url)
new_content = re.sub(r"\[(.*?)\]\((.*?)\)", link_replacer, content)

# YAML header for Pandoc/LaTeX
header = r"""---
header-includes:
    - \usepackage[utf8]{inputenc}
    - \usepackage[T1]{fontenc}
    - \usepackage{graphicx}
    - \usepackage{newunicodechar}
    - \newunicodechar{δ}{$\delta$}
    - \newunicodechar{₂}{$_2$}
    - \usepackage{url}
    - \usepackage{rotating}
---
"""
new_content = header + "\n" + new_content

# Add footnote definitions
# Each footnote references exactly one QR code
new_content += "\n\n"
for foot_id in sorted(footid_to_data.keys()):
    link_text, full_url = footid_to_data[foot_id]
    qr_ref = url_to_ref[full_url]
    # Gebruik "Q" als prefix voor de QR-code:
    footnote_text = f"{link_text} (QR code: [Q{qr_ref}])"
    new_content += f"[^{foot_id}]: {footnote_text}\n"

# Build the Appendix with QR codes in a 4×5 grid (20 per 'page')
appendix = "\n\n# Appendix: QR Codes\n\n"

columns = 4
rows_per_page = 5
items_per_page = columns * rows_per_page

# Sort by the QR reference number
items = sorted(url_to_ref.items(), key=lambda x: x[1])
pages = [items[i:i+items_per_page] for i in range(0, len(items), items_per_page)]

for page in pages:
    # (optioneel) \begin{sidewaysfigure}
    appendix += r"\footnotesize" + "\n"
    appendix += r"\begin{tabular}{@{}" + ("c" * columns) + "@{}}" + "\n"

    for r in range(0, len(page), columns):
        row_data = page[r:r+columns]
        row_cells = []
        for full_url, ref in row_data:
            # Label de QR-code met [QX]
            cell = (
                r"\begin{minipage}[t]{{0.25\textwidth}}\centering "
                rf"\includegraphics[width=3cm]{{qr_codes/qr_{ref}.png}}\\[-2pt]"
                rf"\footnotesize [Q{ref}]"
                r"\end{minipage}"
            )
            row_cells.append(cell)
        while len(row_cells) < columns:
            row_cells.append("")
        appendix += " & ".join(row_cells) + r" \\" + "[6pt]\n"

    appendix += r"\end{tabular}" + "\n\n"

new_content += appendix

# Write the output
with open(output_file, "w", encoding="utf-8") as f:
    f.write(new_content)

