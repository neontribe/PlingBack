from pyramid.response import Response

def aview(request):
    return Response('root')

def configure(config):
    config.add_view(aview)
    config.include('pyramid.tests.includeapp1.two.configure')
    config.commit()
    
