## Use all of our default namespaces
% for ns in namespaces.items():
PREFIX ${ns[0].lower()}: <${str(ns[1])}>
% endfor

DESCRIBE <${sparql.id}> ?person ?account ?target
  WHERE { 
    <${sparql.id}> rev:reviewer ?person.
    <${sparql.id}> pbo:isAbout ?target.
    OPTIONAL { 
      ?person <http://xmlns.com/foaf/0.1/holdsAccount> ?account
    }
}