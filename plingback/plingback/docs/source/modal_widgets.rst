.. _modal-widgets-label:

*******************************
Modal Presentations For Widgets
*******************************

Overview
========

For situations where screen estate is at a premium a modal wrapper has been
provided for the Fastfeedback widget.

When a site visitor clicks on a suitably configured button element a fastfeedback
widget will be displayed (with an additional *close* control) on an overlay on 
top of the current page.

**N.B. No modal wrapper is available for topbar at present**

Try the Plingback Button as a :ref:`greasemonkey-scripts-label` 

Deployment
==========

There are two necessary steps to deploy a button which will launch a 
fastfeedback widget in a modal overlay:

    1. Add a `button` element with a class of `plingback_button` and the relevant pling id as its value.
    2. Load the plingback_modal javascript (ideally at the end of the document body)
    
    .. code-block:: html
    
        <button class="plingback_button" value="44730"><span>Give Feedback</span></button>
        <script type="text/javascript" 
            src="http://plingback.appspot.com/widgets/wrappers/modal/plingback_modal.min.js"></script>
            

Button Styling
--------------
            
The button element can be styled in any way to suit the environment. An example button image and styling follow:

    .. image:: _static/_images/plingback_button.png

    .. code-block:: css
        
        .plingback_button {
			border:0;
			width:200px;
			height:50px;
			background:transparent url(/widgets/wrappers/modal/plingback_button.png) no-repeat left top;
		}
        
        .plingback_button span { display: none; }

		.plingback_button:hover {
			background-position:0 -50px;
		}

Delaying Initialisation
-----------------------

The plingback_modal script will scan the document for plingback buttons as soon as 
it loads. If you need to avoid this behaviour set a global variable 'plingbackbutton_defer_init' to true.
You'll then need to call plingbackbutton() yourself at an appropriate juncture.
 
Plingback button works best when the script is included at the end of
the body tag. Alternatively you can load it in the head after setting 
plingbackbutton_defer_init = true and then run plingbackbutton() on
document.ready() (or appropriate for your environment).