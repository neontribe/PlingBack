/**
 * @author rupert
 */
var scope_name = 'fastfeedback';
window[scope_name] = {};
var ff = window[scope_name];

// Initial Configurations
ff.configure = function () {
	//Get the base config object
	var config = pb.configure();
	
	//Decorate it with our parameters
	
	config.plingback_type = "fastfeedback";
    
    config.plingback_version = "0.1 beta";
	
	config.slide_duration = 300;
	config.show_feedback_link = false;
	config.slides_before = ['attendance','rating_deterrent','comment','reviewer','thankyou'];
	config.slides_after = ['attendance','rating_deterrent', 'comment', 'reviewer','thankyou'];
	
	config.skin_color = pb.utils.getParameterByName('skin_color') ? pb.utils.getParameterByName('skin_color') : 'green' ;
	config.show_feedback_link = pb.utils.getParameterByName('show_feedback_link') ? pb.utils.getParameterByName('show_feedback_link') : config.show_feedback_link ;
	// Load the stlye for the current color choice
	$('link#css-colour').attr('href', colourHref = 'images/' + config.skin_color + '/colours.css');
	//Show a little 'view feedback' link
    if (config.show_feedback_link) {
		$('#bottom').append('<a href="'+config.plings_endpoint + config.pling_id + '/feedback" target="_top">view feedback</a>');
	}
	
    // Store a local reference to the config object
	ff.config = pb.config;
	
	pb.api.bind(pb.api.events.plingLoaded.toString(), ff.plingLoaded);
	pb.api.getPlingDetails(config.pling_id);

};


/**
 * Ui handler for pb.api.events.plingLoaded
 */
ff.plingLoaded = function() {

	ff.configure_slide_flow();
	ff.scroller.init();
	ff.ui.init();
	
	$('span.pling_name').text(ff.config.pling.Name);
	
	if ($('span.pling_name').width() > 250) {
		$('span.pling_name').wrapInner('<marquee direction="left" behavior="alternate" scrollamount="2"></marquee>');
	}
	
	ff.scroller.controller.trigger('goto', [0]);
	
};

ff.configure_slide_flow = function() {
	var flow = ff.config['slides_'+ff.config.mode];
	var slide_sources = $('#slides div.slide');
	slide_sources.remove();
	var nav_sources = $('#navigation a');
	nav_sources.remove();
	var flen = flow.length;
	for (var i=0; i<flen; i++) {
        var nav = jQuery.grep(nav_sources, function(n, index){return ($(n).attr('href') === '#'+flow[i]); });
        if ( nav ) { $(nav[0]).appendTo('#navigation'); }
		var slide = jQuery.grep(slide_sources, function(n, index){return ($(n).attr('id') === flow[i]); });
        if (slide) { $(slide[0]).appendTo('div.slides_container'); }
    }
	//Number the steps
	var final_nav = $('#navigation a');
	for (var j=0; j<final_nav.length; j++) {
		$(final_nav[j]).prepend(j + 1);
	}
	
	$('form').bind('submit', pb.api.send);
};

// Item Posting

ff.api = {};
ff.api.init = function () {
	//$('div.slide form').live('submit', pb.api.send); - busted in IE so we do it in ff.configure_slide_flow
	pb.api.bind(pb.api.events.formSending.toString(), ff.ui.form_sending);
	pb.api.bind(pb.api.events.formSent.toString(), ff.ui.form_sent);
};

// UI

ff.ui = {};

ff.ui.init = function() {
	// Reset form controls
	ff.ui.reset();
    
	ff.ui.attendance.init();
    ff.ui.stars.init();
	ff.ui.deterrent.init();
    ff.ui.comment.init();
    ff.ui.reviewer.init();
	ff.fb.ui.init();   
	
};

ff.ui.reset = function () {
	var forms = $('form');
	forms.each(function () { 
	   this.reset(); 
	   if ($(this).id === 'reviewer_form') {
	   	   $('input[name^="reviewer_"]', this).val('');
	   }
	});
};

ff.ui.enable_submission = function (form) {
	$('button.submit', form).removeAttr('disabled');
};

ff.ui.disable_submission = function (form) {
    $('button.submit', form).attr('disabled', 'disabled');
};

ff.ui.current_form = null;
ff.ui.form_sending = function (event) {
	ff.ui.current_form = $(event.form);
	$('button.submit', ff.ui.current_form).css({
		'background-position' : '0 -78px',
		'visibility' : 'visible'
	});
	$('input, textarea, button.submit', ff.ui.current_form).attr("disabled", "disabled");
};



ff.ui.form_sent = function (event) {
	// Watch for the last form and enable multiuser mode if needed
	if ($(ff.ui.current_form).attr('id') === 'reviewer_form' && ff.config.multiuser) {
		$('#the_end').empty();
		$('#the_end').text('Ready for the next person in ');
		$('#the_end').append('<span id="refresh_counter">5</span> seconds');
		
		// Log out of facebook if needed
		if ($('input[name="reviewer_id_source"]', ff.ui.current_form).val() === 'http://www.facebook.com') {
			ff.fb.logout();
		}
		
		
		setInterval(function () { $('#refresh_counter').text($('#refresh_counter').text() - 1);  }, 1000);
		setTimeout(function () { location.reload(true); }, 5100);
	}
	
	if (ff.scroller.skipTo !== null) {
		ff.scroller.controller.trigger('goto', [ff.scroller.skipTo]);
		ff.scroller.skipTo = null;
	} else {
		ff.scroller.controller.trigger('next');
	}
	
	
	// re-enable the last form and add a hidden element to signal that any subsequent send
	// should cause an overwite
	// The timeout is an attempt to ensure that this form is out of view before
	// its re-enabled :: NB surely this could be neater
	setTimeout(function () {
		  $('button.submit', ff.ui.current_form).css('background-position', '0 0');
		  $('input, textarea', ff.ui.current_form).removeAttr("disabled");
	      ff.ui.current_form.append('<input type="hidden" name="mode" value="overwrite"/>');
		}, ff.config.slide_duration + 500);
	
	
	
}; 

ff.ui.attendance = {};
ff.ui.attendance.init = function () {
	ff.ui.attendance.configure();
	$('#attendance form input[type="radio"]').bind('change', function() {
		ff.ui.enable_submission(this.form);
		ff.ui.deterrent.configure($(this).val());
	});
};

ff.ui.attendance.configure = function () {
	if (ff.config.mode === 'before') {
		ff.ui.comment.hint = 'eg. "I\'ll be coming if I can persuade my friends"';
		$('#attendance1').attr('value', 'willAttend').siblings('span').text("I'd like to go!");
	    $('#attendance2').attr('value', 'willNotAttend').siblings('span').text("I'm not going.");
	    $('#attendance h3').text("Going?");
		$('div#attendance input').click(function() {
			var whichInput = $(this).attr('value');
			if (whichInput === 'willAttend') {
				ff.ui.comment.hint = 'eg. "I\'ll be coming if I can persuade my friends"';
			} else {
				ff.ui.comment.hint = 'eg. "I like the sound of it but can\'t get there"';
			}
			ff.ui.comment.init();
			});
	} else {
		ff.ui.comment.hint = 'eg. "It was very inspiring but it started late"';
		$('div#attendance input').click(function() {
			var whichInput2 = $(this).attr('value');
			if (whichInput2 === 'attended') {
				ff.ui.comment.hint = 'eg. "It was very inspiring but it started late"';
			} else {
				ff.ui.comment.hint = 'eg. "I\'ll try to make it next week"';
			}
			ff.ui.comment.init();
			});
	}
	
};

ff.ui.deterrent = {};

ff.ui.deterrent.configure = function (attendance) {
	switch (attendance) {
		case 'didNotAttend':
		  $('#rating').hide();
		  $('#deterrent').show();
		  break;
		case 'attended':
		  $('#deterrent').hide();
          $('#rating').show();
		  break;
		// From here on we're handling cases wherethe event is in the future
		// the second slide may not be appropriate
		// Some hoops are jumped trough to make it possible
		// for the user to change their mind...
		case 'willNotAttend':
		  $('#rating_deterrent').show();
		  $('#rating').hide();
          $('#deterrent').show();
		  $('#navigation > a[href=#rating_deterrent]').show().animate({opacity:1.0}, 500);
          //Number the steps
          var final_nav = $('#navigation a');
          for (var j=0; j<final_nav.length; j++) {
            $(final_nav[j]).text(j + 1);
          }
          ff.scroller.skipTo = null;
		  break;
		case 'willAttend':
		  $('#rating_deterrent').hide();
		  $('#navigation > a[href=#rating_deterrent]').animate({opacity:0.0}, 500, function(){$('#navigation > a[href=#rating_deterrent]').hide();});
		  //Number the steps
          var m_final_nav = $('#navigation a[href!=#rating_deterrent]');
          for (var j2=0; j2<m_final_nav.length; j2++) {
            $(m_final_nav[j2]).text(j2 + 1);
          }
		  ff.scroller.skipTo = 2;
          break;
	}
};


ff.ui.deterrent.init = function () {

	$("#deterrent label").hover(
	  function () {
		var tipText = $(this).children().text();
		$('#deterrent-tip').text(tipText);
	  }, 
	  function () {
		$('#deterrent-tip').text('');
	});

	$('#deterrent label').toggle(function(event) {
						event.preventDefault();
						ff.ui.enable_submission(this.form);
						$(this)
							//.mouseout(function(event) {
								//console.log(event);
								//$(event.target)
								.addClass('chosen')
								.hover(function() {
									if ($(this).hasClass('chosen')) {
									$(this).addClass('hover');
									}
								}, function() {
									$(this).removeClass('hover');
								})
							//})
							.next('input[type=checkbox]')
							.attr('checked', 'checked');
						
					}, function(event) {
						event.preventDefault();
						$(this)
							.removeClass('chosen hover')
							.next('input[type=checkbox]')
							.attr('checked', '');
						if($('.chosen').length === 0) {
                            ff.ui.disable_submission(this.form);
                        }
					});
					
    $('#deterrent form').each(
	   function(){
	   	ff.ui.disable_submission(this);
	   }
	 );
};

ff.ui.stars = {'rubric':'Choose your Rating'};
ff.ui.stars.init = function () {
	
	$('#stars').stars({
		captionEl: $('#stars-cap'),
		callback: function(ui, type, value) {
			if (value > 0) {
				ff.ui.enable_submission($(ui.element).parents('form'));
				// 
			} else {
				ff.ui.disable_submission($(ui.element).parents('form'));
				$('#stars-cap').text(ff.ui.stars.rubric);
			}
			
		}
	});
	$('#stars-cap').text(ff.ui.stars.rubric);
};

ff.ui.comment = {};
ff.ui.comment.hint = $('#comment-on-it').attr('value');
ff.ui.comment.init = function () {
	$('#comment textarea').keyup(function() {
		if ($(this).val().length > 0) {
			ff.ui.enable_submission(this.form);
		} else {
			ff.ui.disable_submission(this.form);
		}
		
	});
	var comment_input = $('textarea#comment-on-it');
	comment_input.data('pb_hint', ff.ui.comment.hint);
	comment_input.val(ff.ui.comment.hint)
                      .css('color', '#999')
                      .focus(function() {
                                         if ($(this).val() === ff.ui.comment.hint) {
                                              $(this).val('')
											             .css('color', '#000');
                                         }
                                 })
                       .blur(function() {
                                       if ($(this).val() === '') {
                                            $(this).css({'color' : '#999'})
											       .val(ff.ui.comment.hint);
                                       }
                                });
};

ff.ui.reviewer = {};
ff.ui.validator_input = function (input, hint, validator, storage_selector) {
	var target = $(input);
	target.data('pb_hint', hint);
	target.val(hint)
          .css('color', '#999')
          .focus(function() {
                              if ($(this).val() === hint) {
                                 $(this).val('')
										.css('color', '#000');
                               }
                  })
           .blur(function() {
                               if ($(this).val() === '') {
                                   $(this).css('color', '#999')
										  .removeClass('invalid')
										  .val(hint);
                                }
                   });

	// Bind to changes on the form 
    target.keyup(function(){
		//Does the input validate against the supplied validator?
		//if so, copy it into the hidden input identified as the storage and enable the submit button
		var value = $(this).val();
		if (validator(value)) {
			$(this).removeClass('invalid');
			$(storage_selector, this.form).val(value);
			ff.ui.enable_submission(this.form);
		}
		else {
			if (value !== '') {
				$(this).addClass('invalid');
			}
			$(storage_selector, this.form).val('');
			ff.ui.disable_submission(this.form);
		}
		
	});
};

ff.ui.reviewer.init = function () {
    ff.ui.validator_input($('input[name=email]'), 'Your email...', pb.utils.validateEmail, 'input[name=reviewer_email]');
	ff.ui.validator_input($('input[name=phone]'), 'Your phone...', pb.utils.validatePhone, 'input[name=reviewer_phone]');
	
	$("#reviewer #unknown_user button").hover(
	  function () {
		var signText = $(this).text();
		$('#sign-tip').text(signText).css('padding', '5px 0 0 0');
	  }, 
	  function () {
		$('#sign-tip').text('').css('padding', '0');
	});

	var toggle_clicked = function (event) {
		var elem = $(event.target);
		
		//Clear any used inputs
        $('input[name^="reviewer_"]', this.form).val('');
        $('#phone, #email').val('');
		
		$(':animated', elem.form).stop(true, true);
		if (elem.hasClass('open')) { 
			switch (elem.attr('id')) {
				case 'email_button':
					$('div#email-form').hide();
					ff.ui.disable_submission(this.form);
					break;
				case 'phone_button':
					$('div#phone-form').hide();
					ff.ui.disable_submission(this.form);
					break;
				case 'anon_button':
					$('p#anonymous-text').hide();
					ff.ui.disable_submission(this.form);
					break;
			}
			elem.removeClass('open');
			$('#sign-tip').show();
		} else {
			var openable = null;
			switch (elem.attr('id')) {
				case 'email_button':
					openable = $('div#email-form');
					ff.ui.disable_submission(this.form);
					break;
				case 'phone_button':
					openable = $('div#phone-form');
					ff.ui.disable_submission(this.form);
					break;
				case 'anon_button':
					openable = $('p#anonymous-text');
					ff.ui.enable_submission(this.form);
					break;
			}
			
			
			openable.siblings('.slidey').hide();
			$('#sign-tip').hide();
			elem.siblings().removeClass('open');
			openable.slideDown('slow');
			elem.addClass('open');
		}
	};
	$('button#email_button').bind('click', toggle_clicked);
	$('button#phone_button').bind('click', toggle_clicked);
	$('button#anon_button').bind('click', toggle_clicked);
    // Handle toggling the email only form
	/**var etoggler = $('button#email_button');
    //etoggler.toggle(
	//		        function() {
					   $(':animated', this.form).stop(true, true).hide();
					   $('#sign-tip').css({'height':'0', 'padding':'0'}).hide();
					   $('div#phone-form').hide();
					   $('p#anonymous-text').hide();
			           $('div#email-form').slideDown('slow');
			        }, function () {
					   $(':animated', this.form).stop(true, true).hide();
					   $('div#email-form').slideUp('slow');
					   $('#sign-tip').css('padding','0').text('').show();
					}
              );
    */


    /* Handle toggling the phone form
	var togglerPhone = $('button#phone_button');
    togglerPhone.toggle(
			        function() {
					   $(':animated', this.form).stop(true, true).hide();
					   $('#sign-tip').css({'height':'0', 'padding':'0'}).hide();
					   $('div#email-form').hide();
					   $('p#anonymous-text').hide();
			           $('div#phone-form').slideDown('slow');
			        }, function () {
					   $(':animated', this.form).stop(true, true).hide();
					   $('div#phone-form').slideUp('slow');
					   $('#sign-tip').css('padding','0').text('').show();
					}
              );
	*/		  
	// Handle toggling the anonymous message
/*	var atoggler = $('button#anon_button');
    atoggler.toggle(
			        function() {
					   $('#sign-tip').css('height', '0').stop().hide();
			           $('p#anonymous-text').stop().slideDown('slow');
					   $('div#phone-form').stop().hide();
					   $('div#email-form').stop().hide();
					   $('input[name^="reviewer_"]', this.form).val('');
					   ff.ui.enable_submission(this.form);
			        }, function () {
					   $('p#anonymous-text').stop().slideUp('slow');
					   $('#sign-tip').css('padding','0').stop().show().text('');
					   ff.ui.disable_submission(this.form);
					}
              );
*/
    
};

// Scroller

ff.scroller = {};
ff.scroller.controller = null;
ff.scroller.skipTo = null;
ff.scroller.selectNav = function () {
	$(this)
        .parents('#navigation')
            .find('a')
                .removeClass('selected')
           .end()
    .end()
    .addClass('selected');
};

ff.scroller.init = function() {
	var panels = $('#slides .slides_container > div.slide');
	var navigation = $('#navigation a');
	var container = $('#slides .slides_container');
	ff.scroller.controller = container;
	var horizontal = true;
	var options = {
		// Assign the target whilst hiding any overflow
		target: $('#slides').css('overflow', 'hidden'),
        // can be a selector which will be relative to the target
        items: panels,
        navigation: navigation,
        // allow the scroll effect to run both directions
        axis: 'xy',
        onAfter: function (data) {
                var el = $('#navigation').find('a[href$="' + data.id + '"]').get(0);
                ff.scroller.selectNav.call(el);
            }, // our final callback
        // include padding in offset calculation
        offset: parseInt((horizontal ? container.css('paddingTop') : container.css('paddingLeft')) || 0) * -1,
        // duration of the sliding effect
        duration: ff.config.slide_duration,
        // easing - can be used with the easing plugin: 
        // http://gsgd.co.uk/sandbox/jquery/easing/
        easing: 'easeInSine',
		cycle: false
    };
	
	// Ensure the container is large enough for its content
	container.css('width', 
	   panels[0].offsetWidth * $('#slides .slides_container > div').length
	);

	
	$('#content').serialScroll(options);
	navigation.click(ff.scroller.selectNav);
	//Skip buttons
    $('em', navigation).click(function () {ff.scroller.controller.trigger('next');});
};

// Facebook
ff.fb = {app_id:'122322911120189'};
ff.fb.ui = {};
ff.fb.ui.init = function() {
    $('#fb_connect_button').bind('click', ff.fb.login);
	$('.fb_disconnect').live('click', ff.fb.disconnect);
    
};

// no user, clear display
ff.clear_user_info = function() {
    $('#user-info').hide('fast').empty();
    $('#unknown_user').show('fast');
};
 
ff.fb.handle_session_response = function(response) {
    if (!response.session) {
        ff.clear_user_info();
        return;
    }

     // if we have a session, query for the user's profile picture and name
     FB.api(
		'/me',
        function(response) {
			// Build out the display and the form for this user's details
            var user = response;
			var uic = $('#user-info');
			
			//uic.append('<fb:profile-pic uid="'+user.id+'"linked="false" facebook-logo="true" width="30" height="30"></fb:profile-pic>');
			uic.append('<h4><span class="fb_name"><b>Hello, '+user.first_name+'!</b></span></h4>');
			uic.append('<span>We would like to sign your feedback with:</span>');
			var stored_data = $('<div id="stored-data"></div>');
			stored_data.append('<span class="fb_birthday"><strong>BIRTHDAY:</strong> '+user.birthday+'</span>');
			stored_data.append('<span class="fb_email"><strong>EMAIL:</strong> '+user.email+'</span>');
			uic.append(stored_data);
			//uic.append('<span>Press play if okay...</span>');

            var form = $('#reviewer form');
			$('input[name="reviewer_email"]', form).val(user.email);
			$('input[name="reviewer_id"]', form).val(user.id);
			$('input[name="reviewer_birthday"]', form).val(user.birthday);
			$('input[name="reviewer_id_source"]', form).val('http://www.facebook.com');
			
			ff.ui.enable_submission(form);
			
			var disconnect = $('<button class="fb_disconnect" type="button">disconnect</button>');
            disconnect.prependTo('#button-controls');
			
			FB.XFBML.parse(document.getElementById('user-info'));
            uic.show();
            $('#unknown_user').hide();
        }
    );  
};

ff.fb.login = function() {
    FB.login(ff.fb.handle_session_response, {perms:'email,user_birthday'});
};

ff.fb.logout = function() {
    FB.logout(ff.fb.handle_session_response);
};

ff.fb.disconnect = function() {
	//Empty call back - doesn't fire when calling old rest api?
    FB.api({ method: 'Auth.revokeAuthorization' }, function(response) {});
	$('button.fb_disconnect').remove();
    ff.clear_user_info();
    ff.ui.disable_submission($('#reviewer form'));
};


