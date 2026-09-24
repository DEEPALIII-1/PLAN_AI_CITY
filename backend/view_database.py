import sqlite3
import os
import sys

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

def print_table(cursor, table_name, query, limit=50):
    print(f"\n{'='*80}")
    print(f"📊 TABLE: {table_name.upper()}")
    print(f"{'='*80}")
    try:
        cursor.execute(query)
        rows = cursor.fetchall()
        if not rows:
            print("  (No rows found)")
            return
        
        # Get column names
        col_names = [description[0] for description in cursor.description]
        
        # Calculate col widths
        col_widths = [len(col) for col in col_names]
        for row in rows[:limit]:
            for i, val in enumerate(row):
                val_str = str(val) if val is not None else "NULL"
                if len(val_str) > 35:
                    val_str = val_str[:32] + "..."
                if len(val_str) > col_widths[i]:
                    col_widths[i] = min(len(val_str), 35)

        # Header
        header = " | ".join(col_names[i].ljust(col_widths[i]) for i in range(len(col_names)))
        separator = "-+-".join("-" * col_widths[i] for i in range(len(col_names)))
        print(header)
        print(separator)

        # Rows
        for row in rows[:limit]:
            formatted_cells = []
            for i, val in enumerate(row):
                val_str = str(val) if val is not None else "NULL"
                if len(val_str) > 35:
                    val_str = val_str[:32] + "..."
                formatted_cells.append(val_str.ljust(col_widths[i]))
            print(" | ".join(formatted_cells))
        
        if len(rows) > limit:
            print(f"  ... ({len(rows) - limit} more rows)")
        print(f"Total Records: {len(rows)}")
    except Exception as e:
        print(f"Error querying {table_name}: {e}")

def main():
    db_path = os.path.join(os.path.dirname(__file__), "plan_ai_city.db")
    if not os.path.exists(db_path):
        print(f"Database not found at {db_path}")
        return

    print("\n" + "="*80)
    print(f"🚀 PLAN AI CITY - SQLITE DATABASE VIEWER")
    print(f"Database Path: {db_path}")
    print("="*80)

    conn = sqlite3.connect(db_path)
    c = conn.cursor()

    # 1. User Profiles (Dedicated Profile Table)
    print_table(
        c, 
        "user_profiles (Your Stored Profile Details)", 
        "SELECT id, user_id, full_name, email, phone_number, home_city, home_state, account_status, created_at FROM user_profiles"
    )

    # 2. Users (Authentication Table)
    print_table(
        c,
        "users (Login Credentials & Role)",
        "SELECT id, email, role, is_active, created_at FROM users"
    )

    # 3. User Preferences & Persona Clusters
    print_table(
        c,
        "user_preferences (AI Personalization)",
        "SELECT id, user_id, budget_tier, travel_style, preferred_pace, cluster_id FROM user_preferences"
    )

    # 4. Pan-India Cities, Towns & Villages
    print_table(
        c,
        "cities (Pan-India Destinations & Villages)",
        "SELECT id, name, state, locality_type, latitude, longitude, best_time_to_visit FROM cities ORDER BY id"
    )

    # 5. Places Sample
    print_table(
        c,
        "places (Curated & Verified Attractions)",
        "SELECT id, city_id, name, estimated_cost, avg_visit_duration_mins, rating FROM places LIMIT 10"
    )

    conn.close()
    print("\n" + "="*80)
    print("✅ Completed viewing SQLite Database.")
    print("="*80 + "\n")

if __name__ == "__main__":
    main()
