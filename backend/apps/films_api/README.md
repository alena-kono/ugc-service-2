# Movies API (Sprint 5)

**[Link to the project to be reviewed](https://github.com/alena-kono/Async_API_sprint_2)**

## Related services

- [ETL](https://github.com/nikitazigman/yandex_etl)

## Getting started

### Building and running for development

#### Features of development build

- Service uses `elasticsearch` as a database, so `elasticsearch` should be available.
- No rebuilding and restarting of docker containers needed: directory with app code is mounted and uvicorn is configured to reload on changes.
- [`elasticvue`](https://elasticvue.com) service included: debug with elasticsearch web gui.
- `backend` (api) is available at `8000` port, `redis` - `6379` port, `elastic_search_gui` - `8080` port.

#### Running locally

`redis` will be up and available at `6379` port, `elastic` - `9200` port, `elastic_search_gui` - `8080` port.

**Steps:**

1. Create `.env` file at the project's root directory and fill it with necessary environment variables. You can find an examplein `.env.example`.

2. Build and run docker container with test env `root dir`:

 ```bash
./scripts/test.sh up -d
 ```
3. Run `films_api` service (api) locally:

```bash
cd backend/apps/films_api
poetry shell
python src/main.py
 ```

## Running tests

### Functional tests

1. Create `.env` file at the project's root directory and fill it with necessary environment variables. You can find an example of `.env` file in `.env.example`.
2. Run the `Auth` service.
3. Run the `films_api` service
4. Run tests:

 ```bash
 poetry shell
 pytest .
 ```


## Service documentation

OpenAPI 3 documentation:

- Swagger

    ```
    GET /api/openapi
    ```

- ReDoc

    ```
    GET /redoc
    ```

- OpenAPI json

    ```
    GET /api/openapi.json
    ```
