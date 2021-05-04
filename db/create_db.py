from sqlalchemy import MetaData, Table, Column, Integer, String, Boolean, inspect, create_engine

DB_URL = "postgresql://user:user@localhost/xo_db"

engine = create_engine(DB_URL)

metadata = MetaData(engine)

table = Table(
    'users', metadata,
    Column('id', Integer, primary_key=True, autoincrement=True),
    Column('created_at', Integer),
    Column('last_seen_at', Integer),
    Column('login', String(32), nullable=False, unique=True),
    Column('password_hash', String(256), nullable=False),
    Column('online', Boolean, default=False),
    Column('deleted', Boolean, default=False)
)

inspector = inspect(engine)
if 'users' in inspector.get_table_names():
    table.drop(engine)
table.create(engine)

for _t in metadata.tables:
    print("Table: ", _t)
