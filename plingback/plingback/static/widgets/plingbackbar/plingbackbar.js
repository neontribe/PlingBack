/**
 * @author rupert
 */
			
var scope_name = 'plingbackbar';
window[scope_name] = {};
var pbb = window[scope_name];

// Initial Configurations
pbb.configure = function () {
	//Get the base config object
	var config = pb.configure();
	config.show_feedback_link = false;
	//Decorate it with our parameters
	config.show_feedback_link = pb.utils.getParameterByName('show_feedback_link') ? pb.utils.getParameterByName('show_feedback_link') : config.show_feedback_link ;
	config.plingback_type = "topbar";
    config.plingback_version = "0.1 beta";
	//Show a little 'view feedback' link
    if (config.show_feedback_link) {
		$('div#wrapper').append('<a href="'+config.plings_endpoint + config.pling_id + '/feedback" target="_top">view feedback</a>');
	}
	
    // Store a local reference to the config object
	pbb.config = pb.config;
	
	// Bind to api events
	pb.api.bind(pb.api.events.plingLoaded.toString(), pbb.plingLoaded);
	pb.api.bind(pb.api.events.formSending.toString(), pbb.formSending);
	pb.api.bind(pb.api.events.formSent.toString(), pbb.formSent);
	pb.api.getPlingDetails(config.pling_id);

};

/**
 * Ui handler for pling loaded
 */
pbb.plingLoaded = function(event) {
	
	
	// before/after switching
	if (pbb.config.mode === 'before') {
			// if we're pre-event suppress the rating widget
			$('#rating').remove();
			
			// Configure comment settings
			$('#comment-heading').text('Write a comment?');
			pbb.ui.hintValComments = 'e.g. "My third time..."';
			$('#comment-on-it').val(pbb.ui.hintValComments);
			$('#comment-on-it').data('pb_hint', pbb.ui.hintValComments);
	}

    // always
	// Watch for attendance changes to switch the rating mode
    pbb.ui.bind('dataChanged', pbb.ui.switchRatingMode);
	//Change attendance settings
    $('#attendance h2').text((pbb.config.mode === 'before') ? 'Going?' : 'Been?');
    $('#attendance1').val((pbb.config.mode === 'before') ? 'willAttend' : 'attended');
    $('#attendance2').val((pbb.config.mode === 'before') ? 'willNotAttend' : 'didNotAttend');

    $('div#widget-loading').fadeOut('slow', function(){$('div#widget-loading').remove();});

};

/**
 * Ui handler for form sending
 */
pbb.formSending = function(event) {
	var form = event.form; //The form element which fired the submit
	$('<div id="widget-sending">' + 
			'<img src="images/loading_cog.gif" alt="" />' +
			'<br/>' + 
			'...sending...' +
	  '</div>')
	.prependTo('div#wrapper')
	.fadeIn('slow');
};

/**
 * Ui handler for form sent
 */
pbb.formSent = function(event) {
	var data = event.data; //The response from the server
	$('div#widget-sending').remove();
	$('form').remove();
	$('<a id="plings-logo" href="http://www.plings.net/search" target="_top"><span>plings.net</span></a>')
		.insertAfter('h1');
	$('<img id="thank-you" src="images/thankyou.png" alt="Thank you for your feedback! It has been sent to Plings.net" />')
		.insertAfter('h1');
};


pbb.api = {};
pbb.api.init = function () {
	$('form').bind('submit', pb.api.send);
	$('form').bind('reset', pbb.ui.reset);
	//pb.api.bind(pb.api.events.formSending.toString(), function(event){$('.status').text('sending...');});
	//pb.api.bind(pb.api.events.formSent.toString(), function(event){$('.status').text('sent...');});
};

pbb.ui = $({});

pbb.ui.events = {dataChanged:{name:'dataChanged',
                                doc:'Triggered when the user has input data to a widget. Provides access to the data input fieldname as event.field and its validit as event.valid',
                                attrs:['data', 'field', 'valid'],
                                toString: function(){return this.name;},
								trigger: function (field, data, valid) {
									var event = jQuery.Event(this.toString());
									event.field = field;
									event.field_data = data;
									event.valid = valid;
									pbb.ui.trigger(event);
								}}
				};
pbb.ui.submissionTracker = {};
pbb.ui.submissionManager = function (event) {
	if (!event.field_data) {
		delete pbb.ui.submissionTracker[event.field];
	} else {
		pbb.ui.submissionTracker[event.field] = event.valid;
	}
	var form_submissible = true;
	jQuery.each(pbb.ui.submissionTracker, function (key, value){
		if (!value) {
			form_submissible = false;
		}
	});
	if (form_submissible && !jQuery.isEmptyObject(pbb.ui.submissionTracker)) {
	   $('#pbform>button').show();	
	} else {
	   $('#pbform>button').hide();
	}
};

pbb.ui.reset = function() {

	//reset attendance
	if(!$('a#yes-no').hasClass('yes')) {
		$('a#yes-no').trigger('click');
		pbb.ui.events.dataChanged.trigger('attendance', false, false);
	}
	//reset rating
	$('div.ui-stars-cancel a').trigger('click');
	pbb.ui.events.dataChanged.trigger('rating', false, false);
	
	//reset deterrence
	$("input[name='deterrent_value']").removeAttr('checked');
	
	//reset comment
	$('input#comment-on-it').val('').trigger('blur').val(pbb.ui.hintValComments);
	
	//reset reviewer - call a helper for this 'cos we do it a lot
	if ($('#reviewer a:visible').length === 1) {
		pbb.ui.hideReviewerInputs($('#reviewer a:visible'));
	}
	
	return false;
	
};

pbb.ui.switchRatingMode = function(event) {
	if (event.field === 'attendance') {
	   switch (event.field_data) {
	       case 'didNotAttend':
		   pbb.ui.hintValComments = 'e.g. "Didn\'t hear about it"';
		     // $('#rating').hide();
			  //$('#deterrent').show();
			  var openWidth = $('#rating').width();
			  var openWidthUnits = openWidth + 'px';
			  $('#deterrent').css('display', 'none');
			  $('#rating')
				.css({'width' : openWidthUnits})
					.children()
						.fadeOut(250);
				$('#rating')
				.stop()
				.animate({
				opacity: '0'
				}, 250, function() {
					$(this).animate({
					width: '0px'
					}, 250, function() {
						$(this).css('display','none');
						$('#deterrent').css({'width':'0px', 'opacity': '0'})
						.stop()
						.animate({
						width:'132px'
						}, 250, function() {
							$('#deterrent').animate({
							opacity:'1.0'
							}, 250
							)
							.children('h2, div').fadeIn(250);
						});	
					});
				});
		      break;
		   case 'willNotAttend':
			  // Configure comment settings
			  //$('#comment-heading').text('Write a comment?');
			  pbb.ui.hintValComments = 'e.g. "Too late at night"';
		     // $('#rating').hide();
			  //$('#deterrent').show();
			  var openWidth = $('#rating').width();
			  var openWidthUnits = openWidth + 'px';
			  $('#deterrent').css('display', 'none');
			  $('#rating')
				.css({'width' : openWidthUnits})
					.children()
						.fadeOut(250);
				$('#rating')
				.stop()
				.animate({
				opacity: '0'
				}, 250, function() {
					$(this).animate({
					width: '0px'
					}, 250, function() {
						$(this).css('display','none');
						$('#deterrent').css({'width':'0px', 'opacity': '0'})
						.stop()
						.animate({
						width:'132px'
						}, 250, function() {
							$('#deterrent').animate({
							opacity:'1.0'
							}, 250
							)
							.children('h2, div').fadeIn(250);
						});	
					});
				});
		      break;
		   case 'attended':
		   pbb.ui.hintValComments = 'e.g. "I would go again"';
		     // $('#rating').show();
			  //$('#deterrent').hide();
			  var openWidth = $('#deterrent').width();
			  var openWidthUnits = openWidth + 'px';
			  $('#rating').css('display', 'none');
			  $('#deterrent')
				.css({'width' : openWidthUnits})
					.children()
						.fadeOut(250);
				$('#deterrent')
				.stop()
				.animate({
				opacity: '0'
				}, 250, function() {
					$(this).animate({
					width: '0px'
					}, 250, function() {
						$(this).css('display','none');
						$('#rating').css({'width':'0px', 'opacity': '0'})
						.stop()
						.animate({
						width:'168px'
						}, 250, function() {
							$('#rating').animate({
							opacity:'1.0'
							}, 250
							)
							.children('h2, div').fadeIn(250);
						});	
					});
				});
		      break;
		   case 'willAttend':
		   pbb.ui.hintValComments = 'e.g. "My third time..."';
		      $('#rating').hide();
			  $('#deterrent').hide();
		      break;
	   }
	   $('#comment-on-it').val(pbb.ui.hintValComments);
	   $('#comment-on-it').data('pb_hint', pbb.ui.hintValComments);
	}
	
};

pbb.ui.hideReviewerInputs = function(button) {
	var action_button = $(button);
	if (action_button.attr('id') === 'fb_connect_button') { pbb.fb.disconnect(); }
	var removed = $('#sign-input').children('.transient').remove();
	removed.each(function(){pbb.ui.events.dataChanged.trigger($(this).attr('id'), false, false);});
	action_button.siblings('a').show();
	action_button.children('span').css('visibility', 'visible');
	action_button.removeClass('lonely-icon');
	$('#reviewer input[name^=reviewer_]').val('');
};
            
pbb.ui.showReviewerInput = function() {
                
	var update = function(button){
	    // Returns a function which, thanks to this closure, has access to input_type
	    // when it is eventually called we use a count to make sure we only do this once per invocation
	    var counter = 0;
	    return function(){
	        counter = counter + 1;
	        if ( counter === 1) {
	            var input = null;
	            switch (button.attr('id')) {
					case 'phone_button':
						input = $('<input class="transient" type="text" name="phone" id="phone" value="Your phone"/>');
						pbb.ui.init_field(input, 'Your phone...', pb.utils.validatePhone, 'input[name=reviewer_phone]');
						break;
					case 'email_button':
						input = $('<input class="transient" type="text" name="email" id="email" value="Your email"/>');
						pbb.ui.init_field(input, 'Your email...', pb.utils.validateEmail, 'input[name=reviewer_email]');
						break;
					case 'fb_connect_button':
						pbb.fb.login();
						break;
					default:
						input = $('<strong class="transient">Anonymous</strong>');
						break;
				}
						
				if (input) {
					input.appendTo('#sign-input');
				}

                button.addClass('lonely-icon');
	        }
	    };
	    
	};
	
	if ($(this).siblings('a:visible').length > 0) {
	    // In state one
	    $(this).children('span').css('visibility', 'hidden');
	    $(this).siblings('a').fadeOut('fast', update($(this)));
	    //$(this).addClass('lonely-icon');
	
	} else {
	    // return to state one
	    pbb.ui.hideReviewerInputs(this);
	}
                
};

pbb.ui.init_field = function (input, hint, validator, storage_selector) {
        var target = input;
		target.data('storage_selector', storage_selector);
		target.data('pb_hint', hint);
        target.val(hint)
              .css('color', '#666')
              .focus(function() {
                                  if ($(this).val() === hint) {
                                     $(this).val('')
                                            .css('color', '#000');
                                   }
                      })
               .blur(function() {
                                   if ($(this).val() === '') {
                                       $(this).css('color', '#666')
                                              .removeClass('invalid')
											  .removeClass('valid')
                                              .val(hint);
                                    }
                       });
    
        // Bind to changes on the form 
        target.bind('input paste change keyup', function(e){
            //Does the input validate against the supplied validator?
            //if so, copy it into the hidden input identified as the storage and fire an event
            var value = jQuery.trim($(this).val());
            if (validator(value)) {
                $(this).removeClass('invalid');
				$(this).addClass('valid');
                $($(this).data('storage_selector'), this.form).val(value);
                pbb.ui.events.dataChanged.trigger($(this).attr('id'), value, true);
            }
            else {
                if (value !== '') {
                    $(this).addClass('invalid');
                }
                $($(this).data('storage_selector'), this.form).val('');
                pbb.ui.events.dataChanged.trigger($(this).attr('id'), value, false);
            }
            
            
        });
    };
	
pbb.ui.hintValComments = 'eg."Started late but fun"';
pbb.ui.init = function(){
	
	$('#pbform>button').hide();
	pbb.ui.bind(pbb.ui.events.dataChanged.toString(), pbb.ui.submissionManager);
	
	// Setup the attendance
	$('a#yes-no').click(function(){
		if ($(this).hasClass('yes')) {
			$(this).removeClass('yes');
            $(this).siblings('input.false').attr('checked', 'checked');
            pbb.ui.events.dataChanged.trigger('attendance', $("input[name='attendance_value']:checked").val(), true);
		} else {
			$(this).addClass('yes');
            $(this).siblings('input.true').attr('checked', 'checked');
            pbb.ui.events.dataChanged.trigger('attendance', $("input[name='attendance_value']:checked").val(), true);
		}
	});
	
	
	
	// Setup star rating
	$('#stars').stars({
		captionEl: $('#stars-cap'),
		cancelTitle: 'Clear rating',
		callback: function(ui, type, value, event){
			pbb.ui.events.dataChanged.trigger('rating', value, (value > 0) ? true : false);
		}
	});
	
	
	var comment_input = $('input#comment-on-it');
	//Pass the hint along for later evaluation
	comment_input.data('pb_hint', pbb.ui.hintValComments);
	comment_input.val(pbb.ui.hintValComments).css('color', '#666').keyup(function(){
		$(this).css('background-position', '0 -20px');
		if ($(this).val()) {
			pbb.ui.events.dataChanged.trigger('comment', $(this).val(), true);
		}
		else {
			pbb.ui.events.dataChanged.trigger('comment', false, false);
		}
	}).focus(function(){
		if ($(this).val() === pbb.ui.hintValComments) {
			$(this).val('').css('color', '#000').keyup(function(){
				$('#char-count').css('visibility', 'visible');
			});
		}
	}).blur(function(){
		if ($(this).val() === '') {
			$(this).css({
				'color': '#666',
				'background-position': '0 0'
			}).val(pbb.ui.hintValComments);
			$('#char-count').css('visibility', 'hidden');
		}
	});
	
	// Setup for the comment box
	var textCountOptions = {
		'maxCharacterSize': 140,
		'textFontSize': '11px',
		'textColor': '#999',
		'textAlign': 'right',
		'warningColor': '#a64444',
		'warningNumber': 40,
		'isCharacterCount': true,
		'isWordCount': false,
		'customCounter': 'span#char-count',
		'resultPrefix': ''
	};
	$('input#comment-on-it').textareaCount(textCountOptions);
	
	//Setup Reviewer
	$('#unknown_user>div.buttons>a').bind('click', pbb.ui.showReviewerInput);
	
};

// Facebook
pbb.fb = {app_id:'122322911120189'};
pbb.fb.ui = {};
/**
 * Initialize any Facebook UI
 */
pbb.fb.ui.init = function() {
	//$('#fb_connect_button').bind('click', pbb.fb.login);
	//$('#fb_disconnect_button').live('click', pbb.fb.disconnect);
};

//no user, clear display
pbb.clear_user_info = function() {
    //$('#user-info').hide('fast').empty();
    //$('#unknown_user').show('fast');
};

/**
 * Act on discovery of user's fb connect state
 */
pbb.fb.handle_session_response = function(response) {
	if (!response.session) {
		pbb.ui.hideReviewerInputs($('#reviewer a:visible'));
        return;
    }

     // if we have a session, query for the user's profile picture and name
     FB.api(
		'/me',
        function(response) {
			// Build out the display and the form for this user's details
            var user = response;
			var si = $('#sign-input');
			si.html('');
			si.append('<span class="fb_birthday transient"><strong>BIRTHDAY:</strong>'+user.birthday+'</span>');
			si.append('<br class="transient"/>');
			si.append('<span class="fb_email transient"><strong>EMAIL:</strong>'+user.email+'</span>');
			$('#fb_connect_button').addClass('lonely-icon');
            var form = $('#pbform');
			$('input[name="reviewer_email"]', form).val(user.email);
			$('input[name="reviewer_id"]', form).val(user.id);
			$('input[name="reviewer_birthday"]', form).val(user.birthday);
			$('input[name="reviewer_id_source"]', form).val('http://www.facebook.com');
			
			pbb.ui.events.dataChanged.trigger('facebook', user, true);
        }
    );  
};

pbb.fb.login = function() {
    FB.login(pbb.fb.handle_session_response, {perms:'email,user_birthday'});
};

pbb.fb.logout = function() {
    FB.logout(pbb.fb.handle_session_response);
};

pbb.fb.disconnect = function() {
    FB.api({ method: 'Auth.revokeAuthorization' }, function(response) {});
	pbb.ui.events.dataChanged.trigger('facebook', false, false);
};