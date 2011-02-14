import urllib
import urllib2
import simplejson as json
from talis import Talis
from rdflib import ConjunctiveGraph as Graph
from rdfextras.sparql.query import SPARQLQueryResult
from pyramid.interfaces import IDebugLogger


class TripleStore(object):
    """ A root object to supply store connectivity to view code """
    def __init__(self, request):
        self.request = request

        q = self.request.registry.queryUtility
        self.logger = q(IDebugLogger)

        if self.request.registry.settings:
            if (self.request.registry.settings['store_type'] == 'talis'):
                # Configure a connection to the talis store
                self.store = Talis(self.request.registry.settings['talis_store'],
                               self.request.registry.settings['talis_user'],
                               self.request.registry.settings['talis_password'])
                self.debug_sparql = self.request.registry.settings['debug_sparql']
            else:
                self.store = Graph()
                self.debug_sparql = True
        else:
            self.store = Graph()
            self.debug_sparql = True
        
    def query(self, sparql, format='json'):
        
        if self.debug_sparql:
            msg = (sparql)
            self.logger and self.logger.debug(msg)
            
        res = self.store.query(sparql)
        
        # If we're working with a local rdflib graph we'll need to delve to get the results
        if isinstance(res, SPARQLQueryResult):
            return res.result
        else:
            return res
        
    def sync(self):
        if self.request.registry.settings['store_type'] == 'talis':
            self.store.sync()
        else:
            pass

        
        