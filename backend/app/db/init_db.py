from app.core.database import engine, SessionLocal, Base
from app.models import *
from app.db.seed_data import seed_database

def init_db():
    print("Creating database tables...")
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        seed_database(db)
    finally:
        db.close()

if __name__ == "__main__":
    init_db()
