<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01//EN" "http://www.w3.org/TR/html4/strict.dtd">
<html>
  <head>
    <meta http-equiv="Content-Type" content="text/html; charset=iso-8859-1">
    <!--<link rel="stylesheet" type="text/css" href="/css/style.css" />-->

    <title>Plingback : feedback node viewer</title>
    
    <!-- CSS Files  -->
    <link type="text/css" href="/css/graph-base.css" rel="stylesheet" />
    <link type="text/css" href="/css/force-directed-graph.css" rel="stylesheet" />
       
    <!--[if IE]><script language="javascript" type="text/javascript" src="/js/excanvas.js"></script><![endif]-->

    <!-- JIT Library File -->
    <script language="javascript" type="text/javascript" src="/js/jit.js"></script>
    <script language="javascript">
            var json = ${nodes_json|n};
    </script>
    <script language="javascript">
        var labelType, useGradients, nativeTextSupport, animate;

        (function() {
          var ua = navigator.userAgent,
              iStuff = ua.match(/iPhone/i) || ua.match(/iPad/i),
              typeOfCanvas = typeof HTMLCanvasElement,
              nativeCanvasSupport = (typeOfCanvas == 'object' || typeOfCanvas == 'function'),
              textSupport = nativeCanvasSupport 
                && (typeof document.createElement('canvas').getContext('2d').fillText == 'function');
          //I'm setting this based on the fact that ExCanvas provides text support for IE
          //and that as of today iPhone/iPad current text support is lame
          labelType = (!nativeCanvasSupport || (textSupport && !iStuff))? 'Native' : 'HTML';
          nativeTextSupport = labelType == 'Native';
          useGradients = nativeCanvasSupport;
          animate = !(iStuff || !nativeCanvasSupport);
        })();

        var Log = {
          elem: false,
          write: function(text){
            if (!this.elem) 
              this.elem = document.getElementById('log');
            this.elem.innerHTML = text;
            this.elem.style.left = (500 - this.elem.offsetWidth / 2) + 'px';
          }
        };

        $jit.ForceDirected.Plot.EdgeTypes.implement({ 
            'labelled-line': function(adj, canvas) { 
               //plot arrow edge 
               this.edgeTypes.line.call(this, adj, canvas); 
               //get nodes cartesian coordinates 
               var pos = adj.nodeFrom.pos.getc(true); 
               var posChild = adj.nodeTo.pos.getc(true); 
               //check for edge label in data 
               var data = adj.data; 
               if(data.labelid && data.labeltext) { 
                 //now adjust the label placement 
                   var radius = this.viz.canvas.getSize(); 
                   var x = parseInt((pos.x + posChild.x - (data.labeltext.length * 5)) / 
                   2); 
                   var y = parseInt((pos.y + posChild.y ) /2); 
                   this.viz.canvas.getCtx().fillText(data.labeltext, x, y); 
               }
            } 
           });


        function init(){
          // init data
          
          
          
          // init ForceDirected
          var fd = new $jit.ForceDirected({
            //id of the visualization container
            injectInto: 'infovis',
            //Enable zooming and panning
            //by scrolling and DnD
            Navigation: {
              enable: true,
              //Enable panning events only if we're dragging the empty
              //canvas (and not a node).
              panning: 'avoid nodes',
              zooming: 10 //zoom speed. higher is more sensible
            },
            // Change node and edge styles such as
            // color and width.
            // These properties are also set per node
            // with dollar prefixed data-properties in the
            // JSON structure.
            Node: {
              overridable: true,
              color: '#8CC63F',
              type: 'circle',
              dim: 20
            },
            Edge: {
              overridable: true,
              color: '#000000',
              lineWidth: 0.8,
              type: 'labelled-line' 
            },
            //Native canvas text styling
            Label: {
              type: 'Native', //Native or HTML
              size: 14,
              style: 'bold',
              color: '#83548B'
            },
            //Add Tips
            Tips: {
              enable: true,
              onShow: function(tip, node) {
                //count connections
                var count = 0;
                node.eachAdjacency(function() { count++; });
                //display node info in tooltip
                tip.innerHTML = "<div class=\"tip-title\">" + node.name + "</div>"
                  + "<div class=\"tip-text\"><b>connections:</b> " + count + "</div>";
              }
            },
            // Add node events
            Events: {
              enable: true,
              //Change cursor style when hovering a node
              onMouseEnter: function() {
                fd.canvas.getElement().style.cursor = 'move';
              },
              onMouseLeave: function() {
                fd.canvas.getElement().style.cursor = '';
              },
              //Update node positions when dragged
              onDragMove: function(node, eventInfo, e) {
                var pos = eventInfo.getPos();
                node.pos.setc(pos.x, pos.y);
                fd.plot();
              },
              //Implement the same handler for touchscreens
              onTouchMove: function(node, eventInfo, e) {
                $jit.util.event.stop(e); //stop default touchmove event
                this.onDragMove(node, eventInfo, e);
              },
              //Add also a click handler to nodes
              onClick: function(node) {
                if(!node) return;
                // Build the right column relations list.
                // This is done by traversing the clicked node connections.
                var html = "<h4>" + node.name + "</h4><b> connections:</b><ul><li>",
                    list = [];
                node.eachAdjacency(function(adj){
                  list.push(adj.nodeTo.name);
                });
                //append connections information
                $jit.id('inner-details').innerHTML = html + list.join("</li><li>") + "</li></ul>";
              }
            },
            //Number of iterations for the FD algorithm
            iterations: 200,
            //Edge length
            levelDistance: 230,
            
          });
          // load JSON data.
          fd.loadJSON(json);
          // compute positions incrementally and animate.
          fd.computeIncremental({
            iter: 40,
            property: 'end',
            onStep: function(perc){
              Log.write(perc + '% loaded...');
            },
            onComplete: function(){
              Log.write('done');
              fd.animate({
                modes: ['linear'],
                transition: $jit.Trans.Elastic.easeOut,
                duration: 2500
              });
            }
          });
          // end
        }
        
        
        </script>
    
  </head>

  <body onload="init();">
  <div id="container"> 
 
    <div id="left-container"> 
 
 
 
        <div class="text"> 
        <h4> 
            Plingbacks Node Graph    
        </h4> 
 
            
            You can <b>zoom</b> and <b>pan</b> the visualization by <b>scrolling</b> and <b>dragging</b>.<br /><br /> 
            You can <b>change node positions</b> by <b>dragging the nodes around</b>.<br /><br /> 
            The clicked node's connections are displayed in a relations list in the right column.<br /><br /> 
            
            <em>At the moment I only really expect this to work well in Chrome and recent Firefoxes. It might just work in IE...<br/><br/>
            I'd also like to make the graph centre better when it builds itself.<br/><br/></em>
            
            
            
        </div> 
 
        <div id="id-list"></div> 
 
          
</div> 
 
<div id="center-container"> 
    <div id="infovis"></div>    
</div> 
 
<div id="right-container"> 
 
<div id="inner-details"></div> 
 
</div> 
 
<div id="log"></div> 
</div> 
        <!--<div id="wrapper">
            <div id="header">
                <a href="http://www.plings/net"><img src="/images/Plings_badgebox_green.png" class="right"></a>
                <h1>PlingBack</h1>
            </div> 
            <div id="content">
                <h2>Feedback Node Id: <span>${feedback_id}</span></h2>
                 <div id="infovis"></div>  
                   <div id="id-list"></div> 
                   <div id="inner-details"></div> 
                   <div id="log"></div> 
            </div>
            <div id="footer">
            </div>
        </div>-->
  </body>
</html>
