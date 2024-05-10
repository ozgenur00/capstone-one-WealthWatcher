from logging.config import fileConfig
from alembic import context
from sqlalchemy import engine_from_config, pool
import sys

# Projedeki Flask uygulamasına erişmek için doğru yolu sisteme ekleyin
sys.path.append('/home/ozgenur00/personal-finance-manager')

# Flask uygulamasını ve SQLAlchemy nesnesini import edin
from app import app, db

# Alembic yapılandırmasını ve logging'ini yükleyin
config = context.config
fileConfig(config.config_file_name)

# SQLAlchemy bağlantı URL'sini yapılandırın
config.set_main_option('sqlalchemy.url', app.config['SQLALCHEMY_DATABASE_URI'])

# Alembic için hedef metadatayı ayarlayın
target_metadata = db.metadata

def run_migrations_offline():
    """Alembic ile offline migration çalıştır."""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(url=url, target_metadata=target_metadata, literal_binds=True)
    with context.begin_transaction():
        context.run_migrations()

def run_migrations_online():
    """Alembic ile online migration çalıştır."""
    # Engine bağlantısını yapılandır
    connectable = engine_from_config(
        config.get_section(config.config_ini_section),
        prefix='sqlalchemy.',
        poolclass=pool.NullPool
    )

    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)
        with context.begin_transaction():
            context.run_migrations()

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
