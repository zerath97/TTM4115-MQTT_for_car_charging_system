from sqlalchemy.orm import Session

import models, schemas

"""
This file contains methods used for interacting directly with the database. 
"""


# Car
def get_car(db: Session, car_id: str):
    return db.query(models.Car).filter(models.Car.id == car_id).first()


def get_all_cars(db: Session):
    return db.query(models.Car).all()

def create_car(db: Session, car: schemas.CarCreate):
    db_car = models.Car(id=car.id)
    db.add(db_car)
    db.commit()
    db.refresh(db_car)
    return db_car


# Charger
def get_charger(db: Session, charger_id : int):
    return db.query(models.Charger).filter(models.Charger.id == charger_id).first()


def get_all_chargers(db: Session):
    return db.query(models.Charger).all()


def create_charger(db: Session, charger: schemas.ChargerCreate):
    db_charger = models.Charger(is_reservable = charger.is_reservable, station_id = charger.station_id)
    db.add(db_charger)
    db.commit()
    db.refresh(db_charger)
    return db_charger

def activate_charger(db: Session, charger_id: int):
    db_charger = db.query(models.Charger).filter(models.Charger.id == charger_id).first()
    if db_charger is not None: # TODO: add error handling
        db_charger.is_available = False
        db.commit()
        db.refresh(db_charger)
        return db_charger

def update_charger(db: Session, charger_id: int, updated_charger: schemas.ChargerUpdate):
    db_charger = db.query(models.Charger).filter(models.Charger.id == charger_id).first()
    if db_charger is not None: # TODO: add error handling
        if updated_charger.is_reservable is not None:
            db_charger.is_reservable = update_charger.is_reservable
        if updated_charger.is_available is not None:
            db_charger.is_available = updated_charger.is_available
        
        db.commit()
        db.refresh(db_charger)
        return db_charger


# Charging Station
def get_charging_station(db: Session, charging_station_id: int):
    return db.query(models.ChargingStation).filter(models.ChargingStation.id == charging_station_id).first()


def get_all_charging_stations(db: Session):
    return db.query(models.ChargingStation).all()


def create_charging_station(db: Session):
    db_charging_station = models.ChargingStation()
    db.add(db_charging_station)
    db.commit()
    db.refresh(db_charging_station)
    return db_charging_station


# Reservation
def get_reservation(db: Session, reservation_id: int):
    return db.query(models.Reservation).filter(models.Reservation.id == reservation_id).first()


def get_all_reservations(db: Session):
    return db.query(models.Reservation).all()


def create_reservation(db: Session, reservation: schemas.ReservationCreate):
    db_reservation = models.Reservation(
        start_time = reservation.start_time, 
        end_time = reservation.end_time, 
        car_id = reservation.car_id,
        charger_id = reservation.charger_id
    )
    db.add(db_reservation)
    db.commit()
    db.refresh(db_reservation)
    return db_reservation
