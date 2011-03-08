import unittest
import simplejson as json

class FunctionalTests(unittest.TestCase):
    def setUp(self):
        from plingback import main
        app = main({}, **({'store_type':'rdflib',
                           'debug_sparql':False,
                            'enable_delete':True}))
        from webtest import TestApp
        self.testapp = TestApp(app)

    def test_input_bare_post(self):
        """ Posts without a feedback target identifier should fail"""
        res = self.testapp.post('/api/plingbacks', {}, status=400)
        
        
    def test_input_bare_put(self):
        """ Puts without a feedback target identifier should fail"""
        res = self.testapp.put('/api/plingbacks/unique_id', {}, status=400)
        
        
    def test_input_post(self):
        res = self.testapp.post('/api/plingbacks', {'pling_id':'1019868',
                                                    'plingback_type':'automated_testing'})
        self.failUnless(res.status == '201 Created')
        self.failUnless(res.headers.has_key('Location'))
        self.failUnless('application/json' in res.headers['Content-Type'])
        
    def test_put_and_delete(self):
        res = self.testapp.put('/api/plingbacks/test_id_3', {'pling_id':'1019868',
                                                    'plingback_type':'automated_testing'})
        self.failUnless(res.status == '201 Created')
        self.failUnless(res.headers.has_key('Location'))
        self.failUnless('application/json' in res.headers['Content-Type'])
        res = self.testapp.delete('/api/plingbacks/test_id_3')
        self.assertEqual(res.status, '200 OK')
        
    def test_input_post_rating(self):
        res = self.testapp.post('/api/plingbacks', {'pling_id':'1019868',
                                                    'feedback_attribute':'rating',
                                                    'rating_value':'70',
                                                    'plingback_type':'automated_testing'})
        self.failUnless(res.status == '201 Created')
        self.failUnless(res.headers.has_key('Location'))
        self.failUnless('application/json' in res.headers['Content-Type'])
        
    def test_put_rating(self):
        res = self.testapp.put('/api/plingbacks/my_feedback_1', {'pling_id':'1019868',
                                                    'feedback_attribute':'rating',
                                                    'rating_value':'30',
                                                    'plingback_type':'automated_testing'})
        self.failUnless(res.status == '201 Created')
        self.failUnless(res.headers.has_key('Location'))
        self.failUnless('application/json' in res.headers['Content-Type'])
        
    def test_overwrite_rating(self):
        res = self.testapp.put('/api/plingbacks/my_feedback_1/rating', {'pling_id':'1019868',
                                                    'feedback_attribute':'rating',
                                                    'rating_value':'60',
                                                    'plingback_type':'automated_testing'})
        
        self.failUnless('application/json' in res.headers['Content-Type'])
        
    def test_add_activity_uris(self):
        """ Run it twice - the second should be empty """
        res = self.testapp.get('/augmentations/add_activity_nodes')
        self.failUnless('application/json' in res.headers['Content-Type'])
        self.assertEqual(res.status, '200 OK')
        res2 = self.testapp.get('/augmentations/add_activity_nodes')
        res2.mustcontain('[]')
        
    def test_add_activity_data(self):
        pass
        #res = self.testapp.get('/augmentations/add_activity_data')
        #self.failUnless('application/json' in res.headers['Content-Type'])
        #res.mustcontain('1019868') # Working on the activity we expect?
        #res.mustcontain('00EQMX') # Got the right ward?
        
    def test_unaugmented_post_rating(self):
        pass
        #res = self.testapp.post('/api/plingbacks', {'pling_id':'54678',
        #                                            'feedback_attribute':'rating',
        #                                            'rating_value':'10',
        #                                            'plingback_type':'automated_testing'})
        #self.failUnless(res.status == '201 Created')
        #self.failUnless(res.headers.has_key('Location'))
        #self.failUnless('application/json' in res.headers['Content-Type'])
        
