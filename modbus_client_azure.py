from pyModbusTCP.client import ModbusClient
from azure.iot.device import IoTHubDeviceClient, Message
import json
import time

# =============================================
# Konfiguration
# =============================================
MODBUS_HOST = "192.168.8.134"
MODBUS_PORT = 502
UNIT_ID = 1

# WICHTIG: Hier deinen eigenen Connection String eintragen!
# Den bekommst du aus dem Azure Portal (siehe Anleitung unten)
AZURE_CONNECTION_STRING = "HostName=hub-ioy6-rusche-milczek.azure-devices.net;DeviceId=modbus-gateway;SharedAccessKey=+xl8jEZmzHdyBZliKr5f2evPNhhz7kM57zSdEvVvcrU="

# Wie oft Daten gesendet werden sollen (in Sekunden)
SEND_INTERVAL = 2


# =============================================
# Modbus Client Setup
# =============================================
modbus_client = ModbusClient(host=MODBUS_HOST, port=MODBUS_PORT, unit_id=UNIT_ID, auto_open=True)


def read_sensor_data():
    """Liest Sensordaten aus den Input Registern 0-2."""
    regs = modbus_client.read_input_registers(0, 3)
    if regs is None:
        print("FEHLER: Konnte Sensordaten nicht lesen.")
        return None

    return {
        "temperature_celsius": regs[0] / 10.0,
        "temperature_fahrenheit": regs[1] / 10.0,
        "humidity_percent": regs[2] / 10.0
    }


def create_iot_client():
    try:
        client = IoTHubDeviceClient.create_from_connection_string(AZURE_CONNECTION_STRING)
        client.connect()
        print("Erfolgreich mit Azure IoT Hub verbunden!")
        return client
    except Exception as e:
        print(f"FEHLER bei Azure IoT Hub Verbindung: {e}")
        return None


def send_to_azure(iot_client, sensor_data):
    """Sendet Sensordaten als JSON-Nachricht an Azure IoT Hub."""
    message_body = json.dumps({
        "temperature_celsius": sensor_data["temperature_celsius"],
        "temperature_fahrenheit": sensor_data["temperature_fahrenheit"],
        "humidity_percent": sensor_data["humidity_percent"],
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    })

    message = Message(message_body)
    message.content_type = "application/json"
    message.content_encoding = "utf-8"

    message.custom_properties["source"] = "modbus_gateway"
    message.custom_properties["sensor_type"] = "temperature_humidity"

    try:
        iot_client.send_message(message)
        print(f"  -> An Azure IoT Hub gesendet: {message_body}")
    except Exception as e:
        print(f"  -> FEHLER beim Senden an Azure: {e}")


if __name__ == "__main__":
    print("=" * 60)
    print("Modbus TCP Client + Azure IoT Hub - IOY6 Übung 1")
    print(f"Modbus Gateway: {MODBUS_HOST}:{MODBUS_PORT}")
    print(f"Sende-Intervall: {SEND_INTERVAL} Sekunden")
    print("=" * 60)

    iot_client = create_iot_client()
    if iot_client is None:
        print("Konnte keine Verbindung zu Azure IoT Hub herstellen. Beende.")
        exit(1)

    print("\nStarte Datenübertragung (Strg+C zum Beenden)...\n")
    message_count = 0

    try:
        while True:
            data = read_sensor_data()
            if data:
                message_count += 1
                print(f"Messung #{message_count}:")
                print(f"  Temperatur:       {data['temperature_celsius']:.1f} °C / {data['temperature_fahrenheit']:.1f} °F")
                print(f"  Luftfeuchtigkeit: {data['humidity_percent']:.1f} %")

                send_to_azure(iot_client, data)
                print()

            time.sleep(SEND_INTERVAL)

    except KeyboardInterrupt:
        print(f"\n\nBeendet. {message_count} Nachrichten gesendet.")

    finally:
        modbus_client.close()
        iot_client.disconnect()
        print("Verbindungen geschlossen.")
