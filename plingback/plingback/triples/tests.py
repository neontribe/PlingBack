import unittest
import rdflib
import datetime
from rdflib import Graph
from rdflib import BNode, Literal, URIRef, Namespace

rdflib.plugin.register('sparql', rdflib.query.Processor,
                       'rdfextras.sparql.processor', 'Processor')
rdflib.plugin.register('sparql', rdflib.query.Result,
                       'rdfextras.sparql.query', 'SPARQLQueryResult')

from webob.multidict import MultiDict
from pyramid import testing
from pyramid.httpexceptions import HTTPException, HTTPBadRequest, HTTPInternalServerError


from plingback.triples import TripleFactory
from plingback.triples.helpers import FeedbackAttribute
from plingback.namespaces import namespaces as ns
from plingback.resources import TripleStore
        
        

class TripleFactoryTests(unittest.TestCase):
    def setUp(self):
        self.config = testing.setUp()
        self.config.begin()

    def tearDown(self):
        testing.tearDown()
        
    def configure_triple_factory(self, path, params, fbid='feedback_id_value'):
        request = testing.DummyRequest(path=path,
                                       params=MultiDict(params))
        request.context = TripleStore(request)
        tf = TripleFactory(request, fbid)
        return tf
        
    def test_init_feedback_node(self):
        tf = self.configure_triple_factory('/api/plingbacks',
                                           {'pling_id':'pling_id_value',
                                            'plingback_type':'automated_testing'})
        tf.init_feedback_node()
        self.failUnless(len([x for x in tf.request.context.store]) == 6)
        
    def test_init_feedback_node_with_submission_date(self):
        datestring = '2011-02-21T15:36:00'
        tf = self.configure_triple_factory('/api/plingbacks',
                                           {'pling_id':'pling_id_value',
                                            'plingback_type': 'automated_testing',
                                            'submission_date': datestring })
        tf.init_feedback_node()
        date = tf.request.context.query("SELECT ?date WHERE { ?pb <%s> ?date }" % (ns['DC']['date']))
        print date
        self.assertEqual(str(date[0]), datestring)
        
        
        
    def test_remove_feedback_node(self):
        tf = self.configure_triple_factory('/api/plingbacks',
                                           {'pling_id':'pling_id_value',
                                            'plingback_type':'automated_testing'})
        tf.init_feedback_node()
        self.failUnless(len([x for x in tf.request.context.store]) == 6)
        tf.remove_feedback_node()
        # Only the assertion that the activity _is_ an activity should remain
        self.assertEqual(len([x for x in tf.request.context.store]), 1)
        
    def test_missing_feedback_target(self):
        tf = self.configure_triple_factory('/api/plingbacks',
                                           {})
        res = tf.init_feedback_node()
        self.failUnless(isinstance(res, HTTPBadRequest))
        
    def test_init_feedback_node_with_version(self):
        tf = self.configure_triple_factory('/api/plingbacks',
                                           {'pling_id':'pling_id_value',
                                               'plingback_version':'Mk5a',
                                                    'plingback_type':'automated_testing'})
        tf.init_feedback_node()
        self.failUnless(len([x for x in tf.request.context.store]) == 7)
        self.failUnless('Mk5a' in [str(x[2]) for x in tf.request.context.store])
        
    def test_feedback_helper_base(self):
        fbh = FeedbackAttribute('id', {})
        self.failUnlessRaises(NotImplementedError, fbh.triples)
        self.failUnlessRaises(NotImplementedError, fbh.removal_query)
        
    def test_add_rating_attribute(self):
        tf = self.configure_triple_factory('/api/plingbacks',
                                           {'pling_id':'pling_id_value',
                                               'feedback_attribute':'rating',
                                               'rating_value':'70',
                                                    'plingback_type':'automated_testing'})
        tf.add_attribute()
        res = tf.request.context.query("SELECT ?val WHERE { ?pb <%s> ?val }" % (ns['REV']['rating']))
        self.failUnless(res[0].toPython() == 70)
        self.failUnless(len([x for x in tf.request.context.store]) == 1)
    
    def test_bad_rating_attribute(self):
        tf = self.configure_triple_factory('/api/plingbacks',
                                           {'pling_id':'pling_id_value',
                                               'feedback_attribute':'rating',
                                               'rating_value':'NaN',
                                                    'plingback_type':'automated_testing'})
        res = tf.add_attribute()
        self.failUnless(isinstance(res, HTTPBadRequest))
        self.failUnless(len([x for x in tf.request.context.store]) == 0)
        
    def test_remove_rating_attribute(self):
        tf = self.configure_triple_factory('/api/plingbacks',
                                          {'pling_id':'pling_id_value',
                                               'feedback_attribute':'rating',
                                               'rating_value':'70',
                                                    'plingback_type':'automated_testing'})
        tf.add_attribute()
        self.failUnless(len([x for x in tf.request.context.store]) == 1)
        tf.remove_attribute('rating')
        self.failUnless(len([x for x in tf.request.context.store]) == 0)
        
    def test_overwrite_rating_attribute(self):
        tf = self.configure_triple_factory('/api/plingbacks',
                                           {'pling_id':'pling_id_value',
                                               'feedback_attribute':'rating',
                                               'rating_value':'70',
                                                    'plingback_type':'automated_testing'})
        tf.add_attribute()
        self.failUnless(len([x for x in tf.request.context.store]) == 1)
        res = tf.request.context.query("SELECT ?val WHERE { ?pb <%s> ?val }" % (ns['REV']['rating']))
        self.failUnless(str([x for x in res][0]) == '70')
        
        request2 = testing.DummyRequest(path='/api/plingbacks/feedback_id_value/rating',
                                       params=MultiDict({'pling_id':'pling_id_value',
                                               'feedback_attribute':'rating',
                                               'rating_value':'20',
                                                    'plingback_type':'automated_testing'}))
        request2.context = tf.request.context
        tf2 = TripleFactory(request2, 'feedback_id_value')
        tf2.add_attribute(overwrite=True)
        self.failUnless(len([x for x in tf2.request.context.store]) == 1)
        res = tf.request.context.query("SELECT ?val WHERE { ?pb <%s> ?val }" % (ns['REV']['rating']))
        self.failUnless(str([x for x in res][0]) == '20')
        
        
    def test_add_node_with_rating_attribute(self):
        tf = self.configure_triple_factory('/api/plingbacks/feedback_id_value',
                                           {'pling_id':'pling_id_value',
                                            'feedback_attribute':'rating',
                                            'rating_value':'50',
                                            'plingback_type':'automated_testing'})
        tf.init_feedback_node()
        tf.add_attribute()
        res = tf.request.context.query("SELECT ?val WHERE { <%s> <%s> ?val }" % (ns['PB']['feedback_id_value'], 
                                                                    ns['REV']['rating']))
        self.failUnless(res[0].toPython() == 50)
        self.failUnless(len([x for x in tf.request.context.store]) == 7)
        
    def test_add_comment_attribute(self):
        tf = self.configure_triple_factory('/api/plingbacks',
                                           {'pling_id':'pling_id_value',
                                            'feedback_attribute':'comment',
                                            'comment_value':'test comment',
                                            'plingback_type':'automated_testing'})
        tf.add_attribute()
        res = tf.request.context.query("SELECT ?val WHERE { ?pb <%s> ?val }" % (ns['REV']['text']))
        self.failUnless(res[0].toPython() == 'test comment')
        self.failUnless(len([x for x in tf.request.context.store]) == 1)
        
    def test_remove_comment_attribute(self):
        tf = self.configure_triple_factory('/api/plingbacks',
                                           {'pling_id':'pling_id_value',
                                               'feedback_attribute':'comment',
                                               'comment_value':'test comment',
                                                    'plingback_type':'automated_testing'})
        tf.add_attribute()
        self.failUnless(len([x for x in tf.request.context.store]) == 1)
        tf.remove_attribute('comment')
        self.failUnless(len([x for x in tf.request.context.store]) == 0)
        
    def test_add_approval_attribute(self):
        tf = self.configure_triple_factory('/api/plingbacks',
                                           {'pling_id':'pling_id_value',
                                            'feedback_attribute':'approval',
                                            'approval_value':'10',
                                            'plingback_type':'automated_testing'})
        tf.add_attribute()
        res = tf.request.context.query("SELECT ?val WHERE { ?pb <%s> ?val }" % (ns['PBO']['approval']))
        self.failUnless(str([x for x in res][0]) == '10')
        self.failUnless(len([x for x in tf.request.context.store]) == 1)
        
    def test_bad_approval_attribute(self):
        tf = self.configure_triple_factory('/api/plingbacks',
                                           {'pling_id':'pling_id_value',
                                            'feedback_attribute':'approval',
                                            'approval_value':'NaN',
                                            'plingback_type':'automated_testing'})
        res = tf.add_attribute()
        self.failUnless(isinstance(res, HTTPBadRequest))
        self.failUnless(len([x for x in tf.request.context.store]) == 0)
        
    def test_remove_approval_attribute(self):
        tf = self.configure_triple_factory('/api/plingbacks',
                                           {'pling_id':'pling_id_value',
                                            'feedback_attribute':'approval',
                                            'approval_value':'10',
                                            'plingback_type':'automated_testing'})
        tf.add_attribute()
        self.failUnless(len([x for x in tf.request.context.store]) == 1)
        tf.remove_attribute('approval')
        self.failUnless(len([x for x in tf.request.context.store]) == 0)
        
        
    def test_add_attendance_attribute(self):
        tf = self.configure_triple_factory('/api/plingbacks',
                                           {'pling_id':'pling_id_value',
                                               'feedback_attribute':'attendance',
                                               'attendance_value':'Attended',
                                                    'plingback_type':'automated_testing'})
        tf.add_attribute()
        res = tf.request.context.query("SELECT ?val WHERE { ?pb <%s> ?val }" % (ns['PBO']['attendance']))
        self.failUnless(str([x for x in res][0]) == str(ns['PBO']['Attended']))
        self.failUnless(len([x for x in tf.request.context.store]) == 1)
        
    def test_remove_attendance_attribute(self):
        tf = self.configure_triple_factory('/api/plingbacks',
                                           {'pling_id':'pling_id_value',
                                               'feedback_attribute[]':'attendance',
                                               'attendance_value':'Attended',
                                                    'plingback_type':'automated_testing'})
        tf.add_attribute()
        self.failUnless(len([x for x in tf.request.context.store]) == 1)
        tf.remove_attribute()
        self.failUnless(len([x for x in tf.request.context.store]) == 0)
        
    def test_add_deterrent_attribute(self):
        tf = self.configure_triple_factory('/api/plingbacks',
                                           {'pling_id':'pling_id_value',
                                            'feedback_attribute':'deterrent',
                                            'deterrent_value':'Cost',
                                            'plingback_type':'automated_testing'})
        tf.add_attribute()
        res = tf.request.context.query("SELECT ?val WHERE { ?pb <%s> ?val }" % (ns['PBO']['deterrent']))

        self.failUnless('Cost' in [str(x) for x in res])
        self.failUnless(len([x for x in tf.request.context.store]) == 1)  
        
    def test_add_multiple_deterrent_attribute_with_js_list(self):
        params = MultiDict({'pling_id':'pling_id_value',
                            'feedback_attribute':'deterrent',
                            'deterrent_value[]':'Cost',
                            'plingback_type':'automated_testing'})
        params.add('deterrent_value[]', 'Transport')
        tf = self.configure_triple_factory('/api/plingbacks',
                                           params)
        
        tf.add_attribute()
        res = tf.request.context.query("SELECT ?val WHERE { ?pb <%s> ?val }" % (ns['PBO']['deterrent']))
        self.failUnless('Cost' in [str(x) for x in res])
        self.failUnless('Transport' in [str(x) for x in res])
        self.failUnless(len([x for x in tf.request.context.store]) == 2)
        
    def test_remove_multiple_deterrent_attributes(self):
        params = MultiDict({'pling_id':'pling_id_value',
                            'feedback_attribute':'deterrent',
                            'deterrent_value':'Cost',
                            'plingback_type':'automated_testing'})
        params.add('deterrent_value', 'Transport')
        tf = self.configure_triple_factory('/api/plingbacks',
                                           params=params)
        tf.add_attribute()
        self.failUnless(len([x for x in tf.request.context.store]) == 2)
        tf.remove_attribute('deterrent')
        self.failUnless(len([x for x in tf.request.context.store]) == 0)
        
    def test_add_reviewer_attribute(self):
        tf = self.configure_triple_factory('/api/plingbacks',
                                           {'pling_id':'pling_id_value',
                                            'feedback_attribute':'reviewer',
                                            'reviewer_email':'test@example.com',
                                            'reviewer_phone':'01603 727747',
                                            'reviewer_birthday':'10/06/1971',
                                            'reviewer_id':'sn_id',
                                            'reviewer_id_source':'http://bebo.co.uk',
                                            'plingback_type':'automated_testing'})
        
        tf.add_attribute()
        self.failUnless(len([x for x in tf.request.context.store]) == 9)
        
    def test_empty_reviewer_attribute(self):
        tf = self.configure_triple_factory('/api/plingbacks',
                                           {'pling_id':'pling_id_value',
                                            'feedback_attribute':'reviewer',
                                            'plingback_type':'automated_testing'})
        tf.add_attribute()
        self.failUnless(len([x for x in tf.request.context.store]) == 0)
        
    def test_remove_reviewer_attribute(self):
        tf = self.configure_triple_factory('/api/plingbacks',
                                           {'pling_id':'pling_id_value',
                                            'feedback_attribute':'reviewer',
                                            'reviewer_email':'test@example.com',
                                            'reviewer_phone':'01603 727747',
                                            'reviewer_birthday':'10/06/1971',
                                            'reviewer_id':'sn_id',
                                            'reviewer_id_source':'http://bebo.co.uk',
                                            'plingback_type':'automated_testing'})
        tf.add_attribute()
        self.failUnless(len([x for x in tf.request.context.store]) == 9)
        tf.remove_attribute('reviewer')
        self.failUnless(len([x for x in tf.request.context.store]) == 0)
        
    def test_select_attribute_to_add(self):
        params = MultiDict({'pling_id':'pling_id_value',
                            'feedback_attribute[]':'deterrent',
                            'deterrent_value':'Cost',
                                                    'plingback_type':'automated_testing'})
        params.add('deterrent_value', 'Transport')
        params.add('feedback_attribute[]', 'rating')
        params.add('rating_value', '70')
        tf = self.configure_triple_factory('/api/plingbacks',
                                           params)
       
        tf.add_attribute('rating')
        self.failUnless(len([x for x in tf.request.context.store]) == 1)
        tf.remove_attribute('rating')
        tf.add_attribute()
        self.failUnless(len([x for x in tf.request.context.store]) == 3)
        
    def test_unknown_attribute(self):
        tf = self.configure_triple_factory('/api/plingbacks',
                                           {'pling_id':'pling_id_value',
                                            'feedback_attribute[]':'faux',
                                            'faux_value':'oddity',
                                            'plingback_type':'automated_testing'})

        tf.add_attribute()
        self.failUnless(len([x for x in tf.request.context.store]) == 0)
        
    def test_remove_unknown_attribute(self):
        tf = self.configure_triple_factory('/api/plingbacks',
                                           {'pling_id':'pling_id_value',
                                            'feedback_attribute[]':'faux',
                                            'faux_value':'oddity',
                                            'plingback_type':'automated_testing'})
        res = tf.remove_attribute()
        self.failUnless(isinstance(res, HTTPBadRequest))

