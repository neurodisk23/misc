import serial
import time
import string
import pynmea2

while True:
    # Specify the correct serial port name
    port = "/dev/ttyAMA0"  # Correct spelling of "/dev/ttyAMA0"

    try:
        # Initialize serial connection
        ser = serial.Serial(port, baudrate=9600, timeout=0.5)

        # Create NMEA reader object
        dataout = pynmea2.NMEAReader()

        # Read a single NMEA message
        newdata = ser.readline().decode()  # Decode the byte string to a regular string

        # Check if the message is a $GPRMC message
        if newdata.startswith("$GPRMC"):
            # Parse the message
            newmsg = pynmea2.parse(newdata)

            # Extract latitude and longitude
            lat = newmsg.latitude
            lng = newmsg.longitude

            # Create a string to hold the GPS coordinates
            gps = "Latitude: " + str(lat) + " and Longitude: " + str(lng)

            # Print the GPS coordinates
            print(gps)
    except serial.SerialException as e:
        print(f"Error: {e}")
    finally:
        # Always close the serial connection
        ser.close()
