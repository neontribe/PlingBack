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
    
    # Setup the Input API
    # POSTs to the controller create new nodes the posted data will be parsed
    # for subnodes (ratings etc) which will also be created
    config.add_route('create_feedback_node',
                     '/api/plingbacks',
                     view='plingback.input.views.create',
                     view_renderer='json',
                     request_method='POST',
                     factory=InputRoot)
    # PUTs to an id create that node the posted data will be parsed
    # for subnodes (ratings etc) which will also be created
    config.add_route('create_feedback_node_by_id',
                     '/api/plingbacks/{feedback_id}', 
                     view='plingback.input.views.create',
                     view_renderer='json',
                     request_method='PUT',
                     factory=InputRoot)

    # POSTs to a feedback attribute create it
    config.add_route('create_feedback_attribute',
                     '/api/plingbacks/{feedback_id}/{attribute}', 
                     view='plingback.input.views.attribute_handler',
                     view_renderer='json',
                     request_method='POST',
                     factory=InputRoot)
                          
    # PUTs to a feedback attribute overwrite
    config.add_route('update_feedback_attribute',
                     '/api/plingbacks/{feedback_id}/{attribute}', 
                     view='plingback.input.views.attribute_handler',
                     view_renderer='json',
                     request_method='PUT',
                     factory=InputRoot)
    
    
    
    # DELETEs to an id delete that node - only available in development
    if config.registry.settings.get('enable_delete', False):
        config.add_route('delete_feedback_node_by_id',
                         '/api/plingbacks/{feedback_id}', 
                         view='plingback.input.views.delete',
                         view_renderer='json',
                         request_method='DELETE',
                         factory=InputRoot)
   
    # Shards of testing bits + maintanance1    
    config.add_route('populate_id_pool',
                     '/maintenance/ids/populate',
                     view='plingback.maintenance.views.populate_id_pool',
                     view_renderer='json',
                     request_method='GET',
                     factory=InputRoot)
    
    # Augmentations
    config.add_route('add_activity_nodes',
                     '/augmentations/add_activity_nodes',
                     view='plingback.augmentations.views.add_activity_nodes',
                     view_renderer='json',
                     request_method='GET',
                     factory=InputRoot)
    config.add_route('add_activity_data',
                     '/augmentations/add_activity_data',
                     view='plingback.augmentations.views.add_activity_data',
                     view_renderer='json',
                     request_method='GET',
                     factory=InputRoot)
    
    # Route to static resources
    config.add_static_view('static', 'plingback:static')
    
    return config.make_wsgi_app()

