## Use all of our default namespaces
% for ns in namespaces.items():
PREFIX ${ns[0].lower()}: <${str(ns[1])}>
% endfor

SELECT ${sparql.get('select')}

WHERE {
    ## Pling Collector
    ${sparql.get('collector')}
    ## Pling Date Filters
    ${sparql.get('activity_date_filter')}
    ## Plingback collector
    ?plingback pbo:isAbout ${sparql.get('is_about')} .
    ## Plingback Submission Date Filters
    ${sparql.get('submission_date_filter')}
    ## Item Finder
    ${sparql.get('item_finder')}
}
## Grouping
${sparql.get('group')}
## Limit
${sparql.get('limit')}
## Offset
${sparql.get('offset')}
