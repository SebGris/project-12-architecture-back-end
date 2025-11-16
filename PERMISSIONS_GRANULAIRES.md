# Permissions granulaires - Epic Events CRM

## Vue d'ensemble

Ce document décrit les améliorations apportées au système de permissions pour implémenter un contrôle d'accès plus fin sur les commandes CLI.

## Modifications implémentées

### 1. `filter-my-events` - Auto-détection de l'utilisateur

**Avant :**
```bash
epicevents filter-my-events
# Demandait l'ID du contact support
ID du contact support: [...]
```

**Après :**
```bash
epicevents filter-my-events
# Détecte automatiquement l'utilisateur connecté
# Affiche uniquement SES événements
```

**Changements :**
- ✅ Suppression du paramètre `support_contact_id`
- ✅ Utilisation automatique de `auth_service.get_current_user()`
- ✅ Expérience utilisateur améliorée (pas de saisie inutile)

**Code :**
```python
@app.command()
@require_department(Department.SUPPORT)
def filter_my_events():
    # Get current user (already validated as SUPPORT by decorator)
    user = auth_service.get_current_user()
    events = event_service.get_events_by_support_contact(user.id)
```

---

### 2. `update-client` - Restriction pour les commerciaux

**Règle de permission :**
- **GESTION** : Peut modifier tous les clients
- **COMMERCIAL** : Peut modifier uniquement ses propres clients (ceux dont il est le `sales_contact`)

**Implémentation :**
```python
# Permission check: COMMERCIAL can only update their own clients
if current_user.department == Department.COMMERCIAL:
    if client.sales_contact_id != current_user.id:
        console.print_error(
            "Vous ne pouvez modifier que vos propres clients"
        )
        console.print_error(
            f"Ce client est assigné à {client.sales_contact.first_name} {client.sales_contact.last_name}"
        )
        raise typer.Exit(code=1)
```

**Exemple d'erreur :**
```
[ERREUR] Vous ne pouvez modifier que vos propres clients
[ERREUR] Ce client est assigné à Marie Martin
```

---

### 3. `update-contract` - Restriction pour les commerciaux

**Règle de permission :**
- **GESTION** : Peut modifier tous les contrats
- **COMMERCIAL** : Peut modifier uniquement les contrats de ses propres clients

**Implémentation :**
```python
# Permission check: COMMERCIAL can only update contracts of their own clients
if current_user.department == Department.COMMERCIAL:
    if contract.client.sales_contact_id != current_user.id:
        console.print_error(
            "Vous ne pouvez modifier que les contrats de vos propres clients"
        )
        console.print_error(
            f"Ce contrat appartient au client {contract.client.first_name} {contract.client.last_name}, "
            f"assigné à {contract.client.sales_contact.first_name} {contract.client.sales_contact.last_name}"
        )
        raise typer.Exit(code=1)
```

**Exemple d'erreur :**
```
[ERREUR] Vous ne pouvez modifier que les contrats de vos propres clients
[ERREUR] Ce contrat appartient au client Jean Dupont, assigné à John Smith
```

---

### 4. `update-event-attendees` - Restriction pour le support

**Règle de permission :**
- **GESTION** : Peut modifier tous les événements
- **SUPPORT** : Peut modifier uniquement ses propres événements (ceux dont il est le `support_contact`)

**Implémentation :**
```python
# Permission check: SUPPORT can only update their own events
if current_user.department == Department.SUPPORT:
    if not event.support_contact_id or event.support_contact_id != current_user.id:
        console.print_error(
            "Vous ne pouvez modifier que vos propres événements"
        )
        if event.support_contact:
            console.print_error(
                f"Cet événement est assigné à {event.support_contact.first_name} {event.support_contact.last_name}"
            )
        else:
            console.print_error("Cet événement n'a pas encore de contact support assigné")
        raise typer.Exit(code=1)
```

**Exemple d'erreur :**
```
[ERREUR] Vous ne pouvez modifier que vos propres événements
[ERREUR] Cet événement est assigné à Sophie Durand
```

---

## Matrice de permissions

| Commande | GESTION | COMMERCIAL | SUPPORT |
|----------|---------|------------|---------|
| **filter-my-events** | ❌ | ❌ | ✅ (ses events uniquement) |
| **update-client** | ✅ (tous) | ✅ (ses clients) | ❌ |
| **update-contract** | ✅ (tous) | ✅ (ses contrats) | ❌ |
| **update-event-attendees** | ✅ (tous) | ❌ | ✅ (ses events) |

---

## Avantages

### 🔒 Sécurité renforcée
- Les utilisateurs ne peuvent plus modifier les données qui ne leur appartiennent pas
- Prévention des modifications accidentelles ou malveillantes

### 👤 Responsabilisation
- Chaque département ne gère que ce qui le concerne
- Traçabilité claire des modifications

### ✅ Conformité
- Respect du principe de moindre privilège
- Séparation des responsabilités (Separation of Duties)

### 🎯 UX améliorée
- `filter-my-events` ne demande plus d'ID inutile
- Messages d'erreur explicites et informatifs

---

## Tests à effectuer

### Test 1 : `filter-my-events` (SUPPORT)
```bash
# Se connecter en tant que support1
epicevents login
# Username: support1
# Password: password123

# Lister ses événements
epicevents filter-my-events
# ✅ Devrait afficher uniquement les événements assignés à support1
```

### Test 2 : `update-client` (COMMERCIAL)
```bash
# Se connecter en tant que commercial1
epicevents login
# Username: commercial1
# Password: password123

# Tenter de modifier un client qui lui appartient
epicevents update-client
# ID du client: 1 (si appartient à commercial1)
# ✅ Devrait fonctionner

# Tenter de modifier un client d'un autre commercial
epicevents update-client
# ID du client: X (appartient à commercial2)
# ❌ Devrait refuser avec message d'erreur
```

### Test 3 : `update-contract` (COMMERCIAL)
```bash
# Même logique que update-client
# Les commerciaux ne peuvent modifier que les contrats de leurs clients
```

### Test 4 : `update-event-attendees` (SUPPORT)
```bash
# Se connecter en tant que support1
epicevents login

# Modifier un événement qui lui appartient
epicevents update-event-attendees
# ID de l'événement: Y (assigné à support1)
# ✅ Devrait fonctionner

# Modifier un événement d'un autre support
epicevents update-event-attendees
# ID de l'événement: Z (assigné à support2)
# ❌ Devrait refuser
```

---

## Fichiers modifiés

- `src/cli/commands.py` :
  - Ligne ~1058 : `filter_my_events()` - Suppression paramètre, auto-détection
  - Ligne ~1189 : `update_client()` - Ajout vérification COMMERCIAL
  - Ligne ~1327 : `update_contract()` - Ajout vérification COMMERCIAL
  - Ligne ~1474 : `update_event_attendees()` - Ajout vérification SUPPORT

---

## Prochaines étapes

1. ✅ Implémenter les permissions granulaires
2. ⏳ Tests manuels des commandes
3. ⏳ Nettoyage des tests existants
4. ⏳ Ajout de tests unitaires automatisés
5. ⏳ Documentation utilisateur mise à jour

---

## Notes techniques

### Pattern utilisé
Toutes les vérifications de permissions suivent le même pattern :

```python
# 1. Récupérer l'utilisateur connecté
current_user = auth_service.get_current_user()

# 2. Vérifier l'existence de la ressource
resource = service.get_resource(resource_id)

# 3. Vérifier les permissions selon le département
if current_user.department == Department.XXX:
    if resource.owner_id != current_user.id:
        console.print_error("Message d'erreur explicite")
        raise typer.Exit(code=1)

# 4. Continuer avec l'opération
```

### Principe SOLID respecté
- **Open/Closed** : Ajout de permissions sans modifier le décorateur existant
- **Single Responsibility** : Chaque vérification est localisée dans la commande concernée
- **Liskov Substitution** : Les sous-départements (COMMERCIAL, SUPPORT) ajoutent des restrictions sans casser le comportement de base
