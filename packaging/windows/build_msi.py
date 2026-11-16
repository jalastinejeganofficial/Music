"""
Music Desktop - Automated MSI Package Builder
Uses WiX Toolset to compile dist/Music into a native Windows Installer package: dist/Music.msi
"""

import os
import sys
import uuid
import shutil
import zipfile
import subprocess
import urllib.request
import xml.etree.ElementTree as ET

WIX_URL = "https://github.com/wixtoolset/wix3/releases/download/wix3112rtm/wix311-binaries.zip"
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(BASE_DIR, "..", ".."))
DIST_MUSIC = os.path.join(PROJECT_ROOT, "dist", "Music")
DIST_DIR = os.path.join(PROJECT_ROOT, "dist")
WIX_TOOLS_DIR = os.path.join(BASE_DIR, "wix_tools")
MSI_OUTPUT = os.path.join(DIST_DIR, "Music.msi")
ICON_ICO = os.path.join(PROJECT_ROOT, "assets", "icon.ico")

def ensure_wix_tools():
    candle = os.path.join(WIX_TOOLS_DIR, "candle.exe")
    light = os.path.join(WIX_TOOLS_DIR, "light.exe")
    if os.path.exists(candle) and os.path.exists(light):
        print(f"[MSI Builder] Found WiX tools at: {WIX_TOOLS_DIR}")
        return candle, light

    # Check system WiX
    system_candle = shutil.which("candle")
    system_light = shutil.which("light")
    if system_candle and system_light:
        print(f"[MSI Builder] Found system WiX tools in PATH")
        return system_candle, system_light

    print("[MSI Builder] Downloading WiX 3.11 standalone binaries...")
    os.makedirs(WIX_TOOLS_DIR, exist_ok=True)
    zip_path = os.path.join(WIX_TOOLS_DIR, "wix_binaries.zip")
    
    urllib.request.urlretrieve(WIX_URL, zip_path)
    print("[MSI Builder] Extracting WiX tools...")
    with zipfile.ZipFile(zip_path, 'r') as zf:
        zf.extractall(WIX_TOOLS_DIR)
    
    try:
        os.remove(zip_path)
    except Exception:
        pass
    
    if os.path.exists(candle) and os.path.exists(light):
        print("[MSI Builder] WiX tools ready.")
        return candle, light
    else:
        raise RuntimeError("Failed to extract candle.exe and light.exe from WiX distribution.")

def generate_wix_wxs(wxs_path):
    print("[MSI Builder] Scanning files in dist/Music to build WiX XML...")
    if not os.path.exists(DIST_MUSIC):
        raise FileNotFoundError(f"Directory {DIST_MUSIC} does not exist. Build the executable first!")

    # Deterministic GUID generation for components
    UPGRADE_CODE = "a25eb944-71e8-4672-8f19-b7e61da0c9d1"
    
    lines = []
    lines.append('<?xml version="1.0" encoding="UTF-8"?>')
    lines.append('<Wix xmlns="http://schemas.microsoft.com/wix/2006/wi">')
    lines.append('  <Product Id="*" Name="Music" Language="1033" Version="1.0.0.0" Manufacturer="Jalastine Jegan" UpgradeCode="' + UPGRADE_CODE + '">')
    lines.append('    <Package InstallerVersion="200" Compressed="yes" InstallScope="perUser" />')
    lines.append('    <MajorUpgrade DowngradeErrorMessage="A newer version of Music is already installed." />')
    lines.append('    <MediaTemplate EmbedCab="yes" />')
    lines.append('')
    lines.append(f'    <Icon Id="AppIcon.ico" SourceFile="{ICON_ICO}" />')
    lines.append('    <Property Id="ARPPRODUCTICON" Value="AppIcon.ico" />')
    lines.append('    <Property Id="ARPHELPLINK" Value="https://github.com/jalastinejeganofficial/Music" />')
    lines.append('')
    lines.append('    <Directory Id="TARGETDIR" Name="SourceDir">')
    lines.append('      <Directory Id="LocalAppDataFolder">')
    lines.append('        <Directory Id="ProgramsFolder" Name="Programs">')
    lines.append('          <Directory Id="INSTALLFOLDER" Name="Music">')

    comp_refs = []
    file_id_counter = 1
    dir_id_counter = 1

    # Map directories
    # Root files first
    root_files = [f for f in os.listdir(DIST_MUSIC) if os.path.isfile(os.path.join(DIST_MUSIC, f))]
    for rf in root_files:
        src = os.path.join(DIST_MUSIC, rf)
        comp_id = f"CompRoot_{file_id_counter}"
        file_id = f"FileRoot_{file_id_counter}"
        file_guid = str(uuid.uuid5(uuid.NAMESPACE_DNS, f"music.root.{rf}"))
        file_id_counter += 1

        lines.append(f'            <Component Id="{comp_id}" Guid="{file_guid}">')
        if rf.lower() == "music.exe":
            lines.append(f'              <File Id="{file_id}" Source="{src}" KeyPath="yes">')
            lines.append('                <Shortcut Id="DesktopShortcut" Directory="DesktopFolder" Name="Music" WorkingDirectory="INSTALLFOLDER" Icon="AppIcon.ico" IconIndex="0" Advertise="yes" />')
            lines.append('                <Shortcut Id="StartMenuShortcut" Directory="ProgramMenuFolder" Name="Music" WorkingDirectory="INSTALLFOLDER" Icon="AppIcon.ico" IconIndex="0" Advertise="yes" />')
            lines.append('              </File>')
        else:
            lines.append(f'              <File Id="{file_id}" Source="{src}" KeyPath="yes" />')
        lines.append('            </Component>')
        comp_refs.append(comp_id)

    # Subdirectories recursively
    def traverse_dir(current_dir, parent_xml_indent):
        nonlocal dir_id_counter, file_id_counter
        entries = sorted(os.listdir(current_dir))
        for entry in entries:
            full_path = os.path.join(current_dir, entry)
            if os.path.isdir(full_path):
                sub_dir_id = f"Dir_{dir_id_counter}"
                dir_id_counter += 1
                lines.append(f'{parent_xml_indent}  <Directory Id="{sub_dir_id}" Name="{entry}">')
                
                # Check for files in this sub directory
                sub_entries = sorted(os.listdir(full_path))
                files = [se for se in sub_entries if os.path.isfile(os.path.join(full_path, se))]
                dirs = [se for se in sub_entries if os.path.isdir(os.path.join(full_path, se))]
                
                if files:
                    sub_comp_id = f"CompSub_{file_id_counter}"
                    sub_guid = str(uuid.uuid5(uuid.NAMESPACE_DNS, f"music.dir.{full_path}"))
                    lines.append(f'{parent_xml_indent}    <Component Id="{sub_comp_id}" Guid="{sub_guid}">')
                    for f in files:
                        f_path = os.path.join(full_path, f)
                        fid = f"File_{file_id_counter}"
                        file_id_counter += 1
                        lines.append(f'{parent_xml_indent}      <File Id="{fid}" Source="{f_path}" />')
                    lines.append(f'{parent_xml_indent}    </Component>')
                    comp_refs.append(sub_comp_id)

                if dirs:
                    traverse_dir(full_path, parent_xml_indent + "  ")

                lines.append(f'{parent_xml_indent}  </Directory>')

    traverse_dir(DIST_MUSIC, "          ")

    lines.append('          </Directory>')
    lines.append('        </Directory>')
    lines.append('      </Directory>')
    lines.append('      <Directory Id="DesktopFolder" Name="Desktop" />')
    lines.append('      <Directory Id="ProgramMenuFolder" Name="Programs" />')
    lines.append('    </Directory>')
    lines.append('')
    lines.append('    <Feature Id="MainFeature" Title="Music" Level="1">')
    for cr in comp_refs:
        lines.append(f'      <ComponentRef Id="{cr}" />')
    lines.append('    </Feature>')
    lines.append('  </Product>')
    lines.append('</Wix>')

    with open(wxs_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    print(f"[MSI Builder] Generated WiX specification at: {wxs_path} ({len(comp_refs)} components)")

def compile_msi(candle, light, wxs_path):
    print("[MSI Builder] Compiling WiX XML with candle.exe...")
    wixobj_path = os.path.splitext(wxs_path)[0] + ".wixobj"
    subprocess.run([candle, "-out", wixobj_path, wxs_path], check=True)

    print(f"[MSI Builder] Linking and creating MSI installer: {MSI_OUTPUT}...")
    subprocess.run([light, "-out", MSI_OUTPUT, "-sice:ICE38", "-sice:ICE64", "-sice:ICE91", wixobj_path], check=True)

    if os.path.exists(MSI_OUTPUT):
        size_mb = os.path.getsize(MSI_OUTPUT) / (1024 * 1024)
        print(f"=======================================================")
        print(f"✨ MSI Package successfully created!")
        print(f"   Output: {MSI_OUTPUT} ({size_mb:.1f} MB)")
        print(f"=======================================================")
        return True
    return False

if __name__ == "__main__":
    candle_exe, light_exe = ensure_wix_tools()
    wxs_file = os.path.join(BASE_DIR, "Music.wxs")
    generate_wix_wxs(wxs_file)
    compile_msi(candle_exe, light_exe, wxs_file)
