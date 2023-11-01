# UGC API

**[Link to the project to be reviewed](https://github.com/alena-kono/Auth_sprint_1)**

## Getting started

### Building and running for development

#### Features of development build

- No rebuilding and restarting of docker containers needed: directory with app code is mounted and uvicorn is configured to reload on changes.

#### Running locally

Following services will be up and available:

- `api` (uvicorn server) - `8003` port (locally).


**Steps:**

1. Create `.env` file at the project's root directory and fill it with necessary environment variables. You can find an example of `.env` file in `.env.example`.

2. Build and run docker container with dev env:

 ```commandline
./scripts/dev.sh up -d
 ```
