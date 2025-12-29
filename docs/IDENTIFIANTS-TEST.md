# Identifiants de test - Epic Events CRM

## Utilisateurs de test

Ces identifiants ont été créés par le script `seed_database.py` et sont disponibles pour tester l'application.

---

## Département GESTION

### Admin - Alice Dubois
- **Username** : `admin`
- **Password** : `Admin123!`
- **Email** : admin@epicevents.com
- **Téléphone** : +33123456789
- **Permissions** : Toutes (CRUD sur users, clients, contracts, events)

---

## Département COMMERCIAL

### Commercial 1 - John Smith
- **Username** : `commercial1`
- **Password** : `Commercial123!`
- **Email** : john.smith@epicevents.com
- **Téléphone** : +33198765432
- **Permissions** :
  - Créer des clients
  - Modifier ses propres clients
  - Créer des contrats pour ses clients
  - Modifier les contrats de ses clients

### Commercial 2 - Marie Martin
- **Username** : `commercial2`
- **Password** : `Commercial123!`
- **Email** : marie.martin@epicevents.com
- **Téléphone** : +33187654321
- **Permissions** :
  - Créer des clients
  - Modifier ses propres clients
  - Créer des contrats pour ses clients
  - Modifier les contrats de ses clients

---

## Département SUPPORT

### Support 1 - Pierre Durand
- **Username** : `support1`
- **Password** : `Support123!`
- **Email** : pierre.durand@epicevents.com
- **Téléphone** : +33176543210
- **Permissions** :
  - Voir tous les événements
  - Modifier ses propres événements (ceux qui lui sont assignés)
  - Filtrer les événements sans support assigné

### Support 2 - Sophie Bernard
- **Username** : `support2`
- **Password** : `Support123!`
- **Email** : sophie.bernard@epicevents.com
- **Téléphone** : +33165432109
- **Permissions** :
  - Voir tous les événements
  - Modifier ses propres événements (ceux qui lui sont assignés)
  - Filtrer les événements sans support assigné

---

## Notes importantes

⚠️ **Sécurité** :
- Ces mots de passe sont **temporaires** et destinés **uniquement aux tests**
- Tous les mots de passe sont hashés avec bcrypt dans la base de données
- En production, utilisez des mots de passe forts et uniques
- Les utilisateurs devraient changer leur mot de passe au premier login

📝 **Utilisation** :
- Utilisez ces identifiants pour tester les fonctionnalités de l'application
- Testez les différentes permissions selon les départements
- Vérifiez que les commerciaux ne peuvent pas modifier les clients des autres
- Vérifiez que les supports ne peuvent modifier que leurs propres événements

🔄 **Régénération** :
Pour recréer les utilisateurs de test :
```bash
poetry run python seed_database.py
```

---

## Matrice des permissions (RBAC)

| Action | GESTION | COMMERCIAL | SUPPORT |
|--------|---------|------------|---------|
| **Users** |
| Créer un utilisateur | ✅ | ❌ | ❌ |
| Modifier un utilisateur | ✅ | ❌ | ❌ |
| Supprimer un utilisateur | ✅ | ❌ | ❌ |
| Lister les utilisateurs | ✅ | ✅ (lecture seule) | ✅ (lecture seule) |
| **Clients** |
| Créer un client | ✅ | ✅ | ❌ |
| Modifier un client | ✅ | ✅ (ses clients) | ❌ |
| Supprimer un client | ✅ | ❌ | ❌ |
| Lister tous les clients (list-clients) | ✅ | ✅ | ✅ |
| Lister ses clients (my-clients) | ❌ | ✅ | ❌ |
| **Contrats** |
| Créer un contrat | ✅ | ✅ (pour ses clients) | ❌ |
| Modifier un contrat | ✅ | ✅ (ses contrats) | ❌ |
| Supprimer un contrat | ✅ | ❌ | ❌ |
| Lister tous les contrats (list-contracts) | ✅ | ✅ | ✅ |
| Filtrer contrats non signés | ✅ | ✅ | ❌ |
| Filtrer contrats non payés | ✅ | ✅ | ❌ |
| **Événements** |
| Créer un événement | ✅ | ❌ | ❌ |
| Modifier un événement | ✅ | ❌ | ✅ (ses événements) |
| Supprimer un événement | ✅ | ❌ | ❌ |
| Lister tous les événements (list-events) | ✅ | ✅ | ✅ |
| Assigner un support | ✅ | ❌ | ❌ |
| Filtrer événements sans support | ✅ | ❌ | ✅ |

---

## Scénarios de test recommandés

### Test 1 : Authentification
1. Login avec `admin` / `Admin123!` → ✅ Succès
2. Login avec `admin` / `WrongPassword` → ❌ Échec
3. Logout → ✅ Token supprimé

### Test 2 : Permissions COMMERCIAL
1. Login en tant que `commercial1`
2. Créer un client → ✅ Succès
3. Modifier le client créé → ✅ Succès
4. Tenter de créer un utilisateur → ❌ Refusé (permission insuffisante)
5. Tenter de modifier un client de `commercial2` → ❌ Refusé

### Test 3 : Permissions SUPPORT
1. Login en tant que `support1`
2. Lister tous les événements → ✅ Succès
3. Modifier un événement assigné à `support1` → ✅ Succès
4. Tenter de modifier un événement de `support2` → ❌ Refusé
5. Tenter de créer un client → ❌ Refusé

### Test 4 : Permissions GESTION
1. Login en tant que `admin`
2. Créer un utilisateur → ✅ Succès
3. Modifier n'importe quel client → ✅ Succès
4. Supprimer un contrat → ✅ Succès
5. Assigner un support à un événement → ✅ Succès

---

## Date de création
2025-10-12

## Dernière mise à jour
2025-12-29
