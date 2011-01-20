from pyramid.renderers import render
from plingback import namespaces


class SPARQLFragments(object):

    def __init__(self, generator):
        self.generator = generator
        self.attribute = self.generator.attribute
        
        # Translate between scope variables (like the ones we might find in the url path) and the predicates
        # in the PlingBack Ontology
        # 'plings' is None because we're looking for feedback about a single item
        self.scope_to_predicates = {'authorities':'la',
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
        
        self.fragments = {'ratings':{'item_finder':"?plingback rev:rating ?item ."},
                          'comments':{'item_finder':"?plingback rev:text ?item .",
                                 'select' : "?item ?pling"},
                          'approvals':{'item_finder':"?plingback pbo:approval ?inc . ?plingback pbo:plingBackType ?item .",
                                  'select':"?item (COUNT(?inc) AS ?count)",
                                  'group': "GROUP BY ?item"},
                          'count': {'collector':self.generator.id \
                                        and "?pling pbo:%s '%s' ." % (self.scope_to_predicates.get(self.generator.scope), 
                                                                 self.generator.id) \
                                        or '?pling pbo:%s ?group .' % (self.scope_to_predicates.get(self.generator.scope))
                                    }
                    }
        
        self.defaults = {'select':'?item',
                    'group':'',
                    'item_finder':'?plingback pbo:plingBackType ?item',
                    'limit': self.generator.limit and 'LIMIT %s' % (self.generator.limit) or '',
                    'is_about':self.scope_to_predicates.get(self.generator.scope, None) \
                                    and "?pling" or '<%s>' % (self.generator.id),
                    'collector':self.scope_to_predicates.get(self.generator.scope, None) \
                                    and "?pling pbo:%s '%s' ." % (self.scope_to_predicates.get(self.generator.scope), 
                                                                 self.generator.id) \
                                    or '',
                    'offset':self.generator.offset and 'OFFSET %s' % (self.generator.offset) or '',
                    'activity_date_filter': self._activity_date_filter(),
                    'submission_date_filter': self._submission_date_filter()
                    }
    
    def _activity_date_filter(self):
        date_filter = ''
        if self.generator.activity_dates: 
            start_date = self.generator.activity_dates[0]
            end_date = self.generator.activity_dates[1]
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
    
    def _submission_date_filter(self):
        date_filter = ''
        if self.generator.submission_dates: 
            after_date = self.generator.submission_dates[0]
            before_date = self.generator.submission_dates[1]
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
    
        
    def get(self, fragment_name):
        # Pick out an item from self.fragments or pick up a default
        return self.fragments[self.attribute and self.attribute or 'count'].get(fragment_name, self.defaults.get(fragment_name, ''))


class SPARQLGenerator(object):
    
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
        
        self.fragments = SPARQLFragments(self)
        
    def _sparql_config(self):
        """ Returns a dictionary of values of use to one of the provided sparql templates """
        return {'namespaces': namespaces,
                'sparql': self.fragments
                }
        
    def sparql(self):
        # Arbitrate between different templates
        # got an attribute? use the scoped attribute template, other wise count feedback for the scope
        if self.attribute:
            res = render('plingback.sparql:templates/scoped_attribute.mak', self._sparql_config())
        else:
            res = render('plingback.sparql:templates/count_for_scope.mak', self._sparql_config())
            
        return res
