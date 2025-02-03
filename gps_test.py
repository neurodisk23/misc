import serial
import pynmea2
from datetime import datetime

def parse_gps_data(port='/dev/serial0', baudrate=9600):
    ser = serial.Serial(port, baudrate, timeout=1)

    try:
        while True:
            line = ser.readline().decode('utf-8', errors='replace').strip()

            if line.startswith('$'):
                try:
                    msg = pynmea2.parse(line)
                    # Extract data based on NMEA sentence type
                    if isinstance(msg, pynmea2.types.talker.GGA):
                        # GPGGA: Time, Lat, Lon, Altitude, HDOP
                        print(f"[{datetime.now().strftime('%H:%M:%S')}] GPGGA Sentence:")
                        print(f" Time (UTC): {msg.timestamp}")
                        print(f" Latitude: {msg.lat} {msg.lat_dir}")
                        print(f" Longitude: {msg.lon} {msg.lon_dir}")
                        print(f" Altitude: {msg.altitude} {msg.altitude_units}")
                        print(f" HDOP: {msg.horizontal_dil}")
                        print("-" * 40)
                    elif isinstance(msg, pynmea2.types.talker.RMC):
                        # GPRMC: Speed, Date
                        print(f"[{datetime.now().strftime('%H:%M:%S')}] GPRMC Sentence:")
                        print(f" Speed (knots): {msg.spd_over_grnd}")
                        print(f" Date: {msg.datestamp}")
                        print("-" * 40)
                        print("\n\n\n\n")
                        print("-" * 40)
                except Exception as e:
                    print(f"Error parsing data: {e}")
    except KeyboardInterrupt:
        print("Exiting...")
    finally:
        ser.close()

if __name__ == "__main__":
    parse_gps_data()
