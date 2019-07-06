# Python Weekend Challenge      

Code for the Python Weekend Challenge (Prague, last weekend of June 2019)


### Requirements

* Redis instance
* Postgres instance

### Run

Either without Docker:

`pipenv install && pipenv run python main.py`

Or with Docker: 

    docker built -t {name of your image} .
    docker run -p 8080:8080 {name of your image}


# How to use:

Once you have updated the `databases.py` with your credentials (use a `dotenv` file or even better, a tool like Vault) you can use the following routes.

## Routes:

    /search

Main `GET` API endpoint for trip search. Use it like this:

    /search?origin=Prague&destination=Brno&departure=2019-07-10&to_date=2019-07-10&passengers=5

* `origin`: City of origin 
* `destination`: City of destination
* `departure`: Date of departure
* `to_date`: Date of arrival
* `passengers`: Number of passengers

*This will give you as possibilities every single station of the city that you specify*

    /trips

Graphical interface to search on the `search` endpoint

    /combinations

`GET` endpoint to search for trips requiring a connection operated by a different carrier. At the moment it only supports one connection. Supporting more is just a matter of modifying the SQL query to add more layers of joined trip tables.

Use it like this: 

    /combinations?origin=Prag&destination=Berlin&departure=2019-07-11

    