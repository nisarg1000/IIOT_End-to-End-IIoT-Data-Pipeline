import time
from datetime import datetime
from sense_hat import SenseHat
import psycopg2
import os
import traceback

# Configure DB connection using environment variables or defaults
DB_HOST = os.getenv('DB_HOST', '10.137.158.251')   # laptop IP
DB_PORT = os.getenv('DB_PORT', '5432')
DB_NAME = os.getenv('DB_NAME', 'lab12')
DB_USER = os.getenv('DB_USER', 'postgres')
DB_PASS = os.getenv('DB_PASS', '1234')

sense = SenseHat()
sense.clear()
# Function to read sensor data
def get_sensor_readings():
    t = sense.get_temperature()       
    h = sense.get_humidity()
    p = sense.get_pressure()
    o = sense.get_orientation_radians()  
    return {
        "temp_c": round(t, 2),
        "humidity": round(h, 2),
        "pressure": round(p, 2),
        "roll": round(o.get('roll', 0), 3),
        "pitch": round(o.get('pitch', 0), 3),
        "yaw": round(o.get('yaw', 0), 3)
    }

def insert_reading(conn, r):
    with conn.cursor() as cur:
        cur.execute("""
            INSERT INTO sense_readings (temp_c, humidity, pressure, orientation_roll, orientation_pitch, orientation_yaw) 
            VALUES (%s, %s, %s, %s, %s, %s) 
        """, (r['temp_c'], r['humidity'], r['pressure'], r['roll'], r['pitch'], r['yaw']))
        conn.commit()
#
def main(poll_interval=10.0): # seconds
    conn = None
    try:
        conn = psycopg2.connect(
            host=DB_HOST, port=DB_PORT, dbname=DB_NAME, user=DB_USER, password=DB_PASS
        )
        print("Connected to DB")
        while True:
            r = get_sensor_readings()
            print(datetime.utcnow().isoformat(), r) 
            try:
                insert_reading(conn, r)
            except Exception as e:
                print("Insert failed:", e)
                traceback.print_exc()
            time.sleep(poll_interval)
    except Exception as e:
        print("Connection failed:", e)
        traceback.print_exc()
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    main(poll_interval=10)  # every 10s
