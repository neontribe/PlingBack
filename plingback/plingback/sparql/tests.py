import unittest

from pyramid.config import Configurator
from pyramid import testing
from pyramid.mako_templating import MakoLookupTemplateRenderer, renderer_factory as mako_renderer_factory

from plingback.sparql import SPARQLGenerator

class SPARQLTests(unittest.TestCase):
    def setUp(self):
        self.config = testing.setUp()
        self.config.add_settings({'mako.directories':'plingback.sparql:templates'})
        self.config.add_renderer(None, mako_renderer_factory)
        self.config.begin()

    def tearDown(self):
        testing.tearDown()


    def test_scoped_rating_attribute(self):       
        gen = SPARQLGenerator(query_template='scoped_ratings',
                              scope='authorities', 
                              id='33UF',
                              attribute='ratings')
        sparql = gen.sparql()
        self.failUnless("?pling pbo:la '33UF' ." in sparql, 'Pling Collector failure')
        self.failUnless("?plingback pbo:isAbout ?pling ." in sparql, 'Plingback Collector failure')
        self.failUnless("?plingback rev:rating ?item ." in sparql, "Item Collector Failure")
        
    def test_scoped_approval_attribute(self):       
        gen = SPARQLGenerator(query_template='scoped_approvals',
                              scope='LA', 
                              id='33UF',
                              attribute='approvals')
        sparql = gen.sparql()
        self.failUnless("?pling pbo:la '33UF' ." in sparql, 'Pling Collector failure')
        self.failUnless("?plingback pbo:isAbout ?pling ." in sparql, 'Plingback Collector failure')
        self.failUnless("?plingback pbo:approval ?inc ." in sparql, "Item Collector Failure")
        self.failUnless("?plingback pbo:plingBackType ?item ." in sparql, "Item Collector Failure")
        self.failUnless("GROUP BY ?item" in sparql, "Grouping Failure")
        
    def test_pling_rating_attribute(self):
        gen = SPARQLGenerator(query_template='pling_ratings',
                              scope='plings', 
                              id='12345',
                              attribute='ratings')
        sparql = gen.sparql()

        self.failUnless("?plingback pbo:isAbout <http://plings.net/a/12345> ." in sparql)
        self.failUnless("?plingback rev:rating ?item ." in sparql, "Item Collector Failure")
        
    def test_pling_comment_attribute(self):
        gen = SPARQLGenerator(query_template='pling_comments',
                              scope='plings', 
                              id='12345',
                              attribute='comments')
        sparql = gen.sparql()

        self.failUnless("?plingback pbo:isAbout <http://plings.net/a/12345> ." in sparql)
        self.failUnless("?plingback rev:text ?item ." in sparql, "Item Collector Failure")
        
    def test_pling_approval_attribute(self):
        gen = SPARQLGenerator(query_template='pling_approvals',
                              scope='plings', 
                              id='12345',
                              attribute='comments')
        sparql = gen.sparql()
        
        self.failUnless("?plingback pbo:isAbout <http://plings.net/a/12345> ." in sparql, 'Plingback Collector failure')
        self.failUnless("?plingback pbo:approval ?inc ." in sparql, "Item Collector Failure")
        self.failUnless("?plingback pbo:plingBackType ?item ." in sparql, "Item Collector Failure")
        self.failUnless("GROUP BY ?item" in sparql, "Grouping Failure")
        
        
    def test_limit(self):
        gen = SPARQLGenerator(query_template='scoped_comments',
                              scope='authorities', 
                              id='33UF',
                              attribute='comments',
                              limit=10)
        sparql = gen.sparql()
        self.failUnless('LIMIT 10' in sparql)
        
    def test_offset(self):
        gen = SPARQLGenerator(query_template='scoped_comments',
                              scope='authorities', 
                              id='33UF',
                              attribute='comments',
                              offset=5)
        sparql = gen.sparql()
        self.failUnless('OFFSET 5' in sparql)
        
    def test_activity_date_filter_from(self):
        gen = SPARQLGenerator(query_template='scoped_comments',
                              scope='authorities', 
                              id='33UF',
                              attribute='comments',
                              activity_dates=('2011-12-24', None))
        sparql = gen.sparql()
        self.failUnless('?pling pbo:starts ?start .' in sparql)
        self.failUnless('FILTER ( ?start > "2011-12-24T00:00:00Z"^^xsd:dateTime )' in sparql)
        
    def test_activity_date_filter_to(self):
        gen = SPARQLGenerator(query_template='scoped_comments',
                              scope='authorities', 
                              id='33UF',
                              attribute='comments',
                              activity_dates=(None, '2012-01-05'))
        sparql = gen.sparql()
        self.failUnless('?pling pbo:ends ?end .' in sparql)
        self.failUnless('FILTER ( ?end < "2012-01-05T00:00:00Z"^^xsd:dateTime )' in sparql)
        
    def test_activity_date_filter_from_to(self):
        gen = SPARQLGenerator(query_template='scoped_comments',
                              scope='authorities', 
                              id='33UF',
                              attribute='comments',
                              activity_dates=('2011-12-24', '2012-01-05'))
        sparql = gen.sparql()
        self.failUnless('?pling pbo:starts ?start .' in sparql)
        self.failUnless('?pling pbo:ends ?end .' in sparql)
        self.failUnless('?start > "2011-12-24T00:00:00Z"^^xsd:dateTime' in sparql)
        self.failUnless('?end < "2012-01-05T00:00:00Z"^^xsd:dateTime' in sparql)
        self.failUnless('&&' in sparql)
        
    def test_empty_activity_date_filter(self):
        gen = SPARQLGenerator(query_template='scoped_comments',
                              scope='authorities', 
                              id='33UF',
                              attribute='comments',
                              activity_dates=(None, None))
        sparql = gen.sparql()
        self.failUnless('xsd:dateTime' not in sparql)
        
    def test_None_activity_date_filter(self):
        gen = SPARQLGenerator(query_template='scoped_comments',
                              scope='authorities', 
                              id='33UF',
                              attribute='comments',
                              activity_dates=None)
        sparql = gen.sparql()
        self.failUnless('xsd:dateTime' not in sparql)
        
    def test_submission_date_filter_after(self):
        gen = SPARQLGenerator(query_template='scoped_comments',
                              scope='authorities', 
                              id='33UF',
                              attribute='comments',
                              submission_dates=('2011-12-24', None))
        sparql = gen.sparql()
        self.failUnless('?plingback dc:date ?submitted .' in sparql)
        self.failUnless('FILTER ( ?submitted > "2011-12-24T00:00:00Z"^^xsd:dateTime )' in sparql)
        
    def test_submission_date_filter_before(self):
        gen = SPARQLGenerator(query_template='scoped_comments',
                              scope='authorities', 
                              id='33UF',
                              attribute='comments',
                              submission_dates=(None, '2012-01-05'))
        sparql = gen.sparql()
        self.failUnless('?plingback dc:date ?submitted .' in sparql)
        self.failUnless('FILTER ( ?submitted < "2012-01-05T00:00:00Z"^^xsd:dateTime )' in sparql)
        
    def test_submission_date_filter_after_before(self):
        gen = SPARQLGenerator(query_template='scoped_comments',
                              scope='authorities', 
                              id='33UF',
                              attribute='comments',
                              submission_dates=('2011-12-24', '2012-01-05'))
        sparql = gen.sparql()
        self.failUnless('?plingback dc:date ?submitted .' in sparql)
        self.failUnless('?submitted > "2011-12-24T00:00:00Z"^^xsd:dateTime' in sparql)
        self.failUnless('?submitted < "2012-01-05T00:00:00Z"^^xsd:dateTime' in sparql)
        self.failUnless('&&' in sparql)
        
    def test_empty_submission_date_filter(self):
        gen = SPARQLGenerator(query_template='scoped_comments',
                              scope='authorities', 
                              id='33UF',
                              attribute='comments',
                              submission_dates=(None, None))
        sparql = gen.sparql()
        self.failUnless('xsd:dateTime' not in sparql)
        
    def test_None_submission_date_filter(self):
        gen = SPARQLGenerator(query_template='scoped_comments',
                              scope='authorities', 
                              id='33UF',
                              attribute='comments',
                              submission_dates=None)
        sparql = gen.sparql()
        self.failUnless('xsd:dateTime' not in sparql)
        
    ######### Test for the Count Sparql #############
    
    def test_count_feedback_for_scope(self):
        gen = SPARQLGenerator(query_template='scoped_plingback_count',
                              scope='authorities')
        sparql = gen.sparql()
        self.failUnless('SELECT ?group (COUNT(?plingback) as ?noOfFeedbacks)' in sparql)
        self.failUnless('?pling pbo:la ?group .'in sparql)
        self.failUnless('GROUP BY ?group' in sparql)
        
    def test_count_feedback_for_scope_and_id(self):
        gen = SPARQLGenerator(query_template='narrow_scoped_plingback_count',
                              scope='authorities',
                              id='33UF')
        sparql = gen.sparql()
        self.failUnless('SELECT (COUNT(?plingback) as ?noOfFeedbacks)' in sparql)
        self.failUnless("?pling pbo:la '33UF'" in sparql)
        
    def test_count_feedback_for_pling(self):
        gen = SPARQLGenerator(query_template='pling_plingback_count',
                              id='12345')
        sparql = gen.sparql()
        self.failUnless('SELECT (COUNT(?plingback) as ?noOfFeedbacks)' in sparql)
        self.failUnless("?plingback pbo:isAbout <http://plings.net/a/12345>" in sparql)

    