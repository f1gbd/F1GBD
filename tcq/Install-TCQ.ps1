<#
.SYNOPSIS
    Installation automatique de TCQ — Plateforme de communications radio multi-modes
.DESCRIPTION
    Télécharge la dernière version de TCQ.7z depuis GitHub via le lien officiel
    releases/latest/download/TCQ.7z, vérifie le SHA-256, décompresse l'archive
    dans C:\TCQ et crée un raccourci sur le bureau.

    NOTE : GitHub redirige automatiquement releases/latest/download/<asset> vers
    la dernière release contenant cet asset précis. Le dépôt F1GBD héberge
    plusieurs applications (TCQ, IAbrain, etc.) — chacune utilise son propre
    nom d'asset, donc le téléchargement de TCQ.7z trouve toujours la dernière
    release TCQ, indépendamment des autres applications publiées entre-temps.

.AUTHOR
    Jean-Louis (F1GBD / F4JHW) — ADRASEC 77 — FNRASEC
.NOTES
    Doit être lancé en PowerShell administrateur.
#>

#Requires -RunAsAdministrator

# =====================================================================
# Configuration
# =====================================================================
$RepoOwner       = "f1gbd"
$RepoName        = "F1GBD"
$ArchiveName     = "TCQ.7z"
$InstallPath     = "C:\TCQ"
$ExecutableName  = "TCQ.exe"
$ShortcutName    = "TCQ.lnk"
$TempPath        = $env:TEMP

# Lien officiel : GitHub redirige automatiquement vers la dernière release contenant TCQ.7z
$DownloadUrl     = "https://github.com/$RepoOwner/$RepoName/releases/latest/download/$ArchiveName"
# API GitHub pour récupérer les métadonnées (version, SHA-256 dans le corps de la release)
$ApiLatestUrl    = "https://api.github.com/repos/$RepoOwner/$RepoName/releases/latest"

# =====================================================================
# Affichage
# =====================================================================
function Write-Banner {
    Write-Host ""
    Write-Host "=====================================================" -ForegroundColor Cyan
    Write-Host "  TCQ — Installation automatique"                     -ForegroundColor Cyan
    Write-Host "  Plateforme de communications radio multi-modes"     -ForegroundColor Cyan
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
        if ($sevenZip) {
            Write-Ok "7-Zip installé."
            return $sevenZip
        }
        throw "7-Zip introuvable après installation."
    } catch {
        Write-Err "Impossible d'installer 7-Zip automatiquement."
        Write-Host "Veuillez l'installer manuellement depuis https://www.7-zip.org/" -ForegroundColor Yellow
        exit 1
    }
}

# =====================================================================
# Récupération de la version et du SHA-256 attendu via API GitHub
# (lecture seule, juste pour info à l'utilisateur et vérification d'intégrité)
# =====================================================================
function Get-LatestTCQReleaseInfo {
    Write-Step "Récupération des informations de la dernière release TCQ..."
    try {
        $headers = @{ "User-Agent" = "TCQ-Installer" }
        # On récupère les 30 dernières releases pour trouver celle qui contient TCQ.7z
        # (peut ne pas être la "Latest" globale du dépôt si une autre appli a été publiée après)
        $allReleases = Invoke-RestMethod -Uri "https://api.github.com/repos/$RepoOwner/$RepoName/releases?per_page=30" -Headers $headers -ErrorAction Stop

        $tcqRelease = $allReleases | Where-Object {
            -not $_.draft -and ($_.assets | Where-Object { $_.name -eq $ArchiveName })
        } | Select-Object -First 1

        if (-not $tcqRelease) {
            Write-Host "  (Aucune release TCQ trouvée dans les 30 dernières — utilisation du téléchargement direct sans vérification SHA-256)" -ForegroundColor DarkYellow
            return $null
        }

        # Extraction du SHA-256 dans le corps de la release (64 caractères hex)
        $sha256 = $null
        if ($tcqRelease.body) {
            $matches = [regex]::Matches($tcqRelease.body, "([a-fA-F0-9]{64})")
            if ($matches.Count -gt 0) {
                $sha256 = $matches[0].Value.ToLower()
            }
        }

        return [PSCustomObject]@{
            Tag       = $tcqRelease.tag_name
            Date      = $tcqRelease.published_at
            Sha256    = $sha256
            SizeMB    = [math]::Round(($tcqRelease.assets | Where-Object { $_.name -eq $ArchiveName }).size / 1MB, 1)
        }
    } catch {
        Write-Host "  (Impossible de contacter l'API GitHub : $($_.Exception.Message))" -ForegroundColor DarkYellow
        Write-Host "  Le téléchargement direct sera tenté sans vérification SHA-256 préalable." -ForegroundColor DarkYellow
        return $null
    }
}

# =====================================================================
# Téléchargement
# =====================================================================
function Download-Archive {
    param([string]$Url, [string]$OutFile)
    Write-Step "Téléchargement de $ArchiveName..."
    Write-Host "  Source : $Url" -ForegroundColor DarkGray
    try {
        $ProgressPreference = 'SilentlyContinue'
        Invoke-WebRequest -Uri $Url -OutFile $OutFile -UseBasicParsing -ErrorAction Stop
        $ProgressPreference = 'Continue'
        $size = (Get-Item $OutFile).Length / 1MB
        Write-Ok ("Téléchargé ({0:N1} Mo)" -f $size)
    } catch {
        Write-Err "Échec du téléchargement : $($_.Exception.Message)"
        exit 1
    }
}

# =====================================================================
# Vérification SHA-256
# =====================================================================
function Verify-Sha256 {
    param([string]$FilePath, [string]$ExpectedHash)
    Write-Step "Vérification du SHA-256..."
    $actual = (Get-FileHash -Algorithm SHA256 -Path $FilePath).Hash.ToLower()
    if (-not $ExpectedHash) {
        Write-Host "  SHA-256 attendu non trouvé dans la release." -ForegroundColor DarkYellow
        Write-Host "  SHA-256 calculé : $actual" -ForegroundColor DarkYellow
        $rep = Read-Host "Continuer sans vérification ? [O/N]"
        if ($rep -notmatch '^[OoYy]') {
            Write-Err "Installation annulée par l'utilisateur."
            exit 1
        }
        return
    }
    if ($actual -ne $ExpectedHash.ToLower()) {
        Write-Err "SHA-256 ne correspond pas !"
        Write-Host "  Attendu  : $ExpectedHash" -ForegroundColor Red
        Write-Host "  Calculé  : $actual"       -ForegroundColor Red
        Write-Host "L'archive est peut-être corrompue ou altérée. Installation annulée." -ForegroundColor Red
        exit 1
    }
    Write-Ok "SHA-256 vérifié."
}

# =====================================================================
# Décompression
# =====================================================================
function Extract-Archive {
    param([string]$ArchivePath, [string]$DestPath, [string]$SevenZipExe)
    Write-Step "Décompression dans C:\ ..."

    if (Test-Path $DestPath) {
        $backup = "$DestPath.backup_$(Get-Date -Format 'yyyyMMdd_HHmmss')"
        Write-Host "  Installation existante détectée, sauvegarde dans $backup" -ForegroundColor DarkYellow
        try {
            Rename-Item -Path $DestPath -NewName (Split-Path $backup -Leaf) -Force
        } catch {
            Write-Err "Impossible de sauvegarder l'installation existante : $($_.Exception.Message)"
            Write-Host "Fermez TCQ s'il est en cours d'exécution puis relancez le script." -ForegroundColor Yellow
            exit 1
        }
    }

    & $SevenZipExe x $ArchivePath "-oC:\" -y | Out-Null
    if ($LASTEXITCODE -ne 0) {
        Write-Err "Échec de la décompression (code $LASTEXITCODE)."
        exit 1
    }

    if (-not (Test-Path (Join-Path $DestPath $ExecutableName))) {
        Write-Err "L'exécutable $ExecutableName est introuvable après décompression."
        exit 1
    }

    Write-Ok "Décompression terminée."
}

# =====================================================================
# Raccourci bureau
# =====================================================================
function Create-Shortcut {
    param([string]$TargetPath, [string]$ShortcutPath)
    Write-Step "Création du raccourci sur le bureau..."
    try {
        $WshShell = New-Object -ComObject WScript.Shell
        $shortcut = $WshShell.CreateShortcut($ShortcutPath)
        $shortcut.TargetPath       = $TargetPath
        $shortcut.WorkingDirectory = Split-Path $TargetPath -Parent
        $shortcut.Description      = "TCQ - Plateforme communications radio multi-modes"
        $shortcut.Save()
        Write-Ok "Raccourci créé : $ShortcutPath"
    } catch {
        Write-Host "  Impossible de créer le raccourci : $($_.Exception.Message)" -ForegroundColor DarkYellow
    }
}

# =====================================================================
# Programme principal
# =====================================================================
Write-Banner

# 1) 7-Zip
$sevenZip = Get-7ZipPath
if (-not $sevenZip) { $sevenZip = Install-7Zip }
Write-Ok "7-Zip détecté : $sevenZip"

# 2) Infos de la release (version, SHA-256 attendu)
$releaseInfo = Get-LatestTCQReleaseInfo
if ($releaseInfo) {
    Write-Host ""
    Write-Host "  Version       : $($releaseInfo.Tag)"   -ForegroundColor White
    Write-Host "  Taille        : $($releaseInfo.SizeMB) Mo" -ForegroundColor White
    Write-Host "  Date          : $($releaseInfo.Date)" -ForegroundColor White
    if ($releaseInfo.Sha256) {
        Write-Host "  SHA-256       : $($releaseInfo.Sha256)" -ForegroundColor DarkGray
    }
    Write-Host ""
}

# 3) Téléchargement via le lien direct GitHub (qui redirige vers la dernière release contenant TCQ.7z)
$archivePath = Join-Path $TempPath $ArchiveName
Download-Archive -Url $DownloadUrl -OutFile $archivePath

# 4) Vérification SHA-256
$expectedHash = if ($releaseInfo) { $releaseInfo.Sha256 } else { $null }
Verify-Sha256 -FilePath $archivePath -ExpectedHash $expectedHash

# 5) Décompression
Extract-Archive -ArchivePath $archivePath -DestPath $InstallPath -SevenZipExe $sevenZip

# 6) Raccourci bureau
$desktop      = [Environment]::GetFolderPath("Desktop")
$shortcutPath = Join-Path $desktop $ShortcutName
$exePath      = Join-Path $InstallPath $ExecutableName
Create-Shortcut -TargetPath $exePath -ShortcutPath $shortcutPath

# 7) Nettoyage
Write-Step "Nettoyage du fichier temporaire..."
Remove-Item -Path $archivePath -Force -ErrorAction SilentlyContinue
Write-Ok "Terminé."

# =====================================================================
# Résumé final
# =====================================================================
$installedTag = if ($releaseInfo) { " $($releaseInfo.Tag)" } else { "" }
Write-Host ""
Write-Host "=====================================================" -ForegroundColor Green
Write-Host "  Installation TCQ$installedTag terminée avec succès !" -ForegroundColor Green
Write-Host "=====================================================" -ForegroundColor Green
Write-Host ""
Write-Host "  Dossier   : $InstallPath"               -ForegroundColor White
Write-Host "  Exécutable: $exePath"                   -ForegroundColor White
Write-Host "  Raccourci : $shortcutPath"              -ForegroundColor White
Write-Host ""
Write-Host "  Pour lancer TCQ :" -ForegroundColor Yellow
Write-Host "    - Double-cliquez sur le raccourci du bureau, ou" -ForegroundColor Yellow
Write-Host "    - Exécutez : $exePath"                            -ForegroundColor Yellow
Write-Host ""
Write-Host "  Documentation : https://github.com/$RepoOwner/$RepoName/tree/master/tcq" -ForegroundColor Cyan
Write-Host ""
Write-Host "  73 de F1GBD !" -ForegroundColor Magenta
Write-Host ""
