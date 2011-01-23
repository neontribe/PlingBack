## Use all of our default namespaces
% for ns in namespaces.items():
PREFIX ${ns[0].lower()}: <${str(ns[1])}>
% endfor

SELECT (COUNT(?plingback) as ?noOfFeedbacks)
WHERE {
    ## Pling collector
    ?pling pbo:${sparql.scope} '${sparql.id}' .
    ## Pling Date Filters
    ${sparql.activity_date_filter()}
    ?plingback pbo:isAbout ?pling . 
    ## Plingback Submission Date Filters
    ${sparql.submission_date_filter()}
}
ORDER BY DESC(?noOfFeedbacks)