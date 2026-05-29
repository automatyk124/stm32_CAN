import serial
import serial.tools.list_ports
import pandas as pd
import matplotlib.pyplot as plt
import time
from datetime import datetime

# --- KONFIGURACJA ---
# Ustaw swój port COM (np. 'COM3' na Windows, '/dev/ttyUSB0' na Linux)
# Jeśli wpiszesz 'AUTO', program spróbuje znaleźć pierwszy dostępny port
PORT_NAME = 'AUTO' 
BAUD_RATE = 9600
EXCEL_FILE = 'dane_uart.xlsx'
PLOT_FILE = 'wykres_danych.png'

def find_com_port():
    """Automatycznie znajduje pierwszy dostępny port szeregowy."""
    ports = serial.tools.list_ports.comports()
    if not ports:
        raise Exception("Nie znaleziono żadnych portów COM!")
    return ports[0].device

def main():
    # 1. Konfiguracja portu
    if PORT_NAME == 'AUTO':
        port_name = find_com_port()
        print(f"Automatycznie wykryto port: {port_name}")
    else:
        port_name = PORT_NAME

    try:
        ser = serial.Serial(port_name, BAUD_RATE, timeout=1)
        print(f"Połączono z {port_name}... Naciśnij Ctrl+C aby zakończyć.")
        time.sleep(2) # Czekaj na stabilizację połączenia
    except serial.SerialException as e:
        print(f"Błąd połączenia z portem: {e}")
        return

    # Listy do przechowywania danych
    timestamps = []
    values = []
    start_time = time.time()

    try:
        while True:
            if ser.in_waiting > 0:
                # Odczyt linii danych
                line = ser.readline().decode('utf-8').strip()
                
                # Próba konwersji danych na liczbę (float)
                try:
                    if line:
                        value = float(line)
                        current_time = time.time() - start_time
                        
                        values.append(value)
                        timestamps.append(current_time)
                        
                        # Wyświetlanie na konsoli (opcjonalne)
                        print(f"Czas: {current_time:.2f}s | Wartość: {value}")
                except ValueError:
                    print(f"Otrzymano nieprawidłowe dane: {line}")

    except KeyboardInterrupt:
        print("\nZakończono odbieranie danych przez użytkownika.")
    
    finally:
        ser.close()
        print("Port zamknięty.")

    # 2. Zapis do Excela
    if len(values) > 0:
        print("Zapisywanie danych do Excela...")
        df = pd.DataFrame({
            'Czas [s]': timestamps,
            'Wartość': values
        })
        
        # Zapis do pliku .xlsx
        df.to_excel(EXCEL_FILE, index=False, engine='openpyxl')
        print(f"Dane zapisano w pliku: {EXCEL_FILE}")

        # 3. Rysowanie wykresu
        print("Generowanie wykresu...")
        plt.figure(figsize=(10, 6))
        plt.plot(timestamps, values, label='Dane z UART', color='blue', linewidth=1)
        plt.title('Wykres danych z portu szeregowego')
        plt.xlabel('Czas [s]')
        plt.ylabel('Wartość')
        plt.grid(True)
        plt.legend()
        
        # Zapis wykresu do pliku
        plt.savefig(PLOT_FILE)
        print(f"Wykres zapisano w pliku: {PLOT_FILE}")
        
        # Wyświetlenie wykresu (okno się zamknie po kliknięciu X)
        plt.show()
    else:
        print("Brak danych do zapisu i wyświetlenia.")

if __name__ == '__main__':
    main()