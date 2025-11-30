from db import get_connection

def main():
    print("Testing database connection...")
    conn = get_connection()

    if conn:
        cursor = conn.cursor()
        cursor.execute("SELECT 1;")
        result = cursor.fetchone()
        print("DB test result:", result)
        cursor.close()
        conn.close()

if __name__ == "__main__":
    main()
