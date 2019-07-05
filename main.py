import logging
import sys

from waitress import serve

from modules.routes import app

if __name__ == "__main__":

    log = logging.getLogger()
    log.setLevel(logging.INFO)
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(logging.INFO)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    log.addHandler(handler)

    serve(app, host='0.0.0.0', port=8080)
