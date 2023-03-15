# srcs/streamlit_app/utils.py
def check_and_create_index(es, index: str):
    # define data model
    mappings = {
        'mappings': {
            'properties': {
                'author': {'type': 'keyword'},
                'length': {'type': 'keyword'},
                'title': {'type': 'text'},
                'tags': {'type': 'keyword'},
                'content': {'type': 'text'},
            }
        }
    }
    if not es.indices.exists(index):
        es.indices.create(index=index, body=mappings, ignore=400)


def index_search(es, index: str, keywords: str, filters: str,
                 from_i: int, size: int) -> dict:
    """
    Args:
        es: Elasticsearch client instance.
        index: Name of the index we are going to use.
        keywords: Search keywords.
        filters: Tag name to filter medium stories.
        from_i: Start index of the results for pagination.
        size: Number of results returned in each search.
    """
    # search query
    body = {
        'query': {
            'bool': {
                'must': [
                    {
                        'query_string': {
                            'query': keywords,
                            'fields': ['content'],
                            'default_operator': 'AND',
                        }
                    }
                ],
            }
        },
        'highlight': {
            'pre_tags': ['<b>'],
            'post_tags': ['</b>'],
            'fields': {'content': {}}
        },
        'from': from_i,
        'size': size,
        'aggs': {
            'tags': {
                'terms': {'field': 'tags'}
            },
            'match_count': {'value_count': {'field': '_id'}}
        }
    }
    if filters is not None:
        body['query']['bool']['filter'] = {
            'terms': {
                'tags': [filters]
            }
        }

    res = es.search(index=index, body=body)
    # sort popular tags
    sorted_tags = res['aggregations']['tags']['buckets']
    sorted_tags = sorted(
        sorted_tags,
        key=lambda t: t['doc_count'], reverse=True
    )
    res['sorted_tags'] = [t['key'] for t in sorted_tags]
    return res