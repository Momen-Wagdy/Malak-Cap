from flask import Flask, request, jsonify
import mysql.connector
import flet as ft
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

# Define Flet app function to display and update readings
def flet_app(page: ft.Page):
    page.title = "Real-time Sensor Readings"
    
    # Labels to display sensor values
    temperature_text = ft.Text(value="Temperature: N/A °C", size=16)
    humidity_text = ft.Text(value="Humidity: N/A %", size=16)
    gas_text = ft.Text(value="Gas Value: N/A", size=16)
    flame_text = ft.Text(value="Flame Value: N/A", size=16)
    
    # Add the labels to the page
    page.add(
        temperature_text,
        humidity_text,
        gas_text,
        flame_text
    )

    # Function to update the Flet UI with new sensor values
    def update_readings(temperature, humidity, gas, flame):
        temperature_text.value = f"Temperature: {temperature:.2f} °C"
        humidity_text.value = f"Humidity: {humidity:.2f} %"
        gas_text.value = f"Gas Value: {gas}"
        flame_text.value = f"Flame Value: {flame}"
        page.update()
    
    # Flask route to receive and update data
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
            
            # Update Flet UI with new sensor values
            update_readings(temperature, humidity, gas_value, flame_value)
            
            return jsonify({"status": "success"}), 200
        else:
            return jsonify({"status": "no data"}), 400

    # Insert data into MySQL database
    def insert_data(temperature, humidity, gas_value, flame_value):
        cursor = db.cursor()
        cursor.execute("INSERT INTO readings (temperature, humidity, gas_value, flame_value) VALUES (%s, %s, %s, %s)", 
                       (temperature, humidity, gas_value, flame_value))
        db.commit()

# Start Flask server in a separate thread
def run_server():
    app.run(host='0.0.0.0', port=5000)

# Real-time visualization function for historical data
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

# Start Flet app, Flask server, and visualization in separate threads
if __name__ == "__main__":
    Thread(target=run_server).start()
    Thread(target=visualize_data).start()
    ft.app(target=flet_app)
