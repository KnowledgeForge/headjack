from typing import List

from sentence_transformers import SentenceTransformer, util


def semantic_sort(query: str, items: List[str], top_n: int = None) -> List[str]:
    """
    Sorts a list of strings by semantic similarity to a given query, using the Sentence Transformers library and the
    'sentence-transformers/all-MiniLM-L6-v2' pre-trained model.

    Args:
        query (str): The query string to compare against.
        items (list of str): The list of strings to sort by similarity.
        top_n (int, optional): The maximum number of most similar items to return. If not specified, all items will be
            returned.

    Returns:
        list of str: The list of items sorted by similarity to the query, in descending order.

    """
    # Load pre-trained language model
    model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")

    # Encode query and items
    query_embedding = model.encode(query, convert_to_tensor=True)
    item_embeddings = model.encode(items, convert_to_tensor=True)

    # Calculate cosine similarity between query embedding and item embeddings
    cos_scores = util.cos_sim(query_embedding, item_embeddings)[0]

    # Sort items by similarity
    sorted_pairs = sorted(zip(cos_scores, items), reverse=True)
    if top_n:
        sorted_pairs = sorted_pairs[:top_n]
    sorted_items = [item for _, item in sorted_pairs]

    return sorted_items
