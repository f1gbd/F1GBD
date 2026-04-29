<#
.SYNOPSIS
    Installation automatique d'IAbrain pour les opérateurs ADRASEC.

.DESCRIPTION
    Script tout-en-un qui installe :
      1. Ollama (moteur d'inférence local)
      2. Les modèles requis (nomic-embed-text, llama3.2:3b, qwen2.5:7b, bge-m3)
      3. IAbrain.exe (téléchargé depuis GitHub Releases)
      4. Les variables d'environnement Ollama optimales
      5. Un raccourci sur le bureau et dans le menu Démarrer

    Le script est conçu pour fonctionner en mode silencieux : il pose
    aucune question et installe tout avec des défauts sains.

.PARAMETER InstallPath
    Dossier d'installation d'IAbrain (défaut : C:\IAbrain).

.PARAMETER SkipModels
    Ne pas pull les modèles (utile si déjà installés sur un autre serveur Ollama).

.PARAMETER SkipFirewall
    Ne pas ouvrir le port 11434 dans le pare-feu Windows.

.PARAMETER Force
    Forcer la réinstallation même si IAbrain est déjà présent.

.EXAMPLE
    .\Install-IAbrain.ps1
    Installation complète avec les défauts.

.EXAMPLE
    iwr https://github.com/f1gbd/F1GBD/raw/master/iabrain/Install-IAbrain.ps1 | iex
    Installation en une ligne directement depuis GitHub.

.NOTES
    Auteur  : Jean-Louis (F1GBD / F4JHW) - ADRASEC 77
    Version : 1.33.2
    Licence : Usage ADRASEC / FNRASEC

    Prérequis : Windows 10/11, PowerShell 5.1+, droits administrateur.
#>

[CmdletBinding()]
param(
    [string]$InstallPath = "C:\IAbrain",
    [switch]$SkipModels,
    [switch]$SkipFirewall,
    [switch]$Force
)

$ErrorActionPreference = "Stop"
$ProgressPreference    = "Continue"
$script:LogFile        = Join-Path $env:TEMP "IAbrain_Install_$(Get-Date -Format 'yyyyMMdd_HHmmss').log"

# ============================================================
#  CONSTANTES
# ============================================================
$IABRAIN_VERSION       = "1.33.2"
$IABRAIN_ARCHIVE_URL   = "https://github.com/f1gbd/F1GBD/releases/latest/download/IAbrain.7z"
$IABRAIN_REPO_URL      = "https://github.com/f1gbd/F1GBD/tree/master/iabrain"
$OLLAMA_INSTALLER_URL  = "https://ollama.com/download/OllamaSetup.exe"
$OLLAMA_API_URL        = "http://localhost:11434"

# Modèles à installer
$MODELS = @(
    @{ Name = "nomic-embed-text"; Size = "274 Mo"; Role = "Embedder RAG (obligatoire)" },
    @{ Name = "llama3.2:3b";      Size = "2.0 Go"; Role = "Modèle léger (auto-route)" },
    @{ Name = "qwen2.5:7b";       Size = "4.7 Go"; Role = "Modèle complexe (RAG + analyse)" },
    @{ Name = "bge-m3";           Size = "1.2 Go"; Role = "Reranking RAG (qualité +)" }
)

# Variables d'environnement Ollama optimales
$OLLAMA_ENV = @{
    "OLLAMA_KEEP_ALIVE"        = "30m"
    "OLLAMA_FLASH_ATTENTION"   = "1"
    "OLLAMA_KV_CACHE_TYPE"     = "q8_0"
    "OLLAMA_NUM_PARALLEL"      = "1"
    "OLLAMA_MAX_LOADED_MODELS" = "2"
}

# ============================================================
#  HELPERS
# ============================================================
function Write-Log {
    param(
        [string]$Message,
        [ValidateSet("INFO","OK","WARN","ERROR","STEP")]
        [string]$Level = "INFO"
    )
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    $line = "[$timestamp] [$Level] $Message"
    Add-Content -Path $script:LogFile -Value $line -Encoding UTF8

    switch ($Level) {
        "OK"    { Write-Host "  ✓ $Message" -ForegroundColor Green }
        "WARN"  { Write-Host "  ⚠ $Message" -ForegroundColor Yellow }
        "ERROR" { Write-Host "  ✗ $Message" -ForegroundColor Red }
        "STEP"  { Write-Host "`n━━━ $Message ━━━" -ForegroundColor Cyan }
        default { Write-Host "  · $Message" -ForegroundColor Gray }
    }
}

function Test-Administrator {
    $current = [Security.Principal.WindowsIdentity]::GetCurrent()
    $principal = [Security.Principal.WindowsPrincipal]::new($current)
    return $principal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
}

function Invoke-AdminElevation {
    Write-Host "`n⚠ Le script a besoin de droits administrateur." -ForegroundColor Yellow
    Write-Host "Relance automatique en mode élévé...`n" -ForegroundColor Yellow

    $args = @()
    if ($InstallPath -ne "C:\IAbrain") { $args += "-InstallPath", "`"$InstallPath`"" }
    if ($SkipModels)                   { $args += "-SkipModels" }
    if ($SkipFirewall)                 { $args += "-SkipFirewall" }
    if ($Force)                        { $args += "-Force" }

    $argList = "-NoProfile -ExecutionPolicy Bypass -File `"$PSCommandPath`" $($args -join ' ')"
    Start-Process powershell -Verb RunAs -ArgumentList $argList
    exit 0
}

function Test-CommandExists {
    param([string]$Command)
    $oldPref = $ErrorActionPreference
    $ErrorActionPreference = 'SilentlyContinue'
    try { return [bool](Get-Command $Command) }
    finally { $ErrorActionPreference = $oldPref }
}

function Test-OllamaAlive {
    try {
        $r = Invoke-RestMethod -Uri "$OLLAMA_API_URL/api/tags" -TimeoutSec 3 -ErrorAction Stop
        return $true
    }
    catch { return $false }
}

# ============================================================
#  PHASE 1 : VÉRIFICATIONS PRÉALABLES
# ============================================================
function Test-Prerequisites {
    Write-Log "Phase 1 : Vérifications préalables" -Level STEP

    # Privilèges administrateur
    if (-not (Test-Administrator)) {
        Invoke-AdminElevation
    }
    Write-Log "Privilèges administrateur confirmés" -Level OK

    # Version Windows
    $os = Get-CimInstance Win32_OperatingSystem
    $build = [int]$os.BuildNumber
    if ($build -lt 17763) {
        Write-Log "Windows trop ancien (build $build). Windows 10 1809+ ou 11 requis." -Level ERROR
        throw "OS non supporté"
    }
    $osDisplay = if ($build -ge 22000) { "Windows 11" } else { "Windows 10" }
    Write-Log "$osDisplay (build $build) détecté" -Level OK

    # PowerShell version
    if ($PSVersionTable.PSVersion.Major -lt 5) {
        throw "PowerShell 5.1 ou plus récent requis"
    }
    Write-Log "PowerShell $($PSVersionTable.PSVersion) confirmé" -Level OK

    # Espace disque
    $driveLetter = (Split-Path $InstallPath -Qualifier).TrimEnd(':')
    $diskInfo = Get-PSDrive -Name $driveLetter -ErrorAction SilentlyContinue
    if (-not $diskInfo) {
        Write-Log "Lecteur $driveLetter introuvable, utilise C:" -Level WARN
        $diskInfo = Get-PSDrive -Name "C"
        $driveLetter = "C"
    }
    $freeGB = [math]::Round($diskInfo.Free / 1GB, 1)
    if ($freeGB -lt 30) {
        Write-Log "Espace disque insuffisant : ${freeGB} Go libres (30 Go minimum)" -Level WARN
        Write-Log "L'installation peut échouer en cours de route" -Level WARN
    }
    else {
        Write-Log "Espace disque suffisant : ${freeGB} Go libres sur ${driveLetter}:" -Level OK
    }

    # RAM
    $ramGB = [math]::Round((Get-CimInstance Win32_ComputerSystem).TotalPhysicalMemory / 1GB)
    if ($ramGB -lt 16) {
        Write-Log "RAM insuffisante : $ramGB Go (16 Go minimum, 32 Go recommandés)" -Level WARN
        Write-Log "IAbrain fonctionnera mais lentement" -Level WARN
    }
    else {
        Write-Log "RAM : $ramGB Go" -Level OK
    }

    # Connectivité GitHub et Ollama
    foreach ($url in @("https://github.com", "https://ollama.com")) {
        try {
            $null = Invoke-WebRequest -Uri $url -Method Head -TimeoutSec 10 -UseBasicParsing
            Write-Log "Connectivité $url confirmée" -Level OK
        }
        catch {
            Write-Log "Impossible de joindre $url - vérifiez votre connexion" -Level ERROR
            throw "Connectivité Internet requise"
        }
    }

    # Vérification installation existante
    if ((Test-Path "$InstallPath\IAbrain.exe") -and (-not $Force)) {
        Write-Log "IAbrain est déjà installé dans $InstallPath" -Level WARN
        Write-Log "Utilisez -Force pour forcer la réinstallation" -Level WARN
        Write-Log "Le script poursuit en mode mise à jour" -Level INFO
    }
}

# ============================================================
#  PHASE 2 : INSTALLATION OLLAMA
# ============================================================
function Install-OllamaIfNeeded {
    Write-Log "Phase 2 : Installation Ollama" -Level STEP

    # Test si déjà installé et fonctionnel
    if (Test-OllamaAlive) {
        Write-Log "Ollama est déjà installé et opérationnel" -Level OK
        return
    }

    # Test si binaire présent mais service arrêté
    if (Test-CommandExists "ollama") {
        Write-Log "Ollama est installé mais ne répond pas - tentative de démarrage..." -Level INFO
        try {
            Start-Process "ollama" -ArgumentList "serve" -WindowStyle Hidden
            Start-Sleep -Seconds 5
            if (Test-OllamaAlive) {
                Write-Log "Ollama redémarré avec succès" -Level OK
                return
            }
        }
        catch { }
    }

    # Téléchargement de l'installateur
    Write-Log "Téléchargement de l'installateur Ollama..." -Level INFO
    $installerPath = Join-Path $env:TEMP "OllamaSetup.exe"
    try {
        Invoke-WebRequest -Uri $OLLAMA_INSTALLER_URL `
                          -OutFile $installerPath `
                          -UseBasicParsing
        $sizeMB = [math]::Round((Get-Item $installerPath).Length / 1MB, 1)
        Write-Log "Téléchargement OK (${sizeMB} Mo)" -Level OK
    }
    catch {
        throw "Téléchargement Ollama échoué : $_"
    }

    # Installation silencieuse
    Write-Log "Installation silencieuse d'Ollama (peut prendre 1-2 minutes)..." -Level INFO
    try {
        $proc = Start-Process -FilePath $installerPath `
                              -ArgumentList "/SILENT" `
                              -Wait -PassThru `
                              -WindowStyle Hidden
        if ($proc.ExitCode -ne 0) {
            throw "Installateur Ollama a retourné le code $($proc.ExitCode)"
        }
        Write-Log "Ollama installé" -Level OK
    }
    finally {
        Remove-Item $installerPath -ErrorAction SilentlyContinue
    }

    # Attente démarrage du service
    Write-Log "Attente du démarrage du service Ollama..." -Level INFO
    $timeout = 30
    $elapsed = 0
    while (-not (Test-OllamaAlive)) {
        Start-Sleep -Seconds 1
        $elapsed++
        if ($elapsed -ge $timeout) {
            throw "Ollama n'a pas démarré dans le délai imparti ($timeout sec)"
        }
    }
    Write-Log "Service Ollama opérationnel" -Level OK
}

# ============================================================
#  PHASE 3 : VARIABLES D'ENVIRONNEMENT OLLAMA
# ============================================================
function Set-OllamaEnvironment {
    Write-Log "Phase 3 : Configuration variables d'environnement Ollama" -Level STEP

    $changed = $false
    foreach ($var in $OLLAMA_ENV.GetEnumerator()) {
        $current = [Environment]::GetEnvironmentVariable($var.Key, "Machine")
        if ($current -ne $var.Value) {
            [Environment]::SetEnvironmentVariable($var.Key, $var.Value, "Machine")
            Write-Log "$($var.Key) = $($var.Value)" -Level OK
            $changed = $true
        }
        else {
            Write-Log "$($var.Key) déjà configuré" -Level INFO
        }
    }

    if ($changed) {
        Write-Log "Redémarrage d'Ollama pour appliquer les variables..." -Level INFO
        # Tuer Ollama proprement et le relancer
        Get-Process -Name "ollama*" -ErrorAction SilentlyContinue | Stop-Process -Force -ErrorAction SilentlyContinue
        Start-Sleep -Seconds 2
        Start-Process "ollama" -ArgumentList "serve" -WindowStyle Hidden
        Start-Sleep -Seconds 3

        $timeout = 20
        $elapsed = 0
        while (-not (Test-OllamaAlive)) {
            Start-Sleep -Seconds 1
            $elapsed++
            if ($elapsed -ge $timeout) {
                Write-Log "Ollama lent à redémarrer, mais l'installation continue" -Level WARN
                break
            }
        }
        if (Test-OllamaAlive) {
            Write-Log "Ollama redémarré avec les nouvelles variables" -Level OK
        }
    }
}

# ============================================================
#  PHASE 4 : PULL DES MODÈLES
# ============================================================
function Get-OllamaInstalledModels {
    try {
        $r = Invoke-RestMethod -Uri "$OLLAMA_API_URL/api/tags" -TimeoutSec 10
        return @($r.models | ForEach-Object { $_.name })
    }
    catch {
        return @()
    }
}

function Get-OllamaModels {
    if ($SkipModels) {
        Write-Log "Phase 4 : Pull des modèles (SAUTÉ via -SkipModels)" -Level STEP
        return
    }

    Write-Log "Phase 4 : Téléchargement des modèles Ollama" -Level STEP
    Write-Log "Cette étape peut prendre 15-30 minutes selon votre connexion" -Level INFO

    $installed = Get-OllamaInstalledModels

    foreach ($model in $MODELS) {
        $name = $model.Name
        $alreadyInstalled = $installed | Where-Object {
            $_ -eq $name -or $_ -eq "$($name):latest" -or $_ -like "$($name):*"
        }

        if ($alreadyInstalled) {
            Write-Log "$name déjà installé ($($model.Size) - $($model.Role))" -Level OK
            continue
        }

        Write-Log "Téléchargement $name ($($model.Size) - $($model.Role))..." -Level INFO
        try {
            # ollama pull en mode silencieux : on capture la sortie pour ne pas
            # polluer la console, mais on l'écrit dans le log
            $output = & ollama pull $name 2>&1
            if ($LASTEXITCODE -ne 0) {
                throw "ollama pull a retourné $LASTEXITCODE"
            }
            Write-Log "$name installé" -Level OK
        }
        catch {
            Write-Log "Échec du pull $name : $_" -Level ERROR
            Write-Log "Vous pourrez réessayer manuellement : ollama pull $name" -Level WARN
        }
    }
}

# ============================================================
#  PHASE 5 : TÉLÉCHARGEMENT IABRAIN.7Z
# ============================================================
function Get-7ZipPath {
    # Chemins typiques pour 7-Zip
    $paths = @(
        "$env:ProgramFiles\7-Zip\7z.exe",
        "${env:ProgramFiles(x86)}\7-Zip\7z.exe"
    )
    foreach ($p in $paths) {
        if (Test-Path $p) { return $p }
    }
    if (Test-CommandExists "7z") {
        return (Get-Command "7z").Source
    }
    return $null
}

function Install-7ZipIfNeeded {
    $path = Get-7ZipPath
    if ($path) {
        Write-Log "7-Zip détecté : $path" -Level OK
        return $path
    }

    Write-Log "7-Zip non trouvé - installation via winget..." -Level INFO
    if (Test-CommandExists "winget") {
        try {
            $null = winget install --id 7zip.7zip --silent --accept-source-agreements --accept-package-agreements 2>&1
            Start-Sleep -Seconds 2
            $path = Get-7ZipPath
            if ($path) {
                Write-Log "7-Zip installé via winget" -Level OK
                return $path
            }
        }
        catch {
            Write-Log "winget install échoué : $_" -Level WARN
        }
    }

    Write-Log "Installation manuelle de 7-Zip nécessaire depuis https://www.7-zip.org/" -Level ERROR
    throw "7-Zip requis pour décompresser IAbrain.7z"
}

function Download-IAbrainArchive {
    Write-Log "Phase 5 : Téléchargement IAbrain.7z" -Level STEP

    $archivePath = Join-Path $env:TEMP "IAbrain.7z"
    Write-Log "Source : $IABRAIN_ARCHIVE_URL" -Level INFO

    try {
        # Téléchargement avec barre de progression
        $oldPP = $ProgressPreference
        $ProgressPreference = 'Continue'
        Invoke-WebRequest -Uri $IABRAIN_ARCHIVE_URL `
                          -OutFile $archivePath `
                          -UseBasicParsing
        $ProgressPreference = $oldPP

        $sizeMB = [math]::Round((Get-Item $archivePath).Length / 1MB, 1)
        Write-Log "Téléchargement OK (${sizeMB} Mo)" -Level OK
        return $archivePath
    }
    catch {
        Write-Log "Téléchargement échoué : $_" -Level ERROR
        throw "Impossible de télécharger IAbrain.7z depuis GitHub"
    }
}

function Expand-IAbrainArchive {
    param([string]$ArchivePath)

    Write-Log "Phase 5 : Décompression dans $InstallPath" -Level STEP

    $sevenZip = Install-7ZipIfNeeded

    # Sauvegarde de la config existante si présente
    $configBackup = $null
    $configPath = Join-Path $InstallPath "IAbrain.json"
    if (Test-Path $configPath) {
        $configBackup = Join-Path $env:TEMP "IAbrain.json.bak"
        Copy-Item $configPath $configBackup -Force
        Write-Log "Configuration existante sauvegardée" -Level INFO
    }

    # Sauvegarde de la base RAG si présente
    $ragBackup = $null
    $ragPath = Join-Path $InstallPath "IAbrain_rag_db"
    if (Test-Path $ragPath) {
        $ragBackup = Join-Path $env:TEMP "IAbrain_rag_db.bak"
        if (Test-Path $ragBackup) { Remove-Item $ragBackup -Recurse -Force }
        Copy-Item $ragPath $ragBackup -Recurse -Force
        Write-Log "Base RAG existante sauvegardée" -Level INFO
    }

    # Décompression vers le parent (l'archive contient déjà IAbrain/)
    $parent = Split-Path $InstallPath -Parent
    if (-not (Test-Path $parent)) {
        New-Item -ItemType Directory -Path $parent -Force | Out-Null
    }

    try {
        $output = & $sevenZip x $ArchivePath "-o$parent" -y 2>&1
        if ($LASTEXITCODE -ne 0) {
            throw "7-Zip a retourné le code $LASTEXITCODE"
        }
        Write-Log "Archive décompressée" -Level OK
    }
    finally {
        Remove-Item $ArchivePath -ErrorAction SilentlyContinue
    }

    # Restauration config et base RAG
    if ($configBackup -and (Test-Path $configBackup)) {
        Copy-Item $configBackup $configPath -Force
        Remove-Item $configBackup -Force
        Write-Log "Configuration restaurée" -Level OK
    }
    if ($ragBackup -and (Test-Path $ragBackup)) {
        if (Test-Path $ragPath) { Remove-Item $ragPath -Recurse -Force }
        Copy-Item $ragBackup $ragPath -Recurse -Force
        Remove-Item $ragBackup -Recurse -Force
        Write-Log "Base RAG restaurée" -Level OK
    }

    # Vérification
    $exePath = Join-Path $InstallPath "IAbrain.exe"
    if (-not (Test-Path $exePath)) {
        throw "IAbrain.exe introuvable dans $InstallPath après décompression"
    }
    Write-Log "IAbrain.exe vérifié dans $InstallPath" -Level OK
}

# ============================================================
#  PHASE 6 : RACCOURCIS
# ============================================================
function New-IAbrainShortcuts {
    Write-Log "Phase 6 : Création des raccourcis" -Level STEP

    $exePath = Join-Path $InstallPath "IAbrain.exe"
    $iconPath = Join-Path $InstallPath "IAbrain.ico"
    if (-not (Test-Path $iconPath)) { $iconPath = $exePath }

    $WshShell = New-Object -ComObject WScript.Shell

    # Raccourci bureau (utilisateur courant)
    $userDesktop = [Environment]::GetFolderPath('Desktop')
    # Si l'install est en admin, on vise le bureau "All Users"
    $publicDesktop = [Environment]::GetFolderPath('CommonDesktopDirectory')
    $desktopPath = if (Test-Path $publicDesktop) { $publicDesktop } else { $userDesktop }

    $desktopShortcut = Join-Path $desktopPath "IAbrain.lnk"
    try {
        $sc = $WshShell.CreateShortcut($desktopShortcut)
        $sc.TargetPath = $exePath
        $sc.WorkingDirectory = $InstallPath
        $sc.IconLocation = "$iconPath,0"
        $sc.Description = "Assistant IA local pour les opérateurs ADRASEC"
        $sc.Save()
        Write-Log "Raccourci bureau créé : $desktopShortcut" -Level OK
    }
    catch {
        Write-Log "Création raccourci bureau échouée : $_" -Level WARN
    }

    # Raccourci menu Démarrer (Programs)
    $startMenu = [Environment]::GetFolderPath('CommonPrograms')
    $startShortcut = Join-Path $startMenu "IAbrain.lnk"
    try {
        $sc = $WshShell.CreateShortcut($startShortcut)
        $sc.TargetPath = $exePath
        $sc.WorkingDirectory = $InstallPath
        $sc.IconLocation = "$iconPath,0"
        $sc.Description = "Assistant IA local pour les opérateurs ADRASEC"
        $sc.Save()
        Write-Log "Raccourci menu Démarrer créé" -Level OK
    }
    catch {
        Write-Log "Création raccourci menu Démarrer échouée : $_" -Level WARN
    }
}

# ============================================================
#  PHASE 7 : PARE-FEU (OPTIONNEL)
# ============================================================
function Set-FirewallRule {
    if ($SkipFirewall) {
        Write-Log "Phase 7 : Pare-feu (SAUTÉ via -SkipFirewall)" -Level STEP
        return
    }

    Write-Log "Phase 7 : Configuration pare-feu Windows pour Ollama" -Level STEP

    $ruleName = "Ollama IAbrain (port 11434)"
    $existing = Get-NetFirewallRule -DisplayName $ruleName -ErrorAction SilentlyContinue

    if ($existing) {
        Write-Log "Règle pare-feu déjà présente" -Level OK
        return
    }

    try {
        New-NetFirewallRule -DisplayName $ruleName `
                            -Direction Inbound `
                            -Protocol TCP `
                            -LocalPort 11434 `
                            -Action Allow `
                            -Profile Domain,Private `
                            -Description "Permet l'accès à Ollama depuis le réseau ADRASEC local" `
                            | Out-Null
        Write-Log "Règle pare-feu créée (port 11434, profils Domain+Private)" -Level OK
    }
    catch {
        Write-Log "Création règle pare-feu échouée : $_" -Level WARN
        Write-Log "IAbrain fonctionnera quand même en local" -Level INFO
    }
}

# ============================================================
#  PHASE 8 : VALIDATION FINALE
# ============================================================
function Test-Installation {
    Write-Log "Phase 8 : Validation finale" -Level STEP

    $errors = 0

    # IAbrain.exe présent
    $exePath = Join-Path $InstallPath "IAbrain.exe"
    if (Test-Path $exePath) {
        Write-Log "IAbrain.exe présent" -Level OK
    } else {
        Write-Log "IAbrain.exe MANQUANT" -Level ERROR
        $errors++
    }

    # Ollama vivant
    if (Test-OllamaAlive) {
        Write-Log "Ollama répond sur $OLLAMA_API_URL" -Level OK
    } else {
        Write-Log "Ollama ne répond pas - redémarrez votre PC pour activer le service" -Level WARN
        $errors++
    }

    # Modèles minimums
    $installed = Get-OllamaInstalledModels
    foreach ($model in $MODELS) {
        $name = $model.Name
        $found = $installed | Where-Object {
            $_ -eq $name -or $_ -eq "$($name):latest" -or $_ -like "$($name):*"
        }
        if ($found) {
            Write-Log "Modèle $name disponible" -Level OK
        } else {
            Write-Log "Modèle $name MANQUANT" -Level WARN
        }
    }

    # Raccourci bureau
    $desktopShortcut = Join-Path ([Environment]::GetFolderPath('CommonDesktopDirectory')) "IAbrain.lnk"
    if (Test-Path $desktopShortcut) {
        Write-Log "Raccourci bureau opérationnel" -Level OK
    } else {
        Write-Log "Raccourci bureau absent" -Level WARN
    }

    return $errors -eq 0
}

# ============================================================
#  AFFICHAGE FINAL
# ============================================================
function Show-Summary {
    param([bool]$Success)

    Write-Host "`n" -NoNewline
    Write-Host ("═" * 60) -ForegroundColor Cyan

    if ($Success) {
        Write-Host "  🎉 INSTALLATION TERMINÉE AVEC SUCCÈS" -ForegroundColor Green
    } else {
        Write-Host "  ⚠ INSTALLATION TERMINÉE AVEC AVERTISSEMENTS" -ForegroundColor Yellow
    }
    Write-Host ("═" * 60) -ForegroundColor Cyan
    Write-Host ""

    Write-Host "  📁 Dossier d'installation : " -NoNewline
    Write-Host $InstallPath -ForegroundColor White
    Write-Host "  🚀 Pour lancer IAbrain    : " -NoNewline
    Write-Host "double-clic sur le raccourci bureau" -ForegroundColor White
    Write-Host "  📋 Log d'installation     : " -NoNewline
    Write-Host $script:LogFile -ForegroundColor White
    Write-Host ""

    Write-Host "  Première utilisation :" -ForegroundColor Cyan
    Write-Host "    1. Lance IAbrain depuis le bureau" -ForegroundColor Gray
    Write-Host "    2. Vérifie que la pastille de statut est verte (✅ Connecté)" -ForegroundColor Gray
    Write-Host "    3. Menu Connaissances → 🔄 Mettre à jour la base depuis GitHub" -ForegroundColor Gray
    Write-Host "    4. Pose ta première question : 'Parle-moi du logiciel TCQ'" -ForegroundColor Gray
    Write-Host ""

    Write-Host "  Documentation complète : " -NoNewline -ForegroundColor Cyan
    Write-Host $IABRAIN_REPO_URL -ForegroundColor White
    Write-Host ""
    Write-Host ("═" * 60) -ForegroundColor Cyan
    Write-Host ""
}

# ============================================================
#  MAIN
# ============================================================
function Main {
    # En-tête
    Clear-Host
    Write-Host ""
    Write-Host ("═" * 60) -ForegroundColor Cyan
    Write-Host "  IAbrain v$IABRAIN_VERSION - Installation automatique" -ForegroundColor Cyan
    Write-Host "  Assistant IA local pour les opérateurs ADRASEC" -ForegroundColor Cyan
    Write-Host "  Auteur : F1GBD / F4JHW - ADRASEC 77" -ForegroundColor Cyan
    Write-Host ("═" * 60) -ForegroundColor Cyan
    Write-Host ""

    Write-Log "Démarrage installation IAbrain v$IABRAIN_VERSION"
    Write-Log "InstallPath = $InstallPath"
    Write-Log "SkipModels = $SkipModels, SkipFirewall = $SkipFirewall, Force = $Force"

    try {
        Test-Prerequisites
        Install-OllamaIfNeeded
        Set-OllamaEnvironment
        Get-OllamaModels

        $archive = Download-IAbrainArchive
        Expand-IAbrainArchive -ArchivePath $archive

        New-IAbrainShortcuts
        Set-FirewallRule

        $success = Test-Installation
        Show-Summary -Success $success
    }
    catch {
        Write-Host ""
        Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Red
        Write-Host "  ✗ INSTALLATION INTERROMPUE" -ForegroundColor Red
        Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Red
        Write-Host ""
        Write-Host "  Erreur : $_" -ForegroundColor Red
        Write-Host ""
        Write-Host "  Log complet : $script:LogFile" -ForegroundColor Yellow
        Write-Host ""
        Write-Log "ERREUR : $_" -Level ERROR
        Write-Log "Stack : $($_.ScriptStackTrace)" -Level ERROR
        exit 1
    }
}

# Lancement
Main
