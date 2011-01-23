## Use all of our default namespaces
% for ns in namespaces.items():
PREFIX ${ns[0].lower()}: <${str(ns[1])}>
% endfor

SELECT (COUNT(?plingback) as ?noOfFeedbacks)

WHERE {
    ?plingback pbo:isAbout <${str(namespaces['ACTIVITIES'])}${sparql.id}> . 
    ## Plingback Submission Date Filters
    ${sparql.submission_date_filter()}
}
