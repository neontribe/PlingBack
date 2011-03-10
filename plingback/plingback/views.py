

def index(request):
    root_url = request.registry.settings.get('root_url', '')
    return {'root_url': root_url}

    
    
