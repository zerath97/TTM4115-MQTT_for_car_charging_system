from car import BatteryComponent
import sys
import logging


def logger_init(level):
    logger = logging.getLogger("car_logger")
    logger.setLevel(level)
    ch = logging.StreamHandler()
    ch.setLevel(level)
    formatter = logging.Formatter("[%(asctime)s][%(levelname)s]   %(message)s")
    ch.setFormatter(formatter)
    logger.addHandler(ch)



def get_car_id_arg():
    args = sys.argv
    if len(args) < 2:
        raise ValueError("car_id is not specified. Run the program with: python run.py <car_id>")
    
    car_id = args[1]

    return car_id

def run():
    ''' Starts car battery component from args '''
    logger_init(logging.DEBUG)
    
    car_id = get_car_id_arg()
    BatteryComponent(car_id)

def run_from_python(car_id):
    BatteryComponent(car_id)


if __name__ == "__main__":
    run()
