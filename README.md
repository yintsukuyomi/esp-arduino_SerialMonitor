# ESP32 Serial Monitor

This project is a **PyQt6**-based application designed to establish a serial connection with an **ESP32** device and display the incoming data in real-time. The user can select the port, configure the baud rate, read data from the serial port, save the output, and manage the connection status.

---

## 🚀 Features

- **Port Selection**: The application automatically lists all available serial ports and allows the user to select one.
- **Baud Rate Selection**: Choose from various baud rates for the serial connection.
- **Data Reading**: Continuously reads data from the selected serial port and displays it.
- **Output Saving**: Allows saving the incoming data to a text file.
- **Auto-Scroll**: The output area can automatically scroll as new data comes in.
- **Disconnect and Exit**: The user can disconnect the serial connection and close the application easily.

---

## 📋 Requirements

- **Python 3.6+**
- **PyQt6**: For the graphical user interface.
- **PySerial**: For serial communication.

---

## 📥 Installation

1. **Clone or download** this repository to your local machine.

   ```bash
   git clone https://github.com/yintsukuyomi/esp-arduino_SerialMonitor.git
   cd esp-arduino_SerialMonitor
