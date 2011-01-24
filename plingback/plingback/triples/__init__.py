import urllib
import datetime
from rdflib import Graph
from rdflib import BNode, Literal, URIRef, Namespace
from talis import Talis
from pyramid.httpexceptions import HTTPException, HTTPBadRequest, HTTPInternalServerError
from plingback import namespaces as ns
from plingback.triples.helpers import CommentAttribute, RatingAttribute, ReviewerAttribute, \
                                      AttendanceAttribute, DeterrentAttribute, ApprovalAttribute
from plingback.triples.helpers import make_feedback_uri




class TripleFactory(object):
    def __init__(self, graph, request, feedback_id):
        self.graph = graph
        self.request = request
        self.feedback_id = feedback_id
        self.feedback_uri = make_feedback_uri(self.feedback_id)
    
    def init_feedback_node(self):
        """ Add triples for our feedback node to the supplied graph/store object
        
        The data will be extracted from the request which should contain the 
        following keys:
        
        pling_id : the id of the activity under review
        plingback_type : the application submitting the feedback
        plingback_version : the version of the application (OPTIONAL)
        """
                
        # Validation!
        if not self.request.params.get('pling_id'):
            return HTTPBadRequest(detail='Please supply a pling_id')
        pling_id = self.request.params.get('pling_id')
        pling = URIRef('http://plings.net/a/%s' % (pling_id))
    
       
        plingback_type = self.request.params.get('plingback_type',
                                        'unknown' )
        plingback_type_uri = URIRef("http://plingback.plings.net/applications/" 
                                    + urllib.quote_plus(plingback_type.strip()))
        
        self.graph.add((self.feedback_uri, ns['RDFS']['type'], ns['REV']['Review']))
        self.graph.add((self.feedback_uri, ns['PBO']['isAbout'], pling))
        self.graph.add((self.feedback_uri, ns['DC']['date'], Literal(datetime.datetime.now())))
        
        self.graph.add((self.feedback_uri, ns['PBO']['plingBackType'], plingback_type_uri))
        if self.request.params.get('plingback_version'):
            self.graph.add((self.feedback_uri, 
                            ns['PBO']['plingBackVersion'], 
                            Literal(self.request.params.get('plingback_version'))))
            
        return 'OK'
    
    def remove_feedback_node(self):

        query = """
            PREFIX pbo: <%s> 
            PREFIX rdfs: <%s> 
            PREFIX dc: <%s> 
            PREFIX rev: <%s>
            CONSTRUCT { <%s> rdfs:type ?type .
                        <%s> pbo:isAbout ?pling .
                        <%s> dc:date ?date .
                        <%s> pbo:plingBackType ?pbt .
                        <%s> pbo:plingBackVersion ?version .
                      } 
            WHERE { <%s> rdfs:type ?type .
                    <%s> pbo:isAbout ?pling .
                    <%s> dc:date ?date .
                    <%s> pbo:plingBackType ?pbt .
                    OPTIONAL { 
                       <%s> pbo:plingBackVersion ?version .
                      }
            }"""
            
        query = query % (str(ns['PBO']), str(ns['RDFS']), str(ns['DC']), str(ns['REV']),
                 self.feedback_uri, self.feedback_uri, self.feedback_uri, self.feedback_uri,
                 self.feedback_uri, self.feedback_uri, self.feedback_uri, self.feedback_uri, 
                 self.feedback_uri, self.feedback_uri)
        if isinstance(self.graph, Talis):
            local_graph = Graph()
            triples = local_graph.parse(self.request.root.query_store(query, format=None))
        else:
            output_graph = [x for x in self.graph.query(query)][0]
            triples = [x for x in output_graph]
        for triple in triples:
            self.graph.remove(triple)
        
    
    def attribute_factory(self, attribute):
        """ TODO: replace this with an adapter/lookup system """
        map = { 'comment' : CommentAttribute,
                'rating' : RatingAttribute,
                'reviewer':ReviewerAttribute,
                'attendance':AttendanceAttribute,
                'deterrent':DeterrentAttribute,
                'approval':ApprovalAttribute}
        return map[attribute](self.feedback_id, self.request.params)
    
    def _add_feedback_attributes(self, attribute_name=None):   
        """ 
        """
        attributes = []
        if attribute_name:
            attributes = [attribute_name]
        else:
            attributes = self.request.params.getall('feedback_attribute')
            if not attributes:
                # An oddity in WebOb means that if multiple values were submitted for
                # a key via a javascript list we end up with odd key naming
                attributes = self.request.params.getall('feedback_attribute[]')
        
        success = []
        for attribute in attributes:
            try:
                triples = self.attribute_factory(attribute).triples()
                if isinstance(triples, HTTPException):
                    return triples
                for triple in triples:
                    self.graph.add(triple)
                success.append(attribute)
            except KeyError:
                pass
            
        return success

    def remove_attribute(self, attribute_name=None):
        attributes = []
        if attribute_name:
            attributes = [attribute_name]
        else:
            attributes = self.request.params.getall('feedback_attribute')
            if not attributes:
                # An oddity in WebOb means that if multiple values were submitted for
                # a key via a javascript list we end up with odd key naming
                attributes = self.request.params.getall('feedback_attribute[]')
        
        removals = []
        for attribute in attributes:
            res = self._remove_feedback_attribute(attribute)
            if isinstance(res, HTTPException):
                return res
            else:
                removals.append(attribute)
        return removals

    def _remove_feedback_attribute(self, attribute_name):
        """ Queries the store for the triple representing the attribute and then 
        issues removal requests against the graph"""
        #local_graph = Graph()
        #sparqurl = self.graph.urlbase + '/services/sparql?query='
        #import pdb
        #pdb.set_trace()
        try:
            helper = self.attribute_factory(attribute_name)
            query = helper.removal_query()
            if query:
                if isinstance(self.graph, Talis):
                    local_graph = Graph()
                    triples = local_graph.parse(self.request.root.query_store(query, format=None))
                else:
                    output_graph = [x for x in self.graph.query(query)][0]
                    triples = [x for x in output_graph]
                for triple in triples:
                    self.graph.remove(triple)
        except KeyError:
            return HTTPBadRequest(detail='Unknown feedback attribute supplied')
                   
        return 'Removed'
    
        
        
        
    def add_attribute(self, attribute=None, overwrite=False):
        """ Record a feedback attribute 
        
        
        @attribute: the name of the feedback attribute
        @overwrite : overwrite the existing attribute for this node with the new one
                        (an HTTP PUT will trigger this)
        """

        if overwrite:
            self.remove_attribute(attribute_name=attribute)
            
        
        result = self._add_feedback_attributes(attribute_name=attribute)
        
        return result