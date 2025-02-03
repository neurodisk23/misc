import serial  # import serial package
from time import sleep

def GPS_Info():
    global NMEA_buff
    global lat_in_degrees
    global long_in_degrees
    nmea_time = []
    nmea_latitude = []
    nmea_longitude = []
    
    nmea_time = NMEA_buff[0]  # Extract time from GPGGA string
    nmea_latitude = NMEA_buff[1]  # Extract latitude from GPGGA string
    nmea_longitude = NMEA_buff[3]  # Extract longitude from GPGGA string
    nmea_hdop = NMEA_buff[8] 

    print("NMEA Time: ", nmea_time)
    print("NMEA Latitude:", nmea_latitude, "NMEA Longitude:", nmea_longitude)
    print(" HDOP: ", nmea_hdop)
    

    # Check if latitude and longitude values are available
    if nmea_latitude and nmea_longitude:
        try:
            lat = float(nmea_latitude)  # Convert string into float for calculation
            longi = float(nmea_longitude)  # Convert string into float for calculation
        except ValueError as e:
            print("Error converting latitude or longitude to float:", e)
            return

        lat_in_degrees = convert_to_degrees(lat)  # Get latitude in degree decimal format
        long_in_degrees = convert_to_degrees(longi)  # Get longitude in degree decimal format

        print("Latitude in degrees:", lat_in_degrees, "Longitude in degrees:", long_in_degrees)
    else:
        print("No valid latitude or longitude data available.")

# Convert raw NMEA string into degree decimal format   
def convert_to_degrees(raw_value):
    decimal_value = raw_value / 100.00
    degrees = int(decimal_value)
    mm_mmmm = (decimal_value - int(decimal_value)) / 0.6
    position = degrees + mm_mmmm
    position = "%.4f" % (position)
    return position


gpgga_info = "$GPGGA,"
gprmc_info = "$GPRMC"
ser = serial.Serial("/dev/ttyAMA0")  # Open port with baud rate
GPGGA_buffer = 0
NMEA_buff = 0
lat_in_degrees = 0
long_in_degrees = 0

try:
    while True:
        received_data = (str)(ser.readline())  # Read NMEA string received
        GPGGA_data_available = received_data.find(gpgga_info)  # Check for NMEA GPGGA string                 
        if GPGGA_data_available > 0:
            GPGGA_buffer = received_data.split("$GPGGA,", 1)[1]  # Store data coming after "$GPGGA," string 
            NMEA_buff = (GPGGA_buffer.split(','))  # Store comma separated data in buffer
            GPS_Info()  # Get time, latitude, longitude
except KeyboardInterrupt:
    print("Terminated by user.")
