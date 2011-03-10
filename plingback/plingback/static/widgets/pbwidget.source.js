// Put everything inside an anonymous closure to keep us safe and private
( function() {
    
 // Make a unique namespace to work in and assign a $ shortcut  
 var trueName = '';
 for (var i = 0; i < 16; i++) {
  trueName += String.fromCharCode(Math.floor(Math.random() * 26) + 97);
 }
 window[trueName] = {};
 var $ = window[trueName];
 
 $.f = function() {
  return {
   init : function(target) {
    // Could be happier with this: what if the scripts don't execute in order?
    var theScripts = document.getElementsByTagName('SCRIPT');
    for (var i = 0; i < theScripts.length; i++) {
     if (theScripts[i].src.match(target)) {
      
      $.config = {};
      if (theScripts[i].innerHTML) {
       $.config = $.f.parseJson(theScripts[i].innerHTML);
      } 
      else { $.config.err = 'No Configuration Data Supplied'; }
      
      
      if (!$.config.err) {
          
          $.w = document.createElement('IFRAME');
          var base_url = $.config.base_url ? $.config.base_url : 'http://plingback.appspot.com';
          var widget_url = "/widgets/plingbackbar/plingbackbar.html";
          var iframe_style = "border: medium none; width: 100%; height: 65px; overflow: hidden;";
          var thanks_url = $.config.thanks_url ? $.config.thanks_url : false;

          if ($.config.widget) {
            switch ($.config.widget) {
                case 'fastfeedback':
                    widget_url = "/widgets/fastfeedback/fastfeedback.html";
                    iframe_style = "border:0; width: 280px; height: 260px; overflow-y: hidden; overflow-x: hidden;";
                    break;
                case 'topbar':
                    widget_url = "/widgets/plingbackbar/plingbackbar.html";
                    iframe_style = "border:0; width: 100%; height: 65px; overflow-y: hidden; overflow-x: hidden; padding:0; margin:0;";
                    break;
                case 'stars':
                    widget_url = "/widgets/stars/stars.html";
                    iframe_style = "border:0; width: 220px; height: 55px; overflow-y: hidden; overflow-x: hidden; padding:0; margin:0;";
                    break;
            }
          }
          $.w.src = base_url + widget_url;
          $.w.scrolling = "no";
          $.w.frameBorder = "0";
          if ($.config.iframe_style) {
              $.w.style.cssText = $.config.iframe_style;  
          } else {
            $.w.style.cssText = iframe_style;
          }
          
          // Pass appropriate config via the URL
          $.w.src += '?pling_id=' + $.config.pling_id;
          
          if ($.config.skin_color) {
            $.w.src += '&skin_color=' + $.config.skin_color;
          }
          
          if ($.config.thanks_url) {
            $.w.src += '&thanks_url=' + $.config.thanks_url;
          }
          
          if ($.config.multiuser) {
            $.w.src += '&multiuser=true';
          }
            
          $.w.allowtransparency = "true";
          $.w.frameborder = "0";

          
      } else {
          $.w = document.createElement('DIV');
          $.w.innerHTML = 'Error: '+ $.config.err;
      }
      
    var insert_before = document.getElementsByTagName('body')[0].firstChild;
    if ($.config.widget) {
        switch ($.config.widget) {
            case 'fastfeedback':
                insert_before = theScripts[i];
                theScripts[i].parentNode.insertBefore($.w, theScripts[i]);
                break;
            case 'topbar':
                insert_before = document.getElementsByTagName('body')[0].firstChild;
                document.getElementsByTagName('body')[0].insertBefore($.w, insert_before);
                break;
            default:
                insert_before = theScripts[i];
                theScripts[i].parentNode.insertBefore($.w, theScripts[i]);
                break;
                
        }
      } 
      
      theScripts[i].parentNode.removeChild(theScripts[i]);
      break;
     }
    }
   },
   parseJson : function(json) {
    this.parseJson.data = json;
    if ( typeof json !== 'string') {
     return {"err":"trying to parse a non-string JSON object"};
    }
    try {
     var f = Function(['var document,top,self,window,parent,Number,Date,Object,Function,',
      'Array,String,Math,RegExp,Image,ActiveXObject;',
      'return (' , json.replace(/<\!--.+-->/gim,'').replace(/\bfunction\b/g,'function­') , ');'].join(''));
       return f();
    } catch (e) {
     return {"err":"trouble parsing JSON object"};
    }
   }
  };
 }();
 
 // Set the source selector so that we can tidy up our script elements
 var thisScript = /pbwidget.js/;
 
 // Run init once the page has loaded. Don't get involved in window.onload
 if (typeof window.addEventListener !== 'undefined') {
  window.addEventListener('load', function() { $.f.init(thisScript); }, false);
 } else if (typeof window.attachEvent !== 'undefined') {
  window.attachEvent('onload', function() { $.f.init(thisScript); });
 }
 
 // Run immediately if asked to
 if (typeof window.pbwidget_immediate_load !== 'undefined') {
    if (window.pbwidget_immediate_load) {
        $.f.init(thisScript);
    }
    
 }
 
})();