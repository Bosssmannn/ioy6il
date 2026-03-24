from pyModbusTCP.client import ModbusClient
import time

# --- Konfiguration ---
MODBUS_HOST = "192.168.8.134"
MODBUS_PORT = 502
UNIT_ID = 1  # Standard Unit ID, ggf. anpassen

# --- Modbus Client erstellen ---
client = ModbusClient(host=MODBUS_HOST, port=MODBUS_PORT, unit_id=UNIT_ID, auto_open=True)


def read_sensor_data():
    """
    Liest die Input Register 0-2 vom Modbus Gateway.
    Register 0: Temperatur in Celsius (x10)
    Register 1: Temperatur in Fahrenheit (x10)
    Register 2: Relative Luftfeuchtigkeit in % (x10)
    """
    regs = client.read_input_registers(0, 3)  # Ab Register 0, 3 Register lesen

    if regs is None:
        print("FEHLER: Konnte Input Register nicht lesen. Verbindung prüfen!")
        return None

    # Werte durch 10 teilen (Faktor 10 laut Aufgabenstellung)
    temp_celsius = regs[0] / 10.0
    temp_fahrenheit = regs[1] / 10.0
    humidity = regs[2] / 10.0

    return {
        "temperature_celsius": temp_celsius,
        "temperature_fahrenheit": temp_fahrenheit,
        "humidity_percent": humidity
    }


def write_holding_register(address, value):
    """
    Schreibt einen Wert in ein Holding Register.
    """
    success = client.write_single_register(address, value)
    if success:
        print(f"Holding Register {address} erfolgreich auf {value} gesetzt.")
    else:
        print(f"FEHLER: Konnte Holding Register {address} nicht beschreiben.")
    return success


def read_holding_registers(address, count=1):
    """
    Liest Holding Register ab einer bestimmten Adresse.
    """
    regs = client.read_holding_registers(address, count)
    if regs is None:
        print(f"FEHLER: Konnte Holding Register ab {address} nicht lesen.")
    return regs


# Hauptprogramm
if __name__ == "__main__":
    print("=" * 50)
    print("Modbus TCP Client - IOY6 Übung 1")
    print(f"Verbinde zu {MODBUS_HOST}:{MODBUS_PORT}")
    print("=" * 50)

    print("\n--- Sensordaten auslesen (5 Messungen, alle 2 Sekunden) ---")
    for i in range(5):
        data = read_sensor_data()
        if data:
            print(f"Messung {i+1}:")
            print(f"  Temperatur:      {data['temperature_celsius']:.1f} °C / {data['temperature_fahrenheit']:.1f} °F")
            print(f"  Luftfeuchtigkeit: {data['humidity_percent']:.1f} %")
        time.sleep(2)

    print("\n--- Holding Register Test ---")

    test_value = 12345
    print(f"\nSchreibe Wert {test_value} in Holding Register 0...")
    write_holding_register(0, test_value)

    print("Lese Holding Register 0 aus...")
    result = read_holding_registers(0, 1)
    if result:
        print(f"Gelesener Wert: {result[0]}")
        if result[0] == test_value:
            print("Erfolg! Geschriebener und gelesener Wert stimmen überein.")
        else:
            print("ACHTUNG: Werte stimmen nicht überein!")

    client.close()
    print("\nVerbindung geschlossen.")
