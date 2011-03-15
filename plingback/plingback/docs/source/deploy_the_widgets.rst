*********************
Deploying the Widgets
*********************

Quickstart
==========

The Plingback widgets can be included in any HTML page through the use of a 
single script element. The minimal example below will serve to illustrate the 
required options. 

    .. code-block:: html

        <script src="http://plingback.appspot.com/widgets/pbwidget.js"> 
                 {pling_id:"452820"}
        </script>
    
The script element's src attribute points to a script at 
http://plingback.appspot.com/widgets/pbwidget.js which is responsible for 
examining the supplied configuration and inserting the correct widget.

The content of the script element is a set of key names and values in JSON
format. Only one key/value pair is required:

    ``pling_id`` - is a required option which sets up the widget to store 
    feedback for a specific activity. The id for a particular activity can be
    found in the url of the activity's page on http://plings.net. 
    
    For example, the activity 'Horning Youth Venture' can be found at 
    http://www.plings.net/a/452820 - its ``pling_id`` is 452820
    
    It is imagined that, in the vast majority of cases, the ``pling_id`` will
    be inserted by the Content Management System which hosts the page.

A modal presentation - where the widget is invoked by button click and shown on
a modal overlay is also supported: See :ref:`modal-widgets-label`

Additional Configuration Options
================================

    ``widget`` - chooses which widget will be inserted in the page. The default
    value is 'topbar'. Currently supported values are:
    
        * ``topbar`` will insert the Topbar widget immediately after the 
                        document's opening body tag.
        * ``fastfeedback`` will insert a FastFeedback widget at the point in 
                        the document where the script element appears
        * ``stars`` will insert a star rating widget at the point in
                        the document where the script element appears
        
        
    ``skin_color`` - **Fastfeedback widget only** - chooses the dominant colour 
    for the widget's styling. The default value is 'green'. Currently supported 
    values are:
    
        * ``green``  
        * ``orange``
    
    ``iframe_style`` - The default styling of the iframe which pbwidget.js 
    inserts in the page can be replaced by any valid css style supplied through 
    this option. NB: the minimum width and height for correct display of the 
    widgets is as follows:
    
        * ``topbar``: 100% x 65px
        * ``fastfeedback``: 280px x 380px
        * ``stars``: 220px x 50px
    
    ``base_url`` - Overrides the base url used to derive the location of widget 
    resources and the Plingback Input API. The default is 
    'http://plingback.appspot.com'
    
    ``thanks_url`` - If a url is specified under this key a link will be placed 
    on the widget's 'Thank You' slide (which appears after all feedback submissions
    have been completed).
    
Examples
========

FastFeedback
------------

The following snippet renders a Fastfeedback widget for the pling "Arsenal Kickz
Football" (575002), using the orange theme and adding a two pixel border to the 
iframe

    .. code-block:: html
    
        <script src="http://plingback.appspot.com/widgets/pbwidget.js"> 
                 {pling_id:"575002",
                  widget:"fastfeedback",
                  skin_color:"orange",
                  iframe_style:"border: 2px black; width: 280px; height: 380px; overflow-y: hidden; overflow-x: hidden;"}
        </script>
    
TopBar
------

The following snippet renders a TopBar widget for the pling "Arsenal Kickz
Football" (575002)

    .. code-block:: html

        <script src="http://plingback.appspot.com/widgets/pbwidget.js"> 
                 {pling_id:"575002",
                  widget:"topbar"}
        </script>
        
Stars
------

The following snippet renders a Stars widget for the pling "Arsenal Kickz
Football" (575002)

    .. code-block:: html

        <script src="http://plingback.appspot.com/widgets/pbwidget.js">
                 {pling_id:"575002",
                  widget:"stars"}
        </script>

