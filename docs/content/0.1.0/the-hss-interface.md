---
categories: ["docs"]
weight: 20
title: The HSS Interface
tags: ["how-to", "integrations"]
series: ["getting-started"]
series_weight: 3
lightgallery: true
---

Headjack is designed to enable plugging in any search to be used for retrieval. It accomplishes this by prescribing
a headjack search service (HSS) API specification. You can wrap any search solution, even a highly customized one, with
a thin API layer that implements a few endpoints defined in the HSS specification. Headjack can then be configured to use the wrapper
API to retrieve information while creating prompts to send to the language model.

# How Semantic Search Implementations Are Used

When a semantic question or command is sent to Headjack, it performs a semantic search to find the most closely related information.

- Metrics
- Passages from knowledge documents
- People
- Message threads
- and more...

Once headjack has filtered the potentially vast amounts of embedded data down to those pieces of information that are most
relevant to the question or command, it utilizes that information through an assortment of tools. These tools then leverage
available large language models such as any OpenAI or huggingface models to determine specific scoped actions. These scoped
actions are what power Headjacks core features.

- Summarize business terms and concepts
- Find relevant conversations
- Find metrics and even calculate them across various dimensions (see [Integration With DataJunction](../integration-with-datajunction))
- Generate plotly configurations to visualize data
- and more...

Semantic search is a critical component for quickly narrowing large swaths of available information to allow the language model to only
operate on a small subset of closely related and contextually relevant information.
