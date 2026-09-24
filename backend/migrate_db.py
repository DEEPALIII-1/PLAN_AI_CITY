import sqlite3
import datetime

def migrate():
    conn = sqlite3.connect("plan_ai_city.db")
    c = conn.cursor()

    # 1. Check cities columns
    c.execute("PRAGMA table_info(cities)")
    cols = [col[1] for col in c.fetchall()]
    print("Current cities columns:", cols)

    if "district" not in cols:
        c.execute("ALTER TABLE cities ADD COLUMN district VARCHAR(100)")
        print("Added 'district' column to cities.")

    if "locality_type" not in cols:
        c.execute("ALTER TABLE cities ADD COLUMN locality_type VARCHAR(50) DEFAULT 'city'")
        print("Added 'locality_type' column to cities.")

    # 2. Check user_profiles table
    c.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='user_profiles'")
    tbl = c.fetchone()
    if not tbl:
        print("Creating user_profiles table...")
        c.execute("""
            CREATE TABLE user_profiles (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL UNIQUE,
                full_name VARCHAR(150),
                email VARCHAR(255) NOT NULL,
                phone_number VARCHAR(30),
                home_city VARCHAR(100),
                home_state VARCHAR(100),
                country VARCHAR(100) DEFAULT 'India',
                bio TEXT,
                preferred_language VARCHAR(50) DEFAULT 'English',
                account_status VARCHAR(50) DEFAULT 'active',
                total_itineraries_created INTEGER DEFAULT 0,
                total_places_explored INTEGER DEFAULT 0,
                last_login_at DATETIME,
                created_at DATETIME,
                updated_at DATETIME,
                FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
            )
        """)
        c.execute("CREATE INDEX IF NOT EXISTS ix_user_profiles_user_id ON user_profiles (user_id)")
        c.execute("CREATE INDEX IF NOT EXISTS ix_user_profiles_email ON user_profiles (email)")
        print("user_profiles table created successfully.")
    else:
        print("user_profiles table already exists.")

    # 3. Backfill any existing users who lack a user_profiles row
    c.execute("SELECT id, email, full_name, created_at FROM users")
    users = c.fetchall()
    now_str = datetime.datetime.utcnow().isoformat()
    for u_id, u_email, u_name, u_created in users:
        c.execute("SELECT id FROM user_profiles WHERE user_id = ?", (u_id,))
        if not c.fetchone():
            c.execute("""
                INSERT INTO user_profiles 
                (user_id, full_name, email, phone_number, home_city, home_state, country, account_status, total_itineraries_created, total_places_explored, last_login_at, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (u_id, u_name, u_email, None, "Delhi", "Delhi NCR", "India", "active", 0, 0, u_created or now_str, u_created or now_str, now_str))
            print(f"Backfilled profile for user {u_email}")

    conn.commit()
    c.execute("SELECT name FROM sqlite_master WHERE type='table'")
    print("All tables in DB:", [row[0] for row in c.fetchall()])
    conn.close()

if __name__ == "__main__":
    migrate()
