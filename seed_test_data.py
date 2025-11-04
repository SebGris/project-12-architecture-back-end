"""
Script de seed pour peupler la base de données avec des clients, contrats et événements de test.

Usage:
    poetry run python seed_test_data.py

Prérequis:
    - Les utilisateurs doivent déjà exister (exécuter seed_database.py d'abord)

Attention: Ce script écrasera les données existantes (clients, contrats, événements) !
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from datetime import datetime, timedelta
from decimal import Decimal

# Import de tous les modèles
from src.models.user import User, Department
from src.models.client import Client
from src.models.contract import Contract
from src.models.event import Event


def get_users(session):
    """Récupère les utilisateurs existants."""
    users = {
        "commercial1": session.query(User).filter_by(username="commercial1").first(),
        "commercial2": session.query(User).filter_by(username="commercial2").first(),
        "support1": session.query(User).filter_by(username="support1").first(),
        "support2": session.query(User).filter_by(username="support2").first(),
    }

    # Vérifier que tous les utilisateurs existent
    missing = [key for key, user in users.items() if user is None]
    if missing:
        raise ValueError(
            f"Utilisateurs manquants: {', '.join(missing)}. "
            "Exécutez 'poetry run python seed_database.py' d'abord."
        )

    return users


def create_clients(session, users):
    """Crée les clients de test."""

    print("\n" + "=" * 60)
    print("CREATION DES CLIENTS DE TEST")
    print("=" * 60)

    clients_data = [
        {
            "first_name": "Jean",
            "last_name": "Dupont",
            "email": "jean.dupont@example.com",
            "phone": "+33612345678",
            "company_name": "Dupont SA",
            "sales_contact_id": users["commercial1"].id,
        },
        {
            "first_name": "Marie",
            "last_name": "Leblanc",
            "email": "marie.leblanc@example.com",
            "phone": "+33623456789",
            "company_name": "Leblanc Corp",
            "sales_contact_id": users["commercial1"].id,
        },
        {
            "first_name": "Pierre",
            "last_name": "Martin",
            "email": "pierre.martin@example.com",
            "phone": "+33634567890",
            "company_name": "Martin Industries",
            "sales_contact_id": users["commercial2"].id,
        },
        {
            "first_name": "Sophie",
            "last_name": "Bernard",
            "email": "sophie.bernard@example.com",
            "phone": "+33645678901",
            "company_name": "Bernard Consulting",
            "sales_contact_id": users["commercial2"].id,
        },
        {
            "first_name": "Luc",
            "last_name": "Petit",
            "email": "luc.petit@example.com",
            "phone": "+33656789012",
            "company_name": "Petit Enterprises",
            "sales_contact_id": users["commercial1"].id,
        },
    ]

    created_clients = []

    for client_data in clients_data:
        client = Client(**client_data)
        session.add(client)
        created_clients.append(client)
        print(
            f"- Client créé: {client_data['first_name']} {client_data['last_name']} "
            f"({client_data['company_name']})"
        )

    session.commit()

    print(f"\n[OK] {len(created_clients)} clients créés avec succès !")
    print("=" * 60)

    return created_clients


def create_contracts(session, clients):
    """Crée les contrats de test."""

    print("\n" + "=" * 60)
    print("CREATION DES CONTRATS DE TEST")
    print("=" * 60)

    contracts_data = [
        {
            "client_id": clients[0].id,
            "total_amount": Decimal("15000.00"),
            "remaining_amount": Decimal("5000.00"),
            "is_signed": True,
        },
        {
            "client_id": clients[0].id,
            "total_amount": Decimal("8000.00"),
            "remaining_amount": Decimal("8000.00"),
            "is_signed": False,
        },
        {
            "client_id": clients[1].id,
            "total_amount": Decimal("25000.00"),
            "remaining_amount": Decimal("0.00"),
            "is_signed": True,
        },
        {
            "client_id": clients[2].id,
            "total_amount": Decimal("12000.00"),
            "remaining_amount": Decimal("12000.00"),
            "is_signed": False,
        },
        {
            "client_id": clients[2].id,
            "total_amount": Decimal("30000.00"),
            "remaining_amount": Decimal("10000.00"),
            "is_signed": True,
        },
        {
            "client_id": clients[3].id,
            "total_amount": Decimal("18000.00"),
            "remaining_amount": Decimal("6000.00"),
            "is_signed": True,
        },
        {
            "client_id": clients[4].id,
            "total_amount": Decimal("5000.00"),
            "remaining_amount": Decimal("5000.00"),
            "is_signed": False,
        },
    ]

    created_contracts = []

    for contract_data in contracts_data:
        contract = Contract(**contract_data)
        session.add(contract)
        created_contracts.append(contract)

        client = session.query(Client).get(contract_data["client_id"])
        status = "Signé" if contract_data["is_signed"] else "Non signé"
        print(
            f"- Contrat créé: {client.first_name} {client.last_name} - "
            f"{contract_data['total_amount']}€ ({status})"
        )

    session.commit()

    print(f"\n[OK]{len(created_contracts)} contrats créés avec succès !")
    print("=" * 60)

    return created_contracts


def create_events(session, contracts, users):
    """Crée les événements de test."""

    print("\n" + "=" * 60)
    print("CREATION DES EVENEMENTS DE TEST")
    print("=" * 60)

    # Ne créer des événements que pour les contrats signés
    signed_contracts = [c for c in contracts if c.is_signed]

    # Dates futures pour les événements
    base_date = datetime.now() + timedelta(days=30)

    events_data = [
        {
            "name": "Mariage Jean & Claire",
            "contract_id": signed_contracts[0].id,
            "event_start": base_date + timedelta(days=15),
            "event_end": base_date + timedelta(days=15, hours=6),
            "location": "Château de Versailles",
            "attendees": 150,
            "notes": "Cérémonie en extérieur, prévoir plan B en cas de pluie",
            "support_contact_id": users["support1"].id,
        },
        {
            "name": "Conférence Tech 2025",
            "contract_id": signed_contracts[1].id,
            "event_start": base_date + timedelta(days=45),
            "event_end": base_date + timedelta(days=47),
            "location": "Palais des Congrès, Paris",
            "attendees": 500,
            "notes": "Événement sur 3 jours, besoin de matériel audiovisuel",
            "support_contact_id": users["support2"].id,
        },
        {
            "name": "Gala de Charité",
            "contract_id": signed_contracts[2].id,
            "event_start": base_date + timedelta(days=60),
            "event_end": base_date + timedelta(days=60, hours=4),
            "location": "Hôtel Le Meurice, Paris",
            "attendees": 200,
            "notes": "Dîner de gala, vente aux enchères",
            "support_contact_id": users["support1"].id,
        },
        {
            "name": "Lancement de Produit",
            "contract_id": signed_contracts[3].id,
            "event_start": base_date + timedelta(days=20),
            "event_end": base_date + timedelta(days=20, hours=3),
            "location": "Grand Palais Éphémère",
            "attendees": 300,
            "notes": "Présentation produit + cocktail",
            "support_contact_id": None,  # Pas encore assigné
        },
    ]

    created_events = []

    for event_data in events_data:
        event = Event(**event_data)
        session.add(event)
        created_events.append(event)

        contract = session.query(Contract).get(event_data["contract_id"])
        client = session.query(Client).get(contract.client_id)
        support_status = (
            f"Support: {users['support1'].first_name if event_data.get('support_contact_id') == users['support1'].id else users['support2'].first_name if event_data.get('support_contact_id') else 'Non assigné'}"
        )

        print(
            f"- Événement créé: {event_data['name']} - "
            f"Client: {client.first_name} {client.last_name} ({support_status})"
        )

    session.commit()

    print(f"\n[OK]{len(created_events)} événements créés avec succès !")
    print("=" * 60)

    return created_events


def display_summary(session):
    """Affiche un résumé des données créées."""

    print("\n" + "=" * 60)
    print("RESUME DES DONNEES")
    print("=" * 60)

    # Clients
    total_clients = session.query(Client).count()
    print(f"\nClients: {total_clients}")

    for user in session.query(User).filter_by(department=Department.COMMERCIAL):
        count = session.query(Client).filter_by(sales_contact_id=user.id).count()
        print(f"  - {user.first_name} {user.last_name}: {count} client(s)")

    # Contrats
    total_contracts = session.query(Contract).count()
    signed_contracts = session.query(Contract).filter_by(is_signed=True).count()
    unsigned_contracts = total_contracts - signed_contracts
    print(f"\nContrats: {total_contracts}")
    print(f"  - Signés: {signed_contracts}")
    print(f"  - Non signés: {unsigned_contracts}")

    # Montants
    total_amount = (
        session.query(Contract).with_entities(Contract.total_amount).all()
    )
    total_remaining = (
        session.query(Contract).with_entities(Contract.remaining_amount).all()
    )
    sum_total = sum(amount[0] for amount in total_amount)
    sum_remaining = sum(amount[0] for amount in total_remaining)
    print(f"  - Montant total: {sum_total}€")
    print(f"  - Montant restant: {sum_remaining}€")

    # Événements
    total_events = session.query(Event).count()
    assigned_events = (
        session.query(Event).filter(Event.support_contact_id.isnot(None)).count()
    )
    unassigned_events = total_events - assigned_events
    print(f"\nÉvénements: {total_events}")
    print(f"  - Avec support assigné: {assigned_events}")
    print(f"  - Sans support: {unassigned_events}")

    for user in session.query(User).filter_by(department=Department.SUPPORT):
        count = session.query(Event).filter_by(support_contact_id=user.id).count()
        if count > 0:
            print(f"  - {user.first_name} {user.last_name}: {count} événement(s)")

    print("\n" + "=" * 60)


def main():
    """Point d'entrée principal du script."""

    print("\n" + "=" * 60)
    print("SEED TEST DATA - Epic Events CRM")
    print("=" * 60)

    # Connexion à la base de données
    engine = create_engine("sqlite:///data/epic_events_crm.db")
    Session = sessionmaker(bind=engine)
    session = Session()

    try:
        # Récupérer les utilisateurs
        print("\nRécupération des utilisateurs existants...")
        users = get_users(session)
        print("[OK]Utilisateurs trouvés")

        # Supprimer les données existantes
        print("\nSuppression des données existantes...")
        session.query(Event).delete()
        session.query(Contract).delete()
        session.query(Client).delete()
        session.commit()
        print("[OK]Données existantes supprimées")

        # Créer les données de test
        clients = create_clients(session, users)
        contracts = create_contracts(session, clients)
        events = create_events(session, contracts, users)

        # Afficher le résumé
        display_summary(session)

        print("\nSEED TEST DATA TERMINE AVEC SUCCES !")
        print("=" * 60 + "\n")

        print("\nPour tester, vous pouvez maintenant:")
        print("  - poetry run epicevents login")
        print("  - poetry run epicevents filter-unsigned-contracts")
        print("  - poetry run epicevents filter-unpaid-contracts")
        print("  - poetry run epicevents filter-unassigned-events")
        print("\n" + "=" * 60 + "\n")

    except Exception as e:
        print(f"\nERREUR: {e}")
        session.rollback()
        raise

    finally:
        session.close()


if __name__ == "__main__":
    main()
