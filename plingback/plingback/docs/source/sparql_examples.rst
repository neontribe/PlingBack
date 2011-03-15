========================
SPARQL Examples
========================

Overview
********

    

    .. code-block:: none
    
        PREFIX rev:<http://purl.org/stuff/rev#>
        PREFIX pbo:<http://plingback.plings.net/ontologies/plingback#>
        PREFIX dc:<http://purl.org/dc/elements/1.1/>
        DESCRIBE ?s 
        WHERE {
          ?s pbo:plingBackType <http://plingback.plings.net/applications/fastfeedback>  .
          ?s dc:date ?date .
        }
        ORDER BY DESC(?date)
        LIMIT 3
    
    
        