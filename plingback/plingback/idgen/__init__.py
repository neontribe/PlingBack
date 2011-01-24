import random
import urllib2
from rdflib import Graph
from rdflib import BNode, Literal, URIRef, Namespace

from plingback import namespaces as ns

class FeedbackIdManager(object):
    ID_POOL_SIZE = 20
    ID_CANDIDATE_LIMIT = 3
    MAX_ID_ATTEMPTS = 3

    
    def __init__(self, request):
        self.context = request.context
    
    def fetch_candidates(self):
        """Get a list of potential ids"""
        candidates_query = """
          PREFIX pb: <http://plingback.plings.net/ontologies/plingback#>
          SELECT ?s  ?o WHERE { ?s pb:idCandidate ?o } ORDER BY DESC(?o)
          LIMIT %s
        """
        candidates_query = candidates_query % (self.ID_CANDIDATE_LIMIT)
        results = self.context.query_store(candidates_query)['results']['bindings']
        return [(x['s']['value'], x['o']['value']) for x in results]
    
    def get_unique_feedback_id(self):
        """ Get a unique id for a piece of feedback by using the Primary Key Pattern
        
        See http://n2.talis.com/wiki/Primary_Key_Pattern for an overview
        """
    
        
        candidates = []
        attempts = 0
        feedback_id = None
    
        def take_id(candidate):
            """Push a changeset removing our chosen id and adding a replacement
            
            If this succeeds we can go ahead and use the id"""
            self.context.store.remove((candidate[0], ns['PBO']['idCandidate'], Literal(int(float(candidate[1]))) ))
            self.context.store.add((BNode(), ns['PBO']['idCandidate'], Literal(int(float(candidate[1]) + self.ID_POOL_SIZE))))
            try:
                self.context.store.sync()
            except urllib2.URLError, e:
                if e.code == 202:
                    pass
                else:
                    raise
            return int(float(candidate[1]))
            
        while feedback_id == None and attempts < self.MAX_ID_ATTEMPTS:
            if not candidates:
                candidates = self.fetch_candidates()
                
            candidate = random.choice(candidates)
            candidates.remove(candidate)
            
            try:
                feedback_id = take_id(candidate)
            except:
                pass
            
            attempts = attempts + 1
    
        if attempts >= self.MAX_ID_ATTEMPTS:
            log.critical("max attempts exceeded while trying to grab a unique feedback id")
            
        return str(feedback_id)
    
    def populate_id_pool(self):
    
        start = 1
        
        candidates = self.fetch_candidates()
        if candidates:
            start = float(candidates[0][1]) + self.ID_POOL_SIZE
        else:
            start = start + self.ID_POOL_SIZE
            
        for x in range(start, start + self.ID_POOL_SIZE + 1):
            self.context.store.add((BNode(), ns['PBO']['idCandidate'], Literal(x)))
        try:
            self.context.store.sync()
        except urllib2.URLError, e:
            if e.code == 202:
                pass
            else:
                raise
        return "Id Pool Populated"  
        