## Use all of our default namespaces
% for ns in namespaces.items():
PREFIX ${ns[0].lower()}: <${str(ns[1])}>
% endfor

SELECT ?item ?pling

WHERE {

    ?plingback pbo:isAbout <${str(namespaces['ACTIVITIES'])}${sparql.id}> .
    ## Plingback Submission Date Filters
    ${sparql.submission_date_filter()}
    ?plingback rev:text ?item .
}

## Limit
% if sparql.limit:
LIMIT ${sparql.limit}
% endif
## Offset
% if sparql.offset:
OFFSET ${sparql.offset}
% endif