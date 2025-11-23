# Guide de Démonstration - Epic Events CRM

Ce guide présente toutes les commandes pour démontrer la conformité à 100% avec le cahier des charges.

## Table des matières

1. [Prérequis et authentification](#1-prérequis-et-authentification)
2. [Besoins généraux](#2-besoins-généraux)
3. [Équipe GESTION](#3-équipe-gestion)
4. [Équipe COMMERCIAL](#4-équipe-commercial)
5. [Équipe SUPPORT](#5-équipe-support)

---

## 1. Prérequis et authentification

### 1.1 Installation et configuration

```bash
# Installer les dépendances
poetry install

# Configurer la base de données (si première utilisation)
poetry run alembic upgrade head

# Créer un utilisateur admin initial (si nécessaire)
poetry run python scripts/create_admin.py
```

### 1.2 Se connecter

```bash
poetry run epicevents login
# Username: admin
# Password: Admin123!
```

**Explication** :
> "Je me connecte avec un utilisateur du département GESTION. L'application génère un token JWT signé avec HMAC-SHA256, valide pour 24 heures, et le stocke dans `C:\Users\<nom utilisateur>\.epicevents\token` sous Windows ou `~/.epicevents/token` sous Linux/Mac."

**Résultat attendu** :
```
[INFO] Sentry non configuré (SENTRY_DSN manquant)
+-----------------------------------------------------------------------------+
| ✓ Bienvenue Alice Dubois !                                                 |
| Département : GESTION                                                       |
| Session     : Valide pour 24 heures                                        |
+-----------------------------------------------------------------------------+
```

### 1.3 Vérifier l'utilisateur connecté

```bash
poetry run epicevents whoami
```

**Explication** :
> "Cette commande affiche les informations de l'utilisateur actuellement connecté en décodant le token JWT."

**Résultat attendu** :
```
+-----------------------------------------------------------------------------+
| ID          : 1                                                             |
| Username    : admin                                                         |
| Nom complet : Alice Dubois                                                  |
| Email       : alice.dubois@epicevents.com                                   |
| Département : GESTION                                                       |
+-----------------------------------------------------------------------------+
```

### 1.4 Se déconnecter

```bash
poetry run epicevents logout
```

**Explication** :
> "Cette commande supprime le token JWT stocké localement."

**Résultat attendu** :
```
✓ Vous êtes maintenant déconnecté
```

---

## 2. Besoins généraux

### 2.1 ✅ Chaque collaborateur a ses identifiants

**Démonstration** : Voir [1.2 Se connecter](#12-se-connecter)

**Points clés** :
- Authentification par username/password
- Token JWT avec expiration 24h
- Mots de passe hashés avec bcrypt
- Stockage sécurisé du token (permissions 0o600)

### 2.2 ✅ Association à un rôle (département)

```bash
poetry run epicevents whoami
```

**Explication** :
> "Chaque utilisateur est obligatoirement associé à un département (COMMERCIAL, GESTION, ou SUPPORT). Le département est inclus dans le token JWT et vérifié à chaque commande."

**Résultat attendu** :
```
Département : GESTION
```

### 2.3 ✅ Accès en lecture pour tous les collaborateurs

#### Voir tous les contrats non signés

```bash
poetry run epicevents filter-unsigned-contracts
```

**Explication** :
> "Cette commande est accessible à tous les utilisateurs authentifiés (via `@require_department()` sans paramètres). Elle affiche tous les contrats avec `is_signed = False`."

**Résultat attendu** :
```
+-----------------------------------------------------------------------------+
| Contrats non signés                                                         |
+-----------------------------------------------------------------------------+
| Contract ID        : 3                                                      |
| Client             : Jean Martin                                            |
| Total Amount       : 5000.00€                                               |
| Remaining Amount   : 5000.00€                                               |
| Status             : Non signé                                              |
+-----------------------------------------------------------------------------+
Total: 1 contrat(s) non signé(s)
```

#### Voir tous les contrats non payés

```bash
poetry run epicevents filter-unpaid-contracts
```

**Explication** :
> "Affiche tous les contrats avec `remaining_amount > 0`. Accessible à tous les départements."

#### Voir tous les événements sans support

```bash
poetry run epicevents filter-unassigned-events
```

**Explication** :
> "Affiche tous les événements où `support_contact_id IS NULL`. Accessible à tous les départements pour une transparence complète des données."

---

## 3. Équipe GESTION

### Connexion avec un utilisateur GESTION

```bash
poetry run epicevents login
# Username: admin
# Password: Admin123!
```

### 3.1 ✅ Créer des collaborateurs

```bash
poetry run epicevents create-user
```

**Prompts interactifs** :
```
Nom d'utilisateur : john_commercial
Prénom : John
Nom : Doe
Email : john.doe@epicevents.com
Téléphone : 0612345678
Mot de passe : [masqué]

Départements disponibles:
1. COMMERCIAL
2. GESTION
3. SUPPORT

Choisir un département (numéro) : 1
```

**Explication** :
> "Seul le département GESTION peut créer des utilisateurs (`@require_department(Department.GESTION)`). Le mot de passe est automatiquement hashé avec bcrypt avant stockage. Les contraintes UNIQUE sur username et email sont vérifiées."

**Résultat attendu** :
```
+-----------------------------------------------------------------------------+
| ✓ Utilisateur john_commercial créé avec succès!                            |
| ID          : 5                                                             |
| Nom complet : John Doe                                                      |
| Email       : john.doe@epicevents.com                                       |
| Département : COMMERCIAL                                                    |
+-----------------------------------------------------------------------------+
```

### 3.2 ✅ Mettre à jour des collaborateurs

```bash
poetry run epicevents update-user
```

**Prompts interactifs** :
```
ID de l'utilisateur : 5
Nouveau nom d'utilisateur (laisser vide pour ne pas modifier) : [Enter]
Nouveau prénom (laisser vide pour ne pas modifier) : [Enter]
Nouveau nom (laisser vide pour ne pas modifier) : [Enter]
Nouvel email (laisser vide pour ne pas modifier) : john.updated@epicevents.com
Nouveau téléphone (laisser vide pour ne pas modifier) : 0687654321
Nouveau département (1=COMMERCIAL, 2=GESTION, 3=SUPPORT, 0=pas de changement) : 0
```

**Explication** :
> "Cette commande permet de modifier sélectivement les champs d'un utilisateur. Les champs laissés vides ne sont pas modifiés. Réservée au département GESTION."

**Résultat attendu** :
```
+-----------------------------------------------------------------------------+
| Mise à jour d'un utilisateur                                                |
+-----------------------------------------------------------------------------+
| ✓ Utilisateur mis à jour avec succès!                                      |
| ID          : 5                                                             |
| Username    : john_commercial                                               |
| Nom complet : John Doe                                                      |
| Email       : john.updated@epicevents.com                                   |
| Téléphone   : 0687654321                                                    |
| Département : COMMERCIAL                                                    |
+-----------------------------------------------------------------------------+
```

### 3.3 ✅ Supprimer des collaborateurs

```bash
poetry run epicevents delete-user
```

**Prompts interactifs** :
```
ID de l'utilisateur à supprimer : 5
Êtes-vous sûr de vouloir supprimer cet utilisateur ? (oui/non) : True
```

**Explication** :
> "Avant suppression, les informations de l'utilisateur sont affichées. Une confirmation explicite est requise (`--confirm True`). ATTENTION : cette action est irréversible."

**Résultat attendu** :
```
+-----------------------------------------------------------------------------+
| Suppression d'un utilisateur                                                |
+-----------------------------------------------------------------------------+
| ID          : 5                                                             |
| Username    : john_commercial                                               |
| Nom complet : John Doe                                                      |
| Email       : john.updated@epicevents.com                                   |
| Département : COMMERCIAL                                                    |
+-----------------------------------------------------------------------------+
| ✓ Utilisateur john_commercial (ID: 5) supprimé avec succès!                |
+-----------------------------------------------------------------------------+
```

### 3.4 ✅ Créer tous les contrats

```bash
poetry run epicevents create-contract
```

**Prompts interactifs** :
```
ID du client : 1
Montant total : 10000.00
Montant restant : 10000.00
Contrat signé ? : False
```

**Explication** :
> "Le département GESTION peut créer des contrats pour **tous les clients** sans restriction de propriété (contrairement aux COMMERCIAL qui ne peuvent créer que pour leurs propres clients)."

**Résultat attendu** :
```
+-----------------------------------------------------------------------------+
| ✓ Contrat créé avec succès!                                                |
| ID             : 7                                                          |
| Client         : Marie Dupont                                               |
| Montant total  : 10000.00€                                                  |
| Montant restant: 10000.00€                                                  |
| Statut         : Non signé                                                  |
+-----------------------------------------------------------------------------+
```

### 3.5 ✅ Modifier tous les contrats

```bash
poetry run epicevents update-contract
```

**Prompts interactifs** :
```
ID du contrat : 7
Nouveau montant total (laisser vide pour ne pas modifier) : [Enter]
Nouveau montant restant (laisser vide pour ne pas modifier) : 8000.00
Marquer comme signé ? : True
```

**Explication** :
> "Le département GESTION peut modifier **tous les contrats** sans vérification de propriété. Les COMMERCIAL ne peuvent modifier que les contrats de leurs propres clients."

**Résultat attendu** :
```
+-----------------------------------------------------------------------------+
| ✓ Contrat mis à jour avec succès!                                          |
| ID             : 7                                                          |
| Client         : Marie Dupont                                               |
| Montant total  : 10000.00€                                                  |
| Montant restant: 8000.00€                                                   |
| Statut         : Signé ✓                                                    |
+-----------------------------------------------------------------------------+
```

### 3.6 ✅ Filtrer les événements sans support

```bash
poetry run epicevents filter-unassigned-events
```

**Explication** :
> "Voir [2.3 Accès en lecture pour tous](#23--accès-en-lecture-pour-tous-les-collaborateurs). Cette commande est accessible à tous les départements."

### 3.7 ✅ Assigner un support à un événement

```bash
poetry run epicevents assign-support
```

**Prompts interactifs** :
```
ID de l'événement : 2
ID du contact support : 4
```

**Explication** :
> "Seul le département GESTION peut assigner (ou réassigner) un contact support à un événement (`@require_department(Department.GESTION)`). Le système vérifie que l'utilisateur assigné appartient bien au département SUPPORT."

**Résultat attendu** :
```
+-----------------------------------------------------------------------------+
| ✓ Contact support assigné avec succès à l'événement 'Conférence Tech 2025'!|
| Event ID       : 2                                                          |
| Contract ID    : 1                                                          |
| Client         : Marie Dupont                                               |
| Support contact: Sophie Martin (ID: 4)                                      |
+-----------------------------------------------------------------------------+
```

---

## 4. Équipe COMMERCIAL

### Connexion avec un utilisateur COMMERCIAL

```bash
poetry run epicevents logout
poetry run epicevents login
# Username: commercial1
# Password: Commercial123!
```

### 4.1 ✅ Créer des clients (auto-assignation)

```bash
poetry run epicevents create-client
```

**Prompts interactifs** :
```
Prénom : Pierre
Nom : Durant
Email : pierre.durant@example.com
Téléphone : 0698765432
Nom de l'entreprise : TechCorp SARL
```

**Explication** :
> "Lors de la création d'un client, le champ `sales_contact_id` est automatiquement défini avec l'ID de l'utilisateur COMMERCIAL connecté (`client.sales_contact_id = current_user.id`). Aucun paramètre n'est requis, l'assignation est automatique."

**Résultat attendu** :
```
+-----------------------------------------------------------------------------+
| ✓ Client créé avec succès!                                                 |
| ID          : 8                                                             |
| Nom complet : Pierre Durant                                                 |
| Email       : pierre.durant@example.com                                     |
| Entreprise  : TechCorp SARL                                                 |
| Contact commercial: Bob Martin (ID: 2) [Vous]                               |
+-----------------------------------------------------------------------------+
```

### 4.2 ✅ Mettre à jour leurs propres clients

```bash
poetry run epicevents update-client
```

**Prompts interactifs** :
```
ID du client : 8
Nouveau prénom (laisser vide pour ne pas modifier) : [Enter]
Nouveau nom (laisser vide pour ne pas modifier) : [Enter]
Nouvel email (laisser vide pour ne pas modifier) : pierre.updated@example.com
Nouveau téléphone (laisser vide pour ne pas modifier) : [Enter]
Nouveau nom d'entreprise (laisser vide pour ne pas modifier) : [Enter]
```

**Explication** :
> "Un utilisateur COMMERCIAL ne peut modifier que les clients dont il est le `sales_contact` (`client.sales_contact_id == current_user.id`). Si le client appartient à un autre commercial, la commande affiche une erreur."

**Résultat attendu (succès)** :
```
+-----------------------------------------------------------------------------+
| ✓ Client mis à jour avec succès!                                           |
| ID          : 8                                                             |
| Nom complet : Pierre Durant                                                 |
| Email       : pierre.updated@example.com                                    |
| Entreprise  : TechCorp SARL                                                 |
+-----------------------------------------------------------------------------+
```

**Résultat attendu (échec - client d'un autre commercial)** :
```
❌ Vous ne pouvez modifier que vos propres clients
Ce client est assigné à Alice Dubois
```

### 4.3 ✅ Modifier les contrats de leurs clients

```bash
poetry run epicevents update-contract
```

**Prompts interactifs** :
```
ID du contrat : 3
Nouveau montant total (laisser vide pour ne pas modifier) : [Enter]
Nouveau montant restant (laisser vide pour ne pas modifier) : 4500.00
Marquer comme signé ? : [Enter]
```

**Explication** :
> "Un utilisateur COMMERCIAL ne peut modifier que les contrats dont le client lui appartient (`contract.client.sales_contact_id == current_user.id`). La vérification se fait via la relation `contract.client.sales_contact_id`."

**Résultat attendu (succès)** :
```
+-----------------------------------------------------------------------------+
| ✓ Contrat mis à jour avec succès!                                          |
| ID             : 3                                                          |
| Client         : Pierre Durant                                              |
| Montant restant: 4500.00€                                                   |
+-----------------------------------------------------------------------------+
```

**Résultat attendu (échec - contrat d'un autre commercial)** :
```
❌ Vous ne pouvez modifier que les contrats de vos propres clients
```

### 4.4 ✅ Filtrer les contrats non signés

```bash
poetry run epicevents filter-unsigned-contracts
```

**Explication** :
> "Voir [2.3 Accès en lecture](#23--accès-en-lecture-pour-tous-les-collaborateurs). Cette commande affiche tous les contrats non signés, accessible à tous les départements."

### 4.5 ✅ Filtrer les contrats non payés

```bash
poetry run epicevents filter-unpaid-contracts
```

**Explication** :
> "Affiche tous les contrats avec `remaining_amount > 0`. Accessible à tous les départements pour visibilité complète."

### 4.6 ✅ Créer un événement pour un client avec contrat signé

```bash
poetry run epicevents create-event
```

**Prompts interactifs** :
```
Nom de l'événement : Lancement Produit 2026
ID du contrat : 1
Date et heure de début (YYYY-MM-DD HH:MM) : 2026-01-15 14:00
Date et heure de fin (YYYY-MM-DD HH:MM) : 2026-01-15 18:00
Lieu : Palais des Congrès, Paris
Nombre de participants : 150
Notes (optionnel) : Événement de lancement du nouveau produit
ID du contact support (optionnel, laisser vide) : [Enter]
```

**Explication** :
> "Deux vérifications critiques sont effectuées :
> 1. **Contrat signé** : `contract.is_signed == True`
> 2. **Propriété** : `contract.client.sales_contact_id == current_user.id`
>
> Un utilisateur COMMERCIAL ne peut créer des événements que pour les contrats signés de ses propres clients. Les utilisateurs GESTION n'ont pas de restriction de propriété."

**Résultat attendu (succès)** :
```
+-----------------------------------------------------------------------------+
| ✓ Événement créé avec succès!                                              |
| ID          : 10                                                            |
| Nom         : Lancement Produit 2025                                        |
| Contract ID : 1                                                             |
| Client      : Pierre Durant                                                 |
| Début       : 15/06/2025 14:00                                              |
| Fin         : 15/06/2025 18:00                                              |
| Lieu        : Palais des Congrès, Paris                                     |
| Participants: 150                                                           |
+-----------------------------------------------------------------------------+
```

**Résultat attendu (échec - contrat non signé)** :
```
❌ Le contrat #3 n'est pas encore signé.
Seuls les contrats signés peuvent avoir des événements.
```

**Résultat attendu (échec - client d'un autre commercial)** :
```
❌ Vous ne pouvez créer des événements que pour vos propres clients
Ce contrat appartient au client Marie Dupont, assigné à Alice Dubois
```

---

## 5. Équipe SUPPORT

### Connexion avec un utilisateur SUPPORT

```bash
poetry run epicevents logout
poetry run epicevents login
# Username: support1
# Password: Support123!
```

### 5.1 ✅ Filtrer leurs événements assignés

```bash
poetry run epicevents filter-my-events
```

**Explication** :
> "Cette commande affiche **uniquement** les événements assignés à l'utilisateur SUPPORT connecté (`WHERE support_contact_id = current_user.id`). Aucun paramètre n'est requis, l'utilisateur est détecté automatiquement via le token JWT. Réservée au département SUPPORT."

**Résultat attendu** :
```
+-----------------------------------------------------------------------------+
| Mes événements                                                              |
+-----------------------------------------------------------------------------+
| Event ID       : 2                                                          |
| Contract ID    : 1                                                          |
| Client         : Pierre Durant                                              |
| Contact client : pierre.durant@example.com / 0698765432                     |
| Début          : 15/06/2025 14:00                                           |
| Fin            : 15/06/2025 18:00                                           |
| Support contact: Sophie Martin (ID: 4) [Vous]                               |
| Lieu           : Palais des Congrès, Paris                                  |
| Participants   : 150                                                        |
| Notes          : Événement de lancement du nouveau produit                  |
+-----------------------------------------------------------------------------+
| Event ID       : 5                                                          |
| Contract ID    : 3                                                          |
| Client         : Marie Dupont                                               |
| Contact client : marie.dupont@example.com / 0612345678                      |
| Début          : 10/07/2025 09:00                                           |
| Fin            : 10/07/2025 17:00                                           |
| Support contact: Sophie Martin (ID: 4) [Vous]                               |
| Lieu           : Centre de Conventions, Lyon                                |
| Participants   : 80                                                         |
+-----------------------------------------------------------------------------+
✓ Total: 2 événement(s) assigné(s) à Sophie Martin
```

### 5.2 ✅ Mettre à jour leurs événements

```bash
poetry run epicevents update-event
```

**Prompts interactifs** :
```
ID de l'événement : 2
Nouveau nom (laisser vide pour ne pas modifier) : [Enter]
Nouvelle date de début YYYY-MM-DD HH:MM (laisser vide pour ne pas modifier) : [Enter]
Nouvelle date de fin YYYY-MM-DD HH:MM (laisser vide pour ne pas modifier) : [Enter]
Nouveau lieu (laisser vide pour ne pas modifier) : [Enter]
Nouveau nombre de participants (-1 pour ne pas modifier) : 175
Nouvelles notes (laisser vide pour ne pas modifier) : [Enter]
```

**Explication** :
> "Un utilisateur SUPPORT ne peut modifier que les événements qui lui sont assignés (`event.support_contact_id == current_user.id`). Si l'événement appartient à un autre utilisateur SUPPORT ou n'a pas encore de support assigné, la commande affiche une erreur. Les utilisateurs GESTION peuvent modifier tous les événements."

**Résultat attendu (succès)** :
```
+-----------------------------------------------------------------------------+
| Mise à jour du nombre de participants                                       |
+-----------------------------------------------------------------------------+
| ✓ Nombre de participants mis à jour avec succès pour l'événement #2!       |
| ID             : 2                                                          |
| Nom            : Lancement Produit 2025                                     |
| Contrat ID     : 1                                                          |
| Début          : 15/06/2025 14:00                                           |
| Fin            : 15/06/2025 18:00                                           |
| Lieu           : Palais des Congrès, Paris                                  |
| Participants   : 175                                                        |
| Support contact: Sophie Martin (ID: 4)                                      |
+-----------------------------------------------------------------------------+
```

**Résultat attendu (échec - événement d'un autre support)** :
```
❌ Vous ne pouvez modifier que vos propres événements
Cet événement est assigné à Marc Leroy
```

**Résultat attendu (échec - événement sans support)** :
```
❌ Vous ne pouvez modifier que vos propres événements
Cet événement n'a pas encore de contact support assigné
```

---

## 6. Commandes bonus

### 6.1 Signer un contrat (COMMERCIAL)

```bash
poetry run epicevents sign-contract
```

**Prompts interactifs** :
```
ID du contrat : 3
```

**Explication** :
> "Cette commande permet à un utilisateur COMMERCIAL de marquer un contrat comme signé (`is_signed = True`). Vérification de propriété : le client doit appartenir au commercial."

### 6.2 Enregistrer un paiement (COMMERCIAL)

```bash
poetry run epicevents update-contract-payment
```

**Prompts interactifs** :
```
ID du contrat : 1
Montant du paiement : 2000.00
```

**Explication** :
> "Cette commande permet d'enregistrer un paiement pour un contrat. Le `remaining_amount` est automatiquement réduit. Vérification de propriété pour les COMMERCIAL."

**Résultat attendu** :
```
+-----------------------------------------------------------------------------+
| ✓ Paiement enregistré avec succès!                                         |
| ID             : 1                                                          |
| Montant total  : 10000.00€                                                  |
| Montant restant: 2500.00€ (75% payé)                                        |
+-----------------------------------------------------------------------------+
```

---

## 7. Matrice de permissions

| Commande | COMMERCIAL | GESTION | SUPPORT |
|----------|------------|---------|---------|
| `login` / `logout` / `whoami` | ✅ | ✅ | ✅ |
| `create-user` | ❌ | ✅ | ❌ |
| `update-user` | ❌ | ✅ | ❌ |
| `delete-user` | ❌ | ✅ | ❌ |
| `create-client` | ✅ (auto-assigné) | ✅ | ❌ |
| `update-client` | ✅ (ses clients) | ✅ (tous) | ❌ |
| `create-contract` | ✅ (ses clients) | ✅ (tous) | ❌ |
| `update-contract` | ✅ (ses clients) | ✅ (tous) | ❌ |
| `sign-contract` | ✅ (ses clients) | ✅ (tous) | ❌ |
| `update-contract-payment` | ✅ (ses clients) | ✅ (tous) | ❌ |
| `create-event` | ✅ (ses clients + signé) | ✅ (tous + signé) | ❌ |
| `assign-support` | ❌ | ✅ | ❌ |
| `update-event` | ❌ | ✅ (tous) | ✅ (ses événements) |
| `filter-my-events` | ❌ | ❌ | ✅ |
| `filter-unsigned-contracts` | ✅ | ✅ | ✅ |
| `filter-unpaid-contracts` | ✅ | ✅ | ✅ |
| `filter-unassigned-events` | ✅ | ✅ | ✅ |

---

## 8. Scénario complet de démonstration

### Étape 1 : Utiliser un commercial existant

```bash
# Note: commercial2 (Marie Martin) existe déjà dans seed_database.py
# Username: commercial2
# Password: Commercial123!
```

### Étape 2 : Commercial crée un client et un contrat

```bash
# Se connecter en COMMERCIAL
poetry run epicevents login
# Username: commercial2
# Password: Commercial123!

# Créer un client (auto-assignation)
poetry run epicevents create-client
# Prénom: Lucie
# Nom: Bernard
# Email: lucie.bernard@innovtech.fr
# Téléphone: 0645678901
# Entreprise: InnovTech SAS

# Noter l'ID du client (ex: 12)

# Créer un contrat pour ce client
poetry run epicevents create-contract
# ID du client: 12
# Montant total: 15000.00
# Montant restant: 15000.00
# Contrat signé: False

# Noter l'ID du contrat (ex: 8)

# Signer le contrat
poetry run epicevents sign-contract
# ID du contrat: 8

# Enregistrer un paiement
poetry run epicevents update-contract-payment
# ID du contrat: 8
# Montant du paiement: 5000.00

# Créer un événement pour ce contrat signé
poetry run epicevents create-event
# Nom: Formation DevOps 2025
# ID du contrat: 8
# Date début: 2025-09-20 09:00
# Date fin: 2025-09-20 17:00
# Lieu: Salle de formation, Toulouse
# Participants: 25
# Notes: Formation intensive DevOps
# ID support: [laisser vide]

# Noter l'ID de l'événement (ex: 15)

# Se déconnecter
poetry run epicevents logout
```

### Étape 3 : Gestion assigne un support

```bash
# Se connecter en GESTION
poetry run epicevents login
# Username: admin
# Password: Admin123!

# Voir les événements sans support
poetry run epicevents filter-unassigned-events

# Assigner un support à l'événement
poetry run epicevents assign-support
# ID événement: 15
# ID support: 4

# Se déconnecter
poetry run epicevents logout
```

### Étape 4 : Support gère son événement

```bash
# Se connecter en SUPPORT
poetry run epicevents login
# Username: support1
# Password: Support123!

# Voir mes événements assignés
poetry run epicevents filter-my-events

# Mettre à jour un événement assigné
poetry run epicevents update-event
# ID événement: 15
# Laisser vide tous les champs sauf:
# Nouveau nombre de participants: 30

# Se déconnecter
poetry run epicevents logout
```

---

## 9. Conseils pour la démonstration

### Préparer la base de données

Avant la démonstration, assurez-vous d'avoir :
1. ✅ Au moins 1 utilisateur de chaque département (COMMERCIAL, GESTION, SUPPORT)
2. ✅ Quelques clients avec différents `sales_contact_id`
3. ✅ Quelques contrats (signés et non signés, payés et non payés)
4. ✅ Quelques événements (avec et sans support assigné)

### Démontrer les échecs de permission

Pour montrer la robustesse du système, démontrez également les **cas d'échec** :

1. **COMMERCIAL essaie de modifier le client d'un autre commercial**
   ```bash
   poetry run epicevents update-client
   # ID: [client d'un autre commercial]
   # Résultat: ❌ Vous ne pouvez modifier que vos propres clients
   ```

2. **COMMERCIAL essaie de créer un événement pour contrat non signé**
   ```bash
   poetry run epicevents create-event
   # ID contrat: [contrat non signé]
   # Résultat: ❌ Le contrat n'est pas encore signé
   ```

3. **SUPPORT essaie de modifier l'événement d'un autre support**
   ```bash
   poetry run epicevents update-event-attendees
   # ID événement: [événement d'un autre support]
   # Résultat: ❌ Vous ne pouvez modifier que vos propres événements
   ```

### Ordre de démonstration recommandé

1. **Authentification** (2 min)
   - Login/logout/whoami
   - Montrer le token JWT

2. **Besoins généraux** (3 min)
   - Accès en lecture pour tous
   - Filtres disponibles

3. **Gestion** (5 min)
   - CRUD utilisateurs
   - CRUD contrats (tous)
   - Assignation support

4. **Commercial** (5 min)
   - Création client (auto-assignation)
   - CRUD contrats (ses clients)
   - Création événement (vérifications)

5. **Support** (3 min)
   - filter-my-events
   - update-event-attendees

6. **Échecs de permission** (2 min)
   - Montrer les messages d'erreur clairs

**Total : ~20 minutes**

---

## 10. Vérification de la conformité

Pour chaque exigence du cahier des charges, référez-vous aux documents d'analyse :

- ✅ [GENERAL_REQUIREMENTS_ANALYSIS.md](GENERAL_REQUIREMENTS_ANALYSIS.md) - 4/4 (100%)
- ✅ [COMMERCIAL_REQUIREMENTS_ANALYSIS.md](COMMERCIAL_REQUIREMENTS_ANALYSIS.md) - 6/6 (100%)
- ✅ [GESTION_REQUIREMENTS_ANALYSIS.md](GESTION_REQUIREMENTS_ANALYSIS.md) - 7/7 (100%)
- ✅ [SUPPORT_REQUIREMENTS_ANALYSIS.md](SUPPORT_REQUIREMENTS_ANALYSIS.md) - 2/2 (100%)

**Conformité totale : 19/19 exigences (100%)** 🎉
