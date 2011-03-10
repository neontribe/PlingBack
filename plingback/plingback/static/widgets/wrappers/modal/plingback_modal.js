/**
 * Plingback Button
 * 
 * Finds suitably classNamed button elements and adds an onclick behaviour to 
 * display a modal feedback widget.
 * 
 * NB. Each button is expected to:
 *      a) Have the css class 'plingback_button'
 *      b) Have a value attribute containing the appropriate pling id
 *      
 *     The script hides itself within a single function plingbackbutton()
 *     which is called at the end of the script. To disable this automatic call
 *     set a global variable 'plingbackbutton_defer_init' to true. You'll then 
 *     need to call plingbackbutton() yourself at an appropriate juncture.
 *     
 *     Plingback button works best when the script is included at the end of
 *     the body tag. Alternatively you can load it in the head after setting 
 *     plingbackbutton_defer_init = true and then run plingbackbutton() on
 *     document.ready() (or appropriate for your environment).
 *      
 * This script owes a lot to Seth Banks whose modal code is included in full
 * 
 */

function plingbackbutton() {
	/**
	 * COMMON DHTML FUNCTIONS
	 * These are handy functions I use all the time.
	 *
	 * By Seth Banks (webmaster at subimage dot com)
	 * http://www.subimage.com/
	 *
	 * Up to date code can be found at http://www.subimage.com/dhtml/
	 *
	 * This code is free for you to use anywhere, just keep this comment block.
	 */
	
	/**
	 * X-browser event handler attachment and detachment
	 * TH: Switched first true to false per http://www.onlinetools.org/articles/unobtrusivejavascript/chapter4.html
	 *
	 * @argument obj - the object to attach event to
	 * @argument evType - name of the event - DONT ADD "on", pass only "mouseover", etc
	 * @argument fn - function to call
	 */
	function addEvent(obj, evType, fn){
	 if (obj.addEventListener){
	    obj.addEventListener(evType, fn, false);
	    return true;
	 } else if (obj.attachEvent){
	    var r = obj.attachEvent("on"+evType, fn);
	    return r;
	 } else {
	    return false;
	 }
	}
	function removeEvent(obj, evType, fn, useCapture){
	  if (obj.removeEventListener){
	    obj.removeEventListener(evType, fn, useCapture);
	    return true;
	  } else if (obj.detachEvent){
	    var r = obj.detachEvent("on"+evType, fn);
	    return r;
	  } else {
	    alert("Handler could not be removed");
	  }
	}
	
	/**
	 * Code below taken from - http://www.evolt.org/article/document_body_doctype_switching_and_more/17/30655/
	 *
	 * Modified 4/22/04 to work with Opera/Moz (by webmaster at subimage dot com)
	 *
	 * Gets the full width/height because it's different for most browsers.
	 */
	function getViewportHeight() {
	    if (window.innerHeight !== undefined) {
			return window.innerHeight;
		}
	    if (document.compatMode == 'CSS1Compat') {
			return document.documentElement.clientHeight;
		}
	    if (document.body) {
			return document.body.clientHeight;
		}
	    return undefined; 
	}
	function getViewportWidth() {
	    var offset = 17;
	    var width = null;
	    if (window.innerWidth !== undefined) {
			return window.innerWidth;
		}
	    if (document.compatMode === 'CSS1Compat') {
			return document.documentElement.clientWidth;
		}
	    if (document.body) {
			return document.body.clientWidth;
		}
	}
	
	/**
	 * Gets the real scroll top
	 */
	function getScrollTop() {
	    if (self.pageYOffset) // all except Explorer
	    {
	        return self.pageYOffset;
	    }
	    else if (document.documentElement && document.documentElement.scrollTop)
	        // Explorer 6 Strict
	    {
	        return document.documentElement.scrollTop;
	    }
	    else if (document.body) // all other Explorers
	    {
	        return document.body.scrollTop;
	    }
	}
	function getScrollLeft() {
	    if (self.pageXOffset) // all except Explorer
	    {
	        return self.pageXOffset;
	    }
	    else if (document.documentElement && document.documentElement.scrollLeft)
	        // Explorer 6 Strict
	    {
	        return document.documentElement.scrollLeft;
	    }
	    else if (document.body) // all other Explorers
	    {
	        return document.body.scrollLeft;
	    }
	}
	
	/**
	 * SUBMODAL v1.6
	 * Used for displaying DHTML only popups instead of using buggy modal windows.
	 *
	 * By Subimage LLC
	 * http://www.subimage.com
	 *
	 * Contributions by:
	 *  Eric Angel - tab index code
	 *  Scott - hiding/showing selects for IE users
	 *  Todd Huss - inserting modal dynamically and anchor classes
	 *
	 * Up to date code can be found at http://submodal.googlecode.com
	 */
	
	// Popup code
	var gPopupMask = null;
	var gPopupContainer = null;
	var gPopFrame = null;
	var gReturnFunc;
	var gPopupIsShown = false;
	var gDefaultPage = "";
	var gHideSelects = false;
	var gReturnVal = null;
	
	var gTabIndexes = [];
	// Pre-defined list of tags we want to disable/enable tabbing into
	var gTabbableTags = ["A","BUTTON","TEXTAREA","INPUT","IFRAME"];    
	
	// If using Mozilla or Firefox, use Tab-key trap.
	if (!document.all) {
	    document.onkeypress = keyDownHandler;
	}
	
	/**
	 * Initializes popup code on load.  
	 */
	function initPopUp() {
	    // Add the HTML to the body
	    theBody = document.getElementsByTagName('BODY')[0];
	    popmask = document.createElement('div');
	    popmask.id = 'popupMask';
	    popcont = document.createElement('div');
	    popcont.id = 'popupContainer';
	    popcont.innerHTML = '' +
	        '<div id="popupInner">' +
	            '<div id="popupTitleBar">' +
	                '<div id="popupTitle"></div>' +
	                '<div id="popupControls">' +
	                    '<a id="popClose" href="#" >close</a>' +
	                '</div>' +
	            '</div>' +
	            '<iframe src="'+gDefaultPage+'" style="width:100%;height:100%;background-color:transparent;" scrolling="no" frameborder="0" allowtransparency="true" id="popupFrame" name="popupFrame" width="100%" height="100%"></iframe>' +
	        '</div>';
	    theBody.appendChild(popmask);
	    theBody.appendChild(popcont);
	    
		gPopClose = document.getElementById("popClose");
		gPopClose.onclick = function () {hidePopWin();return false;};
	    gPopupMask = document.getElementById("popupMask");
	    gPopupContainer = document.getElementById("popupContainer");
	    gPopFrame = document.getElementById("popupFrame");  
	    
	    // check to see if this is IE version 6 or lower. hide select boxes if so
	    // maybe they'll fix this in version 7?
	    var brsVersion = parseInt(window.navigator.appVersion.charAt(0), 10);
	    if (brsVersion <= 6 && window.navigator.userAgent.indexOf("MSIE") > -1) {
	        gHideSelects = true;
	    }
	    
	    // Add onclick handlers to 'a' elements of class submodal or submodal-width-height
	    var elms = document.getElementsByTagName('a');
	    for (i = 0; i < elms.length; i++) {
	        if (elms[i].className.indexOf("submodal") === 0) { 
	            // var onclick = 'function (){showPopWin(\''+elms[i].href+'\','+width+', '+height+', null);return false;};';
	            // elms[i].onclick = eval(onclick);
	            elms[i].onclick = function(){
	                // default width and height
	                var width = 400;
	                var height = 200;
	                // Parse out optional width and height from className
	                params = this.className.split('-');
	                if (params.length == 3) {
	                    width = parseInt(params[1], 10);
	                    height = parseInt(params[2], 10);
	                }
	                showPopWin(this.href,width,height,null); 
					return false;
	            };
	        }
	    }
	}
	
	
	 /**
	    * @argument width - int in pixels
	    * @argument height - int in pixels
	    * @argument url - url to display
	    * @argument returnFunc - function to call when returning true from the window.
	    * @argument showCloseBox - show the close box - default true
	    */
	function showPopWin(url, width, height, returnFunc, showCloseBox) {
	    // show or hide the window close widget
	    if (showCloseBox || showCloseBox !== false) {
	        document.getElementById("popClose").style.display = "block";
	    } else {
	        document.getElementById("popClose").style.display = "none";
	    }
	    gPopupIsShown = true;
	    disableTabIndexes();
	    gPopupMask.style.display = "block";
	    gPopupContainer.style.display = "block";
	    // calculate where to place the window on screen
	    centerPopWin(width, height);
	    
	    var titleBarHeight = parseInt(document.getElementById("popupTitleBar").offsetHeight, 10);
	
	
	    gPopupContainer.style.width = width + "px";
	    gPopupContainer.style.height = (height+titleBarHeight) + "px";
	    
	    setMaskSize();
	
	    // need to set the width of the iframe to the title bar width because of the dropshadow
	    // some oddness was occuring and causing the frame to poke outside the border in IE6
	    gPopFrame.style.width = parseInt(document.getElementById("popupTitleBar").offsetWidth, 10) + "px";
	    gPopFrame.style.height = (height) + "px";
	    
	    // set the url
	    gPopFrame.src = url;
	    
	    gReturnFunc = returnFunc;
	    // for IE
	    if (gHideSelects === true) {
	        hideSelectBoxes();
	    }
	    
	    window.setTimeout(setPopTitle, 600);
	}
	
	//
	var gi = 0;
	function centerPopWin(width, height) {
	    if (gPopupIsShown === true) {
	        if (width === null || isNaN(width)) {
	            width = gPopupContainer.offsetWidth;
	        }
	        if (height === null) {
	            height = gPopupContainer.offsetHeight;
	        }
	        
	        //var theBody = document.documentElement;
	        var theBody = document.getElementsByTagName("BODY")[0];
	        //theBody.style.overflow = "hidden";
	        var scTop = parseInt(getScrollTop(),10);
	        var scLeft = parseInt(theBody.scrollLeft,10);
	    
	        setMaskSize();
	        
	        //window.status = gPopupMask.style.top + " " + gPopupMask.style.left + " " + gi++;
	        
	        var titleBarHeight = parseInt(document.getElementById("popupTitleBar").offsetHeight, 10);
	        
	        var fullHeight = getViewportHeight();
	        var fullWidth = getViewportWidth();
	        
	        gPopupContainer.style.top = (scTop + ((fullHeight - (height+titleBarHeight)) / 2)) + "px";
	        gPopupContainer.style.left =  (scLeft + ((fullWidth - width) / 2)) + "px";
	        //alert(fullWidth + " " + width + " " + gPopupContainer.style.left);
	    }
	}
	addEvent(window, "resize", centerPopWin);
	addEvent(window, "scroll", centerPopWin);
	window.onscroll = centerPopWin;
	
	
	/**
	 * Sets the size of the popup mask.
	 *
	 */
	function setMaskSize() {
	    var theBody = document.getElementsByTagName("BODY")[0];
	            
	    var fullHeight = getViewportHeight();
	    var fullWidth = getViewportWidth();
	    
	    // Determine what's bigger, scrollHeight or fullHeight / width
	    if (fullHeight > theBody.scrollHeight) {
	        popHeight = fullHeight;
	    } else {
	        popHeight = theBody.scrollHeight;
	    }
	    
	    if (fullWidth > theBody.scrollWidth) {
	        popWidth = fullWidth;
	    } else {
	        popWidth = theBody.scrollWidth;
	    }
	    
	    gPopupMask.style.height = popHeight + "px";
	    gPopupMask.style.width = popWidth + "px";
	}
	
	/**
	 * @argument callReturnFunc - bool - determines if we call the return function specified
	 * @argument returnVal - anything - return value 
	 */
	function hidePopWin(callReturnFunc) {
	    gPopupIsShown = false;
	    var theBody = document.getElementsByTagName("BODY")[0];
	    theBody.style.overflow = "";
	    restoreTabIndexes();
	    if (gPopupMask === null) {
	        return;
	    }
	    gPopupMask.style.display = "none";
	    gPopupContainer.style.display = "none";
	    if (callReturnFunc === true && gReturnFunc !== null) {
	        // Set the return code to run in a timeout.
	        // Was having issues using with an Ajax.Request();
	        gReturnVal = window.frames.popupFrame.returnVal;
	        window.setTimeout('gReturnFunc(gReturnVal);', 1);
	    }
	    gPopFrame.src = gDefaultPage;
	    // display all select boxes
	    if (gHideSelects === true) {
	        displaySelectBoxes();
	    }
	}
	
	/**
	 * Sets the popup title based on the title of the html document it contains.
	 * Uses a timeout to keep checking until the title is valid.
	 */
	function setPopTitle() {
	    //return;
	    if (window.frames.popupFrame.document.title === null) {
	        window.setTimeout("setPopTitle();", 10);
	    } else {
	        document.getElementById("popupTitle").innerHTML = window.frames.popupFrame.document.title;
	    }
	}
	
	// Tab key trap. iff popup is shown and key was [TAB], suppress it.
	// @argument e - event - keyboard event that caused this function to be called.
	function keyDownHandler(e) {
	    if (gPopupIsShown && e.keyCode == 9) {
			return false;
		}
	}
	
	// For IE.  Go through predefined tags and disable tabbing into them.
	function disableTabIndexes() {
	    if (document.all) {
	        var i = 0;
	        for (var j = 0; j < gTabbableTags.length; j++) {
	            var tagElements = document.getElementsByTagName(gTabbableTags[j]);
	            for (var k = 0 ; k < tagElements.length; k++) {
	                gTabIndexes[i] = tagElements[k].tabIndex;
	                tagElements[k].tabIndex="-1";
	                i++;
	            }
	        }
	    }
	}
	
	// For IE. Restore tab-indexes.
	function restoreTabIndexes() {
	    if (document.all) {
	        var i = 0;
	        for (var j = 0; j < gTabbableTags.length; j++) {
	            var tagElements = document.getElementsByTagName(gTabbableTags[j]);
	            for (var k = 0 ; k < tagElements.length; k++) {
	                tagElements[k].tabIndex = gTabIndexes[i];
	                tagElements[k].tabEnabled = true;
	                i++;
	            }
	        }
	    }
	}
	
	
	/**
	 * Hides all drop down form select boxes on the screen so they do not appear above the mask layer.
	 * IE has a problem with wanted select form tags to always be the topmost z-index or layer
	 *
	 * Thanks for the code Scott!
	 */
	function hideSelectBoxes() {
	  var x = document.getElementsByTagName("SELECT");
	
	  for (i=0;x && i < x.length; i++) {
	    x[i].style.visibility = "hidden";
	  }
	}
	
	/**
	 * Makes all drop down form select boxes on the screen visible so they do not 
	 * reappear after the dialog is closed.
	 * 
	 * IE has a problem with wanting select form tags to always be the 
	 * topmost z-index or layer.
	 */
	function displaySelectBoxes() {
	  var x = document.getElementsByTagName("SELECT");
	
	  for (i=0;x && i < x.length; i++){
	    x[i].style.visibility = "visible";
	  }
	}
	
	var setupStyles = function() {
	    var pS = null;
		try {
			pS = document.createElement('style');
		} catch (ex) {
			pS = document.createStyleSheet("styles.css");
		}
	    pS.type = 'text/css';
	    pS.rel = 'stylesheet';
	    pS.media = 'screen';
	    pS.title = 'Plingback Popup Stylesheet';
	    document.getElementsByTagName("head")[0].appendChild(pS);
	    
	    var s = document.styleSheets[document.styleSheets.length - 1];
	
	    var rules = {
	        '#popupTitle':['float:right;', 'font-size: 1.1em;', 'display: none;'],
	        '#popupFrame':['margin: 0px;', 'width: 100%;', 'height: 100%;', 'position: relative;', 
	                       'z-index: 202;',
	                       'overflow: hidden;'],
	        '#popupInner':['border: 0px solid #000000;', 
	                       'background-color: transparent;',
	                       'overflow: visible;'],
	        '#popupMask':['position: absolute;',
	                      'z-index: 200;',
	                      'top: 0px;',
	                      'left: 0px;',
	                      'width: 100%;',
	                      'height: 100%;',
	                      'opacity: .4;',
	                      'filter: alpha(opacity=40);',
	                      'background-color:transparent !important;',
	                      'background-color: #333333;',
	                      'background-image: url("http://plingback.appspot.com/widgets/wrappers/modal/mask.png") !important;', 
	                      'background-image:none;',
	                      'background-repeat: repeat;',
	                      'display:none;'],
	        '#popupTitleBar': ['background: transparent;',
	                           'color: #ffffff;',
	                           'font-weight: bold;',
	                           'height: 1.3em;',
	                           'padding: 5px;',
	                           'position: relative;',
	                           'z-index: 203;'],
	        '#popupContainer': ['position: absolute;',
	                            'background: transparent;',
	                            'z-index: 201;',
	                            'top: 0px;',
	                            'left: 0px;',
	                            'display:none;',
	                            'padding: 0px;'],
			'#popupControls': [ 'position:relative;'],
            '#popupControls a': ['display: block;',
                                 'width: 30px;',
                                 'height: 30px;',
                                 'text-indent: -999999px;',
                                 'position: absolute;',
                                 'top: 10px;',
								 'left: -20px;',
                                 'background:transparent url("http://plingback.appspot.com/widgets/wrappers/modal/close.png");'
                                ]
	    };
	    
	    for (selector in rules) {
	        if (s.addRule) {
	            // it's an IE browser
	            for (i = 0; i < rules[selector].length; i++) {
	                s.addRule(selector, rules[selector][i]);
	            }
				
	            
	        } else {
	            // it's a W3C browser
	            var c_rule = '';
	            for (i=0; i<rules[selector].length; i++) {
	                c_rule += rules[selector][i] + ' ';
	            }
	            s.insertRule(selector + '{' + c_rule + '}', s.cssRules ? s.cssRules.length : 0); 
	        }
	    }
	};
	
	var showFF = function (button) {
	    setupStyles();
	    initPopUp();
	    var url = '/widgets/fastfeedback/fastfeedback.html?';
	    url += 'pling_id=' + button.value; 
	    showPopWin(url, 310, 280, null);
	};
	
	
	var elms = document.getElementsByTagName('button');
	for (i = 0; i < elms.length; i++) {
	    if (elms[i].className.indexOf("plingback_button") === 0) {
	        elms[i].onclick = function(){
	            showFF(this);
	            return false;
	        };
	    }
	}

}
if (window.plingbackbutton_defer_init !== true) {
	plingbackbutton();
}
