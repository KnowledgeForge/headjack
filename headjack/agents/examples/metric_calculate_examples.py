from headjack.models.vector_store import VectorStore
from headjack.agents.examples.metric_calculate_examples_dict import metric_calculate_examples

vector_store = VectorStore('metric_calculate_examples')
vector_store.add(list(metric_calculate_examples['queries'].keys()), [{'index': idx} for idx in metric_calculate_examples['queries'].values()], list(metric_calculate_examples['queries'].keys()))

def get_metric_calculate_examples(query: str, n: int = 1)->str:
    selected_queries = []
    selected_queries_indices = set()
    ret = []
    example_queries = vector_store.query(query, n=n*5)['documents'][0]
    for ex_query in example_queries:
        if len(selected_queries)==n:
            break
        index = metric_calculate_examples['queries'][ex_query]
        if index not in selected_queries_indices:
            selected_queries.append(ex_query)
            selected_queries_indices.add(index)
        full_example="User: "+ex_query+"\n"+metric_calculate_examples['examples'][index]
        ret.append(full_example)
    ret = "\n\n".join(ret)
    import pdb; pdb.set_trace()
    return ret