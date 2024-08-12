from pydantic import BaseModel
from datetime import datetime
from typing import Optional

"""
This file contains the formats of data returned from the server, and received by the server.
The <Entity>Create classes are used when users wants to create a new entity.
The <Entity> classes are used when users are getting an entity from the database.
The <Entity>Update classes are used when users wants to update a entity.
"""


# Reservation
class ReservationBase(BaseModel):
    start_time: datetime
    end_time: datetime
    car_id: str
    charger_id: int

class ReservationCreate(ReservationBase):
    pass

class Reservation(ReservationBase):
    id: int

    class Config:
        orm_mode = True

# Car
class BaseCar(BaseModel):
    id: str

class CarCreate(BaseCar):
    pass

class Car(BaseCar):
    reservations: list[Reservation]

    class Config:
        orm_mode = True



# Charger
class ChargerBase(BaseModel):
    is_reservable: bool
    station_id: int


class ChargerCreate(ChargerBase):
    pass


class ChargerUpdate(BaseModel):
    is_reservable: Optional[bool]
    is_available: Optional[bool]


class Charger(ChargerBase):
    id: int
    reservations: list[Reservation]
    is_available: bool

    class Config:
        orm_mode = True


class ActivateCharger(BaseModel):
    car_id: str
    target_percentage: int
    date_now: Optional[datetime] # field used for debugging, TODO: remove it later.


class ActivateChargerReturn(BaseModel):
    max_charging_time: int # max time to charge in seconds

# Charger Station
class ChargingStation(BaseModel):
    id: int
    chargers: list[Charger]

    class Config:
        orm_mode = True
