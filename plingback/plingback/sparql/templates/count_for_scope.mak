## Use all of our default namespaces
% for ns in namespaces.items():
PREFIX ${ns[0].lower()}: <${str(ns[1])}>
% endfor

SELECT ?group (COUNT(?plingback) as ?noOfFeedbacks)
WHERE {
    ## Pling collector
    ${sparql.get('collector')}
    ## Pling Date Filters
    ${sparql.get('activity_date_filter')}
    ?plingback pbo:isAbout ?pling . 
    ## Plingback Submission Date Filters
    ${sparql.get('submission_date_filter')}
}
GROUP BY ?group
ORDER BY DESC(?noOfFeedbacks)