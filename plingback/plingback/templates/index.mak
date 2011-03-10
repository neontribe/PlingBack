<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01//EN" "http://www.w3.org/TR/html4/strict.dtd">
<html>
	<head>
		<meta http-equiv="Content-Type" content="text/html; charset=iso-8859-1">
		<link rel="stylesheet" type="text/css" href="/css/style.css" />

        <title>Plingback</title>
		
		<script type="text/javascript" src="http://www.google.com/jsapi"></script>
        <script type="text/javascript">
        	var pbwidget_immediate_load = true;
			    var url_root = '${root_url}';
            // Load jQuery
            google.load("jquery", "1.4.2");
            google.setOnLoadCallback(function() {
				    // Adjust the link location for documentation links
				    $('a.doclink').each(function(){
              $(this).attr('href', url_root + $(this).attr('href'));
            });
				
				// Setup the widget demos
        $('#widgetdemo').submit(function () {
					var widgetname = $('select[name=widget]').val();
					var insert_before = null;
					var script = null;
                    switch ($('#widgetdemo select[name=widget]').val()) {
                        case 'topbar':
                            insert_before = document.getElementsByTagName('body')[0].children[0];
    		                    // Build and insert the script tag
    		                    script = document.createElement('script');
    							          script.type = "text/javascript";
    		                    script.src = url_root + "/widgets/pbwidget.js";
    		                    script.text = '{pling_id:"'+ $('input[name=pling_id]').val()+'", widget:"topbar", base_url:"'+url_root+'"}';
    		                    insert_before.parentNode.insertBefore(script, insert_before);
                            break;
                        case 'fastfeedback':
						                insert_before = document.getElementById('widgetdemo');
                            // Build and insert the script tag
                            script = document.createElement('script');
							              script.type = "text/javascript";
                            script.src = url_root + "/widgets/pbwidget.js";
                            script.text = '{pling_id:"'+ $('input[name=pling_id]').val()+'", widget:"fastfeedback", base_url:"'+url_root+'"}';
                            insert_before.parentNode.insertBefore(script, insert_before);
                            break;
					              case 'stars':
                            insert_before = document.getElementById('widgetdemo');
                            // Build and insert the script tag
                            script = document.createElement('script');
							              script.type = "text/javascript";
                            script.src = url_root + "/widgets/pbwidget.js";
                            script.text = '{pling_id:"'+ $('input[name=pling_id]').val()+'", widget:"stars", base_url:"'+url_root+'"}';
                            insert_before.parentNode.insertBefore(script, insert_before);
                            break;
                        case 'plingback_button':
            						    insert_before = document.getElementById('widgetdemo');
            						    button = document.createElement('button');
                            button.setAttribute('value',$('input[name=pling_id]').val());
            					      button.setAttribute('class', 'plingback_button');
            					      button.setAttribute('style', 'border:0;width:200px;height:50px;text-indent:-9999px;background:transparent url(http://plingback.appspot.com/widgets/wrappers/modal/plingback_button.png) no-repeat left top;');
            					      button.innerHTML = 'Give Feedback';
            					      insert_before.parentNode.insertBefore(button, insert_before);
            					      // Build and insert the script tag
            					      script = document.createElement('script');
            							  script.type = "text/javascript";
            					      script.src = url_root + "/widgets/wrappers/modal/plingback_modal.min.js";
            					      insert_before.parentNode.insertBefore(script, insert_before);
                            break;
                    }
                    return false;
                });
            });
        </script>
	</head>

	<body>
        <div id="wrapper">
        <div id="header">
            <a href="http://www.plings/net"><img src="images/Plings_badgebox_green.png" class="right">
</a>		    <h1>PlingBack</h1>
        </div> <!--END header -->
		<div id="content">
		    <h2>Overview</h2>
		    <p>PlingBack is part of the Plings project: more at <a href="http://www.plings.net">www.plings.net</a></p>
<p>Plings is about places to go and things to do for young people.</p>
<p>PlingBack provides different ways to solicit or give feedback about these positive activities.</p>
<p>PlingBack is fed by widgets which pass data to and from the datastore using Input and Output APIs.</p>
<a href="/docs/html">Dive into the <strong>full documentation</strong>!</a>
		    <h2>Widgets</h2>
		    <p>At the moment, PlingBack provides 4 widgets for getting feedback: <strong>FastFeedback</strong>, <strong>TopBar</strong>, <strong>Stars</strong> and <strong>PlingBack Button</strong>.</p>
		    <h3>Widget Documentation</h3>
            <p>For a full explaination of what they do and how they work, check out the documentation.</p>
		    <p><a class="doclink" href="/docs/html/about_the_widgets.html">Widgets Overview</a></p>
		    <h3>Widget Demos</h3>
            <p>If you want to see a widget in action, use this form.</p>
		    <form id="widgetdemo">
			    <label for="pling_id">Enter a Pling Id</label>
			    <input class="textfield" type="text" name="pling_id" value="452820"/>
			    <label for="widget">Choose a widget</label>
			    <select name="widget">
				    <option value="topbar">Top Bar</option>
				    <option value="fastfeedback">FastFeedback</option>
					<option value="stars">Stars</option>
				    <option value="plingback_button">PlingBack Button</option>
			    </select>
			    <input type="submit" value="Go"/>
		    </form>	
		    <h2>Input API</h2>
		    <p>The Plingback Input API exposes a RESTful interface which allows the submission of 
               feedback about a Pling through the use of standard HTTP actions such as POST and PUT.
            </p>
		    <h3>API Documentation</h3>
            <p>For a full explaination of how that works, follow the link below for documentation.</p>
            <p><a class="doclink" href="/docs/html/restapi.html">API</a></p>
            <h2>Developers</h2>
            <img class="left logo" src="images/neontribe_logo80x80.png">
		    <p>PlingBack was developed by Neontribe. If you have any questions or comments, please 
            <a href="mailto:rupert@neontribe.co.uk">e-mail</a>.
            </p>

        </div> <!--END content -->
        <div id="footer">
       </div> <!--END footer -->
        </div> <!--END wrapper -->
	</body>
</html>
