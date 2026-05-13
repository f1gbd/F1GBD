#Requires -Version 5.1
<#
.SYNOPSIS
    Configuration optimisée d'Ollama pour serveur LAN ADRASEC sur mini-PC AMD Ryzen avec iGPU Radeon.

.DESCRIPTION
    Ce script applique automatiquement les variables d'environnement nécessaires
    pour exploiter l'iGPU Radeon via le backend Vulkan d'Ollama.

    Configuration appliquée :
    - Activation du backend Vulkan
    - Suppression des variables ROCm parasites
    - Désactivation de Flash Attention (incompatible Vulkan AMD)
    - Optimisation KV cache, contexte et batch size
    - Exposition LAN du serveur Ollama
    - Maintien des modèles 30 min en mémoire

    Compatible Windows 10/11 + Ollama 0.22 ou supérieur.

.PARAMETER Action
    Action à effectuer :
    - 'Apply' : applique la configuration optimale (par défaut)
    - 'Restore' : restaure la configuration Ollama par défaut
    - 'Check' : affiche la configuration actuelle sans modification
    - 'Bench' : lance un test de performance après application

.PARAMETER ContextLength
    Longueur de contexte Ollama. Défaut: 8192.
    Valeurs recommandées selon la VRAM dédiée :
    - VRAM dédiée < 1 Go : 4096
    - VRAM dédiée 1-4 Go : 8192
    - VRAM dédiée > 4 Go : 16384 ou 32768

.PARAMETER NumBatch
    Taille du batch de calcul. Défaut: 256.
    Réduire à 128 en cas d'erreur 'failed to allocate compute pp buffers'.

.EXAMPLE
    .\Configure-OllamaAMD.ps1
    Applique la configuration par défaut (recommandé).

.EXAMPLE
    .\Configure-OllamaAMD.ps1 -Action Check
    Affiche la configuration actuelle sans rien modifier.

.EXAMPLE
    .\Configure-OllamaAMD.ps1 -Action Apply -ContextLength 4096 -NumBatch 128
    Applique la configuration avec valeurs réduites (mini-PC à faible VRAM dédiée).

.EXAMPLE
    .\Configure-OllamaAMD.ps1 -Action Restore
    Supprime toutes les variables et revient à la configuration Ollama par défaut.

.NOTES
    Auteur     : F1GBD - ADRASEC 77 / FNRASEC
    Version    : 1.0
    Date       : Mai 2026
    Licence    : Diffusion libre au sein du réseau ADRASEC / FNRASEC
    Testé sur  : Geekom A7 Max (Ryzen 9 7940HS, Radeon 780M)
                 LX15 Pro    (Ryzen 7 5825U, Radeon Vega 8)

    Doit être exécuté en tant qu'administrateur (variables système).
#>

[CmdletBinding()]
param(
    [Parameter(Position = 0)]
    [ValidateSet('Apply', 'Restore', 'Check', 'Bench')]
    [string]$Action = 'Apply',

    [Parameter()]
    [ValidateRange(512, 131072)]
    [int]$ContextLength = 8192,

    [Parameter()]
    [ValidateRange(64, 2048)]
    [int]$NumBatch = 256
)

# === Vérification droits admin ===
function Test-Admin {
    $currentUser = [System.Security.Principal.WindowsPrincipal]::new(
        [System.Security.Principal.WindowsIdentity]::GetCurrent())
    return $currentUser.IsInRole([System.Security.Principal.WindowsBuiltInRole]::Administrator)
}

# === Bannière ===
function Show-Banner {
    Write-Host ""
    Write-Host "===============================================================" -ForegroundColor Cyan
    Write-Host "  Configuration Ollama optimisee pour iGPU AMD Radeon" -ForegroundColor Cyan
    Write-Host "  F1GBD / ADRASEC 77 - FNRASEC" -ForegroundColor Cyan
    Write-Host "  Version 1.0 - Mai 2026" -ForegroundColor Cyan
    Write-Host "===============================================================" -ForegroundColor Cyan
    Write-Host ""
}

# === Affichage configuration actuelle ===
function Show-Config {
    Write-Host "--- Configuration Ollama actuelle ---" -ForegroundColor Yellow
    Write-Host ""

    $vars = @(
        @{ Name = 'OLLAMA_VULKAN';            Scope = 'User'    },
        @{ Name = 'HSA_OVERRIDE_GFX_VERSION'; Scope = 'User'    },
        @{ Name = 'OLLAMA_FLASH_ATTENTION';   Scope = 'Machine' },
        @{ Name = 'OLLAMA_KV_CACHE_TYPE';     Scope = 'Machine' },
        @{ Name = 'OLLAMA_KEEP_ALIVE';        Scope = 'Machine' },
        @{ Name = 'OLLAMA_MAX_LOADED_MODELS'; Scope = 'Machine' },
        @{ Name = 'OLLAMA_HOST';              Scope = 'Machine' },
        @{ Name = 'OLLAMA_NUM_PARALLEL';      Scope = 'Machine' },
        @{ Name = 'OLLAMA_CONTEXT_LENGTH';    Scope = 'Machine' },
        @{ Name = 'OLLAMA_NUM_BATCH';         Scope = 'Machine' }
    )

    foreach ($v in $vars) {
        $val = [System.Environment]::GetEnvironmentVariable($v.Name, $v.Scope)
        $displayVal = if ([string]::IsNullOrEmpty($val)) { '<non defini>' } else { $val }
        $color = if ([string]::IsNullOrEmpty($val)) { 'DarkGray' } else { 'Green' }
        $scope = "($($v.Scope))".PadRight(11)
        Write-Host ("  {0,-28} {1} = " -f $v.Name, $scope) -NoNewline
        Write-Host $displayVal -ForegroundColor $color
    }
    Write-Host ""
}

# === Application de la configuration ===
function Apply-Config {
    param([int]$Ctx, [int]$Batch)

    Write-Host "--- Application de la configuration optimisee ---" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Parametres :" -ForegroundColor Gray
    Write-Host "  - Contexte (OLLAMA_CONTEXT_LENGTH) : $Ctx tokens"
    Write-Host "  - Batch size (OLLAMA_NUM_BATCH)    : $Batch"
    Write-Host ""

    try {
        # Variables UTILISATEUR
        [System.Environment]::SetEnvironmentVariable('OLLAMA_VULKAN', '1', 'User')
        Write-Host "  [OK] OLLAMA_VULKAN = 1 (User)" -ForegroundColor Green

        [System.Environment]::SetEnvironmentVariable('HSA_OVERRIDE_GFX_VERSION', $null, 'User')
        Write-Host "  [OK] HSA_OVERRIDE_GFX_VERSION supprimee (User)" -ForegroundColor Green

        # Variables SYSTEME
        [System.Environment]::SetEnvironmentVariable('OLLAMA_FLASH_ATTENTION', '0', 'Machine')
        Write-Host "  [OK] OLLAMA_FLASH_ATTENTION = 0 (Machine)" -ForegroundColor Green

        [System.Environment]::SetEnvironmentVariable('OLLAMA_KV_CACHE_TYPE', 'q8_0', 'Machine')
        Write-Host "  [OK] OLLAMA_KV_CACHE_TYPE = q8_0 (Machine)" -ForegroundColor Green

        [System.Environment]::SetEnvironmentVariable('OLLAMA_KEEP_ALIVE', '30m', 'Machine')
        Write-Host "  [OK] OLLAMA_KEEP_ALIVE = 30m (Machine)" -ForegroundColor Green

        [System.Environment]::SetEnvironmentVariable('OLLAMA_MAX_LOADED_MODELS', '2', 'Machine')
        Write-Host "  [OK] OLLAMA_MAX_LOADED_MODELS = 2 (Machine)" -ForegroundColor Green

        [System.Environment]::SetEnvironmentVariable('OLLAMA_HOST', 'http://0.0.0.0:11434', 'Machine')
        Write-Host "  [OK] OLLAMA_HOST = http://0.0.0.0:11434 (Machine)" -ForegroundColor Green

        [System.Environment]::SetEnvironmentVariable('OLLAMA_NUM_PARALLEL', '1', 'Machine')
        Write-Host "  [OK] OLLAMA_NUM_PARALLEL = 1 (Machine)" -ForegroundColor Green

        [System.Environment]::SetEnvironmentVariable('OLLAMA_CONTEXT_LENGTH', "$Ctx", 'Machine')
        Write-Host "  [OK] OLLAMA_CONTEXT_LENGTH = $Ctx (Machine)" -ForegroundColor Green

        [System.Environment]::SetEnvironmentVariable('OLLAMA_NUM_BATCH', "$Batch", 'Machine')
        Write-Host "  [OK] OLLAMA_NUM_BATCH = $Batch (Machine)" -ForegroundColor Green

        Write-Host ""
        Write-Host "Configuration appliquee avec succes !" -ForegroundColor Green
    }
    catch {
        Write-Host ""
        Write-Host "ERREUR : impossible d'ecrire les variables." -ForegroundColor Red
        Write-Host "Cause probable : droits administrateur insuffisants." -ForegroundColor Red
        Write-Host $_.Exception.Message -ForegroundColor Red
        return $false
    }

    return $true
}

# === Restauration configuration par defaut ===
function Restore-Config {
    Write-Host "--- Restauration configuration Ollama par defaut ---" -ForegroundColor Yellow
    Write-Host ""

    try {
        [System.Environment]::SetEnvironmentVariable('OLLAMA_VULKAN', $null, 'User')
        Write-Host "  [OK] OLLAMA_VULKAN supprimee (User)" -ForegroundColor Green

        $machineVars = @(
            'OLLAMA_FLASH_ATTENTION',
            'OLLAMA_KV_CACHE_TYPE',
            'OLLAMA_KEEP_ALIVE',
            'OLLAMA_MAX_LOADED_MODELS',
            'OLLAMA_HOST',
            'OLLAMA_NUM_PARALLEL',
            'OLLAMA_CONTEXT_LENGTH',
            'OLLAMA_NUM_BATCH'
        )

        foreach ($var in $machineVars) {
            [System.Environment]::SetEnvironmentVariable($var, $null, 'Machine')
            Write-Host "  [OK] $var supprimee (Machine)" -ForegroundColor Green
        }

        Write-Host ""
        Write-Host "Configuration restauree !" -ForegroundColor Green
    }
    catch {
        Write-Host "ERREUR lors de la restauration." -ForegroundColor Red
        return $false
    }

    return $true
}

# === Arret propre d'Ollama ===
function Stop-Ollama {
    Write-Host "--- Arret d'Ollama ---" -ForegroundColor Yellow

    $procs = Get-Process -Name "*ollama*" -ErrorAction SilentlyContinue
    if ($procs) {
        Write-Host "  Processus Ollama detectes : $($procs.Count)" -ForegroundColor Gray
        $procs | Stop-Process -Force
        Start-Sleep -Seconds 3
        Write-Host "  [OK] Tous les processus Ollama ont ete arretes" -ForegroundColor Green
    }
    else {
        Write-Host "  Aucun processus Ollama en cours d'execution" -ForegroundColor Gray
    }
    Write-Host ""
}

# === Recherche du chemin Ollama ===
function Find-OllamaPath {
    $paths = @(
        "$env:LOCALAPPDATA\Programs\Ollama\ollama app.exe",
        "$env:LOCALAPPDATA\Programs\Ollama\Ollama.exe",
        "$env:ProgramFiles\Ollama\ollama app.exe"
    )
    foreach ($p in $paths) {
        if (Test-Path $p) { return $p }
    }
    return $null
}

# === Demarrage d'Ollama ===
function Start-Ollama {
    Write-Host "--- Demarrage d'Ollama ---" -ForegroundColor Yellow

    $ollamaPath = Find-OllamaPath
    if ($ollamaPath) {
        Start-Process -FilePath $ollamaPath
        Write-Host "  [OK] Ollama lance depuis : $ollamaPath" -ForegroundColor Green
        Write-Host "  Attente du demarrage du serveur (10 s)..." -ForegroundColor Gray
        Start-Sleep -Seconds 10
    }
    else {
        Write-Host "  [!] Ollama introuvable. Veuillez le lancer manuellement." -ForegroundColor Yellow
        Write-Host "      Menu Demarrer -> taper 'Ollama' -> clic" -ForegroundColor Gray
    }
    Write-Host ""
}

# === Test de performance ===
function Test-OllamaPerf {
    Write-Host "--- Test de performance ---" -ForegroundColor Yellow
    Write-Host ""

    # Verifier que ollama est accessible
    $ollamaCmd = Get-Command ollama -ErrorAction SilentlyContinue
    if (-not $ollamaCmd) {
        Write-Host "  [!] La commande 'ollama' n'est pas accessible dans ce terminal." -ForegroundColor Yellow
        Write-Host "      Ouvrez un nouveau terminal PowerShell apres redemarrage." -ForegroundColor Gray
        return
    }

    # Verifier qu'un modele est disponible
    Write-Host "  Recherche des modeles disponibles..." -ForegroundColor Gray
    $models = & ollama list 2>$null

    if (-not $models -or $models.Count -lt 2) {
        Write-Host "  [!] Aucun modele installe. Telechargez-en un :" -ForegroundColor Yellow
        Write-Host "      ollama pull mistral-nemo:12b   (recommande RDNA3)" -ForegroundColor Gray
        Write-Host "      ollama pull qwen2.5:7b         (recommande Vega/RDNA2)" -ForegroundColor Gray
        return
    }

    Write-Host "  Modeles disponibles :" -ForegroundColor Gray
    $models | Select-Object -Skip 1 | ForEach-Object {
        Write-Host "    $_" -ForegroundColor Gray
    }
    Write-Host ""
    Write-Host "  Pour mesurer les performances, lancez :" -ForegroundColor Cyan
    Write-Host '    ollama run <modele> --verbose' -ForegroundColor White
    Write-Host '    >>> Ecris un texte de 300 mots sur la propagation HF en bande 40m' -ForegroundColor White
    Write-Host ""
    Write-Host "  Puis dans un autre terminal :" -ForegroundColor Cyan
    Write-Host '    ollama ps' -ForegroundColor White
    Write-Host "    (la colonne PROCESSOR doit afficher 100% GPU)" -ForegroundColor Gray
    Write-Host ""
}

# === Detection du materiel ===
function Show-Hardware {
    Write-Host "--- Detection materielle ---" -ForegroundColor Yellow

    try {
        $cpu = Get-CimInstance Win32_Processor -ErrorAction Stop |
               Select-Object -First 1
        Write-Host "  CPU       : $($cpu.Name.Trim())" -ForegroundColor Gray

        $ramGB = [math]::Round((Get-CimInstance Win32_ComputerSystem).TotalPhysicalMemory / 1GB, 1)
        Write-Host "  RAM       : $ramGB Go" -ForegroundColor Gray

        $gpus = Get-CimInstance Win32_VideoController -ErrorAction Stop |
                Where-Object { $_.Name -match 'Radeon|AMD' }
        foreach ($gpu in $gpus) {
            $vramGB = [math]::Round($gpu.AdapterRAM / 1GB, 2)
            Write-Host "  GPU/iGPU  : $($gpu.Name) (VRAM dediee : $vramGB Go)" -ForegroundColor Gray
        }

        # Recommandation contexte
        $maxVram = 0
        foreach ($gpu in $gpus) {
            $vram = $gpu.AdapterRAM / 1GB
            if ($vram -gt $maxVram) { $maxVram = $vram }
        }

        Write-Host ""
        if ($maxVram -lt 1) {
            Write-Host "  RECOMMANDATION : VRAM dediee tres faible (< 1 Go)" -ForegroundColor Yellow
            Write-Host "    Utilisez : -ContextLength 4096 -NumBatch 128" -ForegroundColor Yellow
            Write-Host "    Modele recommande : qwen2.5:7b" -ForegroundColor Yellow
        }
        elseif ($maxVram -lt 4) {
            Write-Host "  RECOMMANDATION : VRAM dediee modeste ($maxVram Go)" -ForegroundColor Cyan
            Write-Host "    Defaut OK : -ContextLength 8192 -NumBatch 256" -ForegroundColor Cyan
        }
        else {
            Write-Host "  RECOMMANDATION : Bonne VRAM dediee ($maxVram Go)" -ForegroundColor Green
            Write-Host "    Possibilite d'augmenter : -ContextLength 16384" -ForegroundColor Green
        }
    }
    catch {
        Write-Host "  [!] Impossible de detecter le materiel : $($_.Exception.Message)" -ForegroundColor Yellow
    }
    Write-Host ""
}

# === MAIN ===
Show-Banner

if (-not (Test-Admin)) {
    Write-Host "ERREUR : ce script doit etre lance en tant qu'administrateur." -ForegroundColor Red
    Write-Host ""
    Write-Host "Procedure :" -ForegroundColor Yellow
    Write-Host "  1. Menu Demarrer -> taper 'powershell'"
    Write-Host "  2. Clic droit sur Windows PowerShell -> Executer en tant qu'administrateur"
    Write-Host "  3. Naviguer vers le dossier du script :"
    Write-Host "       cd `"$PSScriptRoot`"" -ForegroundColor Gray
    Write-Host "  4. Lancer le script :"
    Write-Host "       .\Configure-OllamaAMD.ps1" -ForegroundColor Gray
    Write-Host ""
    Read-Host "Appuyez sur Entree pour quitter"
    exit 1
}

Show-Hardware

switch ($Action) {
    'Check' {
        Show-Config
    }

    'Apply' {
        Write-Host "Configuration actuelle AVANT modification :" -ForegroundColor Gray
        Show-Config

        $ok = Apply-Config -Ctx $ContextLength -Batch $NumBatch
        if (-not $ok) {
            Read-Host "Appuyez sur Entree pour quitter"
            exit 1
        }

        Write-Host ""
        Write-Host "Configuration finale :" -ForegroundColor Gray
        Show-Config

        Write-Host "===============================================================" -ForegroundColor Cyan
        Write-Host "  PROCHAINES ETAPES" -ForegroundColor Cyan
        Write-Host "===============================================================" -ForegroundColor Cyan
        Write-Host ""
        Write-Host "  1. Quitter Ollama (clic droit icone systeme -> Quit)"
        Write-Host "  2. Fermer TOUTES les fenetres PowerShell"
        Write-Host "  3. Ouvrir un NOUVEAU PowerShell"
        Write-Host "  4. Relancer Ollama depuis le menu Demarrer"
        Write-Host "  5. Verifier avec : ollama ps  (doit afficher 100% GPU)"
        Write-Host ""

        $reponse = Read-Host "Voulez-vous arreter et redemarrer Ollama maintenant ? (O/N)"
        if ($reponse -match '^[Oo]') {
            Stop-Ollama
            Start-Ollama
            Test-OllamaPerf
        }
    }

    'Restore' {
        Write-Host "Configuration actuelle AVANT restauration :" -ForegroundColor Gray
        Show-Config

        $confirm = Read-Host "Confirmer la restauration de la configuration par defaut ? (O/N)"
        if ($confirm -match '^[Oo]') {
            Restore-Config
            Write-Host ""
            Write-Host "Pensez a redemarrer Ollama pour appliquer le changement." -ForegroundColor Yellow
        }
        else {
            Write-Host "Restauration annulee." -ForegroundColor Gray
        }
    }

    'Bench' {
        Test-OllamaPerf
    }
}

Write-Host ""
Write-Host "Script termine." -ForegroundColor Cyan
Write-Host ""
