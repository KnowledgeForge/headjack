# Headjack

Headjack is a chat-based semantic layer for metrics platforms.

# Docker Compose

The included docker compose setup launches a headjack, [chroma](https://github.com/chroma-core/chroma), and jupyter lab container.

Pull down the chroma repo which is contained in this repo as a submodule.
```sh
git submodule init
git submodule update
```

Start the docker compose environment.
```sh
docker compose up
```

Headjack: [http://localhost:16400/docs](http://localhost:16400/docs)
Juptyer Lab: [http://localhost:16401](http://localhost:16401)
ChromaDB: [http://localhost:16402/docs](http://localhost:16402/docs)

# Lint, Test, and Check Coverage

This project includes a Makefile for use with [GNU Make](https://www.gnu.org/software/make/).

Run linters.
```
make lint
```

Run tests.
```
make test
```

Run tests with coverage.
```
make coverage
```
