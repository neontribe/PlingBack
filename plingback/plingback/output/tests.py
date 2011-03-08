import unittest
from pyramid.registry import Registry 
from pyramid.config import Configurator
from pyramid import testing
from pyramid.mako_templating import MakoLookupTemplateRenderer, renderer_factory as mako_renderer_factory
from webob.multidict import MultiDict
from rdflib import Literal, URIRef
from plingback.resources import TripleStore
from plingback.output.formatter import ResultFormatter
from plingback.output.views import handler

class MockSPARQLGenerator(object):
    def __init__(self,
                 scope=None,
                 id=None,
                 attribute=None,
                 activity_dates=None,
                 submission_dates=None,
                 limit=None,
                 offset=None):
        self.scope = scope
        self.id = id
        self.attribute = attribute
        self.activity_dates = activity_dates
        self.submission_dates = submission_dates
        self.limit = limit
        self.offset = offset

class ResultFormatterTests(unittest.TestCase):
    def setUp(self):
        self.config = testing.setUp()
        self.config.begin()

    def tearDown(self):
        testing.tearDown()

    def test_rating_output(self):       
        gen = MockSPARQLGenerator(scope='authorities', 
                              id='33UF',
                              attribute='ratings')
        data = [[Literal(60)],[Literal("duff data")]]
        rf = ResultFormatter(data, gen).format()
        self.failUnless(rf['results']['count'] == 1)
        self.failUnless(rf['results']['median'] == 60)
        
    def test_approval_output(self):       
        gen = MockSPARQLGenerator(scope='authorities', 
                              id='33UF',
                              attribute='approvals')
        data = [[Literal("busted"), URIRef("http://plingback.plings.net/applications/addthis-")],
                [Literal(51), URIRef("http://plingback.plings.net/applications/FBLike")]]
        rf = ResultFormatter(data, gen).format()
        self.failUnless(rf['results']['approvals']["http://plingback.plings.net/applications/FBLike"] == 51)
        
    def test_comment_output(self):       
        gen = MockSPARQLGenerator(scope='authorities', 
                              id='33UF',
                              attribute='comments')
        data = [[Literal("A test comment"), URIRef("http://plings.net/a/452820")],
                [Literal(" "), URIRef("http://plings.net/a/452820")]]
                    
        rf = ResultFormatter(data, gen).format()
        self.failUnless(rf['results']['count'] == 2)
        
    def test_scoped_count_output(self):       
        gen = MockSPARQLGenerator(scope='authorities')
        data = [[Literal("00FY"), Literal(629)],[Literal("00EJ"), Literal(602)]]                  
        rf = ResultFormatter(data, gen).format()
        self.failUnless(rf['totalFeedbackCount'] == 1231)
        
    def test_scoped_id_count_output(self):       
        gen = MockSPARQLGenerator(scope='authorities', id='33UF')
        data = [[Literal(160)]]                    
        rf = ResultFormatter(data, gen).format()
        self.failUnless(rf['totalFeedbackCount'] == 160)
        self.failUnless(rf['queryScope'] == 'authorities')
        self.failUnless(rf['id'] == '33UF')
        
    def test_no_sparql_output(self):
        data = [[Literal(160)]]          
        rf = ResultFormatter(data).format()
        self.failUnless(rf == data)
        
        
class OutputViewTest(unittest.TestCase):   
    def setUp(self):

        self.config = testing.setUp()
        self.config.add_settings({'mako.directories':'plingback.sparql:templates',
                                  'store_type':'rdflib',
                                  'debug_sparql':False})
        self.config.begin()

    def tearDown(self):
        testing.tearDown()
    
    def test_excercise_view(self):
        class MatchedRoute:
            name = 'scoped_attribute'
        
        request = testing.DummyRequest(path='/api/authorities/33UF/ratings',
                                       params={},
                                       matched_route = MatchedRoute(),
                                       matchdict = {'id':'33UF', 'scope':'authorities','attribute':'ratings'})
        request.context = TripleStore(request)
        res = handler(request)
        self.failUnless('33UF' in str(res))
        
        
   