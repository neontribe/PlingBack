*********************
Plingback Output API
*********************

Overview
========

The Plingback Output API exposes a RESTful interface which allows the request of feedback about a Pling or Local Authority through the use of standard HTTP actions such as GET. The request is parsed and the API fetches the data from the Plingback triple store and returns it in JSON format.

The request url structure is:

api/-id_type-/-id-/-output_type-

* id_type - The type of id being specified, "plings", "authorities", "wards", "venues", "providers".
* id - The id of the Pling or Local Authority, Ward etc. E.g. "452820" or "UG33". A Local Authority code is a 4 digit alpha-numeric code (Uppercase letters) representing a council. Some Local authorities may not have any feedback, or even any plings at all. The codes are listed on the plings development site http://www.plings.info/wiki/index.php/Local_Authority_Code.
* output_type - The type of feedback needed E.g. "comments" or "ratings".

An example pling request url would be:

../../api/plings/452820/ratings

This would retrieve all the ratings for the pling 452820.

To retrieve a local authorities ratings an example would be:

../../api/authorities/00FN/ratings

Additional Parameters
======================

Date Ranges
-----------

Two different sorts of date range filtering can be applied, In both cases dates 
should be specified in the format YYYY-MM-DD:

by Activity Date
   Parameters `from` and `to`

by Feedback Submission Date
   Parameters `submitted_after` and `submitted_before`


Pagination
----------

`limit` can be supplied as a query string parameter
`offset` can be supplied as a query string parameter

Comments
========

Comments are requested by specifying "comments" as the last argument in the feedback request URL.

Comments are returned in the following JSON format:

.. code-block:: javascript

    {
      'comments': 
        [
          {'text':'comment1',
           'activity':'http://plings.net/a/8689'},
          {'text':'comment2',
           'activity':'http://plings.net/a/4437'},
          {'text':'comment3',
           'activity':'http://plings.net/a/54833'}
        ],
      'count': 3
    }

* comments - an array of comments
* count - the quantity of comments, note however that some ratings and feedback items are part of the same feedback node. So the total value of ratings and comments does not necessarily add up to the total count of feedback items.

Ratings
=======

Ratings are requested by specifying "ratings" as the last argument in the feedback request URL. The rating's are generated using the the "statlib" statistics library (http://code.google.com/p/python-statlib/). The methods used below are documented here http://code.google.com/p/python-statlib/wiki/StatsDoc.

Ratings are returned in the following JSON format:

.. code-block:: javascript

    {
      'median':
        {
          [value,value2,value3],
        },
      'mode':
        {
          [
            [bincount]
            [value,value2,value3],
          ],
        },
      'mean':
        {
          [value,value2,value3],
        },
      'histogram':
        {
          [
            [value1, value2,value 3],
            lowerreallimit,
            binsize,
            extraPoints
          ],
        },
      'cumfreq':
        {
          [
            [value,value2,value3],
            lowerRealLimit,
            binsize,
            extraPoints
          ]
        },
      'count':
        {
          [value],
        },
    }

* cumfreq, histogram, mean, mode, median - see http://code.google.com/p/python-statlib/wiki/StatsDoc.
* count - The quantity of ratings, note however that some ratings and feedback items are part of the same feedback node. So the total value of ratings and comments does not necessarily add up to the total count of feedback items.

Feedback Totals
===============

Get requests to /api/-id type- will return a listing of ids codes
for which feedback has been logged along with the number of feedback items.

The total number of feedback items is also included.

JSONP
=====

Responses will be wrapped as JSONP if the request contains the parameter `callback`
with an appropriate value. This interface will work with jQuery’s JSONP facilities without modification.


