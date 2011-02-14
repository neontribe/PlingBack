from rdflib import BNode, Literal, URIRef, Namespace
from plingback import namespaces as ns
import urllib2
import xml.etree.ElementTree as etree
import datetime

class ActivityAugmenter(object):
    target_augmentation_version = 1
    
    def __init__(self, request):
        self.request = request
        self.context = self.request.root
        self.sparql_endpoint = self.request.root.query
        
        # A map of the attributes we wish to add
        # The key is the name used by the PB obtology
        # THe dict contains:
        # The xpath used to get the value from the pling xml
        # A function to cast the data into a desired type
        self.attribute_map = {'la':{'xpath':'activity/venue/LA/LACode',
                           'cast':str},
                     'ward':{'xpath':'activity/venue/Ward/WardCode',
                           'cast':str},
                     'provider':{'xpath':'activity/provider',
                           'cast':str,
                           'attribute':'id'},
                     'venue':{'xpath':'activity/venue',
                           'cast':str,
                           'attribute':'id'},
                     'starts':{'xpath':'activity/Starts',
                           'cast':self._pling_time_to_datetime},
                     'ends':{'xpath':'activity/Ends',
                           'cast':self._pling_time_to_datetime}}
        
    def add_activity_nodes(self):
        query = """
        PREFIX pbo: <http://plingback.plings.net/ontologies/plingback#>
        SELECT DISTINCT ?pling
        WHERE {
           ?plingback pbo:isAbout ?pling .
           OPTIONAL { ?pling ?pred pbo:Activity }
           FILTER ( !bound( ?pred ) )

        } LIMIT 10
        """

        activities = self.sparql_endpoint(query)
        added = []
        for activity in activities:
            pling_uri = activity[0]
            self.store.add((pling_uri, ns['RDF']['type'], ns['PBO']['Activity']))
            added.append(pling_uri)
            
        self.context.sync()
        
        return {'augmentation':'add_activity_nodes',
                'uris_updated':added}
        
    
    def _extract_text_or_attr(self, element, xpath, attr_name=None):
        target = element.find(xpath)
        if not attr_name:
            return target.text
        else:
            return target.attrib[attr_name]
        
    def _pling_time_to_datetime(self, data):
        return datetime.datetime.strptime(data, '%Y-%m-%d %H:%M:%S')
        
    def add_activity_data(self):
        # get all plings referred to by plingbacks
        # only return those which don't have an upto date augmentation version
        # Omit those which have a plingFetchError at 404 unless retry_previous_failures

        query = """
        PREFIX pb: <http://plingback.plings.net/ontologies/plingback#>
        PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
        DESCRIBE ?pling
        WHERE {
           ?pling rdf:type pb:Activity .
           OPTIONAL { ?pling pb:augmentation_version ?aug_version }
           FILTER ( !bound(?aug_version) || ?aug_version < %s )

        } LIMIT 1
        """ % (self.target_augmentation_version)
        
        activities = self.sparql_endpoint(query)
        
        triples = []
        for activity in activities:
            activity_id = str(activity[0]).split('/')[-1] 

            #get pling information from rest API
            url = "http://feeds.plings.net/activity.php/%s.xml"
            url += "?APIKey=82EF494E-CB2BC8C1-CA025AEC-1A9394F0-25095SWK-L"
            url += "&suppressLinkedActivities=1"
            url = url % (activity_id)
            
            tree = None
            error = None
            try:
                res = urllib2.urlopen(url)
                #pling_xml = plingfile.read()
                #get la code from xml
                tree = etree.parse(res)
                  
            except urllib2.URLError, e:
                #log.debug('API fetch for pling id %s failed with error %s' % (pling_id, str(e)))
                #log.debug('Marking pling id %s with error code %s' % (pling_id, str(e)))
                error = e
                
 
                
            #add missing data to the pling feedback triple
            if tree:
                triples.append((URIRef(activity[0]), ns['PBO']['augmentation_version'], Literal(self.target_augmentation_version)))
                for attr in self.attribute_map.items():
                    if not activity[1].get(str(ns['PBO'][attr[0]]), None):
                        raw = self._extract_text_or_attr(tree.getroot(), attr[1]['xpath'], attr[1].get('attribute', None))
                        data = attr[1]['cast'](raw)
                        triples.append((URIRef(activity[0]), ns['PBO'][attr[0]], Literal(data)))
                
            if isinstance(error, urllib2.HTTPError):
                triples.append((URIRef('http://plings.net/a/'+activity_id), ns['PBO']['plingFetchError'], Literal(error.code)))
        
        
        for triple in triples:
            self.store.add(triple)
                     
        try:
            self.store.sync()
        except urllib2.HTTPError, e:
            if e.code == 202:
                pass
            else:
                raise
                  
        return str(triples)
        
        
        #return targets
        
    
        
        
    
        
        