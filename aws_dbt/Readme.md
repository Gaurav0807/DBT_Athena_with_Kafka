# Dbt with Kafka 

## Overview

This repository contains scripts for setting up a basic Apache Kafka environment using Docker, implementing a producer script, a consumer script, and loading data into dbt athena and performing ETL Operations

## Prerequisites

- Docker installed on your machine.
- Python 3.8 installed.
- Setup Dbt.

## Kafka Setup

1. Run Docker Compose to start Kafka and Zookeeper containers.

    bash
    docker-compose up -d
    

2. Check if Kafka and Zookeeper containers are running.

    bash
    docker ps
    

## Kafka Producer

### Running the Producer

1. Navigate to the producer directory.

    bash
    cd kafka
    

2. Install Python dependencies.

    bash
    pip install -r requirements.txt
    

3. Run the Kafka producer script.

    bash
    python3 producer.py
    

### Producer Configuration

- Edit producer.py to modify the data being produced and Kafka topic details.

## Kafka Consumer

### Running the Consumer

1. Navigate to the consumer directory.

    bash
    cd kafka
    

2. Install Python dependencies.

    bash
    pip install -r requirements.txt
    

3. Run the Kafka consumer script to load data into PostgreSQL.

    bash
    python3 consumer.py
    

### Consumer Configuration

- Edit consumer.py to customize the consumer behavior, Kafka topic, and other settings.
- load data to s3 bucket.

## Setup DBT
Configure dbt profiles.yml 

## Try running the following commands:
- dbt run
- dbt test
- dbt debug
- dbt compile

# Create virtual environment
- Python -m venv venv(window/Macos)
# Then
To install dbt in your local and configure it with aws athena.
- pip install dbt-core
- pip install dbt-core==1.7.10
- pip install dbt-athena-community==1.7.2

# Create aws configure profile 
- https://docs.aws.amazon.com/cli/latest/userguide/cli-configure-quickstart.html

# Intialisation for dbt project
- dbt init demo_dbt

# dbt command

- dbt clean : this will remove the /dbt_modules and /target
- dbt run --models +modelname - will run modelname and all parents
- dbt run --models modelname+ - will run modelname and all children
- dbt run --models +modelname+ - will run modelname, and all parents and children
- dbt run --exclude modelname - will run all models except modelname

# https://docs.getdbt.com/docs/introduction


