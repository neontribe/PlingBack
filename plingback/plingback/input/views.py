from pyramid.interfaces import IDebugLogger
from pyramid.httpexceptions import HTTPException, HTTPBadRequest, HTTPInternalServerError

from rdflib import BNode, Literal, URIRef, Namespace
import simplejson as json
import random
import urllib
import uuid
import datetime

from plingback.namespaces import namespaces as ns
from plingback.triples import make_feedback_uri, TripleFactory
from plingback.lib import set_trace
from webob.exc import HTTPUnauthorized

ID_POOL_SIZE = 20
ID_CANDIDATE_LIMIT = 3
MAX_ID_ATTEMPTS = 3                 

def create(request): #self, feedback_id=None, method=None):
    """POST /api/plingbacks: Create a new feedback node generating an id
        PUT /api/plingbacks/id: Create a new feedback node using id provided
        
        Get /jsapi/plingbacks"""
    # Bug out early if there's no indication of what the feedback's about
    if not request.params.get('pling_id'):
        return HTTPBadRequest(detail='the request should specify a pling_id')
    
    if request.method.lower() == 'get':
        mode = request.matchdict.get('method').upper()
        if mode not in ['POST', 'PUT']:
            return HTTPBadRequest(detail='To use the jsapi you must specify PUT or POST as the second path element')
        else:
            request.method = mode

    #Arbitrate between POST and PUT requests
    if request.method.lower() == 'post':
        # Generate a UUID
        feedback_id = str(uuid.uuid4())
    elif request.method.lower() == 'put':
        feedback_id = request.matchdict.get('feedback_id', None)
        if not feedback_id:
            if request.params.get('feedback_id'):
                return HTTPBadRequest(detail='the feedback_id should form part of the uri')
            else:
                return HTTPBadRequest(detail='Missing feedback_id')
    
    
    tf = TripleFactory(request, feedback_id)
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
    store_result = request.context.sync()
    
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
    
    tf = TripleFactory(request, request.matchdict.get('feedback_id'))            
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
        tf = TripleFactory(request, request.matchdict.get('feedback_id', None))
        tf.remove_feedback_node()
        # Commit the changes to the store
        request.context.sync()
        
    else:
        return HTTPUnauthorized()
    

def show(self, feedback_id):
    """ Show the contents of the feedback node """
    return viewdata.feedback_js_graph(feedback_id)

