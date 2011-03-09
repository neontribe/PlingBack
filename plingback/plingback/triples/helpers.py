from rdflib import BNode, Literal, URIRef, Namespace
from pyramid.httpexceptions import  HTTPBadRequest

from plingback.namespaces import namespaces as ns

def make_feedback_uri(feedback_id):
    return ns['PB'][feedback_id]

# FeedbackAttribute Classes
class FeedbackAttribute(object):
    """Base Class for feedback attributes"""
    def __init__(self, feedback_id, data):
        self.feedback_id = feedback_id
        self.feedback_uri = make_feedback_uri(feedback_id)
        self.data = data
        
    def _make_triples(self):
        """ Produce a list of rdflib triples ready to add to a graph"""
        raise NotImplementedError
    
    def triples(self):
        """Return a list of triples"""
        return self._make_triples()
        # Removed exception handling 'cos it was inexplicable
        #try:
        #    return self._make_triples()
        #except KeyError:
        #    return []

    def removal_query(self):
        """ Produce a sparql query to construct a set of triple which will be 
        removed in order to update this attribute's data"""
        raise NotImplementedError
    
    
class AttendanceAttribute(FeedbackAttribute):
    """ Helper class for attendance attributes """
    
    def _make_triples(self):
        value = self.data.getone('attendance_value')
        return [(self.feedback_uri, ns['PBO']['attendance'], ns['PBO'][value])]
        
        
    def removal_query(self):
        query = "PREFIX pbo: <%s> "
        query += "CONSTRUCT { <%s> pbo:attendance ?o } WHERE { <%s> pbo:attendance ?o}"
        query = query % (str(ns['PBO']), self.feedback_uri, self.feedback_uri)
        return query
    

    
class DeterrentAttribute(FeedbackAttribute):
    """Helper class for deterrent attributes (why someone didn't/won't go)"""
    
    def _make_triples(self):
        values = self.data.getall('deterrent_value')
        if not values:
            # An oddity in WebOb means that if multiple values were submitted for
            # a key via a javascript list we end up with odd key naming
            values = self.data.getall('deterrent_value[]')
        return [(self.feedback_uri, ns['PBO']['deterrent'], Literal(det)) for det in values]
        
    def removal_query(self):
        query = "PREFIX pbo: <%s> "
        query += "CONSTRUCT { <%s> pbo:deterrent ?o } WHERE { <%s> pbo:deterrent ?o}"
        query = query % (str(ns['PBO']), self.feedback_uri, self.feedback_uri)
        return query
    
class RatingAttribute(FeedbackAttribute):
    """Helper class for rating attributes"""
    
    def _make_triples(self):
        value = self.data.getone('rating_value')
        try:
            rating = '.' in value and float(value) or int(value)
            return [(self.feedback_uri, ns['REV']['rating'], Literal(rating))]
        except ValueError:
            raise HTTPBadRequest(detail='Value "%s" cannot be converted to a numeric type' % (value))

        
    def removal_query(self):
        query = "PREFIX rev: <%s> "
        query += "CONSTRUCT { <%s> rev:rating ?o } WHERE { <%s> rev:rating ?o}"
        query = query % (str(ns['REV']), self.feedback_uri, self.feedback_uri)
        return query
    
class CommentAttribute(FeedbackAttribute):
    """Helper class for comment attributes"""
    
    def _make_triples(self):
        value = self.data.getone('comment_value')
        return [(self.feedback_uri, ns['REV']['text'], Literal(value))]
        
    def removal_query(self):
        query = "PREFIX rev: <%s> "
        query += "CONSTRUCT { <%s> rev:text ?o } WHERE { <%s> rev:text ?o}"
        query = query % (str(ns['REV']), self.feedback_uri, self.feedback_uri)
        return query
    
class ApprovalAttribute(FeedbackAttribute):
    """Helper class for Approval Attributes"""
    
    def _make_triples(self):
        value = self.data.getone('approval_value')
        try:
            approval = '.' in value and float(value) or int(value)
            return [(self.feedback_uri, ns['PBO']['approval'], Literal(approval))]
        except ValueError:
            raise HTTPBadRequest(detail='Value "%s" cannot be converted to a numeric type' % (value))
        
    def removal_query(self):
        query = "PREFIX pbo: <%s> "
        query += "CONSTRUCT { <%s> pbo:approval ?o } WHERE { <%s> pbo:approval ?o}"
        query = query % (str(ns['PBO']), self.feedback_uri, self.feedback_uri)
        return query        
    
    
class ReviewerAttribute(FeedbackAttribute):
    
    def _make_triples(self):

        triples = []
        reviewer = BNode()
        
        # See if we've been provided an email address
        try:
            email = self.data.getone('reviewer_email')
            if email:
                triples.append((reviewer, ns['FOAF']['mbox'], Literal(email)))
        except KeyError:
            pass
        # See if we've been provided a phone number
        try:
            phone = self.data.getone('reviewer_phone')
            if phone:
                triples.append((reviewer, ns['FOAF']['phone'], Literal('tel:' + phone)))
        except KeyError:
            pass
        # See if we've been provided a birthday
        try:
            birthday = self.data.getone('reviewer_birthday')
            if birthday:
                triples.append((reviewer, ns['FOAF']['dateOfBirth'], Literal(birthday)))
        except KeyError:
            pass
        # See if we've been provided a third party id
        try:
            tpid = self.data.getone('reviewer_id')
            tps = self.data.getone('reviewer_id_source')
            if tpid or tps:
                acc = BNode()
                triples.append((reviewer, ns['FOAF']['holdsAccount'], acc))
                triples.append((acc, ns['RDF']['type'], ns['FOAF']['OnlineAccount']))
                if tps:
                    triples.append((acc, ns['FOAF']['accountServiceHomepage'], URIRef(tps)))
                if tpid:
                    triples.append((acc, ns['FOAF']['accountName'], Literal(tpid)))
        except KeyError:
            pass
        
        #If we found some data then add the BNode and type
        if triples:
            triples.append((self.feedback_uri, ns['REV']['reviewer'], reviewer))
            triples.append((reviewer, ns['RDF']['type'], ns['FOAF']['Person']))
        
        return triples

    def removal_query(self):
        query = """
            PREFIX rev: <%s> 
            PREFIX rdfs: <%s> 
            PREFIX foaf: <%s> 
            CONSTRUCT { <%s> rev:reviewer ?rbn .
                                     ?rbn rdf:type foaf:Person .
                                     ?rbn foaf:mbox ?email .
                                     ?rbn foaf:phone ?phone .
                                     ?rbn foaf:dateOfBirth ?dob.
                                     ?rbn foaf:holdsAccount ?acc.
                                     ?acc rdf:type foaf:OnlineAccount.
                                     ?acc foaf:accountServiceHomepage ?homepage.
                                     ?acc foaf:accountName ?accid} 
            WHERE { <%s> rev:reviewer ?rbn .
                            OPTIONAL { 
                                               ?rbn foaf:mbox ?email .
                                               ?rbn foaf:phone ?phone .
                                               ?rbn foaf:dateOfBirth ?dob.
                                               ?rbn foaf:holdsAccount ?acc.
                                               ?acc foaf:accountServiceHomepage ?homepage.
                                               ?acc foaf:accountName ?accid
                              }
            }"""
        query = query % (str(ns['REV']), str(ns['RDF']), str(ns['FOAF']), self.feedback_uri, self.feedback_uri)
        return query