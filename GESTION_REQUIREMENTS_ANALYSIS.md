# Analyse du Respect du Cahier des Charges - Équipe de Gestion

## Cahier des Charges

**Besoins individuels : équipe de gestion**
- ✅ Créer, mettre à jour et supprimer des collaborateurs dans le système CRM
- ✅ Créer et modifier tous les contrats
- ✅ Filtrer l'affichage des événements (événements sans support associé)
- ✅ Modifier des événements (associer un collaborateur support à l'événement)

---

## 1. ✅ Créer, mettre à jour et supprimer des collaborateurs

### 1.1 ✅ Créer des collaborateurs

**Commande:** `create-user`

**Fichier:** [src/cli/commands.py:362-480](src/cli/commands.py#L362-L480)

#### Code de la fonctionnalité

```python
@app.command()
@require_department(Department.GESTION)
def create_user(
    username: str = typer.Option(..., prompt=LABEL_USERNAME, callback=validators.validate_username_callback),
    first_name: str = typer.Option(..., prompt="Prénom", callback=validators.validate_first_name_callback),
    last_name: str = typer.Option(..., prompt="Nom", callback=validators.validate_last_name_callback),
    email: str = typer.Option(..., prompt="Email", callback=validators.validate_email_callback),
    phone: str = typer.Option(..., prompt=PROMPT_TELEPHONE, callback=validators.validate_phone_callback),
    password: str = typer.Option(..., prompt="Mot de passe", hide_input=True, callback=validators.validate_password_callback),
    department_choice: int = typer.Option(
        ...,
        prompt=f"\nDépartements disponibles:\n1. {Department.COMMERCIAL.value}\n2. {Department.GESTION.value}\n3. {Department.SUPPORT.value}\n\nChoisir un département (numéro)",
        callback=validators.validate_department_callback,
    ),
):
    """
    Créer un nouvel utilisateur dans le système CRM.

    Cette commande permet d'enregistrer un nouvel utilisateur avec ses informations
    personnelles et professionnelles. Le mot de passe est automatiquement hashé
    avant d'être stocké en base de données.
    """
    container = Container()
    user_service = container.user_service()

    console.print_separator()
    console.print_header("Création d'un nouvel utilisateur")
    console.print_separator()

    # Convert department choice (int) to Department enum
    departments = list(Department)
    department = departments[department_choice - 1]

    try:
        # Create user via service
        user = user_service.create_user(
            username=username,
            first_name=first_name,
            last_name=last_name,
            email=email,
            phone=phone,
            password=password,
            department=department,
        )

    except IntegrityError as e:
        error_msg = str(e.orig).lower() if hasattr(e, "orig") else str(e).lower()

        if "unique" in error_msg or "duplicate" in error_msg:
            if "username" in error_msg:
                console.print_error(f"Le nom d'utilisateur '{username}' est déjà utilisé")
            elif "email" in error_msg:
                console.print_error(f"L'email '{email}' est déjà utilisé par un autre utilisateur")
            else:
                console.print_error("Erreur: Un utilisateur avec ces informations existe déjà")
        else:
            console.print_error(ERROR_INTEGRITY.format(error_msg=error_msg))
        raise typer.Exit(code=1)

    # Success message
    console.print_success(f"Utilisateur {user.username} créé avec succès!")
    console.print_field(LABEL_ID, str(user.id))
    console.print_field("Nom complet", f"{user.first_name} {user.last_name}")
    console.print_field(LABEL_EMAIL, user.email)
    console.print_field(LABEL_DEPARTMENT, user.department.value)
```

#### Conformité

✅ **CONFORME** - La commande `create-user` permet de :
- Créer des utilisateurs dans tous les départements (COMMERCIAL, GESTION, SUPPORT)
- Valider toutes les données (username unique, email unique, etc.)
- Hacher automatiquement les mots de passe
- Réservée exclusivement au département GESTION via `@require_department(Department.GESTION)`

---

### 1.2 ✅ Mettre à jour des collaborateurs

**Commande:** `update-user`

**Fichier:** [src/cli/commands.py:483-621](src/cli/commands.py#L483-L621)

#### Code de la fonctionnalité

```python
@app.command()
@require_department(Department.GESTION)
def update_user(
    user_id: int = typer.Option(..., prompt="ID de l'utilisateur"),
    username: str = typer.Option(None, prompt="Nouveau nom d'utilisateur (laisser vide pour ne pas modifier)"),
    first_name: str = typer.Option(None, prompt="Nouveau prénom (laisser vide pour ne pas modifier)"),
    last_name: str = typer.Option(None, prompt="Nouveau nom (laisser vide pour ne pas modifier)"),
    email: str = typer.Option(None, prompt="Nouvel email (laisser vide pour ne pas modifier)"),
    phone: str = typer.Option(None, prompt="Nouveau téléphone (laisser vide pour ne pas modifier)"),
    department_choice: int = typer.Option(
        None,
        prompt=f"\nDépartements disponibles:\n1. {Department.COMMERCIAL.value}\n2. {Department.GESTION.value}\n3. {Department.SUPPORT.value}\n\nChoisir un nouveau département (laisser vide pour ne pas modifier)",
    ),
):
    """
    Mettre à jour les informations d'un utilisateur.

    Cette commande permet de modifier les informations d'un utilisateur existant.
    Les champs laissés vides ne seront pas modifiés.
    """
    container = Container()
    user_service = container.user_service()

    # Vérifier que l'utilisateur existe
    user = user_service.get_user(user_id)
    if not user:
        console.print_error(f"Utilisateur avec l'ID {user_id} n'existe pas")
        raise typer.Exit(code=1)

    # Nettoyer les champs vides
    username = username.strip() if username else None
    first_name = first_name.strip() if first_name else None
    last_name = last_name.strip() if last_name else None
    email = email.strip() if email else None
    phone = phone.strip() if phone else None

    # Convert department choice to enum if provided
    department = None
    if department_choice:
        departments = list(Department)
        department = departments[department_choice - 1]

    # Update user via service
    updated_user = user_service.update_user(
        user_id=user_id,
        username=username,
        first_name=first_name,
        last_name=last_name,
        email=email,
        phone=phone,
        department=department,
    )

    # Success message
    console.print_success(f"Utilisateur {updated_user.username} mis à jour avec succès!")
```

#### Conformité

✅ **CONFORME** - La commande `update-user` permet de :
- Mettre à jour les informations d'un utilisateur existant
- Modifier sélectivement les champs (les champs vides ne sont pas modifiés)
- Changer le département d'un utilisateur
- Réservée exclusivement au département GESTION via `@require_department(Department.GESTION)`

---

### 1.3 ✅ Supprimer des collaborateurs

**Commande:** `delete-user`

**Fichier:** [src/cli/commands.py:624-700](src/cli/commands.py#L624-L700)

#### Code de la fonctionnalité

```python
@app.command()
@require_department(Department.GESTION)
def delete_user(
    user_id: int = typer.Option(..., prompt="ID de l'utilisateur à supprimer"),
    confirm: bool = typer.Option(False, prompt="Êtes-vous sûr de vouloir supprimer cet utilisateur ? (oui/non)"),
):
    """
    Supprimer un utilisateur du système CRM.

    Cette commande supprime définitivement un utilisateur de la base de données.
    ATTENTION: Cette action est irréversible.
    """
    container = Container()
    user_service = container.user_service()

    # Vérifier que l'utilisateur existe
    user = user_service.get_user(user_id)
    if not user:
        console.print_error(f"Utilisateur avec l'ID {user_id} n'existe pas")
        raise typer.Exit(code=1)

    # Afficher les informations de l'utilisateur avant suppression
    console.print_separator()
    console.print_header("Suppression d'un utilisateur")
    console.print_separator()
    console.print_field(LABEL_ID, str(user.id))
    console.print_field("Nom complet", f"{user.first_name} {user.last_name}")
    console.print_field(LABEL_USERNAME, user.username)
    console.print_field(LABEL_EMAIL, user.email)
    console.print_field(LABEL_DEPARTMENT, user.department.value)
    console.print_separator()

    # Demander confirmation
    if not confirm:
        console.print_error("Suppression annulée. Utilisez --confirm pour confirmer la suppression.")
        raise typer.Exit(code=1)

    # Supprimer l'utilisateur
    success = user_service.delete_user(user_id)
    if not success:
        console.print_error("Erreur lors de la suppression de l'utilisateur")
        raise typer.Exit(code=1)

    # Success message
    console.print_success(f"Utilisateur {user.username} (ID: {user_id}) supprimé avec succès!")
```

#### Conformité

✅ **CONFORME** - La commande `delete-user` permet de :
- Supprimer un utilisateur du système CRM
- Afficher les informations de l'utilisateur avant suppression
- Demander confirmation obligatoire avant suppression
- Réservée exclusivement au département GESTION via `@require_department(Department.GESTION)`
- Gestion des contraintes via les relations de base de données configurées

---

## 2. ✅ Créer et modifier tous les contrats

### 2.1 ✅ Créer tous les contrats

**Commande:** `create-contract`

**Fichier:** [src/cli/commands.py:483-607](src/cli/commands.py#L483-L607)

#### Code de la fonctionnalité

```python
@app.command()
@require_department(Department.COMMERCIAL, Department.GESTION)
def create_contract(
    client_id: int = typer.Option(..., prompt="ID du client", callback=validators.validate_client_id_callback),
    total_amount: str = typer.Option(..., prompt="Montant total", callback=validators.validate_amount_callback),
    remaining_amount: str = typer.Option(..., prompt="Montant restant", callback=validators.validate_amount_callback),
    is_signed: bool = typer.Option(False, prompt="Contrat signé ?"),
):
    """
    Créer un nouveau contrat dans le système CRM.

    Cette commande permet d'enregistrer un nouveau contrat associé à un client
    existant, avec des montants et un statut de signature.
    """
    from decimal import Decimal

    container = Container()
    contract_service = container.contract_service()
    client_service = container.client_service()

    # Business validation: check if client exists
    client = client_service.get_client(client_id)
    if not client:
        console.print_error(f"Client avec l'ID {client_id} n'existe pas")
        raise typer.Exit(code=1)

    # Convert amounts to Decimal
    total_decimal = Decimal(total_amount)
    remaining_decimal = Decimal(remaining_amount)

    # Business validation: validate contract amounts
    validators.validate_contract_amounts(total_decimal, remaining_decimal)

    # Create contract via service
    contract = contract_service.create_contract(
        client_id=client_id,
        total_amount=total_decimal,
        remaining_amount=remaining_decimal,
        is_signed=is_signed,
    )
```

#### Conformité

✅ **CONFORME** - L'équipe GESTION peut :
- Créer des contrats pour **tous les clients** (pas de restriction de propriété)
- Via `@require_department(Department.COMMERCIAL, Department.GESTION)`
- Pas de vérification que le client leur appartient (contrairement aux COMMERCIAL)

---

### 2.2 ✅ Modifier tous les contrats

**Commande:** `update-contract`

**Fichier:** [src/cli/commands.py:1505-1655](src/cli/commands.py#L1505-L1655)

#### Code de la fonctionnalité

```python
@app.command()
@require_department(Department.COMMERCIAL, Department.GESTION)
def update_contract(
    contract_id: int = typer.Option(..., prompt=PROMPT_ID_CONTRAT, callback=validators.validate_contract_id_callback),
    total_amount: str = typer.Option(None, prompt="Nouveau montant total (laisser vide pour ne pas modifier)"),
    remaining_amount: str = typer.Option(None, prompt="Nouveau montant restant (laisser vide pour ne pas modifier)"),
    is_signed: bool = typer.Option(None, prompt="Marquer comme signé ?"),
):
    """
    Mettre à jour les informations d'un contrat.

    Cette commande permet de modifier les informations d'un contrat existant.
    Les champs laissés vides ne seront pas modifiés.
    """
    container = Container()
    contract_service = container.contract_service()
    auth_service = container.auth_service()

    current_user = auth_service.get_current_user()

    # Vérifier que le contrat existe
    contract = contract_service.get_contract(contract_id)
    if not contract:
        console.print_error(f"Contrat avec l'ID {contract_id} n'existe pas")
        raise typer.Exit(code=1)

    # Permission check: COMMERCIAL can only update contracts of their own clients
    # GESTION can update ALL contracts (no check)
    if current_user.department == Department.COMMERCIAL:
        if contract.client.sales_contact_id != current_user.id:
            console.print_error("Vous ne pouvez modifier que les contrats de vos propres clients")
            raise typer.Exit(code=1)

    # Update contract...
```

#### Conformité

✅ **CONFORME** - L'équipe GESTION peut :
- Modifier **tous les contrats** sans restriction
- Les utilisateurs COMMERCIAL ont une restriction (leurs propres clients uniquement)
- Les utilisateurs GESTION n'ont **aucune restriction** (`if current_user.department == Department.COMMERCIAL` n'affecte pas GESTION)

---

## 3. ✅ Filtrer l'affichage des événements sans support

**Commande:** `filter-unassigned-events`

**Fichier:** [src/cli/commands.py:1235-1289](src/cli/commands.py#L1235-L1289)

### Code de la fonctionnalité

```python
@app.command()
@require_department()
def filter_unassigned_events():
    """
    Afficher tous les événements sans contact support assigné.

    Cette commande liste tous les événements qui n'ont pas encore de contact support.
    """
    container = Container()
    event_service = container.event_service()

    console.print_separator()
    console.print_header("Événements sans contact support")
    console.print_separator()

    events = event_service.get_unassigned_events()

    if not events:
        console.print_success("Aucun événement sans contact support")
        return

    for event in events:
        console.print_field(LABEL_EVENT_ID, str(event.id))
        console.print_field(LABEL_CONTRACT_ID, str(event.contract_id))
        console.print_field(
            LABEL_CLIENT_NAME,
            f"{event.contract.client.first_name} {event.contract.client.last_name}",
        )
        console.print_field(
            LABEL_CLIENT_CONTACT,
            f"{event.contract.client.email}\n{event.contract.client.phone}",
        )
        console.print_field(LABEL_EVENT_DATE_START, format_event_datetime(event.event_start))
        console.print_field(LABEL_EVENT_DATE_END, format_event_datetime(event.event_end))
        console.print_field(LABEL_SUPPORT_CONTACT, LABEL_NON_ASSIGNE)
        console.print_field(LABEL_LOCATION, event.location)
        console.print_field(LABEL_ATTENDEES, str(event.attendees))
        if event.notes:
            console.print_field(LABEL_NOTES, event.notes)
        console.print_separator()

    console.print_success(f"Total: {len(events)} événement(s) sans contact support")
```

### Conformité

✅ **CONFORME** - La commande permet de :
- Afficher tous les événements où `support_contact_id IS NULL`
- Accessible à tous les départements via `@require_department()` (sans paramètres)
- Affiche les détails complets de chaque événement non assigné

---

## 4. ✅ Modifier des événements (associer un support)

**Commande:** `assign-support`

**Fichier:** [src/cli/commands.py:1029-1128](src/cli/commands.py#L1029-L1128)

### Code de la fonctionnalité

```python
@app.command()
@require_department(Department.GESTION)
def assign_support(
    event_id: int = typer.Option(..., prompt="ID de l'événement", callback=validators.validate_event_id_callback),
    support_contact_id: int = typer.Option(..., prompt="ID du contact support", callback=validators.validate_user_id_callback),
):
    """
    Assigner un contact support à un événement.

    Cette commande permet d'assigner ou de réassigner un utilisateur du département
    SUPPORT à un événement existant.
    """
    container = Container()
    event_service = container.event_service()
    user_service = container.user_service()

    console.print_separator()
    console.print_header("Assignation d'un contact support")
    console.print_separator()

    # Vérifier que l'événement existe
    event = event_service.get_event(event_id)
    if not event:
        console.print_error(f"Événement avec l'ID {event_id} n'existe pas")
        raise typer.Exit(code=1)

    # Vérifier que l'utilisateur existe et est du département SUPPORT
    user = user_service.get_user(support_contact_id)
    if not user:
        console.print_error(f"Utilisateur avec l'ID {support_contact_id} n'existe pas")
        raise typer.Exit(code=1)

    try:
        validators.validate_user_is_support(user)
    except ValueError as e:
        console.print_error(str(e))
        raise typer.Exit(code=1)

    # Assigner le contact support
    updated_event = event_service.assign_support_contact(event_id, support_contact_id)

    # Success message
    console.print_success(f"Contact support assigné avec succès à l'événement '{updated_event.name}'!")
    console.print_field(LABEL_EVENT_ID, str(updated_event.id))
    console.print_field(LABEL_CONTRACT_ID, str(updated_event.contract_id))
    console.print_field(
        LABEL_CLIENT_NAME,
        f"{updated_event.contract.client.first_name} {updated_event.contract.client.last_name}",
    )
    console.print_field(
        "Support contact",
        f"{user.first_name} {user.last_name} (ID: {user.id})",
    )
```

### Conformité

✅ **CONFORME** - La commande permet de :
- Assigner un contact support à un événement
- Réassigner un contact support (modifier l'assignation existante)
- Vérifier que l'utilisateur assigné est bien du département SUPPORT
- Réservée exclusivement au département GESTION via `@require_department(Department.GESTION)`

---

## Synthèse de la Conformité

| Exigence | Statut | Commande | Observations |
|----------|--------|----------|--------------|
| Créer des collaborateurs | ✅ CONFORME | `create-user` | Création d'utilisateurs implémentée |
| Mettre à jour des collaborateurs | ✅ CONFORME | `update-user` | Mise à jour d'utilisateurs implémentée |
| Supprimer des collaborateurs | ✅ CONFORME | `delete-user` | Suppression d'utilisateurs implémentée |
| Créer tous les contrats | ✅ CONFORME | `create-contract` | Accès sans restriction pour GESTION |
| Modifier tous les contrats | ✅ CONFORME | `update-contract` | Pas de restriction de propriété pour GESTION |
| Filtrer événements sans support | ✅ CONFORME | `filter-unassigned-events` | Filtre implémenté |
| Modifier événements (assigner support) | ✅ CONFORME | `assign-support` | Assignation/réassignation implémentée |

### Score de Conformité

**7/7 exigences pleinement conformes (100%)**

Toutes les fonctionnalités requises par le cahier des charges sont implémentées ✅

---

## Fonctionnalités Bonus pour GESTION

En plus des exigences du cahier des charges, l'équipe GESTION a accès à :

1. **`create-client`** ([lines 212-359](src/cli/commands.py#L212-L359)) - Créer des clients (partagé avec COMMERCIAL)
2. **`update-client`** ([lines 1360-1501](src/cli/commands.py#L1360-L1501)) - Modifier tous les clients sans restriction
3. **`create-event`** ([lines 823-1025](src/cli/commands.py#L823-L1025)) - Créer des événements pour tous les contrats
4. **Tous les filtres** :
   - `filter-unsigned-contracts` - Contrats non signés
   - `filter-unpaid-contracts` - Contrats non soldés
   - `filter-unassigned-events` - Événements sans support

Ces fonctionnalités donnent à l'équipe GESTION un **contrôle complet** sur tous les aspects du CRM, conformément à leur rôle d'administration.

---

## Conclusion

Votre implémentation est **pleinement conforme** au cahier des charges de l'équipe de gestion (100%). Les points forts :

✅ Création de collaborateurs implémentée
✅ Mise à jour de collaborateurs implémentée
✅ Suppression de collaborateurs implémentée
✅ Accès complet à tous les contrats (création et modification sans restriction)
✅ Filtrage des événements sans support
✅ Assignation de support aux événements
✅ Accès étendu à toutes les fonctionnalités du CRM (clients, contrats, événements)

L'équipe GESTION dispose maintenant d'un **contrôle complet** sur l'ensemble du système, incluant la gestion complète du cycle de vie des utilisateurs (CRUD complet), conformément à leur rôle d'administration.
