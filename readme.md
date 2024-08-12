# Introduction
This project is done by Team 11 in the course TTM4115, the spring of 2024.

For context on the repository it's important to have read our System Specification 3 (course delivery).

# Project Structure
## Files
* `src/components` hold all the different components of this project, which includes: app (UI), car, charger, and server. Each of the component has their own directory.

* `src/components/app` has  a single file `run.py` containing all the UI logic.

* `src/components/car` has two files:
  * `car.py` handles the car component. The component mainly consists of the car state machine and a MQTT client for communication with other components.
  * `run.py` handles initializing the car component, similar to a main file.

* `src/components/charger` has 1 directory and 3 files:
  * `audio_files` stores the audio files used for the application.
  * `audio.py` contains functions used for playing audio through speakers.
  * `charger.py` handles the charger component. The component consists of three classes. One for controlling the state machine, a second one for the MQTT client and a third one for a Raspberry SenseHat. The SenseHat logic includes turning lighting modes for each state of the charger, as well as controlling if the charger nozzle is connected to the car or not. This is done through the joystick's middle-button.
  * `run.py` handles initializing the charger component, similar to a main file.

* `src/components/server` has 8 different files:
  * `crud.py` contains methods used for interacting directly with the SQLite database. 
  * `database.py` handles the database instance.
  * `endpoints.py` defines all the REST API endpoints of the server, which also includes input validation for data sent to the server.
  * `models.py` contains the database model definitions, with their relationships. (Object–relational mapping)
  * `mqtt.py` handles MQTT communication for the server.
  * `run.py` handles starting the HTTP server, similar to a main file.
  * `schemas.py` defines the formats of data returned from the server, and received by the server.
  * `utils.py` contains several utility functions, mostly related to date validation.

* `db.sqlite` is the database file used by the server component containing all the database data. The file extension is `.sqlite` since we are using SQLite as the database engine for this project.

## Components
### Car
The car component represents a car in the charging system. When a car receives a start charging signal the component will simulate being charged until receiving a stop charging signal.

### Charger
The charger component represents a charger in the charging system.
* It is simulated on a Raspberry Pi.
* It runs a state machine.
* It uses a button for simulating a nozzle, which decides wether the charger is available or connected to a car.
* It contains a display screen showing the user the current state of the charger.
* The charger is connected to a webserver.
* It attempts to handle errors for certain functionalities, such as server connection issues.

### Server
The server component is a HTTP server handling all the data stored for this application.

* The server provides REST endpoints that allows *users* to save their car ID, make a reservation, and  get an overview of all chargers.

* The server allows reservable *chargers* to verify that a car has a reservation, and updating the status of chargers between available and unavailable. 

* The server allows *charging station managers* to initialize chargers for their station.

_This is not everything the server does, but rather an overview of the most important functionality._




# Running Components
## Setting up Virtual Environment
### MacOS and Linux
Execute the following commands from the root directory:
```bash
python3.12 -m venv env
source env/bin/activate
pip install -r requirements.txt
```
### Windows
Execute the following commands from the root directory:
```bash
python3.12 -m venv env
source .\venv\Scripts\activate
pip install -r requirements.txt
```

### Raspberry Pi: Known issues
1) PyAudio from 'requirements.txt' may not work on all Raspberry Pi boards without modifications. So be sure to comment this line in the file if issues occur.

## Running
First, activate the virtual environment with `source env/bin/activate` (Mac/Linux) within the root directory.

Each component has slightly different ways of being started:

### App
```
python src/components/app/run.py
```

### Car
```
python src/components/car/run.py <car_id>
```
The `car_id` can be any string, but remember the car needs to be registered in the server database for the component to work correctly.
This is done through the App user interface when prompted for a Car ID.

### Charger
NB! This component is supposed to be ran on a Raspberry Pi with SenseHat attached.
```
python src/components/charger/run.py <charger_id>
```
The `charger_id` can be any integer, but remember the charger needs to be registered in the server database for the component to work correctly.

This has to be done manually as it is a part of the charging station setup process, supposed to be performed by the charging station owner. However, by default, the server database will contain 8 chargers:
* The chargers with ID 1, 2, 3, 4 are *non-reservable* chargers.
* The chargers with ID 5, 6, 7, 8 are *reservable* chargers.


### Server
```
python src/components/server/run.py
```
# Raspberry Pi
## Information about the Pi
Hostname: raspberrypi.local

Username: g11

Password: 711

- SSH should be activated and use Password above to authenticate.
- To connect to it, use Mobile hotspot on your phone.
- Currently only Sindre's network "Sid" is available, you find this under available WiFi networks.
- ### The wifi information:
  * WIFI name: Sid
  * password: 1234567890
## Accessing the project:
Write this in the terminal:
```bash
ssh g11@raspberrypi.local
cd /home/g11/Projects/Spec3-Final/
```

# Using SenseHat to light up display
## Currently available lighting modes (state: description):
1) init: gray background
2) available: green background
3) unavailable: orange background
5) battery status: Two digit number shown in white. When reached battery cap: Blink yellow -> ('Batery_cap')% -> Blink yellow -> "Done..." from right to left.
6) error: Red X

## How to use the different SenseHat lighting modes in your code.
1) When charger program starts up, add the following:
```
from charger import ChargerInterface # For using the sensehat in external file.

interface = SH.ChargerInterface(start_state) # By default use start_state = "init"
interface.start()
```
2) Add the state of what to display on SenseHat in your code:
```
interface.state = your_state # Remember to add this everytime you want to change the display to another one on the list above.
```
3) Give SenseHat information about the battery:
```
interface.battery_cap = your_battery_cap
# Considering you are in charging state when this happens:
interface.state = "battery status"
# Foreach time you read battery status from MQTT update the battery status on SenseHat:
interface.battery = updated_battery_status
```
4) If there is an exit or terminate state/function for your program, add the function that terminates SenseHat too:
```
interface.stop()
```
