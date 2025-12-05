from sqlalchemy import create_engine, text
import numpy as np

DB_URL = "postgresql+psycopg://ai:ai@localhost:5532/ai"

# Create engine
engine = create_engine(DB_URL, future=True)

def test_connection():
    print("🔌 Testing database connection...")
    try:
        with engine.connect() as conn:
            result = conn.execute(text("SELECT version();"))
            print("Connected to:", result.fetchone()[0])
    except Exception as e:
        print("❌ Connection failed:", e)
        return False

    print("✅ Database connection successful")
    return True


def test_pgvector_extension():
    print("\n🔎 Checking for pgvector extension...")
    try:
        with engine.connect() as conn:
            result = conn.execute(text("""
                SELECT extname FROM pg_extension WHERE extname = 'vector';
            """))
            row = result.fetchone()
            if row:
                print("✅ pgvector extension FOUND")
                return True
            else:
                print("❌ pgvector extension NOT found")
                return False
    except Exception as e:
        print("❌ Error checking extension:", e)
        return False


def test_vector_operations():
    print("\n🧪 Testing vector insert & similarity search...")

    try:
        with engine.begin() as conn:
            # Create table
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS vec_test (
                    id SERIAL PRIMARY KEY,
                    embedding vector(3)
                );
            """))

            # Insert example vectors
            conn.execute(text("""
                INSERT INTO vec_test (embedding)
                VALUES ('[1, 0, 0]'),
                       ('[0, 1, 0]'),
                       ('[1, 1, 0]');
            """))

            # Query similarity
            result = conn.execute(text("""
                SELECT id, embedding <-> '[1, 0, 0]' AS distance
                FROM vec_test
                ORDER BY embedding <-> '[1, 0, 0]'
                LIMIT 3;
            """))

            rows = result.fetchall()

            print("Similarity results:")
            for r in rows:
                print(f"ID: {r.id}, Distance: {r.distance}")

        print("✅ Vector operations working")
        return True

    except Exception as e:
        print("❌ Vector test failed:", e)
        return False



if __name__ == "__main__":
    print("=== DATABASE & PGVECTOR TEST ===")
    test_connection()
    test_pgvector_extension()
    test_vector_operations()
