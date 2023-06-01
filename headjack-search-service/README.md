# Headjack Search Service (HSS)

This is an open-source implementation of the [Headjack](https://github.com/KnowledgeForge/headjack)
search service specification.

# Getting Started

Install Headjack Search Service.
```sh
pip install headjack-search-service
```

Start the service.
```sh
headjack-search-service --host 0.0.0.0 --port 16410
```

You can configure the service with the following environment variables.

| Environment Variable         | Description                                     | Example            |
|------------------------------|-------------------------------------------------|--------------------|
| HSS_CHROMA_API_IMPL          | Chroma API implementation (rest or local)       | rest               |
| HSS_CHROMA_DB_IMPL           | Chroma DB implementation                        | duckdb+parquet     |
| HSS_CHROMA_HOST              | Chroma DB Host                                  | 0.0.0.0            |
| HSS_CHROMA_PORT              | Chroma DB Port                                  | 16411              |
| HSS_CHROMA_PERSIST_DIRECTORY | The directory to persist data (local mode only) | /chroma/data/index |

# Docker Compose Demo

To use the docker compose demo, clone this repository.

```sh
git clone https://github.com/KnowledgeForge/headjack-search-service
cd headjack-search-service
```

Pull the chroma repo that's included as a submodule.

```sh
git submodule init
git submodule update
```

Start the docker compose environment.

```sh
docker compose up
```

HSS is now available at [http://localhost:16410](http://localhost:16410).
```sh
curl -X 'GET' \
  'http://localhost:16410/query/?text=How%20were%20our%20Q1%20earnings%20this%20year%3F&collection=knowledge&n=1' \
  -H 'accept: application/json'
```

You can find the swagger docs for the API at [http://localhost:16410/docs](http://localhost:16410/docs).

**note**: If you're seeing poor performance of the chroma container on an M1 Mac, make sure you are not using QEMU emulation.
