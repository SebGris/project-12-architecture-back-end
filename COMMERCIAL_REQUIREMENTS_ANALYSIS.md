# Analyse du Respect du Cahier des Charges - Équipe Commerciale

## Cahier des Charges

**Besoins individuels : équipe commerciale**
- ✅ Créer des clients (le client leur sera automatiquement associé)
- ✅ Mettre à jour les clients dont ils sont responsables
- ✅ Modifier/mettre à jour les contrats des clients dont ils sont responsables
- ✅ Filtrer l'affichage des contrats (contrats non signés, non entièrement payés)
- ⚠️ Créer un événement pour un de leurs clients qui a signé un contrat

---

## 1. ✅ Créer des clients avec auto-assignation

**Commande:** `create-client`

**Fichier:** [src/cli/commands.py:211-359](src/cli/commands.py#L211-L359)

### Code de la fonctionnalité

```python
@app.command()
@require_department(Department.COMMERCIAL, Department.GESTION)
def create_client(
    first_name: str = typer.Option(..., prompt="Prénom", callback=validators.validate_first_name_callback),
    last_name: str = typer.Option(..., prompt="Nom", callback=validators.validate_last_name_callback),
    email: str = typer.Option(..., prompt="Email", callback=validators.validate_email_callback),
    phone: str = typer.Option(..., prompt=PROMPT_TELEPHONE, callback=validators.validate_phone_callback),
    company_name: str = typer.Option(..., prompt="Nom de l'entreprise", callback=validators.validate_company_name_callback),
    sales_contact_id: int = typer.Option(
        0,
        prompt="ID du contact commercial, ENTRER pour auto-assignation (valeur par défaut: 0)",
        callback=validators.validate_sales_contact_id_callback,
    ),
):
    # ...
    current_user = auth_service.get_current_user()

    # Auto-assign for COMMERCIAL users if no sales_contact_id provided
    if sales_contact_id == 0:
        if current_user.department == Department.COMMERCIAL:
            sales_contact_id = current_user.id
            console.print_field(
                LABEL_CONTACT_COMMERCIAL,
                f"Auto-assigné à {current_user.username}",
            )
        else:
            console.print_error("Vous devez spécifier un ID de contact commercial")
            raise typer.Exit(code=1)
    # ...
```

### Conformité

✅ **CONFORME** - L'auto-assignation fonctionne correctement :
- Lorsqu'un utilisateur COMMERCIAL crée un client sans spécifier de `sales_contact_id` (valeur par défaut 0)
- Le client est automatiquement assigné à l'utilisateur connecté (`current_user.id`)
- Un message confirme l'auto-assignation

---

## 2. ✅ Mettre à jour les clients dont ils sont responsables

**Commande:** `update-client`

**Fichier:** [src/cli/commands.py:1335-1477](src/cli/commands.py#L1335-L1477)

### Code de la fonctionnalité

```python
@app.command()
@require_department(Department.COMMERCIAL, Department.GESTION)
def update_client(
    client_id: int = typer.Option(..., prompt="ID du client", callback=validators.validate_client_id_callback),
    first_name: str = typer.Option(None, prompt="Nouveau prénom (laisser vide pour ne pas modifier)"),
    last_name: str = typer.Option(None, prompt="Nouveau nom (laisser vide pour ne pas modifier)"),
    email: str = typer.Option(None, prompt="Nouvel email (laisser vide pour ne pas modifier)"),
    phone: str = typer.Option(None, prompt="Nouveau téléphone (laisser vide pour ne pas modifier)"),
    company_name: str = typer.Option(None, prompt="Nouveau nom d'entreprise (laisser vide pour ne pas modifier)"),
):
    # ...
    current_user = auth_service.get_current_user()

    # Vérifier que le client existe
    client = client_service.get_client(client_id)
    if not client:
        console.print_error(f"Client avec l'ID {client_id} n'existe pas")
        raise typer.Exit(code=1)

    # Permission check: COMMERCIAL can only update their own clients
    if current_user.department == Department.COMMERCIAL:
        if client.sales_contact_id != current_user.id:
            console.print_error("Vous ne pouvez modifier que vos propres clients")
            console.print_error(
                f"Ce client est assigné à {client.sales_contact.first_name} {client.sales_contact.last_name}"
            )
            raise typer.Exit(code=1)
    # ...
```

### Conformité

✅ **CONFORME** - La vérification de propriété est implémentée :
- Un utilisateur COMMERCIAL ne peut modifier que les clients où `client.sales_contact_id == current_user.id`
- Affiche un message d'erreur explicite si le commercial tente de modifier un client qui ne lui appartient pas
- Les utilisateurs GESTION peuvent modifier tous les clients (pas de restriction)

---

## 3. ✅ Modifier/mettre à jour les contrats des clients dont ils sont responsables

**Commande:** `update-contract`

**Fichier:** [src/cli/commands.py:1480-1631](src/cli/commands.py#L1480-L1631)

### Code de la fonctionnalité

```python
@app.command()
@require_department(Department.COMMERCIAL, Department.GESTION)
def update_contract(
    contract_id: int = typer.Option(..., prompt=PROMPT_ID_CONTRAT, callback=validators.validate_contract_id_callback),
    total_amount: str = typer.Option(None, prompt="Nouveau montant total (laisser vide pour ne pas modifier)"),
    remaining_amount: str = typer.Option(None, prompt="Nouveau montant restant (laisser vide pour ne pas modifier)"),
    is_signed: bool = typer.Option(None, prompt="Marquer comme signé ?"),
):
    # ...
    current_user = auth_service.get_current_user()

    # Vérifier que le contrat existe
    contract = contract_service.get_contract(contract_id)
    if not contract:
        console.print_error(f"Contrat avec l'ID {contract_id} n'existe pas")
        raise typer.Exit(code=1)

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
    # ...
```

### Conformité

✅ **CONFORME** - La vérification de propriété via le client est implémentée :
- Un utilisateur COMMERCIAL ne peut modifier que les contrats des clients où `contract.client.sales_contact_id == current_user.id`
- Vérification indirecte de la propriété via la relation `contract → client → sales_contact`
- Message d'erreur détaillé indiquant à qui appartient le client

---

## 4. ✅ Filtrer l'affichage des contrats

### 4.1 Contrats non signés

**Commande:** `filter-unsigned-contracts`

**Fichier:** [src/cli/commands.py:1107-1154](src/cli/commands.py#L1107-L1154)

```python
@app.command()
@require_department()  # Accessible à tous les départements
def filter_unsigned_contracts():
    """
    Afficher tous les contrats non signés.

    Cette commande liste tous les contrats qui n'ont pas encore été signés.
    """
    container = Container()
    contract_service = container.contract_service()

    console.print_separator()
    console.print_header("Contrats non signés")
    console.print_separator()

    contracts = contract_service.get_unsigned_contracts()

    if not contracts:
        console.print_success("Aucun contrat non signé")
        return

    for contract in contracts:
        console.print_field(LABEL_ID, str(contract.id))
        console.print_field(
            LABEL_CLIENT,
            f"{contract.client.first_name} {contract.client.last_name} ({contract.client.company_name})",
        )
        console.print_field(
            LABEL_CONTACT_COMMERCIAL,
            f"{contract.client.sales_contact.first_name} {contract.client.sales_contact.last_name} (ID: {contract.client.sales_contact_id})",
        )
        console.print_field(LABEL_MONTANT_TOTAL, f"{contract.total_amount} €")
        console.print_field(LABEL_MONTANT_RESTANT, f"{contract.remaining_amount} €")
        console.print_field(LABEL_DATE_CREATION, contract.created_at.strftime(FORMAT_DATE))
        console.print_separator()

    console.print_success(f"Total: {len(contracts)} contrat(s) non signé(s)")
```

### 4.2 Contrats non entièrement payés

**Commande:** `filter-unpaid-contracts`

**Fichier:** [src/cli/commands.py:1157-1208](src/cli/commands.py#L1157-L1208)

```python
@app.command()
@require_department()  # Accessible à tous les départements
def filter_unpaid_contracts():
    """
    Afficher tous les contrats non soldés (montant restant > 0).

    Cette commande liste tous les contrats qui ont un montant restant à payer.
    """
    container = Container()
    contract_service = container.contract_service()

    console.print_separator()
    console.print_header("Contrats non soldés")
    console.print_separator()

    contracts = contract_service.get_unpaid_contracts()

    if not contracts:
        console.print_success("Aucun contrat non soldé")
        return

    for contract in contracts:
        console.print_field(LABEL_ID, str(contract.id))
        console.print_field(
            LABEL_CLIENT,
            f"{contract.client.first_name} {contract.client.last_name} ({contract.client.company_name})",
        )
        console.print_field(
            LABEL_CONTACT_COMMERCIAL,
            f"{contract.client.sales_contact.first_name} {contract.client.sales_contact.last_name} (ID: {contract.client.sales_contact_id})",
        )
        console.print_field(LABEL_MONTANT_TOTAL, f"{contract.total_amount} €")
        console.print_field(LABEL_MONTANT_RESTANT, f"{contract.remaining_amount} €")
        console.print_field(
            LABEL_STATUT,
            STATUS_SIGNED if contract.is_signed else STATUS_UNSIGNED,
        )
        console.print_field(LABEL_DATE_CREATION, contract.created_at.strftime(FORMAT_DATE))
        console.print_separator()

    console.print_success(f"Total: {len(contracts)} contrat(s) non soldé(s)")
```

### Conformité

✅ **CONFORME** - Deux filtres sont implémentés :
1. **Contrats non signés** : `filter-unsigned-contracts` affiche tous les contrats avec `is_signed = False`
2. **Contrats non entièrement payés** : `filter-unpaid-contracts` affiche tous les contrats avec `remaining_amount > 0`

**Note:** Ces commandes utilisent `@require_department()` (sans paramètres), donc accessibles à tous les utilisateurs authentifiés (COMMERCIAL, GESTION, SUPPORT).

---

## 5. ✅ Créer un événement pour un client qui a signé un contrat

**Commande:** `create-event`

**Fichier:** [src/cli/commands.py:822-1025](src/cli/commands.py#L822-L1025)

### Code de la fonctionnalité

```python
@app.command()
@require_department(Department.COMMERCIAL, Department.GESTION)
def create_event(
    name: str = typer.Option(..., prompt="Nom de l'événement", callback=validators.validate_event_name_callback),
    contract_id: int = typer.Option(..., prompt=PROMPT_ID_CONTRAT, callback=validators.validate_contract_id_callback),
    event_start: str = typer.Option(..., prompt="Date et heure de début (YYYY-MM-DD HH:MM)"),
    event_end: str = typer.Option(..., prompt="Date et heure de fin (YYYY-MM-DD HH:MM)"),
    location: str = typer.Option(..., prompt="Lieu", callback=validators.validate_location_callback),
    attendees: int = typer.Option(..., prompt="Nombre de participants", callback=validators.validate_attendees_callback),
    notes: str = typer.Option("", prompt="Notes (optionnel)"),
    support_contact_id: int = typer.Option(0, prompt="ID du contact support (0 si aucun)"),
):
    """
    Créer un nouvel événement dans le système CRM.

    Cette commande permet d'enregistrer un nouvel événement associé à un contrat
    existant, avec des détails sur la date, le lieu et le nombre de participants.
    """
    from datetime import datetime

    container = Container()
    event_service = container.event_service()
    contract_service = container.contract_service()
    user_service = container.user_service()
    auth_service = container.auth_service()

    console.print_separator()
    console.print_header("Création d'un nouvel événement")
    console.print_separator()

    # Get current user for permission checks
    current_user = auth_service.get_current_user()

    # Business validation: check if contract exists
    contract = contract_service.get_contract(contract_id)

    if not contract:
        console.print_error(f"Contrat avec l'ID {contract_id} n'existe pas")
        raise typer.Exit(code=1)

    # Business validation: check if contract is signed
    if not contract.is_signed:
        console.print_error(
            f"Le contrat #{contract_id} n'est pas encore signé. "
            "Seuls les contrats signés peuvent avoir des événements."
        )
        raise typer.Exit(code=1)

    # Permission check: COMMERCIAL can only create events for their own clients
    if current_user.department == Department.COMMERCIAL:
        if contract.client.sales_contact_id != current_user.id:
            console.print_error(
                "Vous ne pouvez créer des événements que pour vos propres clients"
            )
            console.print_error(
                f"Ce contrat appartient au client {contract.client.first_name} {contract.client.last_name}, "
                f"assigné à {contract.client.sales_contact.first_name} {contract.client.sales_contact.last_name}"
            )
            raise typer.Exit(code=1)

    # Parse datetime strings
    try:
        start_dt = datetime.strptime(event_start, "%Y-%m-%d %H:%M")
        end_dt = datetime.strptime(event_end, "%Y-%m-%d %H:%M")
    except ValueError:
        console.print_error("Format de date invalide. Utilisez le format: YYYY-MM-DD HH:MM")
        raise typer.Exit(code=1)

    # Business validation: validate event dates and attendees
    try:
        validators.validate_event_dates(start_dt, end_dt, attendees)
    except ValueError as e:
        console.print_error(str(e))
        raise typer.Exit(code=1)

    # Create event via service
    event = event_service.create_event(
        name=name,
        contract_id=contract_id,
        event_start=start_dt,
        event_end=end_dt,
        location=location,
        attendees=attendees,
        notes=notes if notes else None,
        support_contact_id=support_id,
    )
    # ...
```

### Conformité

✅ **CONFORME** - La commande implémente maintenant toutes les vérifications nécessaires :

#### ✅ Vérification 1 : Le contrat doit être signé

```python
# Business validation: check if contract is signed
if not contract.is_signed:
    console.print_error(
        f"Le contrat #{contract_id} n'est pas encore signé. "
        "Seuls les contrats signés peuvent avoir des événements."
    )
    raise typer.Exit(code=1)
```

**Comportement :** Un événement ne peut être créé que si `contract.is_signed == True`, conformément au cahier des charges qui spécifie *"un client qui a signé un contrat"*.

#### ✅ Vérification 2 : Le commercial est propriétaire du client

```python
# Permission check: COMMERCIAL can only create events for their own clients
if current_user.department == Department.COMMERCIAL:
    if contract.client.sales_contact_id != current_user.id:
        console.print_error(
            "Vous ne pouvez créer des événements que pour vos propres clients"
        )
        console.print_error(
            f"Ce contrat appartient au client {contract.client.first_name} {contract.client.last_name}, "
            f"assigné à {contract.client.sales_contact.first_name} {contract.client.sales_contact.last_name}"
        )
        raise typer.Exit(code=1)
```

**Comportement :** Un commercial COMMERCIAL ne peut créer des événements que pour les contrats de **ses propres clients** (où `contract.client.sales_contact_id == current_user.id`). Les utilisateurs GESTION peuvent créer des événements pour tous les clients.

---

## Synthèse de la Conformité

| Exigence | Statut | Commande | Observations |
|----------|--------|----------|--------------|
| Créer des clients avec auto-assignation | ✅ CONFORME | `create-client` | Auto-assignation implémentée correctement |
| Mettre à jour leurs propres clients | ✅ CONFORME | `update-client` | Vérification de propriété OK |
| Modifier les contrats de leurs clients | ✅ CONFORME | `update-contract` | Vérification via client OK |
| Filtrer contrats non signés | ✅ CONFORME | `filter-unsigned-contracts` | Filtre implémenté |
| Filtrer contrats non payés | ✅ CONFORME | `filter-unpaid-contracts` | Filtre implémenté |
| Créer événement pour client signé | ✅ CONFORME | `create-event` | Vérifications signature + propriété implémentées |

### Score de Conformité

**6/6 exigences pleinement conformes (100%)** ✅

Toutes les exigences du cahier des charges pour l'équipe commerciale sont maintenant pleinement implémentées et conformes.

---

## Fonctionnalités Bonus Implémentées

En plus des exigences du cahier des charges, votre code implémente également :

1. **`sign-contract`** ([lines 610-703](src/cli/commands.py#L610-L703)) - Permet à un commercial de signer un contrat pour ses clients
2. **`update-contract-payment`** ([lines 706-819](src/cli/commands.py#L706-L819)) - Permet d'enregistrer un paiement pour un contrat

Ces deux commandes incluent bien les vérifications de propriété nécessaires.

---

## Conclusion

Votre implémentation est **100% conforme** au cahier des charges de l'équipe commerciale. Les points forts :

✅ Auto-assignation des clients lors de la création
✅ Contrôles de permissions robustes pour update_client et update_contract
✅ Filtres de contrats implémentés et fonctionnels
✅ Vérification que seuls les contrats signés peuvent avoir des événements
✅ Vérification que les commerciaux créent des événements uniquement pour leurs propres clients
✅ Fonctionnalités bonus bien sécurisées (sign_contract, update_contract_payment)

L'implémentation respecte intégralement toutes les exigences du cahier des charges et garantit une séparation appropriée des responsabilités entre les départements COMMERCIAL et GESTION.
