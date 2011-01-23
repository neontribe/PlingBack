from pyramid.config import Configurator
from plingback.resources import InputRoot, OutputRoot
from rdflib import Namespace

namespaces = {
    "RDF" : Namespace("http://www.w3.org/1999/02/22-rdf-syntax-ns#"),
    "RDFS" : Namespace("http://www.w3.org/TR/rdf-schema/"),
    "PBO" : Namespace("http://plingback.plings.net/ontologies/plingback#"),
    "PB" : Namespace("http://plingback.plings.net/pb/"),
    "REV" : Namespace("http://purl.org/stuff/rev#"),
    "FOAF" : Namespace("http://xmlns.com/foaf/0.1/"),
    "DC" : Namespace("http://purl.org/dc/elements/1.1/"),
    "ACTIVITIES" : Namespace("http://plings.net/a/")
    }

def main(global_config, **settings):
    """ This function returns a Pyramid WSGI application.
    """
    config = Configurator(settings=settings)
    
    # Set up the output api
    config.add_route('pling_attribute', 
                     '/api/plings/{id}/{attribute}', 
                     view='plingback.output.views.handler',
                     view_renderer='json',
                     request_method='GET',
                     factory=OutputRoot)
    config.add_route('scoped_attribute', 
                     '/api/{scope}/{id}/{attribute}', 
                     view='plingback.output.views.handler',
                     view_renderer='json',
                     request_method='GET',
                     factory=OutputRoot)
    
    config.add_route('scoped_plingback_count', 
                     '/api/{scope}', 
                     view='plingback.output.views.handler',
                     view_renderer='json',
                     request_method='GET',
                     factory=OutputRoot)
    config.add_route('narrow_scoped_plingback_count', 
                     '/api/{scope}/{id}', 
                     view='plingback.output.views.handler',
                     view_renderer='json',
                     request_method='GET',
                     factory=OutputRoot)
    config.add_route('pling_plingback_count', 
                     '/api/plings/{id}', 
                     view='plingback.output.views.handler',
                     view_renderer='json',
                     request_method='GET',
                     factory=OutputRoot)
    
    # Route to static resources
    config.add_static_view('static', 'plingback:static')
    
    return config.make_wsgi_app()

