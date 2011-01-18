from pyramid.config import Configurator
from plingback.resources import Root

def main(global_config, **settings):
    """ This function returns a Pyramid WSGI application.
    """
    config = Configurator(root_factory=Root, settings=settings)
    config.add_view('plingback.views.my_view',
                    context='plingback:resources.Root',
                    renderer='plingback:templates/mytemplate.pt')
    config.add_static_view('static', 'plingback:static')
    return config.make_wsgi_app()

