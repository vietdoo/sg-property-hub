FROM apache/airflow:2.7.1-python3.11

USER root
RUN apt-get update && \
    apt-get install -y gcc python3-dev openjdk-11-jdk && \
    apt-get clean

ENV JAVA_HOME /usr/lib/jvm/java-11-openjdk-amd64

USER airflow

COPY ./requirements.txt /requirements.txt
RUN pip install -r /requirements.txt
# RUN pip install apache-airflow apache-airflow-providers-apache-spark pyspark pymongo
