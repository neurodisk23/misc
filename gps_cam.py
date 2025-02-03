import cv2
import gpsd
import csv
from threading import Thread, Lock
import time

# Shared GPS Data
gps_data = {
    'timestamp': None,
    'latitude': None,
    'longitude': None,
    'speed': None,
    'altitude': None,
    'hdop': None
}

gps_lock = Lock()

def gps_thread_function():
    """Fetch GPS data continuously and update shared variables."""
    gpsd.connect()

    while True:
        try:
            packet = gpsd.get_current()

            if packet.mode >= 2:  # Valid 2D/3D fix
                with gps_lock:
                    gps_data['timestamp'] = packet.time
                    gps_data['latitude'] = packet.lat
                    gps_data['longitude'] = packet.lon
                    gps_data['speed'] = packet.hspeed
                    gps_data['altitude'] = packet.alt
                    gps_data['hdop'] = packet.hdop  # Requires gpsd support
            else:
                with gps_lock:
                    # Reset data if fix is lost
                    gps_data.update({k: None for k in gps_data})

        except Exception as e:
            print(f"GPS Error: {e}")
        time.sleep(0.1)

def main():
    # Video setup
    cap = cv2.VideoCapture('/dev/video0')
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = cap.get(cv2.CAP_PROP_FPS)
    fourcc = cv2.VideoWriter_fourcc(*'XVID')
    out = cv2.VideoWriter('output.avi', fourcc, fps, (width, height))

    # CSV setup
    csv_file = open('gps_log.csv', 'w', newline='')
    csv_writer = csv.writer(csv_file)
    csv_writer.writerow([
        'video_timestamp_sec',
        'gps_timestamp',
        'latitude',
        'longitude',
        'speed',
        'altitude',
        'hdop'
    ])

    # Start GPS thread
    gps_thread = Thread(target=gps_thread_function, daemon=True)
    gps_thread.start()

    start_time = time.time()

    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                break

            video_timestamp_sec = round(time.time() - start_time, 3)

            with gps_lock:
                current_gps = gps_data.copy()

            # Handle None values
            lat = current_gps['latitude'] if current_gps['latitude'] is not None else 0.0
            lon = current_gps['longitude'] if current_gps['longitude'] is not None else 0.0
            speed = current_gps['speed'] if current_gps['speed'] is not None else 0.0
            altitude = current_gps['altitude'] if current_gps['altitude'] is not None else 0.0
            hdop = current_gps['hdop'] if current_gps['hdop'] is not None else 0.0
            gps_time = current_gps['timestamp'] if current_gps['timestamp'] is not None else "N/A"

            # Overlay data (skip if no fix)
            if current_gps['timestamp'] is not None:
                cv2.putText(frame, f"Time: {video_timestamp_sec}s", (10, 30),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                cv2.putText(frame, f"Lat: {lat:.6f}", (10, 60),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                cv2.putText(frame, f"Lon: {lon:.6f}", (10, 90),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                cv2.putText(frame, f"HDOP: {hdop:.1f}", (10, 120),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
            else:
                cv2.putText(frame, "Awaiting GPS fix...", (10, 30),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)

            out.write(frame)
            csv_writer.writerow([
                video_timestamp_sec,
                gps_time,
                lat,
                lon,
                speed,
                altitude,
                hdop
            ])
            csv_file.flush()

            cv2.imshow('Frame', frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

    except KeyboardInterrupt:
        print("Stopped by user.")
    finally:
        cap.release()
        out.release()
        csv_file.close()
        cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
