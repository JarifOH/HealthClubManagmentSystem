import psycopg2


# ========= TRAINER OPERATIONS =========
# 6) Set Availability
# 7) Schedule View


def set_trainer_availability(conn):
    """
    Insert a new availability slot into TrainerAvailability.
    Trigger/constraints will block overlaps if you set them in DDL.
    """
    print("\n=== Set Trainer Availability ===")
    trainer_id = input("Trainer ID: ").strip()
    if not trainer_id.isdigit():
        print("Invalid trainer ID.")
        return

    day_of_week = input("Day of week (e.g., Monday): ").strip()
    start_time = input("Start time (HH:MM): ").strip()
    end_time = input("End time (HH:MM): ").strip()

    try:
        cur = conn.cursor()
        cur.execute(
            """
            INSERT INTO TrainerAvailability(trainer_id, day_of_week, start_time, end_time)
            VALUES (%s, %s, %s::TIME, %s::TIME);
            """,
            (trainer_id, day_of_week, start_time, end_time),
        )
        conn.commit()
        print("Availability added successfully.")
    except psycopg2.Error as e:
        conn.rollback()
        print(f"Error setting availability: {e}")
    finally:
        cur.close()


def view_trainer_schedule(conn):
    """
    Show upcoming group classes and PT sessions for a trainer.
    """
    print("\n=== Trainer Schedule View ===")
    trainer_id = input("Trainer ID: ").strip()
    if not trainer_id.isdigit():
        print("Invalid trainer ID.")
        return

    try:
        cur = conn.cursor()

        print("\nUpcoming Group Classes:")
        cur.execute(
            """
            SELECT class_id, title, start_time, end_time, room_id
            FROM GroupClass
            WHERE trainer_id = %s AND start_time >= NOW()
            ORDER BY start_time;
            """,
            (trainer_id,),
        )
        rows = cur.fetchall()
        if rows:
            for r in rows:
                print(
                    f"Class {r[0]}: {r[1]} | {r[2]} - {r[3]} | Room {r[4]}"
                )
        else:
            print("No upcoming group classes.")

        print("\nUpcoming PT Sessions:")
        cur.execute(
            """
            SELECT pt_session_id, member_id, start_time, end_time, room_id, status
            FROM PTSession
            WHERE trainer_id = %s AND start_time >= NOW()
            ORDER BY start_time;
            """,
            (trainer_id,),
        )
        rows = cur.fetchall()
        if rows:
            for r in rows:
                print(
                    f"Session {r[0]} with Member {r[1]} | "
                    f"{r[2]} - {r[3]} | Room {r[4]} | Status: {r[5]}"
                )
        else:
            print("No upcoming PT sessions.")

    except psycopg2.Error as e:
        print(f"Error fetching schedule: {e}")
    finally:
        cur.close()
