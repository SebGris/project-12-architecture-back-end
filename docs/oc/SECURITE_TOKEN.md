# Sécurité des Tokens - Explication Technique

## Protection des Fichiers de Token

### Code concerné ([auth_service.py:183-187](src/services/auth_service.py#L183-L187))

```python
try:
    os.chmod(self.TOKEN_FILE, 0o600)
except Exception:
    # On Windows, this might not work, but that's okay
    pass
```

## Objectif

Cette implémentation vise à **protéger le fichier de token** contenant les informations d'authentification sensibles (JWT) contre les accès non autorisés.

## Explication Détaillée

### `os.chmod(self.TOKEN_FILE, 0o600)`

La fonction `os.chmod()` modifie les permissions d'accès au fichier en utilisant le système de permissions Unix/Linux.

**Signification de `0o600` (notation octale) :**

| Utilisateur | Chiffre | Permissions | Détail |
|-------------|---------|-------------|--------|
| Propriétaire | 6 | `rw-` | Lecture (4) + Écriture (2) = 6 |
| Groupe | 0 | `---` | Aucun accès |
| Autres | 0 | `---` | Aucun accès |

**Résultat :** `-rw-------` (seul le propriétaire peut lire et modifier le fichier)

### Gestion d'Exception

```python
try:
    ...
except Exception:
    pass
```

**Pourquoi cette gestion ?**

1. **Compatibilité Windows :** Le système de permissions Windows (ACL - Access Control Lists) fonctionne différemment des permissions Unix/Linux
2. **`os.chmod()` peut échouer** sur Windows sans impacter le fonctionnement de l'application
3. Le `pass` permet de **continuer l'exécution** même si la modification des permissions échoue

## Importance pour la Sécurité

### Principe de Moindre Privilège

Cette implémentation respecte le **principe de moindre privilège** (Principle of Least Privilege) :
- ✅ Seul l'utilisateur propriétaire peut accéder au token
- ❌ Les autres utilisateurs du système ne peuvent ni lire ni modifier le fichier
- 🔒 Protection contre les accès latéraux en cas de compromission partielle du système

### Conformité OWASP

Cette pratique répond aux recommandations **OWASP** concernant :
- Le stockage sécurisé des credentials
- La protection des données sensibles au repos (data at rest)
- La limitation de la surface d'attaque

## Alternatives et Améliorations Possibles

### Pour un Environnement de Production

1. **Utilisation d'un coffre-fort de secrets** (Secrets Manager) :
   - AWS Secrets Manager
   - Azure Key Vault
   - HashiCorp Vault

2. **Chiffrement du fichier** :
   - Cryptographie symétrique (AES-256)
   - Stockage de la clé dans un emplacement sécurisé distinct

3. **Variables d'environnement** :
   - Stockage en mémoire plutôt que sur disque
   - Pas de persistance du token

### Pour Windows Spécifiquement

```python
import platform
import win32security
import ntsecuritycon

if platform.system() == 'Windows':
    # Utilisation des ACL Windows natifs
    # pour une protection équivalente
```

## Conclusion

Cette implémentation représente une **bonne pratique de sécurité de base** pour protéger les tokens d'authentification en environnement Unix/Linux, avec une gestion gracieuse de l'incompatibilité Windows. Pour un système de production critique, des mécanismes de protection supplémentaires sont recommandés.
