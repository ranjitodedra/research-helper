import json
import os
import base64
import re
import zipfile

notebook_path = "viz/sumo_static2.ipynb"
output_root = "images2"

os.makedirs(output_root, exist_ok=True)

with open(notebook_path, "r", encoding="utf-8") as f:
    nb = json.load(f)

current_title = "Untitled"
current_subtitle = "image"

image_counter = 1

for cell in nb.get("cells", []):
    # Handle markdown titles
    if cell.get("cell_type") == "markdown":
        text = "".join(cell.get("source", []))
        title_match = re.match(r"# (.+)", text)
        subtitle_match = re.match(r"## (.+)", text)

        if title_match:
            current_title = title_match.group(1).strip()
            os.makedirs(os.path.join(output_root, current_title), exist_ok=True)

        if subtitle_match:
            current_subtitle = subtitle_match.group(1).strip()

    # Handle output images
    if cell.get("cell_type") == "code":
        for output in cell.get("outputs", []):
            data = output.get("data", {})
            if "image/png" in data:
                img_data = base64.b64decode(data["image/png"])
                safe_subtitle = re.sub(r"[^\w\- ]", "_", current_subtitle)
                img_name = f"{safe_subtitle}.png"
                img_path = os.path.join(output_root, current_title, img_name)

                with open(img_path, "wb") as img_file:
                    img_file.write(img_data)

                image_counter += 1

# Zip the result
zip_path = "main_images.zip"
with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zipf:
    for root, _, files in os.walk(output_root):
        for file in files:
            full_path = os.path.join(root, file)
            arcname = os.path.relpath(full_path, output_root)
            zipf.write(full_path, arcname)

zip_path