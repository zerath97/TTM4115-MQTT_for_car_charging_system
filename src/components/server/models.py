from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, DateTime
from sqlalchemy.orm import relationship
from database import Base

"""
This file contains the database model definitions, with their relationships.
(Object–relational mapping)
"""

class Car(Base):
    __tablename__ = "cars"

    id = Column(String, primary_key=True)

    reservations = relationship("Reservation", back_populates="car")

class Charger(Base):
    __tablename__ = "chargers"

    id = Column(Integer, primary_key=True)
    is_reservable = Column(Boolean, default=False)
    is_available = Column(Boolean, default=True)

    station_id = Column(Integer, ForeignKey("stations.id"))

    station = relationship("ChargingStation", back_populates="chargers")
    reservations = relationship("Reservation", back_populates="charger")

class ChargingStation(Base):
    __tablename__ = "stations"

    id = Column(Integer, primary_key=True)

    chargers = relationship("Charger", back_populates="station")


class Reservation(Base):
    __tablename__ = "reservations"

    id = Column(Integer, primary_key=True)
    start_time = Column(DateTime())
    end_time = Column(DateTime())

    car_id = Column(String, ForeignKey("cars.id"))
    charger_id = Column(Integer, ForeignKey("chargers.id"))

    car = relationship("Car", back_populates="reservations")
    charger = relationship("Charger", back_populates="reservations")
