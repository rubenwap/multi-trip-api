# Python Weekend Challenge      

Code for the Python Weekend Challenge (Prague, last weekend of June 2019)

## TODO:

* Move the functions away from `main.py` into their respective module files (placeholders already created)

### Requirements

* Redis instance
* Postgres instance

### Run

Either without Docker:

`pipenv install && pipenv run python main.py`

Or with Docker: 

    docker built -t {name of your image} .
    docker run -p 8080:8080 {name of your image}

