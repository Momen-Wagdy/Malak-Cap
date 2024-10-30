from flask import Flask, request, jsonify
import mysql.connector
import tkinter as tk
from threading import Thread
import matplotlib.pyplot as plt
import datetime

app = Flask(__name__)

# MySQL Database Connection
db = mysql.connector.connect(
    host="localhost",
    user="your_mysql_username",
    password="your_mysql_password",
    database="SensorData"
)

# GUI class to display sensor readings
class SensorGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Sensor Readings")
        
        # Labels for temperature, humidity, gas, and flame sensor readings
        self.temperature_label = tk.Label(root, text="Temperature: ", font=("Arial", 14))
        self.temperature_label.grid(row=0, column=0, padx=10, pady=10)
        
        self.humidity_label = tk.Label(root, text="Humidity: ", font=("Arial", 14))
        self.humidity_label.grid(row=1, column=0, padx=10, pady=10)
        
        self.gas_label = tk.Label(root, text="Gas Value: ", font=("Arial", 14))
        self.gas_label.grid(row=2, column=0, padx=10, pady=10)
        
        self.flame_label = tk.Label(root, text="Flame Value: ", font=("Arial", 14))
        self.flame_label.grid(row=3, column=0, padx=10, pady=10)

        # String variables to store sensor values
        self.temperature_var = tk.StringVar()
        self.humidity_var = tk.StringVar()
        self.gas_var = tk.StringVar()
        self.flame_var = tk.StringVar()

        # Value labels
        self.temperature_value = tk.Label(root, textvariable=self.temperature_var, font=("Arial", 14))
        self.temperature_value.grid(row=0, column=1, padx=10, pady=10)
        
        self.humidity_value = tk.Label(root, textvariable=self.humidity_var, font=("Arial", 14))
        self.humidity_value.grid(row=1, column=1, padx=10, pady=10)
        
        self.gas_value = tk.Label(root, textvariable=self.gas_var, font=("Arial", 14))
        self.gas_value.grid(row=2, column=1, padx=10, pady=10)
        
        self.flame_value = tk.Label(root, textvariable=self.flame_var, font=("Arial", 14))
        self.flame_value.grid(row=3, column=1, padx=10, pady=10)

    # Update sensor readings in GUI
    def update_readings(self, temperature, humidity, gas, flame):
        self.temperature_var.set(f"{temperature:.2f} °C")
        self.humidity_var.set(f"{humidity:.2f} %")
        self.gas_var.set(str(gas))
        self.flame_var.set(str(flame))

# Create the GUI instance
root = tk.Tk()
sensor_gui = SensorGUI(root)

# Insert data into MySQL database
def insert_data(temperature, humidity, gas_value, flame_value):
    cursor = db.cursor()
    cursor.execute("INSERT INTO readings (temperature, humidity, gas_value, flame_value) VALUES (%s, %s, %s, %s)", 
                   (temperature, humidity, gas_value, flame_value))
    db.commit()

# Route to receive data from ESP32
@app.route('/data', methods=['POST'])
def receive_data():
    data = request.get_json()
    if data:
        temperature = data['temperature']
        humidity = data['humidity']
        gas_value = data['gas_value']
        flame_value = data['flame_value']
        
        # Insert data into MySQL
        insert_data(temperature, humidity, gas_value, flame_value)
        
        # Update GUI with new sensor values
        sensor_gui.update_readings(temperature, humidity, gas_value, flame_value)
        
        return jsonify({"status": "success"}), 200
    else:
        return jsonify({"status": "no data"}), 400

# Real-time visualization function
def visualize_data():
    plt.ion()
    fig, ax = plt.subplots()
    
    while True:
        cursor = db.cursor()
        cursor.execute("SELECT timestamp, temperature, humidity, gas_value, flame_value FROM readings ORDER BY id DESC LIMIT 100")
        rows = cursor.fetchall()

        if rows:
            timestamps, temperatures, humidities, gas_values, flame_values = zip(*rows)
            ax.clear()
            ax.plot(timestamps, temperatures, label="Temperature (°C)", color="red")
            ax.plot(timestamps, humidities, label="Humidity (%)", color="blue")
            ax.plot(timestamps, gas_values, label="Gas Value", color="green")
            ax.plot(timestamps, flame_values, label="Flame Value", color="orange")

            plt.xlabel("Timestamp")
            plt.ylabel("Sensor Readings")
            plt.legend(loc="upper right")
            plt.pause(2)

# Start Flask server in a separate thread
def run_server():
    app.run(host='0.0.0.0', port=5000)

# Start the server and visualization in separate threads
Thread(target=run_server).start()
Thread(target=visualize_data).start()

# Run the Tkinter GUI mainloop
root.mainloop()
