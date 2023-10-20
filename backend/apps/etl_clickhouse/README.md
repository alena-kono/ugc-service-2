# ETL from Kafka to Clickhouse

## Getting started

### Building and running for development

**Steps:**

0. Create `.env` file at the project's root directory and fill it with necessary environment variables.
You can find an example of `.env` file in `.env.example`.

1. Execute `clickhouse.ddl` to create `clickhouse` database and tables.

2. Build and run docker container with `dev` env:

     ```commandline
    ./scripts/dev.sh up -d
     ```

3. Activate virtual environment:

     ```commandline
    poetry shell
     ```

4. Run `etl_clickhouse` service locally:

    ```commandline
    python -m src.main
    ```

### Profiling

In order to profile ETL please use PID from pidfile path.
