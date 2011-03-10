from plingback.namespaces import namespaces
from plingback.sparql import SPARQLGenerator

def index(request):
    root_url = request.registry.settings.get('root_url', '')
    return {'root_url': root_url}

def feedback_view(request):
    feedback_id = request.matchdict.get('feedback_id')
    feedback_uri = str(namespaces['PB'][feedback_id])
    import pdb
    pdb.set_trace()
    
    query = SPARQLGenerator('describe_feedback_node', id=feedback_uri).sparql()
    results = request.context.query(query)
    
    return {'feedback_id':feedback_id}

    
    
