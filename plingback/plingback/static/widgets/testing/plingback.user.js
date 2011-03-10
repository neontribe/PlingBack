// ==UserScript==
// ==UserScript==
// @name Plingbackbarify Plings
// @namespace http://plingback.plings.net/applications/fastfeedback
// @description This script adds a plingbackbar to Plings.net activity pages
// @include http://www.plings.net/a/*
// ==/UserScript==

// Identify the pling
var pling = window.location.pathname.substring(window.location.pathname.lastIndexOf('/') + 1, window.location.pathname.length);

// Check that the pling really looks like a pling id (they're integers!)
var pling_id = null;
try {
    pling_id = parseInt(pling);
    
}
catch (e) {
    alert("PlingbackBar Monkey can't find a valid pling id");
}

if (pling_id) {
    // Find the element before which to place our widget
    var insert_before = document.getElementsByTagName('body')[0].children[0];
    if (insert_before) {
        // Build and insert the script tag
        script = document.createElement('script');
        script.src = "http://plingback.appspot.com/widgets/pbwidget.js";
        script.innerHTML = '{"pling_id":"'+pling_id.toString()+'", "widget":"topbar"}';
        insert_before.parentNode.insertBefore(script, insert_before);
    } else {
        alert("PlingbackBar Monkey failed to find a suitable place to put the widget");
    }
}

