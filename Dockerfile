FROM benkalukas/py_weekend_base
WORKDIR /app
COPY . /app
RUN pip install pipenv && pipenv install --system
EXPOSE 8080
CMD python main.py

