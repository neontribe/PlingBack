from pyramid.config import Configurator
from plingback.resources import TripleStore

from pyramid.view import static
static_view = static('plingback:static')


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
                     factory=TripleStore)
    config.add_route('scoped_attribute', 
                     '/api/{scope}/{id}/{attribute}', 
                     view='plingback.output.views.handler',
                     view_renderer='json',
                     request_method='GET',
                     factory=TripleStore)
    
    config.add_route('scoped_plingback_count', 
                     '/api/{scope}', 
                     view='plingback.output.views.handler',
                     view_renderer='json',
                     request_method='GET',
                     factory=TripleStore)
    config.add_route('narrow_scoped_plingback_count', 
                     '/api/{scope}/{id}', 
                     view='plingback.output.views.handler',
                     view_renderer='json',
                     request_method='GET',
                     factory=TripleStore)
    config.add_route('pling_plingback_count', 
                     '/api/plings/{id}', 
                     view='plingback.output.views.handler',
                     view_renderer='json',
                     request_method='GET',
                     factory=TripleStore)
    
    # Setup the Input API
    # POSTs to the controller create new nodes the posted data will be parsed
    # for subnodes (ratings etc) which will also be created
    config.add_route('create_feedback_node',
                     '/api/plingbacks',
                     view='plingback.input.views.create',
                     view_renderer='json',
                     request_method='POST',
                     factory=TripleStore)
    # PUTs to an id create that node the posted data will be parsed
    # for subnodes (ratings etc) which will also be created
    config.add_route('create_feedback_node_by_id',
                     '/api/plingbacks/{feedback_id}', 
                     view='plingback.input.views.create',
                     view_renderer='json',
                     request_method='PUT',
                     factory=TripleStore)

    # POSTs to a feedback attribute create it
    config.add_route('create_feedback_attribute',
                     '/api/plingbacks/{feedback_id}/{attribute}', 
                     view='plingback.input.views.attribute_handler',
                     view_renderer='json',
                     request_method='POST',
                     factory=TripleStore)
                          
    # PUTs to a feedback attribute overwrite
    config.add_route('update_feedback_attribute',
                     '/api/plingbacks/{feedback_id}/{attribute}', 
                     view='plingback.input.views.attribute_handler',
                     view_renderer='json',
                     request_method='PUT',
                     factory=TripleStore)
    
    
    
    # DELETEs to an id delete that node - only available in development
    if config.registry.settings.get('enable_delete', False):
        config.add_route('delete_feedback_node_by_id',
                         '/api/plingbacks/{feedback_id}', 
                         view='plingback.input.views.delete',
                         view_renderer='json',
                         request_method='DELETE',
                         factory=TripleStore)
    
    # Augmentations
    config.add_route('add_activity_nodes',
                     '/augmentations/add_activity_nodes',
                     view='plingback.augmentations.views.add_activity_nodes',
                     view_renderer='json',
                     request_method='GET',
                     factory=TripleStore)
    config.add_route('add_activity_data',
                     '/augmentations/add_activity_data',
                     view='plingback.augmentations.views.add_activity_data',
                     view_renderer='json',
                     request_method='GET',
                     factory=TripleStore)
    
    # Routing for rendered html responses
    config.add_route('index', '/', 
                     'plingback.views.index', 
                     view_renderer='plingback:templates/index.mak')
    
    # Render an html view of a single feedback node
    config.add_route('feedback_view',
                     '/views/plingbacks/{feedback_id}.html',
                     view='plingback.views.feedback_view',
                     view_renderer='plingback:templates/feedback_view.mak',
                     request_method='GET',
                     factory=TripleStore)
    
    # Route to static resources
    config.add_route('catchall_static', '/*subpath', 'plingback.static_view')
    
    return config.make_wsgi_app()

