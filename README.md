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

## UGC db research

### General description
The MongoDB and ClickHouse databases were configured to run as a cluster with two shards, and each shard had one replica.

An Example of test data structure.
```python
{
 'user_id': '710b7656-2f5e-446e-aade-c04d7bf3c4ec',
 'film_id': '2738bd76-57c8-4f27-bcc4-68260c4a26c4',
 'comment': 'Tempor amet ut lorem eiusmod do amet adipiscing do do labore magna aliqua sit ipsum elit adipiscing lorem magna dolore dolor aliqua tempor incididunt amet aliqua aliqua adipiscing magna eiusmod sed labore dolor ut ut et do incididunt magna labore sed consectetur amet eiusmod tempor amet adipiscing e',
 'timestamp': datetime.datetime(2023, 10, 21, 13, 52, 48, 679723)
}
```

Find more information about the experiment [here](backend/research/mongo_vs_all/mongo_test.ipynb)


### ClickHouse
#### Insert batch test:
* Batch size = 1000.  10000 batches had been inserted
* Insertion took 233.7237 seconds
* average insertion time: 0.0234 seconds

#### Read batch test
* Batch size = 1000.
* Reads Number = 1000 times
* Average select time: 0.012428301582986023 sec

#### Aggregation test
* query: `SELECT user_id, COUNT(*) as count FROM collection.test_collection GROUP BY user_id ORDER BY count DESC LIMIT 10` 
* Reads Number = 10 times 
* Average select time: 0.17657093749730848 sec

### MongoDB
#### Insert batch test:
* Batch size = 1000.  10000 batches had been inserted
* Insertion took 181.6199 seconds
* average insertion time: 0.0182 seconds

#### Read batch test
* Batch size = 1000.
* Reads Number = 1000 times
* Average select time: 0.005184496374975424 sec

#### Aggregation test
* query: [{"$group": {"_id": "$user_id", "count": {"$sum": 1}}}, {"$sort": {"count": -1}}, {"$limit": 10}]
* Reads Number = 10 times
* Average aggregate time: 3.495923020900227 sec

### Mongo vs Postgres 
Mongo and Postgres were run as a single node 
the data structure is the same as in the tests above 

### Postgres
#### Insert batch test:
* 100_000 inserted rows
* Insertion took 30.5753 seconds
* average insertion time: 0.0003 seconds

#### Read batch test
* Reads Number = 1000 times 
* Average select time: 0.011274614583002404 sec

### Update test
* Update Number = 1000 times 
* Average update time: 0.0204745907089673 sec

### Mongo
#### Insert batch test:
* 100_000 docs inserted
* Insertion took 37.5226 seconds
* average insertion time: 0.0004 seconds

#### Read batch test
* Reads Number = 100_000 times 
* Average select time: 0.00039721483082976193 sec

#### Update test
* Update Number = 10_000 times 
* Average update time: 0.0003978825124911964 sec

## SERVICE PORTS MAPPING FOR THE LOCAL DEVELOPMENT
0. `movies_admin`: port 8000
1. `auth`: port 8001
2. `films_api`: port 8002
3. `ugc_api`: port 8003

## HOW TO

### How to setup the mongo cluster
1. start dev compose

    `./scripts/dev.sh up -d`
2. setup the cfg mongo server

    `docker exec -it mongocfg1 bash -c 'echo "rs.initiate({_id: \"mongorsconf\", configsvr: true, members: [{_id: 0, host: \"mongocfg1\"}]})" | mongosh'`
3. setup the mongo shard

    `docker exec -it mongors1n1 bash -c 'echo "rs.initiate({_id: \"mongors\", members: [{_id: 0, host: \"mongors\"}]})" | mongosh'`
4. add the shard to the cluster

    `docker exec -it mongos1 bash -c 'echo "sh.addShard(\"mongors/mongors\")" | mongosh'`


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

## Access logs at Kibana
0. Go to [Kibana](http://localhost:5601/app/kibana#/discover?_g=())
1. Create data view by setting up index pattern.
2. Logs will be uploaded automatically.
