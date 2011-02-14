from pyramid.view import view_config
from pyramid.response import Response

from plingback.sparql import SPARQLGenerator
from plingback.output.formatter import ResultFormatter


def handler(request):
    # Use the route name as the sparql template name
    # replace in any attribute name if present
    sparql_template = request.matched_route.name
    attribute = request.matchdict.get('attribute', None)
    if attribute:
        sparql_template = sparql_template.replace('attribute', attribute)
    
    s_gen = SPARQLGenerator(
                query_template=sparql_template,
                scope=request.matchdict.get('scope', None),
                id=request.matchdict.get('id', None),
                attribute=attribute,
                activity_dates=(request.params.get('from', None), request.params.get('to', None)),
                submission_dates=(request.params.get('submitted_after', None), request.params.get('submitted_before', None)),
                offset=request.params.get('offset', None),
                limit=request.params.get('limit', None))

    sparql = s_gen.sparql()
    
    results = request.root.query(sparql)
    
    output = ResultFormatter(results, s_gen).format()
    return output


