/*
	Read Only by HTML5 UP
	html5up.net | @n33co
	Free for personal and commercial use under the CCA 3.0 license (html5up.net/license)
*/

(function($) {

	skel.breakpoints({
		xlarge: '(max-width: 1680px)',
		large: '(max-width: 1280px)',
		medium: '(max-width: 1024px)',
		small: '(max-width: 736px)',
		xsmall: '(max-width: 480px)'
	});

	$(function() {

		var $body = $('body'),
			$header = $('#header'),
			$nav = $('#nav'), $nav_a = $nav.find('a'),
			$wrapper = $('#wrapper');

		// Fix: Placeholder polyfill.
			$('form').placeholder();

		// Prioritize "important" elements on medium.
			skel.on('+medium -medium', function() {
				$.prioritize(
					'.important\\28 medium\\29',
					skel.breakpoint('medium').active
				);
			});

		// Header.
			var ids = [];

			// Set up nav items.
				$nav_a
					.scrolly({ offset: 44 })
					.on('click', function(event) {

						var $this = $(this),
							href = $this.attr('href');

						// Not an internal link? Bail.
							if (href.charAt(0) != '#')
								return;

						// Prevent default behavior.
							event.preventDefault();

						// Remove active class from all links and mark them as locked (so scrollzer leaves them alone).
							$nav_a
								.removeClass('active')
								.addClass('scrollzer-locked');

						// Set active class on this link.
							$this.addClass('active');

					})
					.each(function() {

						var $this = $(this),
							href = $this.attr('href'),
							id;

						// Not an internal link? Bail.
							if (href.charAt(0) != '#')
								return;

						// Add to scrollzer ID list.
							id = href.substring(1);
							$this.attr('id', id + '-link');
							ids.push(id);

					});

			// Initialize scrollzer.
				$.scrollzer(ids, { pad: 300, lastHack: true });

		// Off-Canvas Navigation.

			// Title Bar.
				$(
					'<div id="titleBar">' +
						'<a href="#header" class="toggle"></a>' +
						'<span class="title">' + $('#logo').html() + '</span>' +
					'</div>'
				)
					.appendTo($body);

			// Header.
				$('#header')
					.panel({
						delay: 500,
						hideOnClick: true,
						hideOnSwipe: true,
						resetScroll: true,
						resetForms: true,
						side: 'right',
						target: $body,
						visibleClass: 'header-visible'
					});

			// Fix: Remove navPanel transitions on WP<10 (poor/buggy performance).
				if (skel.vars.os == 'wp' && skel.vars.osVersion < 10)
					$('#titleBar, #header, #wrapper')
						.css('transition', 'none');
	});

})(jQuery);

send_ajax = function (url, data) {
	$.ajax({
		url: url,
		type: 'post',
		data: data,
		success: function (data) {
			console.log(data);
		}
	})
};

function read_less_more(less_id, more_id, less_more){
	var more_obj = document.getElementById(more_id);
	var less_obj = document.getElementById(less_id);
	if(less_more==='more'){
		less_obj.hidden = true;
		more_obj.hidden = false
	}
	else{
		less_obj.hidden = false;
		more_obj.hidden = true
	}

}

function send_email(){
	var data = {};
	var required_fields = ['name', 'email', 'subject', 'message'];
	for(var i=0; i<required_fields.length; i++){
		var field_obj = document.getElementById(required_fields[i]);
		console.log(field_obj.value);
		var field_obj_val = field_obj.value;
		if(field_obj_val){
			data[required_fields[i]] = field_obj_val;
		}
		else{
			swal({title: "Please fill all fields",text: "Please fill <span style='color:#F8BB86'>"+required_fields[i]+ "</span> field.", timer:3000, html: true });
			return
		}
	}
	$.ajax({
		url: '/',
		type: 'post',
		data: data,
		success: function (data) {
			swal({title: "Message sent", text: "Thank you for you message. I'll answer you in a few hours.", type: "success", timer: 5000})
		}
	})
}

function show_hide_contact(){
	var contacts_obj = document.getElementById('show_contacts');
	var contacts_button_obj = document.getElementById('show_contacts_button');
	if(contacts_obj.hidden){
		contacts_obj.hidden = false;
		contacts_button_obj.innerHTML = 'Hide contacts';
	}
	else{
		contacts_obj.hidden = true;
		contacts_button_obj.innerHTML = 'Show contacts';
	}
}
