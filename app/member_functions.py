import psycopg2
from datetime import datetime


# ========= MEMBER OPERATIONS =========
# 1) User Registration
# 2) Profile Management
# 3) Health History - Add metric
# 4) Dashboard
# 5) Group Class Registration


def register_member(conn):
    """
    Create a new member in the Member table.
    """
    print("\n=== Register New Member ===")
    full_name = input("Full name: ").strip()
    email = input("Email: ").strip()
    date_of_birth = input("Date of birth (YYYY-MM-DD, optional): ").strip()
    gender = input("Gender (optional): ").strip()
    phone = input("Phone (optional): ").strip()
    goal_description = input("Goal description (optional): ").strip()
    target_weight = input("Target weight in kg (optional): ").strip()

    if not full_name or not email:
        print("Full name and email are required.")
        return

    try:
        cur = conn.cursor()
        cur.execute(
            """
            INSERT INTO Member(
                full_name, email, date_of_birth, gender,
                phone, goal_description, target_weight
            )
            VALUES (%s, %s,
                    NULLIF(%s, '')::DATE,
                    NULLIF(%s, ''),
                    NULLIF(%s, ''),
                    NULLIF(%s, ''),
                    NULLIF(%s, '')::DECIMAL)
            RETURNING member_id;
            """,
            (
                full_name,
                email,
                date_of_birth,
                gender,
                phone,
                goal_description,
                target_weight,
            ),
        )
        new_id = cur.fetchone()[0]
        conn.commit()
        print(f"Member registered successfully with ID: {new_id}")
    except psycopg2.Error as e:
        conn.rollback()
        print(f"Error registering member: {e}")
    finally:
        cur.close()


def update_member_profile(conn):
    """
    Update editable profile fields for an existing member.
    """
    print("\n=== Update Member Profile ===")
    member_id = input("Enter member ID: ").strip()
    if not member_id.isdigit():
        print("Invalid member ID.")
        return

    try:
        cur = conn.cursor()
        cur.execute(
            "SELECT member_id, full_name, email, phone, goal_description, target_weight "
            "FROM Member WHERE member_id = %s;",
            (member_id,),
        )
        row = cur.fetchone()
        if not row:
            print("Member not found.")
            cur.close()
            return

        print("\nCurrent profile:")
        print(f"ID: {row[0]}")
        print(f"Name: {row[1]}")
        print(f"Email: {row[2]}")
        print(f"Phone: {row[3]}")
        print(f"Goal: {row[4]}")
        print(f"Target weight: {row[5]}")

        print("\nEnter new values (leave blank to keep current):")
        new_email = input("New email: ").strip()
        new_phone = input("New phone: ").strip()
        new_goal = input("New goal description: ").strip()
        new_target_weight = input("New target weight in kg: ").strip()

        fields = []
        params = []

        if new_email:
            fields.append("email = %s")
            params.append(new_email)
        if new_phone:
            fields.append("phone = %s")
            params.append(new_phone)
        if new_goal:
            fields.append("goal_description = %s")
            params.append(new_goal)
        if new_target_weight:
            fields.append("target_weight = %s")
            params.append(new_target_weight)

        if not fields:
            print("No changes provided.")
            cur.close()
            return

        params.append(member_id)
        query = "UPDATE Member SET " + ", ".join(fields) + " WHERE member_id = %s;"
        cur.execute(query, tuple(params))
        conn.commit()
        print("Member profile updated successfully.")

    except psycopg2.Error as e:
        conn.rollback()
        print(f"Error updating profile: {e}")
    finally:
        cur.close()


def add_health_metric(conn):
    """
    Insert a new record into HealthMetric for a member.
    """
    print("\n=== Add Health Metric ===")
    member_id = input("Member ID: ").strip()
    if not member_id.isdigit():
        print("Invalid member ID.")
        return

    weight = input("Weight (kg, optional): ").strip()
    heart_rate = input("Heart rate (bpm, optional): ").strip()
    body_fat_percentage = input("Body fat % (optional): ").strip()
    notes = input("Notes (optional): ").strip()

    try:
        cur = conn.cursor()
        cur.execute(
            """
            INSERT INTO HealthMetric(
                member_id, recorded_at, weight, heart_rate,
                body_fat_percentage, notes
            )
            VALUES (
                %s,
                NOW(),
                NULLIF(%s, '')::DECIMAL,
                NULLIF(%s, '')::INT,
                NULLIF(%s, '')::DECIMAL,
                NULLIF(%s, '')
            );
            """,
            (
                member_id,
                weight,
                heart_rate,
                body_fat_percentage,
                notes,
            ),
        )
        conn.commit()
        print("Health metric added successfully.")
    except psycopg2.Error as e:
        conn.rollback()
        print(f"Error adding health metric: {e}")
    finally:
        cur.close()


def view_member_dashboard(conn):
    """
    Shows dashboard info for a member using the member_dashboard_view.
    Assumes your DDL created:
        CREATE VIEW member_dashboard_view AS ...
    """
    print("\n=== Member Dashboard ===")
    member_id = input("Member ID: ").strip()
    if not member_id.isdigit():
        print("Invalid member ID.")
        return

    try:
        cur = conn.cursor()
        cur.execute(
            """
            SELECT *
            FROM member_dashboard_view
            WHERE member_id = %s;
            """,
            (member_id,),
        )
        row = cur.fetchone()
        if not row:
            print("No dashboard data found for that member.")
            return

        # Adjust indexing if your view columns differ
        (
            m_id,
            full_name,
            goal_description,
            target_weight,
            latest_weight,
            latest_heart_rate,
            latest_body_fat,
            upcoming_classes,
        ) = row

        print(f"\nDashboard for Member {m_id} - {full_name}")
        print("----------------------------------")
        print(f"Goal: {goal_description}")
        print(f"Target Weight: {target_weight}")
        print(f"Latest Weight: {latest_weight}")
        print(f"Latest Heart Rate: {latest_heart_rate}")
        print(f"Latest Body Fat %: {latest_body_fat}")
        print(f"Upcoming Classes: {upcoming_classes}")

    except psycopg2.Error as e:
        print(f"Error fetching dashboard: {e}")
    finally:
        cur.close()


def register_for_group_class(conn):
    """
    Register a member for a group class (ClassRegistration table).
    Enforces capacity and prevents duplicate registration.
    """
    print("\n=== Group Class Registration ===")
    member_id = input("Member ID: ").strip()
    if not member_id.isdigit():
        print("Invalid member ID.")
        return

    try:
        cur = conn.cursor()

        # List upcoming classes with remaining spots
        cur.execute(
            """
            SELECT
                gc.class_id,
                gc.title,
                gc.start_time,
                gc.end_time,
                gc.capacity,
                COALESCE(COUNT(cr.registration_id), 0) AS current_reg
            FROM GroupClass gc
            LEFT JOIN ClassRegistration cr
                ON gc.class_id = cr.class_id
            WHERE gc.start_time > NOW()
            GROUP BY gc.class_id, gc.title, gc.start_time, gc.end_time, gc.capacity
            ORDER BY gc.start_time;
            """
        )
        classes = cur.fetchall()

        if not classes:
            print("No upcoming classes available.")
            return

        print("\nAvailable upcoming classes:")
        for c in classes:
            class_id, title, start_time, end_time, capacity, current_reg = c
            remaining = capacity - current_reg
            print(
                f"ID {class_id}: {title} "
                f"({start_time} - {end_time}) "
                f"Capacity: {capacity} | Registered: {current_reg} | Remaining: {remaining}"
            )

        class_id = input("\nEnter class ID to register for: ").strip()
        if not class_id.isdigit():
            print("Invalid class ID.")
            return

        # Check member already registered
        cur.execute(
            """
            SELECT 1 FROM ClassRegistration
            WHERE member_id = %s AND class_id = %s;
            """,
            (member_id, class_id),
        )
        if cur.fetchone():
            print("You are already registered for this class.")
            return

        # Check capacity again, to be safe
        cur.execute(
            """
            SELECT gc.capacity, COALESCE(COUNT(cr.registration_id), 0)
            FROM GroupClass gc
            LEFT JOIN ClassRegistration cr
                ON gc.class_id = cr.class_id
            WHERE gc.class_id = %s
            GROUP BY gc.capacity;
            """,
            (class_id,),
        )
        row = cur.fetchone()
        if not row:
            print("Class not found.")
            return

        capacity, current_reg = row
        if current_reg >= capacity:
            print("Class is full. Cannot register.")
            return

        # Insert registration
        cur.execute(
            """
            INSERT INTO ClassRegistration(member_id, class_id)
            VALUES (%s, %s);
            """,
            (member_id, class_id),
        )
        conn.commit()
        print("Successfully registered for the class.")

    except psycopg2.Error as e:
        conn.rollback()
        print(f"Error registering for class: {e}")
    finally:
        cur.close()
