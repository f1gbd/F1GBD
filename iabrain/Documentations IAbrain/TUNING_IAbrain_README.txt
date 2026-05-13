===============================================================================

  OPTIMISATION D'UN SERVEUR OLLAMA LOCAL SUR MINI-PC AMD RYZEN

  Kit de diffusion ADRASEC 77 / FNRASEC
  Version 3.0 — Mai 2026
  Auteur : F1GBD / ADRASEC 77 / Seine-et-Marne

===============================================================================


CONTENU DE L'ARCHIVE
--------------------

Ce kit contient trois fichiers :

  1. README.txt                          Le présent fichier (à lire en premier)
  2. todo_ollama_adrasec_v3.docx         Document technique complet, 16 pages
  3. Configure-OllamaAMD.ps1             Script PowerShell d'installation auto


À QUI S'ADRESSE CE KIT
----------------------

Aux opérateurs ADRASEC, formateurs FNRASEC, et toute personne du réseau de
radio-amateurs disposant d'un mini-PC à base d'AMD Ryzen (avec iGPU Radeon)
souhaitant mettre en service un serveur LLM local (Ollama) pour assister :

  - La rédaction de scénarios d'exercice
  - La production de RETEX
  - La rédaction de documents FNRASEC (procédures, ICS-213, SITREP, etc.)
  - L'analyse de logs ou de traces radio
  - L'assistance à la rédaction de scripts Python (TCQ, APRS, CoT, etc.)

Le kit fonctionne pour les configurations suivantes :

  - Mini-PC ou portable AMD Ryzen 5000U/H, 6000H, 7000HS, 8040HS, AI 300
  - Système Windows 10 ou Windows 11
  - Ollama version 0.22 ou supérieure


PROBLÈME RÉSOLU PAR CE KIT
--------------------------

À l'installation par défaut sous Windows, Ollama n'exploite PAS l'iGPU
Radeon AMD et tourne en mode 100% CPU. Ce kit permet d'activer le backend
Vulkan pour utiliser l'iGPU, ce qui apporte :

  - Doublement de la vitesse de génération (eval rate)
  - Multiplication par 6 de la vitesse de traitement de prompt (prompt eval)
  - Libération du CPU pour les autres logiciels (TCQ, VARA HF, etc.)
  - Aucun achat de matériel nécessaire


DÉMARRAGE RAPIDE (5 minutes)
----------------------------

Si vous êtes pressé(e), voici la procédure express :

  Étape 1 : Décompresser le ZIP dans un dossier de travail
            Exemple : C:\ADRASEC\OllamaConfig\

  Étape 2 : Ouvrir Windows PowerShell EN ADMINISTRATEUR
            Menu Démarrer -> taper "powershell"
            Clic droit sur Windows PowerShell
            -> "Exécuter en tant qu'administrateur"

  Étape 3 : Autoriser l'exécution du script (une seule fois)
            Dans PowerShell admin, taper :

                Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned

            Répondre "O" (Oui) à la demande de confirmation.

  Étape 4 : Naviguer vers le dossier contenant le script
            Exemple :

                cd C:\ADRASEC\OllamaConfig

  Étape 5 : Si le script vient d'un téléchargement, le débloquer
            (Windows marque les fichiers téléchargés comme suspects)

                Unblock-File -Path .\Configure-OllamaAMD.ps1

  Étape 6 : Lancer le script

                .\Configure-OllamaAMD.ps1

  Étape 7 : Suivre les instructions affichées par le script
            Le script propose automatiquement de redémarrer Ollama.

  Étape 8 : Tester que tout fonctionne
            Dans un terminal PowerShell normal (pas admin) :

                ollama run mistral-nemo:12b --verbose
                >>> Bonjour, présente-toi en 50 mots

            Dans un autre terminal :

                ollama ps

            La colonne PROCESSOR doit afficher "100% GPU".


DOCUMENTATION DÉTAILLÉE
-----------------------

Pour une compréhension complète et le déploiement sur un poste de
production, lire le document :

    todo_ollama_adrasec_v3.docx

Ce document de 16 pages couvre :

  - Choix du matériel selon l'architecture iGPU AMD (Vega, RDNA2, RDNA3)
  - Diagnostic initial
  - Méthode interface graphique (pour ceux qui préfèrent le clic-souris)
  - Méthode PowerShell copier-coller
  - Méthode script .ps1 autonome (recommandée)
  - Vérification du fonctionnement
  - Résultats de benchmark mesurés sur deux configurations réelles
  - Résolution des erreurs d'allocation mémoire (par paliers)
  - Choix du modèle LLM selon l'usage
  - Mise à jour et maintenance d'Ollama
  - To-do list récapitulative
  - Conseils de déploiement et de sécurité


UTILISATION DU SCRIPT POWERSHELL
--------------------------------

Le script Configure-OllamaAMD.ps1 propose 4 modes via le paramètre -Action :

  Apply (défaut)    Applique la configuration optimale
                    Exemple : .\Configure-OllamaAMD.ps1

  Check             Affiche la configuration actuelle (audit, sans modif)
                    Exemple : .\Configure-OllamaAMD.ps1 -Action Check

  Restore           Restaure la configuration Ollama par défaut
                    Exemple : .\Configure-OllamaAMD.ps1 -Action Restore

  Bench             Affiche les commandes pour mesurer les performances
                    Exemple : .\Configure-OllamaAMD.ps1 -Action Bench

Paramètres optionnels :

  -ContextLength <int>    Longueur de contexte Ollama (défaut : 8192)
                          Valeurs recommandées :
                            VRAM dédiée < 1 Go  : 4096
                            VRAM dédiée 1-4 Go  : 8192 (défaut)
                            VRAM dédiée > 4 Go  : 16384 ou 32768

  -NumBatch <int>         Taille du batch de calcul (défaut : 256)
                          Réduire à 128 si erreur "failed to allocate"

Exemples avancés :

  Configuration pour mini-PC à faible VRAM (Vega 7/8) :
    .\Configure-OllamaAMD.ps1 -ContextLength 4096 -NumBatch 128

  Configuration pour mini-PC RDNA3 récent :
    .\Configure-OllamaAMD.ps1 -ContextLength 16384 -NumBatch 512

  Aide intégrée détaillée :
    Get-Help .\Configure-OllamaAMD.ps1 -Detailed


SÉCURITÉ ET CONFIANCE
---------------------

Comme pour tout script PowerShell téléchargé, il est RECOMMANDÉ d'ouvrir
le fichier Configure-OllamaAMD.ps1 dans un éditeur de texte AVANT de
l'exécuter, pour vérifier qu'il ne contient que des manipulations attendues.

  - Le script est commenté en français
  - Toutes les variables modifiées sont préfixées OLLAMA_
  - Aucune connexion réseau n'est établie
  - Aucun fichier n'est téléchargé
  - Aucune donnée personnelle n'est lue ou transmise

Éditeurs recommandés pour la relecture :
  - Notepad (Bloc-notes Windows)
  - Notepad++
  - VS Code (avec coloration syntaxique PowerShell)


DÉPANNAGE COURANT
-----------------

PROBLÈME : "Le fichier ne peut pas être chargé car l'exécution de scripts
            est désactivée sur ce système"

SOLUTION : Exécuter en PowerShell admin :
              Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned

-------------------------------------------------------------------------------

PROBLÈME : "Le terme '.\Configure-OllamaAMD.ps1' n'est pas reconnu"

SOLUTION : Vérifier que vous êtes dans le bon dossier :
              pwd
           Naviguer si besoin :
              cd C:\ADRASEC\OllamaConfig

-------------------------------------------------------------------------------

PROBLÈME : "ERREUR : ce script doit être lancé en tant qu'administrateur"

SOLUTION : Fermer PowerShell, rouvrir avec clic droit
           -> "Exécuter en tant qu'administrateur"

-------------------------------------------------------------------------------

PROBLÈME : Après application, ollama ps affiche encore "100% CPU"

SOLUTION : Vérifier que :
           1. Ollama a bien été redémarré (clic droit icône -> Quit, relancer)
           2. Vous avez ouvert un NOUVEAU terminal PowerShell après modif
           3. Les drivers AMD Adrenalin sont à jour (depuis amd.com)

           Consulter ensuite la section 9 du document v3 (Résolution des
           erreurs d'allocation mémoire) si le problème persiste.

-------------------------------------------------------------------------------

PROBLÈME : Erreur "failed to allocate compute pp buffers" au lancement
            d'un modèle

SOLUTION : VRAM dédiée insuffisante. Relancer le script avec des valeurs
           réduites :
              .\Configure-OllamaAMD.ps1 -ContextLength 4096 -NumBatch 128

           Voir section 9 du document pour les paliers complets.

-------------------------------------------------------------------------------

PROBLÈME : Régression de performance après mise à jour d'Ollama

SOLUTION : Effectuer un rollback vers la version précédente
           Voir section 11.6 du document v3.


PERFORMANCES ATTENDUES (À TITRE INDICATIF)
------------------------------------------

Mistral Nemo 12B (Q4_K_M, contexte 8192) après optimisation :

  Ryzen 5000U + Vega 7/8 + DDR4-3200 :
    - eval rate         : 6 à 8 tokens/s
    - prompt eval rate  : 30 à 50 tokens/s
    - Verdict           : utilisable, modèle 7B conseillé pour interactif

  Ryzen 6000H + RDNA2 + DDR5-4800 :
    - eval rate         : 8 à 12 tokens/s
    - prompt eval rate  : 60 à 90 tokens/s

  Ryzen 7000HS/8000HS + RDNA3 + DDR5-5600 :
    - eval rate         : 10 à 14 tokens/s
    - prompt eval rate  : 100 à 150 tokens/s
    - Verdict           : recommandé pour serveur ADRASEC

  Ryzen AI 300 + RDNA3.5 :
    - eval rate         : 12 à 18 tokens/s
    - prompt eval rate  : 150 à 250 tokens/s

Note : ces valeurs sont indicatives, mesurées en mai 2026 avec Ollama 0.23.
Les versions ultérieures d'Ollama améliorent régulièrement les performances.


COMPATIBILITÉ ET LIMITES
------------------------

Ce kit fonctionne avec :
  - Windows 10 (build 19041+) et Windows 11 (toutes versions)
  - Ollama 0.22 ou supérieur (versions 0.23.x recommandées)
  - PowerShell 5.1 (intégré à Windows) ou PowerShell 7+
  - Architectures AMD Vega 7/8 / RDNA 2 / RDNA 3 / RDNA 3.5

Limites connues :

  - Les iGPU AMD restent 10 à 30 fois plus lents que les GPU NVIDIA
    dédiés (RTX 4060+) pour l'inférence LLM
  - Les modèles 70B sont impraticables en local sur iGPU (< 3 t/s)
  - Pour des besoins de modèles très capables, Claude (Anthropic) ou
    ChatGPT (OpenAI) restent supérieurs. Un LLM local complète mais
    ne remplace pas totalement les services cloud.
  - Sur les mini-PC avec BIOS bridé (Geekom, GMKtec récents), l'option
    "UMA Frame Buffer Size" peut être indisponible. Dans ce cas, rester
    sur l'optimisation logicielle (le script s'en charge).


MAINTENANCE ET MISE À JOUR
--------------------------

Ollama est mis à jour fréquemment. Pour rester à jour :

  - Vérifier hebdomadairement la disponibilité d'une mise à jour
    (clic droit icône Ollama -> "Restart to update" si disponible)
  - Mettre à jour les modèles mensuellement :
        ollama pull mistral-nemo:12b
        ollama pull qwen2.5:7b
  - Refaire un benchmark trimestriel pour détecter les gains/régressions
  - Mettre à jour les drivers AMD Adrenalin semestriellement

Le détail complet de la procédure de maintenance figure en section 11
du document v3.


RECOMMANDATIONS DE MODÈLES SELON LE MATÉRIEL
--------------------------------------------

Pour un serveur ADRASEC, télécharger les modèles adaptés :

  Ryzen 5000U / Vega 7/8 :
      ollama pull qwen2.5:7b         (généraliste, RAG)
      ollama pull llama3.2:3b        (très rapide, court)
      ollama pull mistral:7b         (alternative)

  Ryzen 7000HS+ / RDNA3 :
      ollama pull mistral-nemo:12b   (rédaction, scénarios)
      ollama pull qwen2.5:14b        (raisonnement)
      ollama pull qwen2.5-coder:14b  (assistance code Python)
      ollama pull nomic-embed-text   (embeddings RAG)


BONNES PRATIQUES DE DÉPLOIEMENT EN ADRASEC
------------------------------------------

  - Limiter l'exposition d'Ollama au réseau ADRASEC interne uniquement
    (Ollama n'a pas d'authentification native)

  - En cas d'accès distant nécessaire, utiliser un reverse proxy
    (Caddy, Nginx) avec authentification

  - Surveiller les logs d'accès dans :
      C:\Users\<utilisateur>\AppData\Local\Ollama\server.log

  - Toujours relire et valider le contenu généré par le LLM avant
    intégration dans un document officiel ADRASEC

  - Conserver la mention "contenu généré par assistant IA, relu et
    validé par l'opérateur" pour traçabilité

  - Ne jamais utiliser le LLM pour produire du contenu opérationnel
    en temps réel pendant une mission active sans relecture humaine

  - Pour les documents d'exercice, conserver les mentions obligatoires
    "EXERCICE - EXERCICE - EXERCICE" et "FICTIF - FICTIF - FICTIF"
    conformément au protocole FNRASEC


HISTORIQUE DES VERSIONS
-----------------------

  v1.0 (mai 2026)  Document initial — diagnostic et procédure A7 Max
  v2.0 (mai 2026)  Ajout LX15 Pro (Vega 8), comparatif iGPU,
                   résolution erreurs allocation, choix matériel
  v3.0 (mai 2026)  Ajout script .ps1 autonome, section mise à jour
                   et maintenance, ce README d'accompagnement


CONTACT ET RETOURS D'EXPÉRIENCE
-------------------------------

Ce kit est mis à disposition gracieusement au réseau ADRASEC / FNRASEC.

Tout retour d'expérience (nouveaux benchmarks sur d'autres configurations
matérielles, signalement de problèmes, suggestions d'amélioration) est
bienvenu et sera intégré aux versions futures.

Contact : F1GBD via le réseau ADRASEC 77 / FNRASEC


LICENCE ET DIFFUSION
--------------------

Ce kit (document + script + README) est libre de diffusion au sein du
réseau ADRASEC / FNRASEC et plus largement de la communauté radio-amateur
française et francophone.

Vous pouvez :
  - Le redistribuer sans modification
  - L'utiliser pour former d'autres opérateurs
  - L'intégrer à des documents de formation ADRASEC
  - Le traduire si besoin

Merci de conserver la mention de l'auteur F1GBD / ADRASEC 77 en cas de
redistribution, et de partager en retour vos améliorations.


===============================================================================

  Bonne mise en service de votre serveur Ollama ADRASEC !

  73 de F1GBD
  ADRASEC 77 / FNRASEC

===============================================================================
