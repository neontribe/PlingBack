import urllib
import datetime
from rdflib import BNode, Literal, URIRef, Namespace
from pyramid.httpexceptions import HTTPException, HTTPBadRequest, HTTPInternalServerError
from plingback.namespaces import namespaces as ns
from plingback.triples.helpers import CommentAttribute, RatingAttribute, ReviewerAttribute, \
                                      AttendanceAttribute, DeterrentAttribute, ApprovalAttribute
from plingback.triples.helpers import make_feedback_uri




class TripleFactory(object):
    def __init__(self, request, feedback_id):
        self.context = request.context
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
        submission_date : the datetime at which the feedback was collected (OPTIONAL - default now)
        """
                
        # Validation!
        if not self.request.params.get('pling_id'):
            return HTTPBadRequest(detail='Please supply a pling_id')
        pling_id = self.request.params.get('pling_id')
        pling = URIRef('http://plings.net/a/%s' % (pling_id))
        
        # Validation!
        submitted = self.request.params.get('submission_date', None)
        if submitted:
            try:
                submitted = datetime.datetime.strptime(submitted, '%Y-%m-%dT%H:%M:%S')
            except ValueError:
                return HTTPBadRequest(detail='"submission_date" should be supplied in "%Y-%m-%dT%H:%M:%S" (iso-8601) format')
    
       
        plingback_type = self.request.params.get('plingback_type',
                                        'unknown' )
        plingback_type_uri = URIRef("http://plingback.plings.net/applications/" 
                                    + urllib.quote_plus(plingback_type.strip()))
        
        self.context.store.add((self.feedback_uri, ns['RDF']['type'], ns['REV']['Review']))
        self.context.store.add((pling, ns['REV']['hasReview'], self.feedback_uri))
        self.context.store.add((pling, ns['RDF']['type'], ns['PBO']['Activity']))
        self.context.store.add((self.feedback_uri, ns['PBO']['isAbout'], pling))
        
        if submitted:
            self.context.store.add((self.feedback_uri, ns['DC']['date'], Literal(submitted)))
        else:
            self.context.store.add((self.feedback_uri, ns['DC']['date'], Literal(datetime.datetime.now())))
        
        self.context.store.add((self.feedback_uri, ns['PBO']['plingBackType'], plingback_type_uri))
        if self.request.params.get('plingback_version'):
            self.context.store.add((self.feedback_uri, 
                            ns['PBO']['plingBackVersion'], 
                            Literal(self.request.params.get('plingback_version'))))
            
        return 'OK'
    
    def remove_feedback_node(self):

        query = """
            PREFIX pbo: <%s> 
            PREFIX rdf: <%s> 
            PREFIX dc: <%s> 
            PREFIX rev: <%s>
            CONSTRUCT { <%s> rdf:type ?type .
                        <%s> pbo:isAbout ?pling .
                        <%s> dc:date ?date .
                        <%s> pbo:plingBackType ?pbt .
                        <%s> pbo:plingBackVersion ?version .
                        ?pling rev:hasReview <%s> .
                      } 
            WHERE { <%s> rdf:type ?type .
                    <%s> pbo:isAbout ?pling .
                    <%s> dc:date ?date .
                    <%s> pbo:plingBackType ?pbt .
                    OPTIONAL { 
                       <%s> pbo:plingBackVersion ?version .
                      }
            }"""
            
        query = query % (str(ns['PBO']), str(ns['RDF']), str(ns['DC']), str(ns['REV']),
                 self.feedback_uri, self.feedback_uri, self.feedback_uri, self.feedback_uri,
                 self.feedback_uri, self.feedback_uri, self.feedback_uri, self.feedback_uri, 
                 self.feedback_uri, self.feedback_uri, self.feedback_uri)
        
        triples = [x for x in self.context.query(query)]
        for triple in triples:
            self.context.store.remove(triple)
        
    
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
                    self.context.store.add(triple)
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
        try:
            helper = self.attribute_factory(attribute_name)
            query = helper.removal_query()
            if query:
                triples = [x for x in self.context.query(query)]
                for triple in triples:
                    self.context.store.remove(triple)
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