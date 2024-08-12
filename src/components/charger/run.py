from charger import ChargerComponent
import sys
import logging


def logger_init(level):
    logger = logging.getLogger("charger_logger")
    logger.setLevel(level)
    ch = logging.StreamHandler()
    ch.setLevel(level)
    formatter = logging.Formatter("[%(asctime)s][%(levelname)s]   %(message)s")
    ch.setFormatter(formatter)
    logger.addHandler(ch)

def get_charger_id_arg():
    args = sys.argv
    if len(args) < 2:
        raise ValueError("charger_id is not specified. Run the program with: python run.py <charger_id>")
    
    charger_id = int(args[1])

    return charger_id

def run():
    ''' Starts charger component from args '''
    logger_init(logging.DEBUG)

    charger_id = get_charger_id_arg()
    ChargerComponent(charger_id)

def run_from_python(charger_id):
    ChargerComponent(charger_id)


if __name__ == "__main__":
    run()
