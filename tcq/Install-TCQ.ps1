<#
.SYNOPSIS
    Installation automatique de TCQ — Plateforme de communications radio multi-modes
.DESCRIPTION
    Récupère la dernière release contenant TCQ.7z (en interrogeant l'API GitHub),
    télécharge l'archive, vérifie le SHA-256, décompresse dans C:\TCQ et crée un
    raccourci sur le bureau.

    POURQUOI cette logique : le dépôt F1GBD héberge plusieurs applications (TCQ,
    IAbrain, etc.). Le lien `releases/latest/download/TCQ.7z` ne fonctionne que
    si la release marquée "Latest" est une release TCQ — sinon GitHub retourne
    404. Ce script contourne le problème en listant toutes les releases via
    l'API GitHub et en sélectionnant la plus récente qui contient TCQ.7z.

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
$TagPrefix       = "tcq-"
$InstallPath     = "C:\TCQ"
$ExecutableName  = "TCQ.exe"
$ShortcutName    = "TCQ.lnk"
$TempPath        = $env:TEMP
$ApiReleasesUrl  = "https://api.github.com/repos/$RepoOwner/$RepoName/releases?per_page=30"

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
# Recherche de la dernière release contenant TCQ.7z
# (PAS de releases/latest qui retourne la release "Latest" globale du dépôt)
# =====================================================================
function Get-LatestTCQRelease {
    Write-Step "Recherche de la dernière release TCQ sur GitHub..."
    try {
        $headers = @{ "User-Agent" = "TCQ-Installer" }
        $allReleases = Invoke-RestMethod -Uri $ApiReleasesUrl -Headers $headers -ErrorAction Stop

        if (-not $allReleases -or $allReleases.Count -eq 0) {
            Write-Err "Aucune release trouvée sur le dépôt $RepoOwner/$RepoName."
            exit 1
        }

        # Filtre principal : releases non-draft dont le tag commence par "tcq-"
        # (cohérent avec la convention de nommage : tcq-v10.10.0, tcq-v10.11.0, etc.)
        $tcqReleases = @($allReleases | Where-Object {
            (-not $_.draft) -and ($_.tag_name -like "$TagPrefix*")
        })

        # Fallback : si aucune release préfixée n'est trouvée (ex: anciennes releases v10.x non migrées),
        # on cherche par nom d'asset TCQ.7z pour assurer la compatibilité ascendante.
        if ($tcqReleases.Count -eq 0) {
            Write-Host "  (Aucune release avec préfixe '$TagPrefix' — recherche par nom d'asset...)" -ForegroundColor DarkYellow
            $tcqReleases = @($allReleases | Where-Object {
                (-not $_.draft) -and ($_.assets | Where-Object { $_.name -eq $ArchiveName })
            })
        }

        if ($tcqReleases.Count -eq 0) {
            Write-Err "Aucune release TCQ trouvée."
            Write-Host "  Vérifiez sur https://github.com/$RepoOwner/$RepoName/releases" -ForegroundColor Yellow
            exit 1
        }

        $latestTcq = $tcqReleases[0]
        Write-Ok "Release TCQ trouvée : $($latestTcq.tag_name) (publiée le $($latestTcq.published_at))"
        return $latestTcq
    } catch {
        Write-Err "Impossible de contacter l'API GitHub : $($_.Exception.Message)"
        exit 1
    }
}

function Find-TCQAsset {
    param($Release)
    $asset = $Release.assets | Where-Object { $_.name -eq $ArchiveName }
    if (-not $asset) {
        Write-Err "Archive '$ArchiveName' introuvable dans la release $($Release.tag_name)."
        exit 1
    }
    return $asset
}

function Get-ExpectedSha256 {
    param($Release)
    $body = $Release.body
    if (-not $body) { return $null }
    $matches = [regex]::Matches($body, "([a-fA-F0-9]{64})")
    if ($matches.Count -gt 0) {
        return $matches[0].Value.ToLower()
    }
    return $null
}

# =====================================================================
# Téléchargement
# =====================================================================
function Download-Archive {
    param([string]$Url, [string]$OutFile)
    Write-Step "Téléchargement de $ArchiveName..."
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

# 2) Récupération de la release TCQ (filtrée parmi toutes les releases du dépôt)
$release      = Get-LatestTCQRelease
$asset        = Find-TCQAsset -Release $release
$expectedHash = Get-ExpectedSha256 -Release $release
$tag          = $release.tag_name

Write-Host ""
Write-Host "  Version       : $tag"           -ForegroundColor White
Write-Host "  Taille        : $([math]::Round($asset.size/1MB,1)) Mo" -ForegroundColor White
Write-Host "  Date          : $($release.published_at)" -ForegroundColor White
Write-Host ""

# 3) Téléchargement via l'URL spécifique de cette release (pas releases/latest)
$archivePath = Join-Path $TempPath $ArchiveName
Download-Archive -Url $asset.browser_download_url -OutFile $archivePath

# 4) Vérification SHA-256
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
Write-Host ""
Write-Host "=====================================================" -ForegroundColor Green
Write-Host "  Installation TCQ $tag terminée avec succès !"        -ForegroundColor Green
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
