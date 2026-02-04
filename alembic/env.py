# from logging.config import fileConfig

# from dotenv import load_dotenv
# import os

# load_dotenv()


# import os

# from sqlalchemy import create_engine, pool
# from alembic import context

# # Alembic Config object
# config = context.config

# # Configure logging
# if config.config_file_name is not None:
#     fileConfig(config.config_file_name)

# # Import your metadata
# from app.database import Base
# target_metadata = Base.metadata


# # 🔑 Read DB URL from environment
# DATABASE_URL = os.getenv("DATABASE_URL")

# if not DATABASE_URL:
#     raise RuntimeError("DATABASE_URL environment variable is not set")


# def run_migrations_offline() -> None:
#     """Run migrations in 'offline' mode."""
#     context.configure(
#         url=DATABASE_URL,
#         target_metadata=target_metadata,
#         literal_binds=True,
#         dialect_opts={"paramstyle": "named"},
#     )

#     with context.begin_transaction():
#         context.run_migrations()


# def run_migrations_online() -> None:
#     """Run migrations in 'online' mode."""
#     connectable = create_engine(
#         DATABASE_URL,
#         poolclass=pool.NullPool,
#     )

#     with connectable.connect() as connection:
#         context.configure(
#             connection=connection,
#             target_metadata=target_metadata,
#         )

#         with context.begin_transaction():
#             context.run_migrations()


# if context.is_offline_mode():
#     run_migrations_offline()
# else:
#     run_migrations_online()


from logging.config import fileConfig
from alembic import context
from sqlalchemy import create_engine, pool
import os
from app.database import Base, db_path  # Import your Base and SQLite path

# Alembic Config object
config = context.config

# Configure logging
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# ✅ Target metadata from database.py
target_metadata = Base.metadata

# ✅ Force Alembic to use the local SQLite path in AppData
LOCAL_DATABASE_URL = f"sqlite:///{db_path}"

def run_migrations_offline():
    """Run migrations in 'offline' mode."""
    context.configure(
        url=LOCAL_DATABASE_URL,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online():
    """Run migrations in 'online' mode."""
    connectable = create_engine(
        LOCAL_DATABASE_URL,
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
