from fastapi import APIRouter
from sqlalchemy.orm import Session
import schemas
from database import get_db
from fastapi import Depends, HTTPException
import crud
from mqtt import MQTTClient
import utils
import models

"""
This file contains definitions for all the REST API endpoints of the server.
"""

router = APIRouter()
mqtt_client = MQTTClient()
mqtt_client.start()

# Car
@router.get("/cars/{car_id}", response_model=schemas.Car)
def get_car(car_id: str, db: Session = Depends(get_db)):
    db_car = crud.get_car(db, car_id)
    if db_car is None:
        raise HTTPException(status_code=404, detail="Car not found")
    return db_car


@router.post("/cars/", response_model=schemas.Car)
def create_car(car: schemas.CarCreate, db: Session = Depends(get_db)):
    db_car = crud.get_car(db, car_id=car.id)
    if db_car is not None:
        raise HTTPException(status_code=400, detail="Car already exists")
    return crud.create_car(db, car)


# Charger
@router.get("/chargers/{charger_id}", response_model=schemas.Charger)
def get_charger(charger_id: int, db: Session = Depends(get_db)):
    db_charger = crud.get_charger(db, charger_id)
    if db_charger is None:
        raise HTTPException(status_code=404, detail="Charger not found")
    return db_charger


@router.post("/chargers/", response_model=schemas.Charger)
def create_charger(charger: schemas.ChargerCreate, db: Session = Depends(get_db)):
    db_station = crud.get_charging_station(db, charger.station_id)
    if db_station is None:
        raise HTTPException(status_code=400, detail="Station of station_id does not exist")
    
    return crud.create_charger(db, charger)


@router.post("/chargers/{charger_id}/activate/", status_code=200)
def activate_charger(activate_charger: schemas.ActivateCharger, charger_id: int, db: Session = Depends(get_db)):
    '''
    This method will try to activate a given charger for a car.
    For non-reservable chargers, the charger must be available to start a charging session.
    For reservable chargers, the car must also have an reservation for the current 30-minute time slot.
    '''
    # Check if charger is valid
    db_charger = crud.get_charger(db, charger_id)
    if db_charger is None:
        raise HTTPException(status_code=404, detail="Charger not found")
    
    # Check of car is valid
    db_car = crud.get_car(db, car_id=activate_charger.car_id)
    if db_car is None:
        raise HTTPException(status_code=400, detail="Car not found")
    
    if not db_charger.is_available:
        raise HTTPException(status_code=400, detail="Charger currently is unavailable")
    
    if activate_charger.target_percentage > 100 or activate_charger.target_percentage <= 0:
        raise HTTPException(status_code=400, detail="Target percentage is not between 0 and 100.")
    
    max_charging_time = 30 * 60 # 30 minutes in seconds

    if db_charger.is_reservable:
        can_charge = False
        reservation_end_time = None
        if activate_charger.date_now is None:
            for r in db_car.reservations:
                if r.charger_id == charger_id and utils.is_now_in_range(r.start_time, r.end_time):
                    can_charge = True
                    reservation_end_time = r.end_time
                    break
        else:
            for r in db_car.reservations:
                if r.charger_id == charger_id and utils.is_datetime_in_range(activate_charger.date_now, r.start_time, r.end_time):
                    can_charge = True
                    reservation_end_time = r.end_time
                    break

        if can_charge:
            max_charging_time = min(utils.get_seconds_until(reservation_end_time), 30 * 60)
        else:
            raise HTTPException(status_code=400, detail="The car has no reservation for the given charger at this time.")

    # Charger is set to unavailable because the charging will start
    crud.update_charger(db, charger_id, schemas.ChargerUpdate(is_available=False, is_reservable=None))

    # Notify the charger to allow car to start charging
    mqtt_client.send_start_charging_to_charger(charger_id, activate_charger.car_id, activate_charger.target_percentage, max_charging_time)

    return schemas.ActivateChargerReturn(max_charging_time=max_charging_time)


@router.post("/chargers/{charger_id}/deactivate/", status_code=200)
def activate_charger(charger_id: int, db: Session = Depends(get_db)):
    ''' This method will make a charger available again, after charging is finished.'''
    # Check if charger is valid
    db_charger = crud.get_charger(db, charger_id)
    if db_charger is None:
        raise HTTPException(status_code=404, detail="Charger not found")

    if db_charger.is_available:
        raise HTTPException(status_code=404, detail="Charger is currently available")
    
    crud.update_charger(db, charger_id, schemas.ChargerUpdate(is_available=True, is_reservable=None))


# Charging Station
@router.get("/stations/{station_id}", response_model=schemas.ChargingStation)
def get_station(station_id: int, db: Session = Depends(get_db)):
    db_station = crud.get_charging_station(db, station_id)
    if db_station is None:
        raise HTTPException(status_code=404, detail="Charging station not found")
    return db_station


@router.post("/stations/", response_model=schemas.ChargingStation)
def create_station(db: Session = Depends(get_db)):
    return crud.create_charging_station(db)


# Reservation
@router.get("/reservations/{reservation_id}", response_model=schemas.Reservation)
def get_reservation(reservation_id: int, db: Session = Depends(get_db)):
    db_reservation = crud.get_reservation(db, reservation_id)
    if db_reservation is None:
        raise HTTPException(status_code=404, detail="Reservation not found")
    
    return db_reservation


@router.post("/reservations/", response_model=schemas.Reservation)
def create_reservation(reservation: schemas.ReservationCreate, db: Session = Depends(get_db)):
    '''
    This method will make a reservation for a car to a charger.
    To make a reservation, the following must be satisfied:
        * The charger must be reservable
        * The charging time-slot must be in the future
        * The charging time-slot must start either HH:00 or HH:30, and end exactly 30 minutes after
        * The charger cannot already be booked for the time-slot
    '''
    db_car = crud.get_car(db, car_id=reservation.car_id)
    if db_car is None:
        raise HTTPException(status_code=400, detail="Car of car_id does not exist")
    
    db_charger: models.Charger = crud.get_charger(db, reservation.charger_id)
    if db_charger is None:
        raise HTTPException(status_code=404, detail="Charger of charger_id does not exist")

    if not db_charger.is_reservable:
        raise HTTPException(status_code=404, detail="Charger of charger_id is not reservable")
    
    if utils.is_date_aware(reservation.start_time) or utils.is_date_aware(reservation.end_time):
        # Format of date should be: YYYY-MM-DDTHH:MM (ISO)
        raise HTTPException(
            status_code=400, 
            detail="One of the datetimes are aware, e.g. specified with a timezone. The dates should be naive."
            )
    
    if utils.is_date_passed(reservation.start_time) or utils.is_date_passed(reservation.end_time):
        raise HTTPException(status_code=400, detail="One of the datetimes has already passed.")
    
    
    if not (utils.is_valid_time(reservation.start_time) and utils.is_valid_time(reservation.end_time)):
        raise HTTPException(status_code=400, detail="The start time or end time is not HH:30 or HH:00") 

    if not utils.is_30_minutes(reservation.start_time, reservation.end_time):
        raise HTTPException(status_code=400, detail="Time slot is not exactly 30 minutes long.")
    
    
    # check if charger is already booked
    for r in db_charger.reservations:
        if r.start_time == reservation.start_time and r.end_time == reservation.end_time:
            raise HTTPException(status_code=400, detail="Charger is already booked for the specified timeslot.")

    return crud.create_reservation(db, reservation)


@router.get("/hello", status_code=200)
def hello():
    return "hello"