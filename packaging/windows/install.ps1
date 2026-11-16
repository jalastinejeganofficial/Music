# ==============================================================================
# Music App - Windows Package Manager & Automated Installer
# Usage:
#   powershell -ExecutionPolicy Bypass -File install.ps1
# Or one-liner from the web:
#   irm https://raw.githubusercontent.com/jalastinejeganofficial/Music/main/packaging/windows/install.ps1 | iex
# ==============================================================================

[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12 -bor [Net.SecurityProtocolType]::Tls13

Write-Host "=====================================================" -ForegroundColor Cyan
Write-Host "   🎵 Music Desktop - Windows Package Manager        " -ForegroundColor Yellow
Write-Host "=====================================================" -ForegroundColor Cyan

$Repo = "jalastinejeganofficial/Music"
$DownloadUrl = "https://github.com/$Repo/releases/latest/download/Music-Windows-x64.zip"
$InstallDir = Join-Path $env:LOCALAPPDATA "Programs\Music"
$DesktopDir = [Environment]::GetFolderPath('Desktop')
$ProgramsDir = [Environment]::GetFolderPath('Programs')
$TempZip = Join-Path $env:TEMP "Music-Windows-x64.zip"

# Check if local zip exists first (offline or development install)
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path -ErrorAction SilentlyContinue
if (-not $ScriptDir) { $ScriptDir = (Get-Location).Path }

$LocalZipCandidates = @(
    "$ScriptDir\Music-Windows-x64.zip",
    "$ScriptDir\..\..\dist\Music-Windows-x64.zip",
    "$PWD\dist\Music-Windows-x64.zip",
    "$PWD\Music-Windows-x64.zip"
)

$FoundLocalZip = $null
foreach ($cand in $LocalZipCandidates) {
    if (Test-Path $cand) {
        $FoundLocalZip = (Resolve-Path $cand).Path
        break
    }
}

if ($FoundLocalZip) {
    Write-Host "[1/4] Found local package: $FoundLocalZip" -ForegroundColor Green
    Copy-Item -Path $FoundLocalZip -Destination $TempZip -Force
} else {
    Write-Host "[1/4] Downloading latest Music package from GitHub..." -ForegroundColor Cyan
    Write-Host "      URL: $DownloadUrl" -ForegroundColor DarkGray
    try {
        $wc = New-Object System.Net.WebClient
        $wc.DownloadFile($DownloadUrl, $TempZip)
        Write-Host "      Download completed successfully." -ForegroundColor Green
    } catch {
        Write-Host "      [!] Failed to download from GitHub releases ($($_))." -ForegroundColor Yellow
        Write-Host "      Checking for local dist/Music folder..." -ForegroundColor Yellow
        $LocalDistMusic = Join-Path (Get-Location) "dist\Music"
        if (Test-Path $LocalDistMusic) {
            Write-Host "      Using local dist/Music folder." -ForegroundColor Green
            if (Test-Path $InstallDir) { Remove-Item -Recurse -Force $InstallDir -ErrorAction SilentlyContinue }
            New-Item -ItemType Directory -Force -Path $InstallDir | Out-Null
            Copy-Item -Path "$LocalDistMusic\*" -Destination $InstallDir -Recurse -Force
            $InstalledFromFolder = $true
        } else {
            Write-Error "Could not download package and no local build was found. Please ensure internet access or run build_windows.bat first."
            exit 1
        }
    }
}

# Step 2: Extract to Programs/Music
if (-not $InstalledFromFolder) {
    Write-Host "[2/4] Installing application to: $InstallDir" -ForegroundColor Cyan
    if (Test-Path $InstallDir) {
        # Terminate any running instance before overwriting
        Get-Process Music -ErrorAction SilentlyContinue | Stop-Process -Force -ErrorAction SilentlyContinue
        Start-Sleep -Seconds 1
        Remove-Item -Recurse -Force $InstallDir -ErrorAction SilentlyContinue
    }
    New-Item -ItemType Directory -Force -Path $InstallDir | Out-Null
    
    # Extract
    $ExtractTemp = Join-Path $env:TEMP "MusicExtract_$(Get-Random)"
    Expand-Archive -Path $TempZip -DestinationPath $ExtractTemp -Force
    
    # If the zip extracted into a subfolder 'Music', copy its contents
    if (Test-Path (Join-Path $ExtractTemp "Music\Music.exe")) {
        Copy-Item -Path (Join-Path $ExtractTemp "Music\*") -Destination $InstallDir -Recurse -Force
    } elseif (Test-Path (Join-Path $ExtractTemp "Music.exe")) {
        Copy-Item -Path (Join-Path $ExtractTemp "*") -Destination $InstallDir -Recurse -Force
    } else {
        # Fallback find Music.exe anywhere in extracted tree
        $foundExe = Get-ChildItem -Path $ExtractTemp -Filter "Music.exe" -Recurse | Select-Object -First 1
        if ($foundExe) {
            Copy-Item -Path (Join-Path $foundExe.DirectoryName "*") -Destination $InstallDir -Recurse -Force
        }
    }
    Remove-Item -Recurse -Force $ExtractTemp -ErrorAction SilentlyContinue
    Remove-Item -Force $TempZip -ErrorAction SilentlyContinue
    Write-Host "      Files extracted successfully." -ForegroundColor Green
}

$ExePath = Join-Path $InstallDir "Music.exe"
if (-not (Test-Path $ExePath)) {
    Write-Error "Music.exe was not found in $InstallDir!"
    exit 1
}

# Step 3: Create Desktop & Start Menu Shortcuts
Write-Host "[3/4] Creating Desktop and Start Menu shortcuts..." -ForegroundColor Cyan
try {
    $WshShell = New-Object -ComObject WScript.Shell
    
    # Desktop Shortcut
    $DesktopShortcut = Join-Path $DesktopDir "Music.lnk"
    $Shortcut = $WshShell.CreateShortcut($DesktopShortcut)
    $Shortcut.TargetPath = $ExePath
    $Shortcut.WorkingDirectory = $InstallDir
    $Shortcut.IconLocation = "$ExePath,0"
    $Shortcut.Description = "Music - YouTube Music Player & Scraper"
    $Shortcut.Save()
    Write-Host "      [+] Desktop shortcut: $DesktopShortcut" -ForegroundColor Green
    
    # Start Menu Shortcut
    $StartMenuShortcut = Join-Path $ProgramsDir "Music.lnk"
    $Shortcut2 = $WshShell.CreateShortcut($StartMenuShortcut)
    $Shortcut2.TargetPath = $ExePath
    $Shortcut2.WorkingDirectory = $InstallDir
    $Shortcut2.IconLocation = "$ExePath,0"
    $Shortcut2.Description = "Music - YouTube Music Player & Scraper"
    $Shortcut2.Save()
    Write-Host "      [+] Start Menu shortcut: $StartMenuShortcut" -ForegroundColor Green
} catch {
    Write-Host "      [!] Shortcut creation warning: $_" -ForegroundColor Yellow
}

# Step 4: Automatically launch Frontend + Backend Software
Write-Host "[4/4] 🚀 Launching Music desktop application..." -ForegroundColor Green
Write-Host "      Frontend and Backend starting automatically..." -ForegroundColor DarkGray

Start-Process -FilePath $ExePath -WorkingDirectory $InstallDir

Write-Host ""
Write-Host "✨ Installation complete! Music is now running." -ForegroundColor Cyan
Write-Host "=====================================================" -ForegroundColor Cyan
