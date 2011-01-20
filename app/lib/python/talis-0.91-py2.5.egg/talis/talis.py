###
### This is Free Software
###
### Copyright (c) 2009 Open Knowledge Foundation
###
### Permission is hereby granted, free of charge, to any person obtaining a copy of
### this software and associated documentation files (the "Software"), to deal in
### the Software without restriction, including without limitation the rights to
### use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies
### of the Software, and to permit persons to whom the Software is furnished to do
### so, subject to the following conditions:
### 
### The above copyright notice and this permission notice shall be included in all
### copies or substantial portions of the Software.
### 
### THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
### IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
### FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
### AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
### LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
### OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
### SOFTWARE.
###

import urllib
import urllib2
import logging
import traceback
from datetime import datetime

from rdflib import ConjunctiveGraph as Graph
from rdflib import BNode, URIRef, Literal, Namespace, RDF
import uuid

try:
	from etree import ElementTree
except ImportError:
	from elementtree import ElementTree

__all__ = ['Talis']

USER_AGENT = 'CKAN-RDF 1.0'

#RDF = Namespace('http://www.w3.org/1999/02/22-rdf-syntax-ns#')
CS = Namespace('http://purl.org/vocab/changeset/schema#')
DC = Namespace('http://purl.org/dc/terms/')

class Talis(object):
	"""
	Interface for the Talis triplestore.

	Initialisation can take optional username and password which
	are used for operations on the triplestore (such as storing
	data) that require authentication.

	Initialisation may take a versioned keyword which defaults to
	false. If true, this enables the use of versioned changesets.

	This class makes extensive use of the Python logging facility.
	Be aware that enabling the DEBUG logging level will generate
	copious output of all data exchanged with the triplestore 
	server.

	>>> t = Talis("ckan-dev1")
	>>> q = "SELECT * WHERE { <http://irl.styx.org/> <http://purl.org/dc/terms/title> ?o }"
	>>> for title, in t.query(q):
	...     print repr(title)
	...
	rdflib.Literal(u'Idiosyntactix Research Laboratories')
	>>>
	"""
	def __init__(self, store, username=None, password=None, versioned=False):
		self.urlbase = "http://api.talis.com/stores/%s" % (store,)
		self.username = username
		self.password = password
		self.versioned = versioned
		self.log = logging.getLogger("talis[%s]" % (store,))
		self._changesets = {}

	def __del__(self):
		## make sure to flush any unsaved changes
		self.sync()

	def add(self, statement):
		"""
		Add a statement to the triplestore
		"""
		s,p,o = statement
		changes = self._changesets.get(s, [])
		changes.append(["addition", p, o])
		self._changesets[s] = changes
	def remove(self, statement):
		"""
		Remove a statement from the triplestore
		"""
		s,p,o = statement
		changes = self._changesets.get(s, [])
		changes.append(["removal", p, o])
		self._changesets[s] = changes

	def changesets(self):
		"""
		Return an RDF serialized representation of the current changes
		in the buffer, and empty the buffer.
		"""
		if not self._changesets:
			return
		g = Graph()
		last = None
		for s in self._changesets:
			### Create the changeset for this subject, with a unique ID
			csuuid = uuid.uuid3(uuid.NAMESPACE_OID, "%s/%s" % (
				str(s),
				datetime.now().strftime("%s")
			))
			csuri = BNode()
			g.add((csuri, RDF.type, CS["ChangeSet"]))
			g.add((csuri, CS["subjectOfChange"], s))
			g.add((csuri, CS["createdDate"], Literal(datetime.now())))
			g.add((csuri, CS["creatorName"], Literal(USER_AGENT)))
			g.add((csuri, CS["changeReason"], Literal("Auto-Generated %s" % csuuid)))
			### If we are storing version information we need to link the changes
			if self.versioned:
				if last:
					g.add((csuri, CS["preceedingChangeSet"], last))
				last = csuri
			for op, p, o in self._changesets[s]:
				opnode = BNode()
				g.add((csuri, CS[op], opnode))
				g.add((opnode, RDF.type, RDF.Statement))
				g.add((opnode, RDF.subject, s))
				g.add((opnode, RDF.predicate, p))
				g.add((opnode, RDF.object, o))
		self._changesets = {}
		return g.serialize()

	def sync(self):
		"""
		Upload any queued changesets.
		"""
		data = self.changesets()
		if not data:
			return ## nothing to do
		content_type = 'application/vnd.talis.changeset+xml'
		if self.versioned:
			path = "/meta/changesets"
		else:
			path = "/meta"
		self.upload(data, path=path, content_type=content_type)

	def upload(self, data, path="/meta", content_type='application/rdf+xml'):
		"""
		Upload the given rdf datat to the triplestore.
		This generally requires a username and password
		to have been set.
		"""
		###
		### build the authenticator
		###
		if self.username and self.password:
			# create a password manager
			password_mgr = urllib2.HTTPPasswordMgrWithDefaultRealm()
			# Add the username and password.
			# If we knew the realm, we could use it instead of ``None``.
			password_mgr.add_password(None, self.urlbase, self.username, self.password)
			handler = urllib2.HTTPDigestAuthHandler(password_mgr)
			# create "opener" (OpenerDirector instance)
			urlopen = urllib2.build_opener(handler).open
		else:
			urlopen = urllib2.urlopen

		url = self.urlbase + path
		headers = {
			'User-Agent' : USER_AGENT,
			'Content-Type' : content_type
		}
		self.log.info("POST %d bytes %s to %s" % (len(data), content_type, url))
		self.log.debug("DATA:\n%s" % (data,))
		req = urllib2.Request(url, data, headers)
		try:
			t0 = datetime.now()
			fp = urlopen(req)
			response = fp.read()
			fp.close()
			t1 = datetime.now()
			seconds = int(t1.strftime("%s"))-int(t0.strftime("%s"))
			if seconds: bps = float(len(data))/seconds
			else: bps = 1000000000
			self.log.info("POST completed [200] in %ss (%.02fbps)" % (t1-t0, bps))
		except urllib2.HTTPError, e:
			if e.code in (201, 204):
				###
				### successful posts can return 204, urllib2 treats this as an error
				###
				t1 = datetime.now()
				seconds = int(t1.strftime("%s"))-int(t0.strftime("%s"))
				if seconds: bps = float(len(data))/seconds
				else: bps = 1000000000
				self.log.info("POST completed [%s] in %ss (%.02fbps)" % (e.code, t1-t0, bps))
				response = ""
			else:
				self.log.error("HTTP Response %s: %s\n%s" % (e.code, e.msg, e.hdrs))
				if e.message:
					self.log.error("%s" % (e.message,))
				raise
		except:
			self.log.error("Error in post to %s:\n%s" % (url, traceback.format_exc()))
			raise
		return response

	def query(self, query, initNs = None):
		r"""
		Execute a SPARQL query against the triplestore and
		return a generator for result rows. The results are
		returned in a form similar to that of an rdflib graph,
		namely a list of bound variables.

		The contents of initNs should be a dictionary with
		namespace prefixes. The default value is 

			{
				'rdf': 'http://www.w3.org/1999/02/22-rdf-syntax-ns#',
				'rdfs': 'http://www.w3.org/2000/01/rdf-schema#',
				'xsd': 'http://www.w3.org/2001/XMLSchema#',
				'dc': 'http://purl.org/dc/terms/'
			}

		and these values will be added to any initNs passed in.
		The contents of the resulting  dictionary are prepended
		to the query before it is sent to the server.

		>>> initNs = {
		...    'scv': 'http://purl.org/NET/scovo#',
		...    'cra': 'http://www.ckan.net/package/ukgov-finances-cra#'
		... }
		>>> t = Talis("ckan-dev1")
		>>> q = '\
		... SELECT SUM(?amount) { \n\
		...     ?scotland a cra:Area . \n\
		...     ?scotland dc:spatial "SCOTLAND" . \n\
		...     ?exp cra:area ?scotland . \n\
		...     ?exp a cra:Expenditure . \n\
		...     ?exp rdf:value ?amount \n\
		... }'
		>>> for amount, in t.query(q, initNs=initNs):
		...     print amount
		...
		329687.94
		>>>
		"""
		###
		### first make sure any unapplied changes have been applied
		### to the remote store
		###
		self.sync()

		###
		### prepare the query
		###
		defaultNs = {
			'rdf': 'http://www.w3.org/1999/02/22-rdf-syntax-ns#',
			'rdfs': 'http://www.w3.org/2000/01/rdf-schema#',
			'xsd': 'http://www.w3.org/2001/XMLSchema#',
			'dc': 'http://purl.org/dc/terms/'
		}
		ns = defaultNs.copy()
		if initNs:
			ns.update(initNs)
		q = "\n".join(map(lambda x: "PREFIX %s: <%s>" % x, ns.items())) + "\n" + query
		self.log.debug("SPARQL Query:\n%s" % (q,))
		###
		### prepare the HTTP request
		###
		url = self.urlbase + "/services/sparql"
		headers = {
			'User-Agent': USER_AGENT,
			'Content-Type': 'application/x-www-form-urlencoded',
			'Accept': 'application/xml'
		}
		data = urllib.urlencode({'query': q, 'output': 'xml'})
		req = urllib2.Request(url, data, headers)
		try:
			t0 = datetime.now()
			fp = urllib2.urlopen(req)
			response = fp.read()
			fp.close()
			t1 = datetime.now()
			self.log.info("SPARQL Query took %s" % (t1-t0,))
			self.log.debug("SPARQL Result:\n%s" % (response,))
		except urllib2.HTTPError, e:
			self.log.error("HTTP Response %s: %s" % (e.code, e.msg))
			if e.message:
				self.log.error("%s" % (e.message,))
			raise
		except:
			self.log.error("Error in post to %s:\n%s" % (url, traceback.format_exc()))
			raise
		###
		### parse the result using ElementTree
		###
		tree = ElementTree.fromstring(response)
	
		sparql_ns = "http://www.w3.org/2005/sparql-results#"	
		head = "{%s}head" % (sparql_ns,)
		binding = "{%s}binding" % (sparql_ns,)
		variable =  "{%s}variable" % (sparql_ns,)
		result = "{%s}result" % (sparql_ns,)
		results = "{%s}results" % (sparql_ns,)
		uri = "{%s}uri" % (sparql_ns,)
		literal = "{%s}literal" % (sparql_ns,)

		###
		### find the list of bound output variables
		###
		variables = map(lambda x: x.get("name"), tree.findall("%s/%s" % (head, variable)))
		###
		### iterate through the results and yield them
		###
		for r in tree.findall("%s/%s" % (results, result)):
			row = {}
			for b in r.findall(binding):
				v = b.getchildren()[0]
				if v.tag == uri:
					value = URIRef(v.text)
				elif v.tag == literal:
					datatype = v.get("datatype")
					if datatype:
						value = Literal(float(v.text), datatype=URIRef(datatype))
					else:
						value = Literal(v.text)
				row[b.get("name")] = value
			yield map(lambda x: row[x], variables)				

if __name__ == '__main__':
	import doctest
	logging.basicConfig(
		level=logging.INFO,
		format = "%(name)s:%(levelname)s - %(message)s"
	)
	doctest.testmod()
