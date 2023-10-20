# UGC Service (Sprint 9)

**[Link to the project to be reviewed](https://github.com/alena-kono/ugc-service-2)**

## Analytical db research
Find more information about the experiment [here](backend/research/clickhouse_vs_vertica/clickhouse_vs_vertica.ipynb)
Find additional 3rd party comparison information [here](backend/research/clickhouse_vs_vertica/Performance-comparison-of-SQL-based-Columnar-Database-Systems-.pdf)

### Clickhouse:
Description: simple table 4 nodes 

Insert test:    
* batch_size = 1000 rows
* batch_numbers = 1000 
* Average insert time: 0.01610767674446106 sec
* Total time: 19.779046058654785 sec

Select test:
* 1000 rows 1000 times
* Average select time: 0.00768980404199101 sec

### Vertica:
description: jbfavre/vertica:latest image

Insert test:
* batch_size = 1000 rows
* batch_numbers = 1000 
* Averae insert time: 0.05144338369369507 sec
* Total time: 56.20524001121521 sec

Select test:
* 1000 rows 1000 times
* Average select time: 0.040490149666002256 sec


## SERVICE PORTS MAPPING FOR THE LOCAL DEVELOPMENT
0. `movies_admin`: port 8000
1. `auth`: port 8001
2. `films_api`: port 8002
3. `ugc_api`: port 8003

## HOW TO

### HOW TO START

0. Create the `.env` files for each application in the `backend/apps` folder
1. Run the `dev` compose (see [here](#start-a-dev-infrastructure))
2. Apply migrations from the `auth` service `backend/apps/auth`
```bash
cd backend/apps/auth
poetry shell
poetry install
alembic upgrade head
```

### START A DEV INFRASTRUCTURE

```
./scripts/dev.sh up
```

### HOW TO RUN THE TESTS

0. Run the test infrastructure
``` bash
./scripts/test.sh up -d
```

1. Go to the service you want to run test for
``` bash
cd backend/apps/auth
```

2. Init the poetry env
``` bash
poetry shell
```

2. Run the main file
``` bash
python -m src.main
```

3. In separate terminal run the `pytest` script
``` bash
pytest .
```
