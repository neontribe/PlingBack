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