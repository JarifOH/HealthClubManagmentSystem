import psycopg2

def get_connection():
    try:
        conn = psycopg2.connect(
            host="localhost",
            database="comp3005FinalProject",    
            user="postgres",          
            password="password", 
            port="port_number"               
        )
        print("Database connection successful!")
        return conn

    except Exception as e:
        print("Database connection failed!")
        print("Error:", e)
        return None
