<p align="center">
  <img src="../images/ADRAlink_logo.png" alt="ADRAlink" width="90">
</p>

# ADRAlink Pi — Fiche exploitation terrain

*Boîtier serveur ADRASEC — opérateur. Garder à côté du Pi.*

---

## 1. Allumer

1. Brancher l'**antenne / interface radio**, puis l'**alimentation** du Pi.
2. Attendre ~40 s : l'**écran** affiche le **tableau de bord ADRAlink**.
3. Vérifier l'en-tête : **Indicatif**, **IP**, transport, et les 4 pastilles
   **PAT · VARA · Serveur · Portail** au **vert**, `PAT : OK`.

> Rien à taper : serveur, portail, client web et (si activé) VARA FM démarrent
> tout seuls.

## 2. Vérifier que ça marche

- Sur un téléphone connecté au **WiFi ADRAlink** : ouvrir **`http://adralink.fr/`**
  (ou `http://IP-DU-PI/`). La page de téléchargement doit s'afficher.
- Bouton **« Utiliser dans le navigateur »** → écran de saisie : test = envoyer
  un court message, il apparaît dans le journal du tableau de bord.

## 3. Le sinistré

- Se connecte au **WiFi ADRAlink** (pas besoin d'Internet ni de forfait).
- **Android** : télécharge l'app, **ou** « Utiliser dans le navigateur ».
- **PC / tablette / iPhone** : « Utiliser dans le navigateur » (`/app`).
- Il **note son identifiant** (8 caractères) pour relire la réponse plus tard.

## 4. Changer le transport / le digipeater (SSH)

```bash
sudo adralink-config
```

Menu : **Telnet** (sans radio) · **VARA FM / HF / SAT** · **ARDOP**, puis
l'**indicatif RMS** (ex. `F1GBD`) et un **digipeater** éventuel (ex. `F5ZYI-7`).
→ construit `varafm:///F1GBD via F5ZYI-7` et redémarre le serveur.

## 5. Superviser / dépanner

| Besoin | Commande (SSH) |
|---|---|
| État des services | `systemctl status adralink-server --no-pager` |
| Journal en direct | `journalctl -u adralink-server -f` (ou `-u pat`, `-u vara`) |
| VARA en écoute ? | `ss -ltnp \| grep 8300` |
| Forcer une session radio | `curl -s -X POST http://127.0.0.1:8080/api/v1/operator/connect` |
| `adralink.fr` ne répond pas | DNS du routeur → IP du Pi (PORTAL_SETUP.md) ; côté tel. : `http://` + DNS privé désactivé |

## 6. Éteindre proprement

```bash
sudo poweroff
```

Attendre l'**extinction complète** (LED) **avant** de couper l'alimentation.

---

*Accès : `http://adralink.fr/` · `/app` (client web) · API `:8080`. Config : `sudo
adralink-config`. — ADRAlink v1.1.2 · F1GBD / ADRASEC 77 / FNRASEC · GNU GPL v3.0*
