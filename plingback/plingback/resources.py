import urllib
import urllib2
import simplejson as json
from talis import Talis
from rdflib import ConjunctiveGraph as Graph
from pyramid.interfaces import IDebugLogger


class OutputRoot(object):
    """ A root object to supply store connectivity to view code """
    def __init__(self, request):
        self.request = request
        self.sparql_endpoint = 'http://api.talis.com/stores/%s/services/sparql' % \
                                (self.request.registry.settings['talis_store'])
        

        self.debug_sparql = self.request.registry.settings['debug_sparql']
        q = self.request.registry.queryUtility
        self.logger = q(IDebugLogger)
        
        
        

    def query_store(self, sparql, format='json'):
        """ Use the supplied sparql to query the store returning a dictionary of data """
        # Prepare to authenticate our query
        passman = urllib2.HTTPPasswordMgrWithDefaultRealm()
        passman.add_password(None, 
                             self.sparql_endpoint, 
                             self.request.registry.settings['talis_user'], 
                             self.request.registry.settings['talis_password'])
        authhandler = urllib2.HTTPDigestAuthHandler(passman)
        opener = urllib2.build_opener(authhandler)
        urllib2.install_opener(opener)
        
        if self.debug_sparql:
            msg = (sparql)
            self.logger and self.logger.debug(msg)
        
        params = {'query':sparql}
        if format:
            params['output'] = format
        url_query = urllib.urlencode(params)
        res = urllib2.urlopen(self.sparql_endpoint + '?' + url_query)
        
        if format == 'json':
            # Deserialize for convenince
            return json.loads(res.read())
        else:
            return res
    
class InputRoot(OutputRoot):
    
    def __init__(self, request):
        super(InputRoot, self).__init__(request)
        
        if (self.request.registry.settings['store_type'] == 'talis'):
            # Configure a connection to the talis store
            self.store = Talis(self.request.registry.settings['talis_store'],
                               self.request.registry.settings['talis_user'],
                               self.request.registry.settings['talis_password'])
        else:
            self.store = Graph()