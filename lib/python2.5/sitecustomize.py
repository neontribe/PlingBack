import tempfile, os, site, sys
home = os.path.normpath(os.path.join(os.path.dirname(__file__), '../../'))
app_path = os.path.join(home, 'app')
if app_path not in sys.path:
    sys.path.append(app_path)
lib_path = os.path.join(app_path, 'lib', 'python')
if lib_path not in sys.path:
    site.addsitedir(lib_path)

def activate_gae(location):
    if location not in sys.path:
        sys.path.append(location)
    for path in '../lib/antlr3', '../lib/yaml/lib', '../lib/webob', '../lib/django':
        path = os.path.join(location, path)
        if path not in sys.path:
            sys.path.append(path)
    from google.appengine.tools import dev_appserver
    from google.appengine.tools.dev_appserver_main import         DEFAULT_ARGS, ARG_CLEAR_DATASTORE, ARG_LOG_LEVEL,         ARG_DATASTORE_PATH, ARG_HISTORY_PATH
    gae_opts = DEFAULT_ARGS.copy()
    gae_opts[ARG_CLEAR_DATASTORE] = False
    gae_opts[ARG_DATASTORE_PATH] = os.path.join(tempfile.gettempdir(), 'wikistorage.datastore')
    gae_opts[ARG_HISTORY_PATH] = os.path.join(tempfile.gettempdir(), 'wikistorage.history')
    config = dev_appserver.LoadAppConfig(app_path, {})[0]
    dev_appserver.SetupStubs(config.application, **gae_opts)
    if not os.environ.get('APPLICATION_ID'):
        ## FIXME: should come up with a proper name:
        os.environ['APPLICATION_ID'] = 'miscapp'
    if not os.environ.get('SERVER_SOFTWARE'):
        os.environ['SERVER_SOFTWARE'] = 'Development/interactive'
    import runner

try:
    import google
    gae_location = os.path.dirname(google.__file__)
except ImportError:
    gae_location_fn = os.path.join(home, 'gae-location.txt')
    fp = open(gae_location_fn)
    gae_location = [line for line in fp.readlines()
                    if line.strip() and not line.strip().startswith('#')]
    if gae_location:
        gae_location = gae_location[0].strip()
        gae_location = os.path.expandvars(os.path.expanduser(gae_location))
    if not gae_location or not os.path.exists(gae_location):
        print >> sys.stderr, (
            "File %s doesn't contain a valid path" % gae_location_fn)
        gae_location = None
if gae_location:
    activate_gae(gae_location)
