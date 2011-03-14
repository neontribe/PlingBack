/*!
 * jQuery UI Stars v3.0.1
 * http://plugins.jquery.com/project/Star_Rating_widget
 *
 * Copyright (c) 2010 Marek "Orkan" Zajac (orkans@gmail.com)
 * Dual licensed under the MIT and GPL licenses.
 * http://docs.jquery.com/License
 *
 * $Rev: 164 $
 * $Date:: 2010-05-01 #$
 * $Build: 35 (2010-05-01)
 *
 * Depends:
 *	jquery.ui.core.js
 *	jquery.ui.widget.js
 *
 */
(function($) {

$.widget('ui.stars', {
	options: {
		inputType: 'radio', // [radio|select]
		split: 0, // decrease number of stars by splitting each star into pieces [2|3|4|...]
		disabled: false, // set to [true] to make the stars initially disabled
		cancelTitle: 'Cancel Rating',
		cancelValue: 0, // default value of Cancel btn.
		cancelShow: true,
		disableValue: true, // set to [false] to not disable the hidden input when Cancel btn is clicked, so the value will present in POST data.
		oneVoteOnly: false,
		showTitles: false,
		captionEl: null, // jQuery object - target for text captions 
		callback: null, // function(ui, type, value, event)

		/*
		 * CSS classes
		 */
		starWidth: 16, // width of the star image
		cancelClass: 'ui-stars-cancel',
		starClass: 'ui-stars-star',
		starOnClass: 'ui-stars-star-on',
		starHoverClass: 'ui-stars-star-hover',
		starDisabledClass: 'ui-stars-star-disabled',
		cancelHoverClass: 'ui-stars-cancel-hover',
		cancelDisabledClass: 'ui-stars-cancel-disabled'
	},
	
	_create: function() {
		var self = this, o = this.options, starId = 0;
		this.element.data('former.stars', this.element.html());

		o.isSelect = o.inputType == 'select';
		this.$form = $(this.element).closest('form');
		this.$selec = o.isSelect ? $('select', this.element)  : null;
		this.$rboxs = o.isSelect ? $('option', this.$selec)   : $(':radio', this.element);

		/*
		 * Map all inputs from $rboxs array to Stars elements
		 */
		this.$stars = this.$rboxs.map(function(i)
		{
			var el = {
				value:      this.value,
				title:      (o.isSelect ? this.text : this.title) || this.value,
				isDefault:  (o.isSelect && this.defaultSelected) || this.defaultChecked
			};

			if(i==0) {
				o.split = typeof o.split != 'number' ? 0 : o.split;
				o.val2id = [];
				o.id2val = [];
				o.id2title = [];
				o.name = o.isSelect ? self.$selec.get(0).name : this.name;
				o.disabled = o.disabled || (o.isSelect ? $(self.$selec).attr('disabled') : $(this).attr('disabled'));
			}

			/*
			 * Consider it as a Cancel button?
			 */
			if(el.value == o.cancelValue) {
				o.cancelTitle = el.title;
				return null;
			}

			o.val2id[el.value] = starId;
			o.id2val[starId] = el.value;
			o.id2title[starId] = el.title;

			if(el.isDefault) {
				o.checked = starId;
				o.value = o.defaultValue = el.value;
				o.title = el.title;
			}

			var $s = $('<div/>').addClass(o.starClass);
			var $a = $('<a/>').attr('title', o.showTitles ? el.title : '').text(el.value);

			/*
			 * Prepare division settings
			 */
			if(o.split) {
				var oddeven = (starId % o.split);
				var stwidth = Math.floor(o.starWidth / o.split);
				$s.width(stwidth);
				$a.css('margin-left', '-' + (oddeven * stwidth) + 'px');
			}

			starId++;
			return $s.append($a).get(0);
		});

		/*
		 * How many Stars?
		 */
		o.items = starId;

		/*
		 * Remove old content
		 */
		o.isSelect ? this.$selec.remove() : this.$rboxs.remove();

		/*
		 * Append Stars interface
		 */
		this.$cancel = $('<div/>').addClass(o.cancelClass).append( $('<a/>').attr('title', o.showTitles ? o.cancelTitle : '').text(o.cancelValue) );
		o.cancelShow &= !o.disabled && !o.oneVoteOnly;
		o.cancelShow && this.element.append(this.$cancel);
		this.element.append(this.$stars);

		/*
		 * Initial selection
		 */
		if(o.checked === undefined) {
			o.checked = -1;
			o.value = o.defaultValue = o.cancelValue;
			o.title = '';
		}
		
		/*
		 * The only FORM element, that has been linked to the stars control. The value field is updated on each Star click event
		 */
		this.$value = $("<input type='hidden' name='"+o.name+"' value='"+o.value+"' />");
		this.element.append(this.$value);


		/*
		 * Attach stars event handler
		 */
		this.$stars.bind('click.stars', function(e) {
			if(!o.forceSelect && o.disabled) return false;

			var i = self.$stars.index(this);
			o.checked = i;
			o.value = o.id2val[i];
			o.title = o.id2title[i];
			self.$value.attr({disabled: o.disabled ? 'disabled' : '', value: o.value});

			fillTo(i, false);
			self._disableCancel();

			!o.forceSelect && self.callback(e, 'star');
		})
		.bind('mouseover.stars', function() {
			if(o.disabled) return false;
			var i = self.$stars.index(this);
			fillTo(i, true);
		})
		.bind('mouseout.stars', function() {
			if(o.disabled) return false;
			fillTo(self.options.checked, false);
		});


		/*
		 * Attach cancel event handler
		 */
		this.$cancel.bind('click.stars', function(e) {
			if(!o.forceSelect && (o.disabled || o.value == o.cancelValue)) return false;

			o.checked = -1;
			o.value = o.cancelValue;
			o.title = '';
			
			self.$value.val(o.value);
			o.disableValue && self.$value.attr({disabled: 'disabled'});

			fillNone();
			self._disableCancel();

			!o.forceSelect && self.callback(e, 'cancel');
		})
		.bind('mouseover.stars', function() {
			if(self._disableCancel()) return false;
			self.$cancel.addClass(o.cancelHoverClass);
			fillNone();
			self._showCap(o.cancelTitle);
		})
		.bind('mouseout.stars', function() {
			if(self._disableCancel()) return false;
			self.$cancel.removeClass(o.cancelHoverClass);
			self.$stars.triggerHandler('mouseout.stars');
		});


		/*
		 * Attach onReset event handler to the parent FORM
		 */
		this.$form.bind('reset.stars', function(){
			!o.disabled && self.select(o.defaultValue);
		});


		/*
		 * Clean up to avoid memory leaks in certain versions of IE 6
		 */
		$(window).unload(function(){
			self.$cancel.unbind('.stars');
			self.$stars.unbind('.stars');
			self.$form.unbind('.stars');
			self.$selec = self.$rboxs = self.$stars = self.$value = self.$cancel = self.$form = null;
		});


		/*
		 * Star selection helpers
		 */
		function fillTo(index, hover) {
			if(index != -1) {
				var addClass = hover ? o.starHoverClass : o.starOnClass;
				var remClass = hover ? o.starOnClass    : o.starHoverClass;
				self.$stars.eq(index).prevAll('.' + o.starClass).andSelf().removeClass(remClass).addClass(addClass);
				self.$stars.eq(index).nextAll('.' + o.starClass).removeClass(o.starHoverClass + ' ' + o.starOnClass);
				self._showCap(o.id2title[index]);
			}
			else fillNone();
		};
		function fillNone() {
			self.$stars.removeClass(o.starOnClass + ' ' + o.starHoverClass);
			self._showCap('');
		};


		/*
		 * Finally, set up the Stars
		 */
		this.select(o.value);
		o.disabled && this.disable();

	},

	/*
	 * Private functions
	 */
	_disableCancel: function() {
		var o = this.options, disabled = o.disabled || o.oneVoteOnly || (o.value == o.cancelValue);
		if(disabled)  this.$cancel.removeClass(o.cancelHoverClass).addClass(o.cancelDisabledClass);
		else          this.$cancel.removeClass(o.cancelDisabledClass);
		this.$cancel.css('opacity', disabled ? 0.5 : 1);
		return disabled;
	},
	_disableAll: function() {
		var o = this.options;
		this._disableCancel();
		if(o.disabled)  this.$stars.filter('div').addClass(o.starDisabledClass);
		else            this.$stars.filter('div').removeClass(o.starDisabledClass);
	},
	_showCap: function(s) {
		var o = this.options;
		if(o.captionEl) o.captionEl.text(s);
	},

	/*
	 * Public functions
	 */
	value: function() {
		return this.options.value;
	},
	select: function(val) {
		var o = this.options, e = (val == o.cancelValue) ? this.$cancel : this.$stars.eq(o.val2id[val]);
		o.forceSelect = true;
		e.triggerHandler('click.stars');
		o.forceSelect = false;
	},
	selectID: function(id) {
		var o = this.options, e = (id == -1) ? this.$cancel : this.$stars.eq(id);
		o.forceSelect = true;
		e.triggerHandler('click.stars');
		o.forceSelect = false;
	},
	enable: function() {
		this.options.disabled = false;
		this._disableAll();
	},
	disable: function() {
		this.options.disabled = true;
		this._disableAll();
	},
	destroy: function() {
		this.$form.unbind('.stars');
		this.$cancel.unbind('.stars').remove();
		this.$stars.unbind('.stars').remove();
		this.$value.remove();
		this.element.unbind('.stars').html(this.element.data('former.stars')).removeData('stars');
		return this;
	},
	callback: function(e, type) {
		var o = this.options;
		o.callback && o.callback(this, type, o.value, e);
		o.oneVoteOnly && !o.disabled && this.disable();
	}
});

$.extend($.ui.stars, {
	version: '3.0.1'
});

})(jQuery);
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

var stars = function(){
  var config = null;
  var caption = $('<span id="caption"></span>');
  var messageholder = $('<span id="message_holder"><span id="messages"></span></span>');
  var messages = $('#messages', messageholder);
  
  function form_sending(){
    caption.text('');
    messages.html('Saving').fadeIn(30);
  }
  
  function form_sent(){
    // Once the form's sent we need to fetch the current rating via the output api
    // then slide in a disabled stars thing showing it
    $.ajax({ 
      url:'/api/plings/' + config.pling_id + '/ratings',
      dataType: 'json',
      success: function(data, status, xhr) {
        $('#rating_title').text("Average Rating");
        $('#rat').data('stars').select( (Math.round(data.results.mean / 20)*20).toString() );
        var plur = (data.results.count > 1) ? 's' :'';
        caption.text(" (" + data.results.count + " vote" + plur + ")");
        
        // Display confirmation message to the user
        messages.text("Thanks!").stop().css("opacity", 1).fadeIn(30);
    
        // Hide confirmation message after 2 sec...
        setTimeout(function(){
          $("#messages").fadeOut(1000);
        }, 2000);
      }
    });
  }
  
  function init(){
    // Configure the api
    config = pb.configure();
    config.plingback_type = "stars";
    config.plingback_version = "0.2 alpha";
  
    // set up the ui
    $("#rat").children().not("select, #rating_title").hide();
    $('#rat').stars({inputType: "select",
                     captionEl: caption,
                     oneVoteOnly: true,
                     callback: function(ui, type, value){
                          pb.api.send({target:{form:ui.$form}});
                        }
                     });
    
    // Put the caption and message elements AFTER the stars
    
    messageholder.appendTo('#details');
  caption.appendTo('#details');
    
    // listen for the sucessful submission
    pb.api.bind(pb.api.events.formSending.toString(), form_sending);
    pb.api.bind(pb.api.events.formSent.toString(), form_sent);
  
  //All done? Fade in the ui
  $('#ui').fadeIn();
    
  }
  
  // Expose public api via a returned pointer object
  return {
    init:init
  };
}();
      
stars.init();