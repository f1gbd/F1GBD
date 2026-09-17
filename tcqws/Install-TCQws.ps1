<#
.SYNOPSIS
    Installation automatique de TCQws — FT4 / FT8, radiogrammes ADRASEC et alerte FLASH.

.DESCRIPTION
    Récupère la dernière release TCQws (tag « tcqws-v… ») en interrogeant l'API
    GitHub, télécharge TCQws.7z, vérifie le SHA-256, décompresse dans C:\TCQws
    et crée un raccourci sur le bureau.

    POURQUOI passer par l'API : le dépôt F1GBD héberge plusieurs applications
    (TCQ, TCQws, PDFteleporter…). Le lien releases/latest/download/… pointe sur
    la release mise en avant du dépôt, qui est celle de TCQ. Ce script liste
    les releases et prend la plus récente dont le tag commence par « tcqws- ».
    Il n'installe et ne modifie QUE C:\TCQws : une installation de TCQ
    existante n'est pas touchée.

    MISE À JOUR : les fichiers d'exploitation sont conservés (réglages
    ft4_config.json, log ADIF wsjtx_log*.adi, journal ft4_ALL.TXT, dossier
    radiogrammes\), et l'ancienne installation est sauvegardée à côté.

.AUTHOR
    Jean-Louis (F1GBD / F4JHW) — ADRASEC 77 — FNRASEC
.NOTES
    À lancer en PowerShell administrateur.
#>

#Requires -RunAsAdministrator

# =====================================================================
# Configuration
# =====================================================================
$RepoOwner      = "f1gbd"
$RepoName       = "F1GBD"
$ArchiveName    = "TCQws.7z"
$TagPrefix      = "tcqws-"
$InstallPath    = "C:\TCQws"
$ExecutableName = "TCQws.exe"
$ShortcutName   = "TCQws.lnk"
$TempPath       = $env:TEMP
$ApiReleasesUrl = "https://api.github.com/repos/$RepoOwner/$RepoName/releases?per_page=30"

# Fichiers et dossiers de l'utilisateur, repris d'une installation précédente
$AGarder = @("ft4_config.json", "ft4_ALL.TXT", "radiogrammes", "diag_tx")

# =====================================================================
# Affichage
# =====================================================================
function Write-Banner {
    Write-Host ""
    Write-Host "=====================================================" -ForegroundColor Cyan
    Write-Host "  TCQws — Installation automatique"                   -ForegroundColor Cyan
    Write-Host "  FT4 / FT8, radiogrammes ADRASEC, alerte FLASH"      -ForegroundColor Cyan
    Write-Host "  ADRASEC 77 / FNRASEC — F1GBD"                       -ForegroundColor Cyan
    Write-Host "=====================================================" -ForegroundColor Cyan
    Write-Host ""
}

function Write-Step { param([string]$m) Write-Host ">> $m" -ForegroundColor Yellow }
function Write-Ok   { param([string]$m) Write-Host "[OK] $m" -ForegroundColor Green }
function Write-Err  { param([string]$m) Write-Host "[ERREUR] $m" -ForegroundColor Red }

# =====================================================================
# 7-Zip
# =====================================================================
function Get-7ZipPath {
    $candidates = @(
        "$env:ProgramFiles\7-Zip\7z.exe",
        "${env:ProgramFiles(x86)}\7-Zip\7z.exe"
    )
    foreach ($p in $candidates) { if (Test-Path $p) { return $p } }
    return $null
}

function Install-7Zip {
    Write-Step "7-Zip n'est pas installé. Tentative d'installation via winget..."
    try {
        winget install -e --id 7zip.7zip --accept-package-agreements --accept-source-agreements --silent | Out-Null
        Start-Sleep -Seconds 2
        $sevenZip = Get-7ZipPath
        if ($sevenZip) { Write-Ok "7-Zip installé."; return $sevenZip }
        throw "7-Zip introuvable après installation."
    } catch {
        Write-Err "Impossible d'installer 7-Zip automatiquement."
        Write-Host "Installez-le depuis https://www.7-zip.org/ puis relancez." -ForegroundColor Yellow
        exit 1
    }
}

# =====================================================================
# Dernière release TCQws (et pas celle d'une autre application du dépôt)
# =====================================================================
function Get-LatestTcqwsRelease {
    Write-Step "Recherche de la dernière release TCQws sur GitHub..."
    try {
        $headers = @{ "User-Agent" = "TCQws-Installer" }
        $all = Invoke-RestMethod -Uri $ApiReleasesUrl -Headers $headers -ErrorAction Stop
        if (-not $all -or $all.Count -eq 0) {
            Write-Err "Aucune release trouvée sur $RepoOwner/$RepoName."
            exit 1
        }
        $releases = @($all | Where-Object { (-not $_.draft) -and ($_.tag_name -like "$TagPrefix*") })
        if ($releases.Count -eq 0) {
            # Repli : une release TCQws se reconnaît aussi à son archive TCQws.7z
            $releases = @($all | Where-Object {
                (-not $_.draft) -and ($_.assets | Where-Object { $_.name -eq $ArchiveName })
            })
        }
        if ($releases.Count -eq 0) {
            Write-Err "Aucune release TCQws trouvée."
            Write-Host "  Voir https://github.com/$RepoOwner/$RepoName/releases" -ForegroundColor Yellow
            exit 1
        }
        $r = $releases[0]
        Write-Ok "Release TCQws : $($r.tag_name) (publiée le $($r.published_at))"
        return $r
    } catch {
        Write-Err "Impossible de contacter l'API GitHub : $($_.Exception.Message)"
        exit 1
    }
}

function Find-TcqwsAsset {
    param($Release)
    $asset = $Release.assets | Where-Object { $_.name -eq $ArchiveName }
    if (-not $asset) {
        Write-Err "Archive '$ArchiveName' absente de la release $($Release.tag_name)."
        exit 1
    }
    return $asset
}

function Get-ExpectedSha256 {
    param($Release)
    if (-not $Release.body) { return $null }
    $m = [regex]::Matches($Release.body, "([a-fA-F0-9]{64})")
    if ($m.Count -gt 0) { return $m[0].Value.ToLower() }
    return $null
}

# =====================================================================
# Téléchargement et vérification
# =====================================================================
function Get-Archive {
    param([string]$Url, [string]$OutFile)
    Write-Step "Téléchargement de $ArchiveName..."
    try {
        $ProgressPreference = 'SilentlyContinue'
        Invoke-WebRequest -Uri $Url -OutFile $OutFile -UseBasicParsing -ErrorAction Stop
        $ProgressPreference = 'Continue'
        Write-Ok ("Téléchargé ({0:N1} Mo)" -f ((Get-Item $OutFile).Length / 1MB))
    } catch {
        Write-Err "Échec du téléchargement : $($_.Exception.Message)"
        exit 1
    }
}

function Confirm-Sha256 {
    param([string]$FilePath, [string]$ExpectedHash)
    Write-Step "Vérification du SHA-256..."
    $actual = (Get-FileHash -Algorithm SHA256 -Path $FilePath).Hash.ToLower()
    if (-not $ExpectedHash) {
        Write-Host "  SHA-256 attendu absent de la release." -ForegroundColor DarkYellow
        Write-Host "  SHA-256 calculé : $actual" -ForegroundColor DarkYellow
        $rep = Read-Host "Continuer sans vérification ? [O/N]"
        if ($rep -notmatch '^[OoYy]') { Write-Err "Installation annulée."; exit 1 }
        return
    }
    if ($actual -ne $ExpectedHash.ToLower()) {
        Write-Err "SHA-256 ne correspond pas !"
        Write-Host "  Attendu : $ExpectedHash" -ForegroundColor Red
        Write-Host "  Calculé : $actual"       -ForegroundColor Red
        exit 1
    }
    Write-Ok "SHA-256 vérifié."
}

# =====================================================================
# Installation (C:\TCQws uniquement)
# =====================================================================
function Save-UserFiles {
    param([string]$DestPath)
    if (-not (Test-Path $DestPath)) { return $null }
    $garde = Join-Path $TempPath ("TCQws_garde_" + (Get-Date -Format 'yyyyMMdd_HHmmss'))
    New-Item -ItemType Directory -Path $garde -Force | Out-Null
    $n = 0
    foreach ($nom in $AGarder) {
        $src = Join-Path $DestPath $nom
        if (Test-Path $src) { Copy-Item $src $garde -Recurse -Force; $n++ }
    }
    Get-ChildItem $DestPath -Filter "wsjtx_log*.adi" -ErrorAction SilentlyContinue | ForEach-Object {
        Copy-Item $_.FullName $garde -Force; $n++
    }
    if ($n -gt 0) { Write-Ok "$n élément(s) d'exploitation mis de côté." }
    return $garde
}

function Restore-UserFiles {
    param([string]$Garde, [string]$DestPath)
    if (-not $Garde -or -not (Test-Path $Garde)) { return }
    Get-ChildItem $Garde -Force | ForEach-Object {
        Copy-Item $_.FullName (Join-Path $DestPath $_.Name) -Recurse -Force
    }
    Write-Ok "Réglages, log ADIF, journal et radiogrammes restaurés."
    Remove-Item $Garde -Recurse -Force -ErrorAction SilentlyContinue
}

function Expand-TcqwsArchive {
    param([string]$ArchivePath, [string]$DestPath, [string]$SevenZipExe)
    Write-Step "Installation dans $DestPath ..."

    if (Test-Path $DestPath) {
        $backup = "$DestPath.backup_$(Get-Date -Format 'yyyyMMdd_HHmmss')"
        Write-Host "  Installation existante : sauvegarde dans $backup" -ForegroundColor DarkYellow
        try {
            Rename-Item -Path $DestPath -NewName (Split-Path $backup -Leaf) -Force
        } catch {
            Write-Err "Impossible de sauvegarder l'installation existante : $($_.Exception.Message)"
            Write-Host "Fermez TCQws s'il est ouvert, puis relancez le script." -ForegroundColor Yellow
            exit 1
        }
    }

    & $SevenZipExe x $ArchivePath "-oC:\" -y | Out-Null
    if ($LASTEXITCODE -ne 0) { Write-Err "Échec de la décompression (code $LASTEXITCODE)."; exit 1 }
    if (-not (Test-Path (Join-Path $DestPath $ExecutableName))) {
        Write-Err "$ExecutableName introuvable après décompression."
        exit 1
    }
    Write-Ok "Décompression terminée."
}

function New-DesktopShortcut {
    param([string]$TargetPath, [string]$ShortcutPath)
    Write-Step "Création du raccourci sur le bureau..."
    try {
        $WshShell = New-Object -ComObject WScript.Shell
        $s = $WshShell.CreateShortcut($ShortcutPath)
        $s.TargetPath       = $TargetPath
        $s.WorkingDirectory = Split-Path $TargetPath -Parent
        $s.Description      = "TCQws - FT4/FT8, radiogrammes ADRASEC, alerte FLASH"
        $s.Save()
        Write-Ok "Raccourci créé : $ShortcutPath"
    } catch {
        Write-Host "  Raccourci impossible : $($_.Exception.Message)" -ForegroundColor DarkYellow
    }
}

# =====================================================================
# Programme principal
# =====================================================================
Write-Banner

$sevenZip = Get-7ZipPath
if (-not $sevenZip) { $sevenZip = Install-7Zip }
Write-Ok "7-Zip : $sevenZip"

$release      = Get-LatestTcqwsRelease
$asset        = Find-TcqwsAsset -Release $release
$expectedHash = Get-ExpectedSha256 -Release $release
$tag          = $release.tag_name

Write-Host ""
Write-Host "  Version : $tag" -ForegroundColor White
Write-Host "  Taille  : $([math]::Round($asset.size/1MB,1)) Mo" -ForegroundColor White
Write-Host "  Date    : $($release.published_at)" -ForegroundColor White
Write-Host ""

$archivePath = Join-Path $TempPath $ArchiveName
Get-Archive -Url $asset.browser_download_url -OutFile $archivePath
Confirm-Sha256 -FilePath $archivePath -ExpectedHash $expectedHash

$garde = Save-UserFiles -DestPath $InstallPath
Expand-TcqwsArchive -ArchivePath $archivePath -DestPath $InstallPath -SevenZipExe $sevenZip
Restore-UserFiles -Garde $garde -DestPath $InstallPath

$desktop      = [Environment]::GetFolderPath("Desktop")
$shortcutPath = Join-Path $desktop $ShortcutName
$exePath      = Join-Path $InstallPath $ExecutableName
New-DesktopShortcut -TargetPath $exePath -ShortcutPath $shortcutPath

Write-Step "Nettoyage du fichier temporaire..."
Remove-Item -Path $archivePath -Force -ErrorAction SilentlyContinue
Write-Ok "Terminé."

Write-Host ""
Write-Host "=====================================================" -ForegroundColor Green
Write-Host "  Installation TCQws $tag terminée !"                  -ForegroundColor Green
Write-Host "=====================================================" -ForegroundColor Green
Write-Host ""
Write-Host "  Dossier    : $InstallPath"  -ForegroundColor White
Write-Host "  Exécutable : $exePath"      -ForegroundColor White
Write-Host "  Raccourci  : $shortcutPath" -ForegroundColor White
Write-Host ""
Write-Host "  Premier essai sans radio :" -ForegroundColor Yellow
Write-Host "    $exePath --demo"          -ForegroundColor Yellow
Write-Host ""
Write-Host "  Mode d'emploi : $InstallPath\README_TCQws.md" -ForegroundColor Cyan
Write-Host "  Documentation : https://github.com/$RepoOwner/$RepoName/tree/master/tcqws" -ForegroundColor Cyan
Write-Host ""
Write-Host "  TCQ n'a pas été modifié (installation séparée dans C:\TCQ)." -ForegroundColor DarkGray
Write-Host ""
Write-Host "  73 de F1GBD !" -ForegroundColor Magenta
Write-Host ""
