import serial
import numpy as np
import pandas as pd

def read_calibration_data(calibration_file):
    """
    Reads the calibration data from the specified file.
    Each line in the file should have the format:
    RoomID,Ancla1:-XX,Ancla2:-YY,Ancla3:-ZZ,...
    """
    calibration_data = []
    with open(calibration_file, 'r') as f:
        for line in f:
            line = line.strip()
            if line:
                parts = line.split(',')
                room_name = parts[0]
                calib_row = {'Room': room_name}
                for part in parts[1:]:
                    try:
                        device, rssi = part.split(':')
                        calib_row[device] = float(rssi)
                    except ValueError:
                        continue
                calibration_data.append(calib_row)
    return pd.DataFrame(calibration_data)

def read_live_data(ser):
    """
    Reads live RSSI data from the serial port.
    Expects data in the format: AnclaX:-YY
    """
    live_data = {}
    # Read data from the serial port until we have readings from all devices
    while len(live_data) < 5:
        line = ser.readline().decode().strip()
        if line:
            try:
                device, rssi = line.split(':')
                live_data[device] = float(rssi)
            except ValueError:
                continue
    return live_data

def compute_distance(calibration_row, live_data):
    """
    Computes the Euclidean distance between the calibration data and live data.
    """
    devices = ['Ancla1', 'Ancla2', 'Ancla3', 'Ancla4', 'Ancla5']
    distances = []
    for device in devices:
        if device in live_data and device in calibration_row:
            distances.append((live_data[device] - calibration_row[device])**2)
        else:
            # Assign a large error if data is missing
            distances.append(10000)
    return np.sqrt(sum(distances))

def find_closest_room(calibration_data, live_data):
    """
    Finds the room with the calibration data closest to the live data.
    """
    min_distance = float('inf')
    closest_room = None
    for idx, row in calibration_data.iterrows():
        room_name = row['Room']
        calibration_row = row
        distance = compute_distance(calibration_row, live_data)
        if distance < min_distance:
            min_distance = distance
            closest_room = room_name
    return closest_room

def main():
    # Specify the calibration file path
    calibration_file = r"C:\Users\Pablo\Desktop\Programas PYTHON\calibra_coordenadas.txt"
    # Read calibration data
    calibration_data = read_calibration_data(calibration_file)
    
    # Open serial port
    ser = serial.Serial('COM1', 9600, timeout=1)
    print("Listening for live data on COM1...")
    
    try:
        while True:
            # Read live data from the serial port
            live_data = read_live_data(ser)
            if live_data:
                # Find the closest matching room
                room = find_closest_room(calibration_data, live_data)
                print(f"The tag is located in room: {room}")
    except KeyboardInterrupt:
        print("Program terminated by user.")
    finally:
        ser.close()

if __name__ == "__main__":
    main()
