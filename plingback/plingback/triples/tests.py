import unittest
import rdflib
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
from plingback import namespaces as ns

class TripleFactoryTests(unittest.TestCase):
    def setUp(self):
        self.config = testing.setUp()
        self.config.begin()

    def tearDown(self):
        testing.tearDown()
        
    def test_init_feedback_node(self):
        graph = Graph()
        request = testing.DummyRequest(path='/api/plingbacks',
                                       params=MultiDict({'pling_id':'pling_id_value',
                                                    'plingback_type':'automated_testing'}))
        tf = TripleFactory(graph, request, 'feedback_id_value')
        tf.init_feedback_node()
        self.failUnless(len([x for x in graph]) == 4)
        
    def test_remove_feedback_node(self):
        graph = Graph()
        request = testing.DummyRequest(path='/api/plingbacks',
                                       params=MultiDict({'pling_id':'pling_id_value',
                                                    'plingback_type':'automated_testing'}))
        tf = TripleFactory(graph, request, 'feedback_id_value')
        tf.init_feedback_node()
        self.failUnless(len([x for x in graph]) == 4)
        tf.remove_feedback_node()
        self.assertEqual(len([x for x in graph]), 0)
        
    def test_missing_feedback_target(self):
        graph = Graph()
        request = testing.DummyRequest(path='/api/plingbacks',
                                       params=MultiDict({}))
        tf = TripleFactory(graph, request, 'feedback_id_value')
        res = tf.init_feedback_node()
        self.failUnless(isinstance(res, HTTPBadRequest))
        
    def test_init_feedback_node_with_version(self):
        graph = Graph()
        request = testing.DummyRequest(path='/api/plingbacks',
                                       params=MultiDict({'pling_id':'pling_id_value',
                                               'plingback_version':'Mk5a',
                                                    'plingback_type':'automated_testing'}))
        tf = TripleFactory(graph, request, 'feedback_id_value')
        tf.init_feedback_node()
        self.failUnless(len([x for x in graph]) == 5)
        self.failUnless('Mk5a' in [str(x[2]) for x in graph])
        
    def test_feedback_helper_base(self):
        fbh = FeedbackAttribute('id', {})
        self.failUnlessRaises(NotImplementedError, fbh.triples)
        self.failUnlessRaises(NotImplementedError, fbh.removal_query)
        
    def test_add_rating_attribute(self):
        graph = Graph()
        request = testing.DummyRequest(path='/api/plingbacks',
                                       params=MultiDict({'pling_id':'pling_id_value',
                                               'feedback_attribute':'rating',
                                               'rating_value':'70',
                                                    'plingback_type':'automated_testing'}))
        tf = TripleFactory(graph, request, 'feedback_id_value')
        tf.add_attribute()
        res = graph.query("SELECT ?val WHERE { ?pb <%s> ?val }" % (ns['REV']['rating']))
        self.failUnless(str([x for x in res][0]) == '70')
        self.failUnless(len([x for x in graph]) == 1)
    
    def test_bad_rating_attribute(self):
        graph = Graph()
        request = testing.DummyRequest(path='/api/plingbacks',
                                       params=MultiDict({'pling_id':'pling_id_value',
                                               'feedback_attribute':'rating',
                                               'rating_value':'NaN',
                                                    'plingback_type':'automated_testing'}))
        tf = TripleFactory(graph, request, 'feedback_id_value')
        res = tf.add_attribute()
        self.failUnless(isinstance(res, HTTPBadRequest))
        self.failUnless(len([x for x in graph]) == 0)
        
    def test_remove_rating_attribute(self):
        graph = Graph()
        request = testing.DummyRequest(path='/api/plingbacks',
                                       params=MultiDict({'pling_id':'pling_id_value',
                                               'feedback_attribute':'rating',
                                               'rating_value':'70',
                                                    'plingback_type':'automated_testing'}))
        tf = TripleFactory(graph, request, 'feedback_id_value')
        tf.add_attribute()
        self.failUnless(len([x for x in graph]) == 1)
        tf.remove_attribute('rating')
        self.failUnless(len([x for x in graph]) == 0)
        
    def test_overwrite_rating_attribute(self):
        graph = Graph()
        request = testing.DummyRequest(path='/api/plingbacks',
                                       params=MultiDict({'pling_id':'pling_id_value',
                                               'feedback_attribute':'rating',
                                               'rating_value':'70',
                                                    'plingback_type':'automated_testing'}))
        tf = TripleFactory(graph, request, 'feedback_id_value')
        tf.add_attribute()
        self.failUnless(len([x for x in graph]) == 1)
        res = graph.query("SELECT ?val WHERE { ?pb <%s> ?val }" % (ns['REV']['rating']))
        self.failUnless(str([x for x in res][0]) == '70')
        
        request2 = testing.DummyRequest(path='/api/plingbacks/feedback_id_value/rating',
                                       params=MultiDict({'pling_id':'pling_id_value',
                                               'feedback_attribute':'rating',
                                               'rating_value':'20',
                                                    'plingback_type':'automated_testing'}))
        tf = TripleFactory(graph, request2, 'feedback_id_value')
        tf.add_attribute(overwrite=True)
        self.failUnless(len([x for x in graph]) == 1)
        res = graph.query("SELECT ?val WHERE { ?pb <%s> ?val }" % (ns['REV']['rating']))
        self.failUnless(str([x for x in res][0]) == '20')
        
        
    def test_add_node_with_rating_attribute(self):
        graph = Graph()
        params = MultiDict({'pling_id':'pling_id_value',
                            'feedback_attribute':'rating',
                            'rating_value':'50',
                            'plingback_type':'automated_testing'})
        request = testing.DummyRequest(path='/api/plingbacks/feedback_id_value',
                                       params=params)
        tf = TripleFactory(graph, request, 'feedback_id_value')
        tf.init_feedback_node()
        tf.add_attribute()
        res = graph.query("SELECT ?val WHERE { <%s> <%s> ?val }" % (ns['PB']['feedback_id_value'], 
                                                                    ns['REV']['rating']))
        self.failUnless(str([x for x in res][0]) == '50')
        self.failUnless(len([x for x in graph]) == 5)
        
    def test_add_comment_attribute(self):
        graph = Graph()
        request = testing.DummyRequest(path='/api/plingbacks',
                                       params=MultiDict({'pling_id':'pling_id_value',
                                               'feedback_attribute':'comment',
                                               'comment_value':'test comment',
                                                    'plingback_type':'automated_testing'}))
        tf = TripleFactory(graph, request, 'feedback_id_value')
        tf.add_attribute()
        res = graph.query("SELECT ?val WHERE { ?pb <%s> ?val }" % (ns['REV']['text']))
        self.failUnless(str([x for x in res][0]) == 'test comment')
        self.failUnless(len([x for x in graph]) == 1)
        
    def test_remove_comment_attribute(self):
        graph = Graph()
        request = testing.DummyRequest(path='/api/plingbacks',
                                       params=MultiDict({'pling_id':'pling_id_value',
                                               'feedback_attribute':'comment',
                                               'comment_value':'test comment',
                                                    'plingback_type':'automated_testing'}))
        tf = TripleFactory(graph, request, 'feedback_id_value')
        tf.add_attribute()
        self.failUnless(len([x for x in graph]) == 1)
        tf.remove_attribute('comment')
        self.failUnless(len([x for x in graph]) == 0)
        
    def test_add_approval_attribute(self):
        graph = Graph()
        request = testing.DummyRequest(path='/api/plingbacks',
                                       params=MultiDict({'pling_id':'pling_id_value',
                                               'feedback_attribute':'approval',
                                               'approval_value':'10',
                                                    'plingback_type':'automated_testing'}))
        tf = TripleFactory(graph, request, 'feedback_id_value')
        tf.add_attribute()
        res = graph.query("SELECT ?val WHERE { ?pb <%s> ?val }" % (ns['PBO']['approval']))
        self.failUnless(str([x for x in res][0]) == '10')
        self.failUnless(len([x for x in graph]) == 1)
        
    def test_bad_approval_attribute(self):
        graph = Graph()
        request = testing.DummyRequest(path='/api/plingbacks',
                                       params=MultiDict({'pling_id':'pling_id_value',
                                               'feedback_attribute':'approval',
                                               'approval_value':'NaN',
                                                    'plingback_type':'automated_testing'}))
        tf = TripleFactory(graph, request, 'feedback_id_value')
        res = tf.add_attribute()
        self.failUnless(isinstance(res, HTTPBadRequest))
        self.failUnless(len([x for x in graph]) == 0)
        
    def test_remove_approval_attribute(self):
        graph = Graph()
        request = testing.DummyRequest(path='/api/plingbacks',
                                       params=MultiDict({'pling_id':'pling_id_value',
                                               'feedback_attribute':'approval',
                                               'approval_value':'10',
                                                    'plingback_type':'automated_testing'}))
        tf = TripleFactory(graph, request, 'feedback_id_value')
        tf.add_attribute()
        self.failUnless(len([x for x in graph]) == 1)
        tf.remove_attribute('approval')
        self.failUnless(len([x for x in graph]) == 0)
        
        
    def test_add_attendance_attribute(self):
        graph = Graph()
        request = testing.DummyRequest(path='/api/plingbacks',
                                       params=MultiDict({'pling_id':'pling_id_value',
                                               'feedback_attribute':'attendance',
                                               'attendance_value':'Attended',
                                                    'plingback_type':'automated_testing'}))
        tf = TripleFactory(graph, request, 'feedback_id_value')
        tf.add_attribute()
        res = graph.query("SELECT ?val WHERE { ?pb <%s> ?val }" % (ns['PBO']['attendance']))
        self.failUnless(str([x for x in res][0]) == str(ns['PBO']['Attended']))
        self.failUnless(len([x for x in graph]) == 1)
        
    def test_remove_attendance_attribute(self):
        graph = Graph()
        request = testing.DummyRequest(path='/api/plingbacks',
                                       params=MultiDict({'pling_id':'pling_id_value',
                                               'feedback_attribute[]':'attendance',
                                               'attendance_value':'Attended',
                                                    'plingback_type':'automated_testing'}))
        tf = TripleFactory(graph, request, 'feedback_id_value')
        tf.add_attribute()
        self.failUnless(len([x for x in graph]) == 1)
        tf.remove_attribute()
        self.failUnless(len([x for x in graph]) == 0)
        
    def test_add_deterrent_attribute(self):
        graph = Graph()
        request = testing.DummyRequest(path='/api/plingbacks',
                                       params=MultiDict({'pling_id':'pling_id_value',
                                               'feedback_attribute':'deterrent',
                                               'deterrent_value':'Cost',
                                                    'plingback_type':'automated_testing'}))
        tf = TripleFactory(graph, request, 'feedback_id_value')
        tf.add_attribute()
        res = graph.query("SELECT ?val WHERE { ?pb <%s> ?val }" % (ns['PBO']['deterrent']))

        self.failUnless('Cost' in [str(x) for x in res])
        self.failUnless(len([x for x in graph]) == 1)  
        
    def test_add_multiple_deterrent_attribute_with_js_list(self):
        graph = Graph()
        params = MultiDict({'pling_id':'pling_id_value',
                            'feedback_attribute':'deterrent',
                            'deterrent_value[]':'Cost',
                                                    'plingback_type':'automated_testing'})
        params.add('deterrent_value[]', 'Transport')
        request = testing.DummyRequest(path='/api/plingbacks',
                                       params=params)
        tf = TripleFactory(graph, request, 'feedback_id_value')
        tf.add_attribute()
        res = graph.query("SELECT ?val WHERE { ?pb <%s> ?val }" % (ns['PBO']['deterrent']))
        self.failUnless('Cost' in [str(x) for x in res])
        self.failUnless('Transport' in [str(x) for x in res])
        self.failUnless(len([x for x in graph]) == 2)
        
    def test_remove_multiple_deterrent_attributes(self):
        graph = Graph()
        params = MultiDict({'pling_id':'pling_id_value',
                            'feedback_attribute':'deterrent',
                            'deterrent_value':'Cost',
                                                    'plingback_type':'automated_testing'})
        params.add('deterrent_value', 'Transport')
        request = testing.DummyRequest(path='/api/plingbacks',
                                       params=params)
        tf = TripleFactory(graph, request, 'feedback_id_value')
        tf.add_attribute()
        self.failUnless(len([x for x in graph]) == 2)
        tf.remove_attribute('deterrent')
        self.failUnless(len([x for x in graph]) == 0)
        
    def test_add_reviewer_attribute(self):
        graph = Graph()
        params = MultiDict({'pling_id':'pling_id_value',
                            'feedback_attribute':'reviewer',
                            'reviewer_email':'test@example.com',
                            'reviewer_phone':'01603 727747',
                            'reviewer_birthday':'10/06/1971',
                            'reviewer_id':'sn_id',
                            'reviewer_id_source':'http://bebo.co.uk',
                                                    'plingback_type':'automated_testing'})
        request = testing.DummyRequest(path='/api/plingbacks',
                                       params=params)
        tf = TripleFactory(graph, request, 'feedback_id_value')
        tf.add_attribute()
        self.failUnless(len([x for x in graph]) == 9)
        
    def test_empty_reviewer_attribute(self):
        graph = Graph()
        params = MultiDict({'pling_id':'pling_id_value',
                            'feedback_attribute':'reviewer',
                                                    'plingback_type':'automated_testing'})
        request = testing.DummyRequest(path='/api/plingbacks',
                                       params=params)
        tf = TripleFactory(graph, request, 'feedback_id_value')
        tf.add_attribute()
        self.failUnless(len([x for x in graph]) == 0)
        
    def test_remove_reviewer_attribute(self):
        graph = Graph()
        params = MultiDict({'pling_id':'pling_id_value',
                            'feedback_attribute':'reviewer',
                            'reviewer_email':'test@example.com',
                            'reviewer_phone':'01603 727747',
                            'reviewer_birthday':'10/06/1971',
                            'reviewer_id':'sn_id',
                            'reviewer_id_source':'http://bebo.co.uk',
                                                    'plingback_type':'automated_testing'})
        request = testing.DummyRequest(path='/api/plingbacks',
                                       params=params)
        tf = TripleFactory(graph, request, 'feedback_id_value')
        tf.add_attribute()
        self.failUnless(len([x for x in graph]) == 9)
        tf.remove_attribute('reviewer')
        self.failUnless(len([x for x in graph]) == 0)
        
    def test_select_attribute_to_add(self):
        graph = Graph()
        params = MultiDict({'pling_id':'pling_id_value',
                            'feedback_attribute[]':'deterrent',
                            'deterrent_value':'Cost',
                                                    'plingback_type':'automated_testing'})
        params.add('deterrent_value', 'Transport')
        params.add('feedback_attribute[]', 'rating')
        params.add('rating_value', '70')
        request = testing.DummyRequest(path='/api/plingbacks',
                                       params=params)
        tf = TripleFactory(graph, request, 'feedback_id_value')
        tf.add_attribute('rating')
        self.failUnless(len([x for x in graph]) == 1)
        tf.remove_attribute('rating')
        tf.add_attribute()
        self.failUnless(len([x for x in graph]) == 3)
        
    def test_unknown_attribute(self):
        graph = Graph()
        params = MultiDict({'pling_id':'pling_id_value',
                            'feedback_attribute[]':'faux',
                            'faux_value':'oddity',
                                                    'plingback_type':'automated_testing'})
        
        request = testing.DummyRequest(path='/api/plingbacks',
                                       params=params)
        tf = TripleFactory(graph, request, 'feedback_id_value')
        tf.add_attribute()
        self.failUnless(len([x for x in graph]) == 0)
        
    def test_remove_unknown_attribute(self):
        graph = Graph()
        params = MultiDict({'pling_id':'pling_id_value',
                            'feedback_attribute[]':'faux',
                            'faux_value':'oddity',
                                                    'plingback_type':'automated_testing'})
        
        request = testing.DummyRequest(path='/api/plingbacks',
                                       params=params)
        tf = TripleFactory(graph, request, 'feedback_id_value')
        res = tf.remove_attribute()
        self.failUnless(isinstance(res, HTTPBadRequest))

