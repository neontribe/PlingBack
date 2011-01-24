
from pyramid.interfaces import IDebugLogger
from pyramid.httpexceptions import HTTPException, HTTPBadRequest, HTTPInternalServerError


from talis import Talis
from rdflib import Graph
from rdflib import BNode, Literal, URIRef, Namespace
import simplejson as json
import random
import urllib
import datetime

from plingback import namespaces as ns
from plingback.idgen import FeedbackIdManager
from plingback.triples import make_feedback_uri, TripleFactory
from webob.exc import HTTPUnauthorized

ID_POOL_SIZE = 20
ID_CANDIDATE_LIMIT = 3
MAX_ID_ATTEMPTS = 3

def set_trace():
 
    import pdb, sys
    sys.stdout = sys.__stdout__
    sys.stdin = sys.__stdin__
    debugger = pdb.Pdb()
    debugger.set_trace(sys._getframe().f_back)

                 

def create(request): #self, feedback_id=None, method=None):
    """POST /api/plingbacks: Create a new feedback node generating an id
        PUT /api/plingbacks/id: Create a new feedback node using id provided
        
        Get /jsapi/plingbacks"""
        
    feedback_id = None

    if request.method.lower() == 'get':
        mode = request.matchdict.get('method').upper()
        if mode not in ['POST', 'PUT']:
            return HTTPBadRequest(detail='To use the jsapi you must specify PUT or POST as the second path element')
        else:
            request.method = mode

    #Arbitrate between POST and PUT requests
    if request.method.lower() == 'post':
        id_mgr = FeedbackIdManager(request)
        feedback_id = id_mgr.get_unique_feedback_id()
        if not feedback_id:
            return HTTPInternalServerError(details='Failed to generate a unique feedback_id')
    elif request.method.lower() == 'put':
        feedback_id = request.matchdict.get('feedback_id', None)
        if not feedback_id:
            if request.params.get('feedback_id'):
                return HTTPBadRequest(detail='the feedback_id should form part of the uri')
            else:
                return HTTPBadRequest(detail='Missing feedback_id')
    
    
    tf = TripleFactory(request.context.store, request, feedback_id)
    #Build the feedback node into the local graph
    init = tf.init_feedback_node()
    # Propagate any exception NB: can we not find a way to 'raise' errors?
    if isinstance(init, HTTPException):
        return init
    # Add any feedbackdata that we can find in the request
    attrs = tf.add_attribute()
    if isinstance(attrs, HTTPException):
        return attrs
    
    # Commit the changes to the store
    store_result = request.context.store.sync()
    
    # We've done a create so add an appropriate Location header
    # and set the response code appropriately
    feedback_uri = tf.feedback_uri
    request.response_headerlist = [('Location',str(feedback_uri))]
    request.response_status = '201 Created'
    
    # Build a return json
    output = {'feedback_id': feedback_id,
              'feedback_uri': str(feedback_uri)}
    
    return output

def attribute_handler(request):
    overwrite = False
    if request.method.lower() == 'get':
        mode = request.matchdict.get('method')
        if mode not in ['POST', 'PUT']:
            return HTTPBadRequest(detail='To use the jsapi you must specify PUT or POST as the second path element')
        else:
            request.method = mode
    if request.method == 'PUT':
        overwrite = True
    
    tf = TripleFactory(request.context.store, request, request.matchdict.get('feedback_id'))            
    attrs = tf.add_attribute(overwrite=overwrite)
    if isinstance(attrs, HTTPException):
        return attrs   
        
    feedback_uri = tf.feedback_uri
    
    # Build a return json
    output = {'feedback_id': tf.feedback_id,
              'feedback_uri': str(feedback_uri)}
    
    return output
    

def delete(request):
    if request.registry.settings.get('enable_delete', False):
        tf = TripleFactory(request.context.store, request, request.matchdict.get('feedback_id', None))
        tf.remove_feedback_node()
        # Commit the changes to the store
        request.context.store.sync()
        
    else:
        return HTTPUnauthorized()
    
        

    

def show(self, feedback_id):
    """ Show the contents of the feedback node """
    return viewdata.feedback_js_graph(feedback_id)

