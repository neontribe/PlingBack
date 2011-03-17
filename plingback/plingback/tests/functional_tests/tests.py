import unittest
import simplejson as json
from pyramid.httpexceptions import *
import time

# In order to limit pollution of the store we'll work with a fixed feedback id throughout the tests
import uuid
#FB_ID = uuid.uuid4()
FB_ID = 'testing-node-1'
P_ID = '452820'

class FunctionalTests(unittest.TestCase):
    """ Test that everything works as expected when interacting with a real talis store """
    def setUp(self):
        from plingback import main
        app = main({}, **({'store_type':'talis',
                           'talis_store':'plings-dev2',
                           'talis_user':'plings',
                           'talis_password':'ck6sjkfp',
                           'debug_sparql':False,
                            'enable_delete':True,
                            'root_url':'http://testing.com',
                            'mako.directories':'plingback:templates'}))
        from webtest import TestApp
        self.testapp = TestApp(app)
        # Check we're clear of leftover data
        #self.testapp.get('/views/plingbacks/%s.html' % FB_ID, status=404)
        
        
    def tearDown(self):
        #self.testapp.delete('/api/plingbacks/%s' % FB_ID, status=204)
        pass
        
        
    
    
    ##### GENERAL SETUP TESTS #####
    def test_index_view(self):
        res = self.testapp.get('/')
        res.mustcontain('http://testing.com')

    def test_input_bare_post(self):
        """ Posts without a feedback target identifier should fail"""
        self.assertRaises(HTTPBadRequest, self.testapp.post, '/api/plingbacks', {})
        
    def test_input_bare_put(self):
        """ Puts without a feedback target identifier should fail"""
        self.assertRaises(HTTPBadRequest, self.testapp.put, '/api/plingbacks/unique_id', {})
        
    def test_put_view_delete(self):
        #Create a feedback node
        res = self.testapp.put('/api/plingbacks/%s' % FB_ID, {'pling_id':P_ID,
                                                    'plingback_type':'automated_testing'})
        self.failUnless(res.status == '201 Created')
        self.failUnless(res.headers.has_key('Location'))
        self.failUnless('application/json' in res.headers['Content-Type'])
        # View it to check that it's been instantiated
        res = self.testapp.get('/views/plingbacks/%s.html' % FB_ID)
        # Delete it
        res = self.testapp.delete('/api/plingbacks/%s' % FB_ID)
        self.assertEqual(res.status, '204 No Content')   
        # Check that it has gone
        self.testapp.get('/views/plingbacks/%s.html' % FB_ID, status=404)
        
    def teest_put_rating(self):
        res = self.testapp.put('/api/plingbacks/%s' % FB_ID, {'pling_id':P_ID,
                                                    'feedback_attribute':'rating',
                                                    'rating_value':'30',
                                                    'plingback_type':'automated_testing'})
        self.failUnless(res.status == '201 Created')
        self.failUnless(res.headers.has_key('Location'))
        self.failUnless('application/json' in res.headers['Content-Type'])
        # Check output
        data = self.testapp.get('/api/plings/%s/ratings' % P_ID)
        obj = json.loads(data.body)
        self.assertEqual(obj['results']['mean'] == 30.0)
        
    
    #===========================================================================
    #      
    #    
    # def test_input_post_rating(self):
    #    res = self.testapp.post('/api/plingbacks', {'pling_id':'1019868',
    #                                                'feedback_attribute':'rating',
    #                                                'rating_value':'70',
    #                                                'plingback_type':'automated_testing'})
    #    self.failUnless(res.status == '201 Created')
    #    self.failUnless(res.headers.has_key('Location'))
    #    self.failUnless('application/json' in res.headers['Content-Type'])
    #    
    # def test_put_rating(self):
    #    res = self.testapp.put('/api/plingbacks/my_feedback_1', {'pling_id':'1019868',
    #                                                'feedback_attribute':'rating',
    #                                                'rating_value':'30',
    #                                                'plingback_type':'automated_testing'})
    #    self.failUnless(res.status == '201 Created')
    #    self.failUnless(res.headers.has_key('Location'))
    #    self.failUnless('application/json' in res.headers['Content-Type'])
    #    
    # def test_overwrite_rating(self):
    #    res = self.testapp.put('/api/plingbacks/my_feedback_1/rating', {'pling_id':'1019868',
    #                                                'feedback_attribute':'rating',
    #                                                'rating_value':'60',
    #                                                'plingback_type':'automated_testing'})
    #    
    #    self.failUnless('application/json' in res.headers['Content-Type'])
    #    
    # def test_view_feedback_node(self):
    #    res = self.testapp.get('/views/plingbacks/my_feedback_1.html')
    #    res.mustcontain('http://plingback.plings.net/pb/my_feedback_1-http://plingback.plings.net/ontologies/plingback#isAbout/http://plings.net/a/1019868')
    #    
    # def test_delete_feedback_node(self):
    #    res = self.testapp.delete('/api/plingbacks/my_feedback_1')
    #    self.assertEqual(res.status, '204 No Content')
    #    self.testapp.get('/views/plingbacks/my_feedback_1.html', status=404)
    #    
    # 
    # def test_add_activity_uris(self):
    #    """ Run it twice - the second should be empty """
    #    res = self.testapp.get('/augmentations/add_activity_nodes')
    #    self.failUnless('application/json' in res.headers['Content-Type'])
    #    self.assertEqual(res.status, '200 OK')
    #    res2 = self.testapp.get('/augmentations/add_activity_nodes')
    #    res2.mustcontain('[]')
    #    
    # def test_add_activity_data(self):
    #    pass
    #    #res = self.testapp.get('/augmentations/add_activity_data')
    #    #self.failUnless('application/json' in res.headers['Content-Type'])
    #    #res.mustcontain('1019868') # Working on the activity we expect?
    #    #res.mustcontain('00EQMX') # Got the right ward?
    #    
    # def test_unaugmented_post_rating(self):
    #    pass
    #    #res = self.testapp.post('/api/plingbacks', {'pling_id':'54678',
    #    #                                            'feedback_attribute':'rating',
    #    #                                            'rating_value':'10',
    #    #                                            'plingback_type':'automated_testing'})
    #    #self.failUnless(res.status == '201 Created')
    #    #self.failUnless(res.headers.has_key('Location'))
    #    #self.failUnless('application/json' in res.headers['Content-Type'])
    #    
    #===========================================================================
