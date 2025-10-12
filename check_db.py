"""
Script de vérification de la base de données Epic Events.
Affiche la structure des tables créées par Alembic.
"""
from sqlalchemy import create_engine, inspect

# Connexion à la base de données
engine = create_engine("sqlite:///epic_events.db")
inspector = inspect(engine)

# Lister toutes les tables
print("=" * 50)
print("Tables dans la base de donnees:")
print("=" * 50)
for table_name in inspector.get_table_names():
    print(f"  - {table_name}")

# Détails de chaque table
tables = ["users", "clients", "contracts", "events"]
for table in tables:
    print(f"\n{'=' * 50}")
    print(f"Colonnes de la table '{table}':")
    print("=" * 50)
    for column in inspector.get_columns(table):
        nullable = "NULL" if column["nullable"] else "NOT NULL"
        print(f"  - {column['name']:<20} {str(column['type']):<20} {nullable}")

    # Afficher les clés étrangères
    fks = inspector.get_foreign_keys(table)
    if fks:
        print(f"\n  Cles etrangeres:")
        for fk in fks:
            print(
                f"    -> {fk['constrained_columns'][0]} -> {fk['referred_table']}.{fk['referred_columns'][0]}"
            )

print("\n" + "=" * 50)
print("Verification terminee avec succes!")
print("=" * 50)
