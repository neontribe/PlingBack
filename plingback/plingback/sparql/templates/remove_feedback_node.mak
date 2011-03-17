## Use all of our default namespaces
% for ns in namespaces.items():
PREFIX ${ns[0].lower()}: <${str(ns[1])}>
% endfor

CONSTRUCT { <${sparql.id}> rdf:type ?type .
            <${sparql.id}> pbo:isAbout ?pling .
            <${sparql.id}> dc:date ?date .
            <${sparql.id}> pbo:plingBackType ?pbt .
            <${sparql.id}> pbo:plingBackVersion ?version .
            ?pling rev:hasReview <${sparql.id}> .
            <${sparql.id}> pbo:attendance ?attend .
            <${sparql.id}> pbo:deterrent ?det .
            <${sparql.id}> rev:rating ?rat .
            <${sparql.id}> rev:comment ?comment .
            <${sparql.id}> pbo:approval ?approval .
            <${sparql.id}> rev:reviewer ?rbn .
            ?rbn rdf:type foaf:Person .
            ?rbn foaf:mbox ?email .
            ?rbn foaf:phone ?phone .
            ?rbn foaf:dateOfBirth ?dob.
            ?rbn foaf:holdsAccount ?acc.
            ?acc rdf:type foaf:OnlineAccount.
            ?acc foaf:accountServiceHomepage ?homepage.
            ?acc foaf:accountName ?accid .
            
          } 
WHERE { <${sparql.id}> rdf:type ?type .
        <${sparql.id}> pbo:isAbout ?pling .
        <${sparql.id}> dc:date ?date .
        <${sparql.id}> pbo:plingBackType ?pbt .
        OPTIONAL { 
           <${sparql.id}> pbo:plingBackVersion ?version .
           <${sparql.id}> pbo:attendance ?attend .
           <${sparql.id}> pbo:deterrent ?det .
           <${sparql.id}> rev:rating ?rat .
           <${sparql.id}> rev:comment ?comment .
           <${sparql.id}> pbo:approval ?approval .
           <${sparql.id}> rev:reviewer ?rbn .
           ?rbn foaf:mbox ?email .
           ?rbn foaf:phone ?phone .
           ?rbn foaf:dateOfBirth ?dob.
           ?rbn foaf:holdsAccount ?acc.
           ?acc foaf:accountServiceHomepage ?homepage.
           ?acc foaf:accountName ?accid.
                              
        }
}

