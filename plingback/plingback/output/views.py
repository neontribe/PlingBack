from pyramid.view import view_config
from pyramid.response import Response

from plingback.sparql import SPARQLGenerator
from plingback.output.formatter import ResultFormatter


def handler(request):
    s_gen = SPARQLGenerator(
                scope=request.matchdict.get('scope', None),
                id=request.matchdict.get('id', None),
                attribute=request.matchdict.get('attribute', None),
                activity_dates=(request.params.get('from', None), request.params.get('to', None)),
                submission_dates=(request.params.get('submitted_after', None), request.params.get('submitted_before', None)),
                offset=request.params.get('offset', None),
                limit=request.params.get('limit', None))

    sparql = s_gen.sparql()
    
    results = request.root.query_store(sparql)


    return ResultFormatter(results, s_gen).format()

