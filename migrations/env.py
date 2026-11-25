"""Database migrations use the Flask application's configured database."""
from alembic import context
from flask import current_app

db = current_app.extensions["migrate"].db
target_metadata = db.metadata


def run_migrations_offline():
    context.configure(url=str(db.engine.url).replace("%", "%%"),
                      target_metadata=target_metadata, literal_binds=True)
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online():
    with db.engine.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata,
                          compare_type=True)
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
