// ==UserScript==
// ==UserScript==
// @name PlingbackButtonify Plings
// @namespace http://plingback.plings.net/applications/fastfeedback
// @description This script adds a plingbackbutton to Plings.net activity pages
// @include http://www.plings.net/a/*
// ==/UserScript==

// Identify the pling
var pling = window.location.pathname.substring(window.location.pathname.lastIndexOf('/') + 1, window.location.pathname.length);

// Check that the pling really looks like a pling id (they're integers!)
var pling_id = null;
try {
    pling_id = parseInt(pling, 10);
    
}
catch (e) {
    alert("PlingbackBar Monkey can't find a valid pling id");
}

if (pling_id) {
    // Find the element before which to place our widget
    var insert_before = document.getElementById('activityOrganiser');
    if (insert_before) {
		// Build and insert the button
		button = document.createElement('button');
		button.setAttribute('value',pling_id);
		button.setAttribute('class', 'plingback_button');
		button.setAttribute('style', 'border:0;width:200px;height:50px;text-indent:-9999px;background:transparent url(http://plingback.appspot.com/widgets/wrappers/modal/plingback_button.png) no-repeat left top;');
		button.innerHTML = 'Give Feedback';
		insert_before.parentNode.insertBefore(button, insert_before);
        // Build and insert the script tag
        script = document.createElement('script');
        script.src = "http://plingback.appspot.com/widgets/wrappers/modal/plingback_modal.min.js";
        insert_before.parentNode.insertBefore(script, insert_before);
    } else {
        alert("PlingbackBar Monkey failed to find a suitable place to put the widget");
    }
}

