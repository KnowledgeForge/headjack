<p align="center">
  <img src="https://raw.githubusercontent.com/KnowledgeForge/headjack/main/docs/assets/images/headjack-logo-small.png" alt="Headjack logo"></a>
</p>
<p align="center">
    <b>Headjack</b>
</p>

<p align="center">
  <a href="https://github.com/KnowledgeForge/headjack/actions/workflows/python-checks.yml" target="_blank">
    <img src="https://github.com/KnowledgeForge/headjack/actions/workflows/python-checks.yml/badge.svg?branch=main" alt="Tests">
  </a>
</p>

## Install Using Pip

```sh
pip install headjack
```

## Start the Headjack Server

```
headjack
```

# Docker Compose

The included docker compose setup launches headjack, a demo implementation of the headjack search service API spec, and a headjack UI
that allows trying out the collection of headjack tools. Headjack uses the OpenAI API in the background and requires an OpenAI account and
[API key](https://platform.openai.com/account/api-keys).

Clone this repo.
```sh
git clone git@github.com:KnowledgeForge/headjack.git
cd headjack
```

Create a local secrets.env file in the root containing your API key.

*secrets.env*
```
OPENAI_API_KEY=<Your API key here>
```

Start the docker compose environment.
```sh
docker compose up
```

Headjack UI: [http://localhost:4000](http://localhost:4000)
Headjack Server Swagger Docs: [http://localhost:8679/docs](http://localhost:8679/docs)
Example Headjack Search Service Swagger Docs: [http://localhost:16410/docs](http://localhost:16410/docs)

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
