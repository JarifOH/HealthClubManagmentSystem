import psycopg2


# ========= ADMIN OPERATIONS =========
# 8) Room Booking (Add/List Rooms)
# 9) Class Management (Create/Update Group Classes)
# 10) Equipment Maintenance (log + view/update status)


# ---- Rooms ----

def add_room(conn):
    print("\n=== Add Room ===")
    name = input("Room name: ").strip()
    room_type = input("Room type (e.g., Yoga, Strength): ").strip()
    capacity = input("Capacity: ").strip()

    if not capacity.isdigit():
        print("Capacity must be a positive integer.")
        return

    try:
        cur = conn.cursor()
        cur.execute(
            """
            INSERT INTO Room(name, room_type, capacity)
            VALUES (%s, %s, %s);
            """,
            (name, room_type, int(capacity)),
        )
        conn.commit()
        print("Room added successfully.")
    except psycopg2.Error as e:
        conn.rollback()
        print(f"Error adding room: {e}")
    finally:
        cur.close()


def list_rooms(conn):
    print("\n=== List All Rooms ===")
    try:
        cur = conn.cursor()
        cur.execute(
            """
            SELECT room_id, name, room_type, capacity
            FROM Room
            ORDER BY room_id;
            """
        )
        rows = cur.fetchall()
        if not rows:
            print("No rooms found.")
            return
        for r in rows:
            print(
                f"Room {r[0]}: {r[1]} | Type: {r[2]} | Capacity: {r[3]}"
            )
    except psycopg2.Error as e:
        print(f"Error listing rooms: {e}")
    finally:
        cur.close()


# ---- Group Classes ----

def create_group_class(conn):
    print("\n=== Create Group Class ===")
    title = input("Title: ").strip()
    description = input("Description: ").strip()
    start_time = input("Start (YYYY-MM-DD HH:MM): ").strip()
    end_time = input("End   (YYYY-MM-DD HH:MM): ").strip()
    capacity = input("Capacity: ").strip()
    trainer_id = input("Trainer ID: ").strip()
    room_id = input("Room ID: ").strip()

    if not capacity.isdigit():
        print("Capacity must be integer.")
        return

    try:
        cur = conn.cursor()
        cur.execute(
            """
            INSERT INTO GroupClass(
                title, description, start_time, end_time,
                capacity, trainer_id, room_id
            )
            VALUES (
                %s, %s,
                %s::TIMESTAMP, %s::TIMESTAMP,
                %s, %s, %s
            );
            """,
            (
                title,
                description,
                start_time,
                end_time,
                int(capacity),
                trainer_id or None,
                room_id or None,
            ),
        )
        conn.commit()
        print("Group class created successfully.")
    except psycopg2.Error as e:
        conn.rollback()
        print(f"Error creating class: {e}")
    finally:
        cur.close()


def update_group_class(conn):
    print("\n=== Update Group Class ===")
    class_id = input("Class ID to update: ").strip()
    if not class_id.isdigit():
        print("Invalid class ID.")
        return

    try:
        cur = conn.cursor()
        cur.execute(
            """
            SELECT class_id, title, description, start_time, end_time,
                   capacity, trainer_id, room_id
            FROM GroupClass
            WHERE class_id = %s;
            """,
            (class_id,),
        )
        row = cur.fetchone()
        if not row:
            print("Class not found.")
            return

        print("\nCurrent values:")
        print(f"Title: {row[1]}")
        print(f"Description: {row[2]}")
        print(f"Start: {row[3]}")
        print(f"End: {row[4]}")
        print(f"Capacity: {row[5]}")
        print(f"Trainer ID: {row[6]}")
        print(f"Room ID: {row[7]}")

        print("\nEnter new values (blank = keep current):")
        title = input("New title: ").strip()
        description = input("New description: ").strip()
        start_time = input("New start (YYYY-MM-DD HH:MM): ").strip()
        end_time = input("New end (YYYY-MM-DD HH:MM): ").strip()
        capacity = input("New capacity: ").strip()
        trainer_id = input("New trainer ID: ").strip()
        room_id = input("New room ID: ").strip()

        fields = []
        params = []

        if title:
            fields.append("title = %s")
            params.append(title)
        if description:
            fields.append("description = %s")
            params.append(description)
        if start_time:
            fields.append("start_time = %s::TIMESTAMP")
            params.append(start_time)
        if end_time:
            fields.append("end_time = %s::TIMESTAMP")
            params.append(end_time)
        if capacity:
            fields.append("capacity = %s")
            params.append(int(capacity))
        if trainer_id:
            fields.append("trainer_id = %s")
            params.append(trainer_id)
        if room_id:
            fields.append("room_id = %s")
            params.append(room_id)

        if not fields:
            print("No changes provided.")
            return

        params.append(class_id)
        query = "UPDATE GroupClass SET " + ", ".join(fields) + " WHERE class_id = %s;"
        cur.execute(query, tuple(params))
        conn.commit()
        print("Group class updated successfully.")

    except psycopg2.Error as e:
        conn.rollback()
        print(f"Error updating class: {e}")
    finally:
        cur.close()


# ---- Equipment Maintenance ----

def log_equipment_issue(conn):
    print("\n=== Log Equipment Issue ===")
    equipment_id = input("Equipment ID: ").strip()
    if not equipment_id.isdigit():
        print("Invalid equipment ID.")
        return

    issue_description = input("Issue description: ").strip()

    try:
        cur = conn.cursor()
        cur.execute(
            """
            INSERT INTO EquipmentMaintenance(
                equipment_id, issue_description, status
            )
            VALUES (%s, %s, 'Open');
            """,
            (equipment_id, issue_description),
        )
        conn.commit()
        print("Equipment issue logged as 'Open'.")
    except psycopg2.Error as e:
        conn.rollback()
        print(f"Error logging equipment issue: {e}")
    finally:
        cur.close()


def view_maintenance_requests(conn):
    print("\n=== Equipment Maintenance Requests ===")
    try:
        cur = conn.cursor()
        cur.execute(
            """
            SELECT em.maintenance_id,
                   e.equipment_id,
                   e.name,
                   em.issue_description,
                   em.status,
                   em.reported_at,
                   em.assigned_to,
                   em.resolved_at
            FROM EquipmentMaintenance em
            JOIN Equipment e ON em.equipment_id = e.equipment_id
            ORDER BY em.reported_at DESC;
            """
        )
        rows = cur.fetchall()
        if not rows:
            print("No maintenance records found.")
            return

        for r in rows:
            print(
                f"[#{r[0]}] Equip {r[1]} - {r[2]} | "
                f"Status: {r[4]} | Reported: {r[5]} | "
                f"Assigned to: {r[6]} | Resolved at: {r[7]}\n"
                f"    Issue: {r[3]}"
            )
    except psycopg2.Error as e:
        print(f"Error viewing maintenance: {e}")
    finally:
        cur.close()


def update_maintenance_status(conn):
    print("\n=== Update Maintenance Status ===")
    maintenance_id = input("Maintenance ID: ").strip()
    if not maintenance_id.isdigit():
        print("Invalid ID.")
        return

    new_status = input("New status (Open/In Progress/Resolved): ").strip()
    assigned_to = input("Assigned to (optional): ").strip()

    try:
        cur = conn.cursor()
        if new_status.lower() == "resolved":
            cur.execute(
                """
                UPDATE EquipmentMaintenance
                SET status = %s,
                    assigned_to = NULLIF(%s, ''),
                    resolved_at = NOW()
                WHERE maintenance_id = %s;
                """,
                (new_status, assigned_to, maintenance_id),
            )
        else:
            cur.execute(
                """
                UPDATE EquipmentMaintenance
                SET status = %s,
                    assigned_to = NULLIF(%s, ''),
                    resolved_at = NULL
                WHERE maintenance_id = %s;
                """,
                (new_status, assigned_to, maintenance_id),
            )
        conn.commit()
        print("Maintenance status updated.")
    except psycopg2.Error as e:
        conn.rollback()
        print(f"Error updating maintenance: {e}")
    finally:
        cur.close()


# ---- Wrapper Functions for Main Menu ----

def manage_rooms(conn):
    """Wrapper function to manage rooms (add/list)."""
    while True:
        print("\n=== Room Management ===")
        print("1. Add Room")
        print("2. List All Rooms")
        print("0. Back to Admin Menu")
        
        choice = input("Select an option: ").strip()
        
        if choice == "1":
            add_room(conn)
        elif choice == "2":
            list_rooms(conn)
        elif choice == "0":
            break
        else:
            print("Invalid choice, please try again.")


def manage_group_classes(conn):
    """Wrapper function to manage group classes (create/update)."""
    while True:
        print("\n=== Group Class Management ===")
        print("1. Create Group Class")
        print("2. Update Group Class")
        print("0. Back to Admin Menu")
        
        choice = input("Select an option: ").strip()
        
        if choice == "1":
            create_group_class(conn)
        elif choice == "2":
            update_group_class(conn)
        elif choice == "0":
            break
        else:
            print("Invalid choice, please try again.")


def manage_equipment_maintenance(conn):
    """Wrapper function to manage equipment maintenance (log/view/update)."""
    while True:
        print("\n=== Equipment Maintenance ===")
        print("1. Log Equipment Issue")
        print("2. View Maintenance Requests")
        print("3. Update Maintenance Status")
        print("0. Back to Admin Menu")
        
        choice = input("Select an option: ").strip()
        
        if choice == "1":
            log_equipment_issue(conn)
        elif choice == "2":
            view_maintenance_requests(conn)
        elif choice == "3":
            update_maintenance_status(conn)
        elif choice == "0":
            break
        else:
            print("Invalid choice, please try again.")
