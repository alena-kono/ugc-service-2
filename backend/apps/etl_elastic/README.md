## Getting Started
### Building and Running for Development
#### Instructions
Create a .env file in the project's config directory and populate it with the necessary environment variables. An example .env file can be found in configs/env_template.

1. Start the Docker container:

```shell
docker compose -f docker-compose-dev.yaml up -d
```

2. Install the project dependencies:

```shell
poetry install
```
3. Activate the virtual environment:

```shell
poetry shell
```
4. To execute the ETL service on your host machine, use the following command:

```shell
python etl/main.py
```

### Building and Running for Production
#### Instructions
Create a prod.env file in the project's root directory and fill it with the necessary environment variables. You can refer to the provided .env.example file for guidance.

1. Build and launch the Docker container:

```shell
docker compose up -d --build
```
2. If fortune favors you, everything should work seamlessly.
