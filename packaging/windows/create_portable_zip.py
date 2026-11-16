"""
Helper script to zip the PyInstaller output into dist/Music-Windows-x64.zip
"""
import os
import zipfile
import shutil

dist_dir = os.path.join(os.path.dirname(__file__), "..", "..", "dist")
dist_dir = os.path.abspath(dist_dir)
music_folder = os.path.join(dist_dir, "Music")
zip_output = os.path.join(dist_dir, "Music-Windows-x64.zip")

if not os.path.exists(music_folder):
    print(f"Error: {music_folder} does not exist.")
    exit(1)

print(f"Packaging {music_folder} into {zip_output}...")
if os.path.exists(zip_output):
    os.remove(zip_output)

with zipfile.ZipFile(zip_output, 'w', zipfile.ZIP_DEFLATED) as zipf:
    for root, dirs, files in os.walk(music_folder):
        for file in files:
            file_path = os.path.join(root, file)
            arcname = os.path.relpath(file_path, music_folder)
            zipf.write(file_path, os.path.join("Music", arcname))

size_mb = os.path.getsize(zip_output) / (1024 * 1024)
print(f"Done! Created {zip_output} ({size_mb:.1f} MB)")
