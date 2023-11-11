import logging
import requests
from os import environ

import azure.functions as func

from hello_world import PLAYTHING_NAME  # TODO add core and include a ping enable setting in core_config.json

def main(mytimer: func.TimerRequest) -> None:
    if mytimer.past_due:
        logging.info('The timer is past due!')
    
    url_base = environ.get("PLAYGROUND_PING_URL_BASE", None)  # e.g. = "https://dlpg-test1.azurewebsites.net"

    if url_base is None:
        logging.warn(f"Environ PLAYGROUND_PING_URL_BASE is not set; abort pinging {PLAYTHING_NAME}.")
    else:
        url = f"{url_base}/{PLAYTHING_NAME}/ping"
        req = requests.get(url)

        logging.info(f"Ping {url} from timerTrigger => HTTP {req.status_code}, Content: {req.text}")
