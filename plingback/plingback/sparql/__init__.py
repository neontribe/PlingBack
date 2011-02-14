from pyramid.renderers import render
from plingback.namespaces import namespaces

class SPARQLGenerator(object):
    
    # Translate between scope variables (like the ones we might find in the url path) and the predicates
    # in the PlingBack Ontology
    # 'plings' is None because we're looking for feedback about a single item
    scope_to_predicate = {'authorities':'la',
                          'LA':'la',
                          'plings':None,
                          'wards':'ward',
                          'ward':'ward',
                          'venues':'venue',
                          'v':'venue',
                          'providers':'provider',
                          'o':'provider',
                          'uk':'pling'
                         }
    
    def __init__(self,
                 query_template,
                 scope=None,
                 id=None,
                 attribute=None,
                 activity_dates=None,
                 submission_dates=None,
                 limit=None,
                 offset=None):
        
        self.query_template = query_template
        self.scope = self.scope_to_predicate.get(scope, None)
        self.id = id
        self.attribute = attribute
        self.activity_dates = activity_dates
        self.submission_dates = submission_dates
        self.limit = limit
        self.offset = offset
        
        
        
    def _sparql_config(self):
        """ Returns a dictionary of values of use to one of the provided sparql templates """
        return {'namespaces': namespaces,
                'sparql': self
                }
        
    def activity_date_filter(self):
        date_filter = ''
        if self.activity_dates: 
            start_date = self.activity_dates[0]
            end_date = self.activity_dates[1]
            if start_date or end_date:
                date_collector = ''
                date_filter_wrapper = 'FILTER (%s) '
                filter = ''
                if start_date:
                    date_collector += '?pling pbo:starts ?start . '
                    filter += ' ?start > "%sT00:00:00Z"^^xsd:dateTime ' % (start_date)
                    if end_date:
                        filter += '&&'
                if end_date:
                    date_collector += '?pling pbo:ends ?end .'
                    filter += ' ?end < "%sT00:00:00Z"^^xsd:dateTime ' % (end_date)
                date_filter += date_collector
                date_filter += date_filter_wrapper % (filter)
        return date_filter
    
    def submission_date_filter(self):
        date_filter = ''
        if self.submission_dates: 
            after_date = self.submission_dates[0]
            before_date = self.submission_dates[1]
            if after_date or before_date:
                date_collector = '?plingback dc:date ?submitted .'
                date_filter_wrapper = ' FILTER (%s) '
                filter = ''
                if after_date:
                    filter += ' ?submitted > "%sT00:00:00Z"^^xsd:dateTime ' % (after_date)
                    if before_date:
                        filter += '&&'
                if before_date:
                    filter += ' ?submitted < "%sT00:00:00Z"^^xsd:dateTime ' % (before_date)
                date_filter += date_collector
                date_filter += date_filter_wrapper % (filter)
        return date_filter
        
    def sparql(self):
        res = render('plingback.sparql:templates/%s.mak' % (self.query_template), self._sparql_config())   
        return res
