from sqlalchemy import text

from db.database import SessionLocal


def test_connection():
    try:
        session = SessionLocal()
        session.execute(text("SELECT * from media"))  # trivial query to test connection
        print("✅ Connection to database successful.")
    except Exception as e:
        print("❌ Failed to connect to database:", e)
    finally:
        session.close()


if __name__ == "__main__":
    test_connection()
