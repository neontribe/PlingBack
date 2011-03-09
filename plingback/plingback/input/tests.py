import unittest
from webob.multidict import MultiDict
from pyramid.config import Configurator
from pyramid import testing
from pyramid.registry import Registry 
from pyramid.mako_templating import MakoLookupTemplateRenderer, renderer_factory as mako_renderer_factory

from plingback.resources import TripleStore
from plingback.input.views import *


class InputControllerTests(unittest.TestCase):
    use_jsapi = False
    
    def setUp(self):
        reg = Registry()
        reg.settings = {'store_type':'rdflib',
                        'debug_sparql':True}
        self.config = testing.setUp(reg)
        
        self.config.begin()

    def tearDown(self):
        testing.tearDown()
        
    def mock_request(self, path, params, method='GET', feedback_id=None):
        matchdict = {}
        if feedback_id:
            matchdict.update({'feedback_id':feedback_id})
            
        if not self.use_jsapi:
            request = testing.DummyRequest(path=path,
                                       params=MultiDict(params),
                                       post= (method=='POST') and params or None,
                                       method = method,
                                       matchdict = matchdict)
        else:
            matchdict.update({'method':method})
            jspath = path.split('/')
            jspath.insert(2, method.lower())
            jspath = '/'.join(jspath)
            request = testing.DummyRequest(path=jspath,
                                       params=MultiDict(params),
                                       method = 'GET',
                                       matchdict = matchdict)
        request.context = TripleStore(request)
        return request
    
    def mock_params(self, initial={}):
        initial.update({'pling_id':'5678',
                        'plingbackType':'automated_testing'})
        return initial
    
    def test_misplaced_feedback_id(self):
        params = self.mock_params({'feedback_id':'888999000'})
        request = self.mock_request('/api/plingbacks',
                                    params,
                                    'PUT')
        self.assertRaises(HTTPBadRequest, create, request)
        
    def test_missing_feedback_id(self):
        params = self.mock_params()
        request = self.mock_request('/api/plingbacks',
                                    params,
                                    'PUT')
        self.assertRaises(HTTPBadRequest, create, request)

    
    def test_create(self):
        params = self.mock_params()
        request = self.mock_request('/api/plingbacks',
                                    params,
                                    'POST')
        res = create(request)
        self.assertEqual(request.response_status, '201 Created')
        
    def test_create_missing_pling_id(self):
        params = self.mock_params()
        del params['pling_id']
        request = self.mock_request('/api/plingbacks',
                                    params,
                                    'POST')
        self.assertRaises(HTTPBadRequest, create, request)
        
    def test_put_attribute(self):
        params = self.mock_params({'feedback_attribute':'rating',
                                   'rating_value':'70'})
        request = self.mock_request('/api/plingbacks/888-999-111/rating',
                                    params,
                                    'PUT',
                                    '888-999-111')
        res = attribute_handler(request)
        self.failUnless('888-999-111' in str(res))
        
    def test_delete_attribute(self):
        self.config.add_settings({'enable_delete':True})
        params = self.mock_params({})
        request = self.mock_request('/api/plingbacks/999-999-111',
                                    params,
                                    'DELETE',
                                    '999-999-111')
        res = delete(request)
        self.failUnless(res.status == '204 No Content')
        
    def test_delete_disabled(self):
        params = self.mock_params({})
        request = self.mock_request('/api/plingbacks/999-999-111',
                                    params,
                                    'DELETE',
                                    '999-999-111')
        self.assertRaises(HTTPUnauthorized, delete, request)
        
class JSAPITests(InputControllerTests):
    """ Repeat all the input api test through the JSAPI layer"""
    
    use_jsapi = True
    
    def test_create_bad_method(self):
        params = self.mock_params()
        request = self.mock_request('/api/plingbacks',
                                    params,
                                    'HEAD')
        self.assertRaises(HTTPBadRequest, create, request)
    
    def test_attribute_bad_method(self):
        params = self.mock_params()
        request = self.mock_request('/api/plingbacks/888-999-111/rating',
                                    params,
                                    'HEAD')
        self.assertRaises(HTTPBadRequest, attribute_handler, request)

        
    