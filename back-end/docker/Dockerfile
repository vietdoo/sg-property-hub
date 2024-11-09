FROM python:3-slim-buster

WORKDIR /code

COPY ./requirements.txt /code/requirements.txt
RUN pip install --upgrade pip
RUN pip install -r /code/requirements.txt
COPY ./api /code/app

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "9292"]