---
categories: ["docs"]
weight: 10
title: Getting Started
authors: ["Headjack Devs"]
tags: ["how-to", "integrations"]
series: ["getting-started"]
series_weight: 10
lightgallery: true
---

The easiest way to try Headjack is to use the docker compose setup that provides a demo environment.

Clone the GitHub repo and change into the repo's root directory
```sh
git clone https://github.com/KnowledgeForge/headjack
cd headjack
```

Create a local secrets.env file in the root containing your API key.
*secrets.env*
```sh
OPENAI_API_KEY=<Your API key here>
```

Start the docker compose environment.
```sh
docker compose up
```

# The Demo Environment

The demo environment contains a few containers that represent components of a typical headjack deployment.

### headjack

This container runs the headjack API server. This server runs the main headjack logic that includes the prompt
engineering as well as interfacing with external tools such as a metrics platform or headjack search implementation.

### headjack-search-service

The headjack search service (HSS) specification is an API spec for plugging in a semantic search system to be used for
retrieval. The demo environment contains an example implementation of this specification that's powered by a vector
database. At startup, the demo environment indexes a set of unstructured documents that can be found in the
[examples](https://github.com/KnowledgeForge/headjack/tree/main/headjack-search-service/examples) directory. To read more
about the HSS specification, see [The HSS Interface](../the-hss-interface) page.

### headjack-ui

At its core, headjack is an API with REST and websocket endpoints that can be integrated into other tools and user interfaces.
However, the demo environment comes with a headjack UI for purposes of making it easy to demo and try out headjack.