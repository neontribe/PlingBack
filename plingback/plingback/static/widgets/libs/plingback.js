/**
 * @author rupert
 */
var scope_name = 'plingback';
window[scope_name] = {};
var pb = window[scope_name];

//Initial Configurations
pb.config = {'gen_feedback_id':true,
			 'fixed_feedback_id':false,
			 'feedback_uri':null};


pb.configure = function () {
	
	//pb.config.plings_endpoint = "/api/plings_proxy/";
	pb.config.plings_endpoint = "http://feeds.plings.net/activity.php/";
	pb.config.pling_id = pb.utils.getParameterByName('pling_id');
	
	//Take responsibility for generating feedback ids
	if (pb.config.gen_feedback_id) {
		pb.config.feedback_id = pb.utils.genUUID();
	}
	
	// Respect any fixed_feedback_id which has been supplied
	if (pb.config.fixed_feedback_id) {
		pb.config.feedback_id = pb.config.fixed_feedback_id;
	}
	
	// Detect multiuser mode
	pb.config.multiuser = pb.utils.getParameterByName('multiuser') ? true : false;
	
	pb.config.thanks_url_id = pb.utils.getParameterByName('thanks_url');
	    
	pb.config.plingback_endpoint = "/api/plingbacks";
	
	return pb.config;
};

/**
 * pb.api 
 */
pb.api = $({});

pb.api.events = {plingLoaded:{name:'plingLoaded',
	  							doc:'Triggered when pling data has been fetched. Provides access to the data as event.pling',
	  							attrs:['pling'],
	  							toString: function(){return this.name;}},
	  			formSending:{name:'formSending',
	  							doc:'Triggered when a form has been serialized we are awaiting the server response. Provides access to the form object as event.form',
	  							attr:['form'],
	  							toString: function(){return this.name;}},
	  			formSent:{name:'formSent',
	  							doc:'Triggered when a server response to a form send has been recieved. Provides access to the response as event.data',
	  							attr:['data'],
	  							toString: function(){return this.name;}}
				};



pb.api.getPlingDetails = function(pling_id, ui_callback) {
	$.getJSON(pb.config.plings_endpoint 
	        + pb.config.pling_id.toString()
			+ '.json?suppressLinkedActivities=true&callback=?', pb.api.pling_loaded);
};

pb.api.pling_loaded = function(pling) {
	pb.config.pling = pling.activity;
	// Choose our mode based on the current time and the pling start time
	if (Date.parseString(pb.config.pling.Starts, 'yyyy-MM-dd HH:mm:ss').isBefore(new Date())) {
		pb.config.mode = 'after';
	} else {
		pb.config.mode = 'before';
	}
	
	//Emit an event
	var event = jQuery.Event(pb.api.events.plingLoaded.toString());
	event.pling = pb.config.pling;
	pb.api.trigger(event);
	
};


pb.api.send = function (event) {
	var form = null;
	if (event.target.tagName === 'FORM') {
		form = $(event.target);
	} else {
		form = $(event.target.form);
	}
	
	var data = {};
	data.pling_id = pb.config.pling_id;
	data.plingback_type = pb.config.plingback_type;
  data.plingback_version = pb.config.plingback_version;
	
	//Rip through the form removing the hint text for any fields which have one
	$('input', form).each(function(){
		$(this).val($(this).val() === $(this).data('pb_hint') ? '' : $(this).val());
	});
	
	//Extract successful fields from the form
	var form_data = form.serializeArray();
	jQuery.each(form.serializeArray(), function(i,v){
		//Try to supress useless submissions
		if ( v.value === 0 || v.value ) {
			if (data.hasOwnProperty(v.name)) {
	            if (data[v.name] instanceof Array) {
	                data[v.name].push(v.value);
	            } else {
	                data[v.name] = [data[v.name], v.value];
	            }
	        } else {
	            data[v.name] = v.value;
	        }
		}
	});

	
	var url = pb.config.plingback_endpoint;
	var type = 'post'; // Default to posting to the endpoint - we'll look for a feedback_id in the return
	if (pb.config.feedback_id) {
		// We know our id so we're bound to be doing a PUT
        data.feedback_id = pb.config.feedback_id;
		url += '/';
		url += pb.config.feedback_id;
		type = 'put';
		
		// We've spoken to the server before so we'll POST to the attribute
		// the attribute name is the id of the form
		if (pb.config.feedback_uri) {
			type = 'post';
			url += '/';
            url +=  data.feedback_attribute;
		}
		// Check for a marker in the form to tell us that this is an update
		if ($('input[name=mode]', form).val() === 'overwrite') { 
            // We've submitted this attribute previously
            // so we append the put to the attribute name in order to overwite
            type = 'put';
		}
    }
    
	
	jQuery.ajax({
	   type: type,
	   url: url, 
	   data:data, 
	   success: pb.api.sendCallback, 
	   dataType: "json"
	   });
	
	var sending_event = jQuery.Event(pb.api.events.formSending.toString());
	sending_event.form = form;
	pb.api.trigger(sending_event);
	return false;
};

pb.api.sendCallback = function (data) {
	pb.config.feedback_id = data.feedback_id;
	pb.config.feedback_uri = data.feedback_uri;	
	var event = jQuery.Event(pb.api.events.formSent.toString());
	event.data = data;
	pb.api.trigger(event);
};

//Utilities
pb.utils = {};

pb.utils.getParameterByName = function (name) {
	name = name.replace(/[\[]/,"\\\[").replace(/[\]]/,"\\\]");
	var regexS = "[\\?&]"+name+"=([^&#]*)";
	var regex = new RegExp( regexS );
	var results = regex.exec( window.location.href );
	if( results === null ) {
		return "";
	} else {
		return results[1];
	}
};

/**
 * genUUID is taken from 
 * Math.uuid.js (v1.4)
 * http://www.broofa.com
 * mailto:robert@broofa.com
 */
pb.utils.genUUID = function() {
    return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function(c) {
      var r = Math.random()*16|0, v = c == 'x' ? r : (r&0x3|0x8);
      return v.toString(16);
    }).toUpperCase();
};

pb.utils.validateEmail = function(email) {
	// regex from Scott Gonzalez: http://projects.scottsplayground.com/email_address_validation/
	var validator = /^((([a-z]|\d|[!#\$%&'\*\+\-\/=\?\^_`{\|}~]|[\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF])+(\.([a-z]|\d|[!#\$%&'\*\+\-\/=\?\^_`{\|}~]|[\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF])+)*)|((\x22)((((\x20|\x09)*(\x0d\x0a))?(\x20|\x09)+)?(([\x01-\x08\x0b\x0c\x0e-\x1f\x7f]|\x21|[\x23-\x5b]|[\x5d-\x7e]|[\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF])|(\\([\x01-\x09\x0b\x0c\x0d-\x7f]|[\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF]))))*(((\x20|\x09)*(\x0d\x0a))?(\x20|\x09)+)?(\x22)))@((([a-z]|\d|[\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF])|(([a-z]|\d|[\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF])([a-z]|\d|-|\.|_|~|[\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF])*([a-z]|\d|[\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF])))\.)+(([a-z]|[\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF])|(([a-z]|[\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF])([a-z]|\d|-|\.|_|~|[\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF])*([a-z]|[\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF])))\.?$/i;
    
	return validator.test(email);
};

pb.utils.validatePhone = function(phone) {
	var phoneTrimmed = phone.replace(/\s+/g, "");
	var validator = /^((\+\d{1,3}(-| |\s)?\(?\d\)?(-| |\s)?\d{1,5})|(\(?\d{2,6}\)?))(-| |\s)?(\d{3,4})(-| |\s)?(\d{4})(( x| ext)\d{1,5}){0,1}$/;
	return validator.test(phoneTrimmed);
};
