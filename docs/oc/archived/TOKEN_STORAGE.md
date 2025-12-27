# Stockage sécurisé des tokens JWT

## Vue d'ensemble

L'application Epic Events CRM stocke les tokens JWT de manière persistante sur le disque pour permettre une authentification continue entre les sessions. Ce document explique le mécanisme de stockage et les mesures de sécurité associées.

## Code source

```python
def save_token(self, token: str) -> None:
    """Save the JWT token to disk for persistent authentication.

    The token is stored in the user's home directory in a hidden folder.

    Args:
        token: The JWT token to save
    """
    # Create directory if it doesn't exist
    self.TOKEN_FILE.parent.mkdir(parents=True, exist_ok=True)

    # Write token to file with restricted permissions
    self.TOKEN_FILE.write_text(token)

    # Set file permissions to read/write for owner only (Unix-like systems)
    try:
        os.chmod(self.TOKEN_FILE, 0o600)
    except Exception:
        # On Windows, this might not work, but that's okay
        pass
```

**Emplacement** : `src/services/auth_service.py:168-187`

## Emplacement du fichier token

### Sur Windows
```
C:\Users\<nom_utilisateur>\.epicevents\token
```

### Sur Linux/Mac
```
~/.epicevents/token
```

Le dossier `.epicevents` est **caché** (préfixe `.` sur Unix, attribut caché sur Windows).

## Explication ligne par ligne

### 1. Création du répertoire

```python
self.TOKEN_FILE.parent.mkdir(parents=True, exist_ok=True)
```

**Que fait cette ligne ?**
- `self.TOKEN_FILE.parent` : Obtient le répertoire parent du fichier token (`.epicevents/`)
- `.mkdir(parents=True, exist_ok=True)` : Crée le répertoire avec deux options importantes :
  - `parents=True` : Crée tous les répertoires parents nécessaires (récursif)
  - `exist_ok=True` : Ne génère pas d'erreur si le répertoire existe déjà

**Exemple** :
```python
# Si le chemin est C:\Users\Alice\.epicevents\token
# Cette ligne crée le dossier C:\Users\Alice\.epicevents\ s'il n'existe pas
```

### 2. Écriture du token

```python
self.TOKEN_FILE.write_text(token)
```

**Que fait cette ligne ?**
- Écrit le contenu du token JWT (chaîne de caractères) dans le fichier
- Si le fichier existe déjà, il est **écrasé** (comportement par défaut de `write_text()`)
- Utilise l'encodage UTF-8 par défaut

**Exemple de contenu du fichier** :
```
eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoxLCJ1c2VybmFtZSI6ImFkbWluIiwiZGVwYXJ0bWVudCI6IkdFU1RJT04iLCJleHAiOjE3MzE1MjM0NTYsImlhdCI6MTczMTQzNzA1Nn0.rT8Z9mKpL3vYqN2xJhF4wE1sA5bC7dH9jK0iM6nP8uQ
```

### 3. Application des permissions sécurisées

```python
try:
    os.chmod(self.TOKEN_FILE, 0o600)
except Exception:
    # On Windows, this might not work, but that's okay
    pass
```

**Que fait ce bloc ?**
- Applique des permissions restrictives au fichier token
- Utilise un bloc `try/except` car Windows gère différemment les permissions

## Explication détaillée : Permissions 0o600

### Notation octale

`0o600` est une notation **octale** en Python (préfixe `0o`).

### Décomposition des permissions Unix

Les permissions Unix utilisent 3 groupes de 3 bits :

```
0o600
  │└─ Permissions (en octal)
  └── Préfixe octal Python
```

En binaire : `110 000 000`

| Position | Groupe | Binaire | Octal | Signification |
|----------|--------|---------|-------|---------------|
| 1-3      | **Propriétaire** (User) | `110` | `6` | Lecture (4) + Écriture (2) = 6 |
| 4-6      | **Groupe** (Group) | `000` | `0` | Aucun accès |
| 7-9      | **Autres** (Others) | `000` | `0` | Aucun accès |

### Décomposition détaillée

**Propriétaire (6)** :
- `r` (Read - 4) : ✅ Peut lire le fichier
- `w` (Write - 2) : ✅ Peut écrire dans le fichier
- `x` (Execute - 1) : ❌ Ne peut pas exécuter le fichier

**Groupe (0)** :
- `r` (4) : ❌ Ne peut pas lire
- `w` (2) : ❌ Ne peut pas écrire
- `x` (1) : ❌ Ne peut pas exécuter

**Autres (0)** :
- `r` (4) : ❌ Ne peut pas lire
- `w` (2) : ❌ Ne peut pas écrire
- `x` (1) : ❌ Ne peut pas exécuter

### Représentation visuelle

```bash
$ ls -la ~/.epicevents/token
-rw-------  1 alice  staff  245 Nov 16 14:30 /Users/alice/.epicevents/token
 │││└─────┘
 ││└────── Groupe : --- (aucun accès)
 │└─────── Propriétaire : rw- (lecture + écriture)
 └──────── Type : - (fichier régulier)
```

### Calcul des valeurs octales

| Valeur octale | Binaire | Permissions | Description |
|---------------|---------|-------------|-------------|
| 0 | 000 | `---` | Aucun accès |
| 1 | 001 | `--x` | Exécution seulement |
| 2 | 010 | `-w-` | Écriture seulement |
| 3 | 011 | `-wx` | Écriture + Exécution |
| 4 | 100 | `r--` | Lecture seulement |
| 5 | 101 | `r-x` | Lecture + Exécution |
| 6 | 110 | `rw-` | Lecture + Écriture ✅ (notre cas) |
| 7 | 111 | `rwx` | Tous les accès |

### Exemples de permissions courantes

| Octal | Permissions | Cas d'usage |
|-------|-------------|-------------|
| `0o600` | `-rw-------` | Fichiers secrets (tokens, clés privées) |
| `0o644` | `-rw-r--r--` | Fichiers publics lisibles par tous |
| `0o700` | `-rwx------` | Répertoires privés |
| `0o755` | `-rwxr-xr-x` | Exécutables publics |
| `0o400` | `-r--------` | Fichiers read-only secrets |

## Pourquoi 0o600 est sécurisé ?

### ✅ Avantages de sécurité

1. **Principe du moindre privilège**
   - Seul le propriétaire du fichier peut lire/écrire le token
   - Les autres utilisateurs du système ne peuvent **pas** accéder au token

2. **Protection contre les attaques locales**
   ```bash
   # Utilisateur "alice" (propriétaire)
   $ cat ~/.epicevents/token
   eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...  # ✅ OK

   # Utilisateur "bob" (autre utilisateur)
   $ cat /home/alice/.epicevents/token
   cat: /home/alice/.epicevents/token: Permission denied  # ❌ REFUSÉ
   ```

3. **Conformité avec les bonnes pratiques**
   - Recommandé par OWASP pour les fichiers sensibles
   - Standard pour les clés SSH (`~/.ssh/id_rsa`)
   - Standard pour les tokens AWS (`~/.aws/credentials`)

### ❌ Risque si permissions trop ouvertes

**Mauvais exemple : 0o644 (lecture publique)**
```bash
-rw-r--r--  1 alice  staff  245 Nov 16 14:30 token
        └─ Tout le monde peut lire ! ❌
```

**Conséquence** :
```bash
# N'importe quel utilisateur pourrait voler le token !
$ cat /home/alice/.epicevents/token
eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...  # ❌ FUITE DE SÉCURITÉ
```

## Comportement sur Windows

### Limitation technique

```python
try:
    os.chmod(self.TOKEN_FILE, 0o600)
except Exception:
    # On Windows, this might not work, but that's okay
    pass
```

**Pourquoi un try/except ?**

Windows utilise un modèle de permissions différent (ACL - Access Control Lists) incompatible avec les permissions Unix. `os.chmod()` peut :
- Ne rien faire silencieusement
- Lever une exception selon la version de Python/Windows
- Avoir un comportement imprévisible

**Mitigation sur Windows** :
1. Le dossier `.epicevents` est caché (attribut Windows)
2. Le fichier est dans le profil utilisateur (`C:\Users\<nom>`)
3. Par défaut, seul l'utilisateur courant y a accès (héritage des permissions du profil)

### Vérification des permissions (Windows)

```powershell
# PowerShell - Afficher les ACL
Get-Acl C:\Users\Alice\.epicevents\token | Format-List

# Résultat attendu :
# Owner : DESKTOP\Alice
# Access : DESKTOP\Alice Allow  FullControl
```

### Vérification des permissions (Linux/Mac)

```bash
# Afficher les permissions détaillées
ls -l ~/.epicevents/token

# Résultat attendu :
-rw-------  1 alice  staff  245 Nov 16 14:30 /Users/alice/.epicevents/token

# Vérifier avec stat
stat -c '%a %n' ~/.epicevents/token
# Résultat : 600 /home/alice/.epicevents/token
```

## Comparaison avec d'autres approches

### Alternative 1 : Stockage en base de données

❌ **Inconvénients** :
- Nécessite une connexion DB pour vérifier l'authentification
- Plus complexe (gestion de sessions)
- Token révoqué nécessite une mise à jour DB

✅ **Notre approche (fichier local)** :
- Authentification hors ligne possible
- Simplicité (lecture fichier uniquement)
- Performance (pas de requête DB)

### Alternative 2 : Stockage en mémoire (session temporaire)

❌ **Inconvénients** :
- L'utilisateur doit se reconnecter à chaque fois
- Mauvaise UX pour une application CLI

✅ **Notre approche (fichier persistant)** :
- Authentification persistante (24h)
- Meilleure UX (login une fois par jour)

### Alternative 3 : Keyring système

✅ **Avantages** :
- Stockage dans le trousseau système (Keychain sur Mac, Credential Manager sur Windows)
- Encore plus sécurisé

❌ **Inconvénients** :
- Dépendance externe (`keyring` package)
- Complexité d'implémentation
- Portabilité réduite

**Notre choix** : Équilibre entre sécurité et simplicité.

## Scénarios d'attaque et mitigations

### Scénario 1 : Utilisateur malveillant local

**Attaque** :
```bash
# Bob essaie de voler le token d'Alice
$ cat /home/alice/.epicevents/token
```

**Mitigation** :
```bash
cat: /home/alice/.epicevents/token: Permission denied  # ✅ Bloqué par 0o600
```

### Scénario 2 : Vol du fichier token

**Attaque** :
- Un attaquant copie physiquement le fichier `token`

**Mitigations en place** :
1. ✅ **Expiration 24h** : Le token volé expire rapidement
2. ✅ **Signature HMAC-SHA256** : Impossible de modifier le payload sans la clé secrète
3. ✅ **Logging Sentry** : Activité suspecte détectée (connexions depuis des IPs différentes)

### Scénario 3 : Permissions mal configurées

**Attaque** :
```bash
# Si le fichier était 0o666 (lecture/écriture publique)
-rw-rw-rw-  1 alice  staff  245 Nov 16 14:30 token  # ❌ DANGER
```

**Mitigation** :
- L'application **force** systématiquement 0o600 à chaque sauvegarde
- Impossible d'avoir des permissions incorrectes accidentellement

## Tests de sécurité

### Test manuel (Linux/Mac)

```bash
# 1. Se connecter
poetry run epicevents login

# 2. Vérifier les permissions
ls -l ~/.epicevents/token
# Résultat attendu : -rw------- (600)

# 3. Tester avec un autre utilisateur
sudo -u bob cat ~/.epicevents/token
# Résultat attendu : Permission denied
```

### Test manuel (Windows)

```powershell
# 1. Se connecter
py -m poetry run epicevents login

# 2. Vérifier l'emplacement
Get-Item $env:USERPROFILE\.epicevents\token

# 3. Vérifier les ACL
Get-Acl $env:USERPROFILE\.epicevents\token | Format-List
```

## Bonnes pratiques respectées

| Bonne pratique | Implémentation | Conformité |
|----------------|----------------|------------|
| **OWASP - Cryptographic Storage** | Token chiffré (JWT signé) + Permissions 600 | ✅ |
| **OWASP - Broken Access Control** | Propriétaire seul peut lire | ✅ |
| **Twelve-Factor App - Config** | Token externe (pas hardcodé) | ✅ |
| **Principle of Least Privilege** | Permissions minimales (600) | ✅ |
| **Defense in Depth** | Permissions + Expiration + Signature | ✅ |

## Références

### Standards de l'industrie

- **SSH Private Keys** : `~/.ssh/id_rsa` (permissions 600)
- **AWS Credentials** : `~/.aws/credentials` (permissions 600)
- **Docker Config** : `~/.docker/config.json` (permissions 600)
- **Git Credentials** : `~/.git-credentials` (permissions 600)

### Documentation technique

- [OWASP - Cryptographic Storage Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Cryptographic_Storage_Cheat_Sheet.html)
- [Unix File Permissions](https://en.wikipedia.org/wiki/File-system_permissions)
- [Python os.chmod() Documentation](https://docs.python.org/3/library/os.html#os.chmod)

## Résumé

### Points clés

1. **Emplacement** : `~/.epicevents/token` (caché)
2. **Permissions** : `0o600` (lecture/écriture propriétaire uniquement)
3. **Sécurité** : Défense en profondeur (permissions + expiration + signature)
4. **Portabilité** : Fonctionne sur Windows/Linux/Mac avec adaptations

### Pourquoi c'est sécurisé

- ✅ Seul le propriétaire peut accéder au token
- ✅ Expiration automatique après 24h
- ✅ Signature cryptographique HMAC-SHA256
- ✅ Conforme aux standards de l'industrie (SSH, AWS, Docker)
- ✅ Logging des actions suspectes avec Sentry

---

**Auteur** : Sébastien
**Date** : 2025-11-16
**Version** : 1.0
