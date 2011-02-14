APP_NAME = 'plingback:main'
APP_ARGS = ({},)
APP_KWARGS = dict({'store_type':'talis',
                   'talis_store':'plings-dev2',
                   'talis_user':'plings',
                   'talis_password':'ck6sjkfp',
                   'debug_sparql':True,
                   'enable_delete':True,
                   'mako.directories':'plingback.sparql:templates'})
# You can overwrite these separately for different dev/live settings:
DEV_APP_ARGS = APP_ARGS
DEV_APP_KWARGS = APP_KWARGS
REMOVE_SYSTEM_LIBRARIES = ['webob']
