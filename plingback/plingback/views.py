from plingback.namespaces import namespaces
from plingback.sparql import SPARQLGenerator
import json
from pyramid.httpexceptions import HTTPNotFound

def index(request):
    root_url = request.registry.settings.get('root_url', '')
    return {'root_url': root_url}

def feedback_view(request):
    feedback_id = request.matchdict.get('feedback_id')
    feedback_uri = str(namespaces['PB'][feedback_id])

    
    query = SPARQLGenerator('describe_feedback_node', id=feedback_uri).sparql()
    results = request.context.query(query)
    
    nodes = {}
    for triple in results:
        # Skip etag triple 'cos they're dull
        if str(triple[1]) != 'http://schemas.talis.com/2005/dir/schema#etag':
            nd0 = nodes.get(triple[0], {})
            nd0['name'] = triple[0]
            nd0['id'] = triple[0]
            adjs = nd0.get('adjacencies', [])
            adj = {}
            adj['nodeTo'] = triple[2]
            adj['data'] = {'labeltext': str(triple[1]),
                           'labelid': triple[0] + '-' + triple[1] + '/' + triple[2]}
            adjs.append(adj)
            nd0['adjacencies'] = adjs
            
            nodes[triple[0]] = nd0
            
            nd1 = nodes.get(triple[2], {})
            nd1['name'] = triple[2]
            nd1['id'] = triple[2]
            nodes[triple[2]] = nd1
    
    if not nodes:
        raise HTTPNotFound()
        
    
    return {'feedback_id':feedback_id,
            'nodes_json':json.dumps(nodes.values(), sort_keys=True, indent=4)}

    
    
