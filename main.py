# app/main.py

from db import get_connection

# ---- import your feature functions ----
# Make sure these names exist in the three modules.
from member_functions import (
    register_member,            # User Registration
    update_member_profile,      # Profile Management
    add_health_metric,          # Health History – Add metric
    view_member_dashboard,      # Dashboard
    register_for_group_class,   # Group Class Registration
)

from trainer_functions import (
    set_trainer_availability,   # Set Availability
    view_trainer_schedule,      # Schedule View
)

from admin_functions import (
    manage_rooms,               # Room Booking (Add/List Rooms)
    manage_group_classes,       # Class Management (Create/Update Group Classes)
    manage_equipment_maintenance,  # Equipment Maintenance (log + view/update)
)


# ---------- MENUS ----------

def member_menu(conn):
    while True:
        print("\n=== Member Menu ===")
        print("1. User Registration")
        print("2. Profile Management")
        print("3. Add Health Metric")
        print("4. View Dashboard")
        print("5. Register for Group Class")
        print("0. Back to Main Menu")

        choice = input("Select an option: ").strip()

        if choice == "1":
            register_member(conn)
        elif choice == "2":
            update_member_profile(conn)
        elif choice == "3":
            add_health_metric(conn)
        elif choice == "4":
            view_member_dashboard(conn)
        elif choice == "5":
            register_for_group_class(conn)
        elif choice == "0":
            break
        else:
            print("Invalid choice, please try again.")


def trainer_menu(conn):
    while True:
        print("\n=== Trainer Menu ===")
        print("1. Set Availability")
        print("2. View Schedule")
        print("0. Back to Main Menu")

        choice = input("Select an option: ").strip()

        if choice == "1":
            set_trainer_availability(conn)
        elif choice == "2":
            view_trainer_schedule(conn)
        elif choice == "0":
            break
        else:
            print("Invalid choice, please try again.")


def admin_menu(conn):
    while True:
        print("\n=== Admin Menu ===")
        print("1. Room Booking (Add/List Rooms)")
        print("2. Group Class Management")
        print("3. Equipment Maintenance")
        print("0. Back to Main Menu")

        choice = input("Select an option: ").strip()

        if choice == "1":
            manage_rooms(conn)
        elif choice == "2":
            manage_group_classes(conn)
        elif choice == "3":
            manage_equipment_maintenance(conn)
        elif choice == "0":
            break
        else:
            print("Invalid choice, please try again.")


# ---------- MAIN APP ----------

def main():
    print("Connecting to database...")
    conn = get_connection()

    if not conn:
        # get_connection already prints the error
        print("Could not connect to database. Exiting.")
        return

    # quick sanity check (similar to your old SELECT 1 test)
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT 1;")
            result = cur.fetchone()
            print("DB test result:", result)
    except Exception as e:
        print("Database test query failed:", e)
        conn.close()
        return

    # top-level menu
    while True:
        print("\n=== Health Club Management System ===")
        print("1. Member")
        print("2. Trainer")
        print("3. Admin")
        print("0. Exit")

        role = input("Select your role: ").strip()

        if role == "1":
            member_menu(conn)
        elif role == "2":
            trainer_menu(conn)
        elif role == "3":
            admin_menu(conn)
        elif role == "0":
            print("Goodbye!")
            break
        else:
            print("Invalid choice, please try again.")

    conn.close()


if __name__ == "__main__":
    main()

