from sqlalchemy import create_engine
from sqlalchemy.orm.session import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
SQL_DATABASE = 'sqlite:///./data.db'

# engine will be used to make session
# the connect_args are only there as long as we use sqlite, for others such as pgsql or mysql this wont be necessary
engine = create_engine(SQL_DATABASE, connect_args={'check_same_thread': False})

# this sessionmaker uses the engine to create a SessionLocal which
# when called returns our database session which we can query
SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)

# we will make our models (and hence tables) with this base
Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
