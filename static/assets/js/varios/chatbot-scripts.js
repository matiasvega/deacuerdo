const dni_deudor = JSON.parse(document.getElementById('dni_deudor').textContent)
//const nro_wpp = JSON.parse(document.getElementById('nro_wpp').textContent)


$('.usrInput').on('keyup keypress', function (e) {
	let keyCode = e.keyCode || e.which
	let text = $(".usrInput").val()
	if (keyCode === 13) {
		evalAndSend(e,text)
	}
})

$('#btn_send').click(function (e) {
	let text = $(".usrInput").val()
	let extra = ''

	if ($('#keypad').attr('type') === 'file') {
		let fileInput = document.getElementById('keypad')

		let file = fileInput.files[0]
		text = file.name

		let base64 = getBase64(file)
		base64.then(function (data) {
			extra = data
		})

		setTimeout(function () {
			evalAndSend(e, text, extra)
		},1000)
	} else {
		if (text === "" || $.trim(text) === '') {
			extra = $('#keypad_select').val()
			text = $('#keypad_select option:selected').text()
		}
		evalAndSend(e, text, extra)
	}
})

function evalAndSend(e, text, extra = '') {
	if (text === "" || $.trim(text) === '') {
		e.preventDefault()
		return false
	} else {
		$(".usrInput").blur()
		setUserResponse(text)

		if ($('#keypad').attr('type') === 'file') {
			send(extra)
		} else if ($('#keypad_select').hasClass('provincia') || $('#keypad_select').hasClass('localidad')) {
			send(extra)
		} else {
			send(text)
		}
		e.preventDefault()
		return false
	}
}

function botEscribiendo(accion) {
	if (accion === 'mostrar') {
		let BotResponse = '<div class="bot_puntos ">' +
								'<img class="botAvatar" src="/static/assets/img/logos/deacuerdo-iso-orange@2x.png" alt="">' +
							  	'<div class="chat-bubble color_1">' +
								  	'<div class="typing">' +
									  	'<div class="dot"></div>' +
									  	'<div class="dot"></div>' +
									  	'<div class="dot"></div>' +
								  	'</div>' +
							  	'</div>' +
							  	'<div class="clearfix"></div>'
							'</div>'

		$(BotResponse).appendTo('.chats').hide().fadeIn(750)
		scrollToBottomOfResults()
	} else {
		$('.bot_puntos').remove()
	}
}

async function getBase64(file) {
	function readFile(file) {
	  	return new Promise((resolve, reject) => {
			const reader = new FileReader()

			reader.onloadend = res => {
			  //resolve(res.target.result.replace("data:", "").replace(/^.+,/, ""))
				resolve(res.target.result)
			}
			reader.onerror = err => reject(err)

			reader.readAsDataURL(file)
	  	})
	}

	return await readFile(file)
}

//------------------------------------- Set user response------------------------------------
function setUserResponse(val) {
	let current = new Date()
	let UserResponse = '<img class="userAvatar" src="/static/assets/img/icons-28@4x.png" alt="">' +
		               '<p class="userMsg">' +
							val + '<br>' +
							'<span class="msgTime">' + current.toLocaleTimeString() + '</span>' +
					   '</p>' +
					   '<div class="clearfix"></div>'
	$(UserResponse).appendTo('.chats').show('slow')
	$(".usrInput").val('')
	scrollToBottomOfResults()
	$('.suggestions').remove()
}

//---------------------------------- Scroll to the bottom of the chats-------------------------------
function scrollToBottomOfResults() {
	let terminalResultsDiv = document.getElementById('chats')
	terminalResultsDiv.scrollTop = terminalResultsDiv.scrollHeight
}

function send(message) {
	$('.keypad').hide()
	if (document.querySelectorAll('.bot_puntos').length === 0) {
		botEscribiendo('mostrar')
	}
	console.log("Mensaje del usuario:", message)
	$.ajax({
		url: 'http://74.207.227.51:5005/webhooks/custom_chann/webhook',
		type: 'POST',
		data: JSON.stringify({
			"message": message,
			"sender": dni_deudor,
		}),
		success: function (data, textStatus) {
			if (message !== '/restart') {
				setBotResponse(data)
			} else {
				send('hola')
			}
			console.log("Rasa Response: ", data, "\n Status:", textStatus)
		},
		error: function (errorMessage) {
			setBotResponse("")
			console.log('Error' + errorMessage)
		}
	});
}

//------------------------------------ Set bot response -------------------------------------
function setBotResponse(val) {
	botEscribiendo('quitar')
	setTimeout(function () {
		let msg, current = new Date()

		resetKeypad()

		if (val.length < 1) {
			msg = 'No tengo una respuesta para su consulta'

			let BotResponse = '<img class="botAvatar" src="/static/assets/img/logos/deacuerdo-iso-orange@2x.png" alt="">' +
							  '<p class="botMsg color_1">' +
									msg + '<br>' +
							  		'<span class="msgTime">' + current.toLocaleTimeString() + '</span>' +
							  '</p>' +
							  '<div class="clearfix"></div>'
			$(BotResponse).appendTo('.chats').hide().fadeIn(750)
		} else {
			for (let i = 0; i < val.length; i++) {
				if (val[i].hasOwnProperty("text")) {
					let BotResponse = '<img class="botAvatar" src="/static/assets/img/logos/deacuerdo-iso-orange@2x.png" alt="">' +
									  '<p class="botMsg color_1">' +
											val[i].text + '<br>' +
							  				'<span class="msgTime">' + current.toLocaleTimeString() + '</span>' +
							  		  '</p>' +
									  '<div class="clearfix"></div>'
					$(BotResponse).appendTo('.chats').hide().fadeIn(750)
				}

				//check if there is image
				if (val[i].hasOwnProperty("image")) {
					let BotResponse = '<div class="singleCard">' +
						'<img class="imgcard" src="' + val[i].image + '" alt="">' +
						'</div><div class="clearfix">'
					$(BotResponse).appendTo('.chats').hide().fadeIn(750)
				}

				//check if there is button message
				if (val[i].hasOwnProperty("buttons")) {
					addSuggestion(val[i].buttons)
				}

				//check if there is custom options
				if (val[i].hasOwnProperty("custom")) {
					if (val[i].custom['keypad'] === 'disabled') {
						$('.keypad').hide()
					}
					if (val[i].custom['keypad'] === 'readonly') {
						$('#keypad').prop('readonly', true)
					}
					if (val[i].custom['input_type'] !== undefined) {
						let custom_type = val[i].custom['input_type']
						let select_data = val[i].custom['select_data']
						let extra_data = val[i].custom['extra_data']

						if (custom_type !== 'select') {
							$('#keypad').prop('type', val[i].custom['input_type'])
						}

						if (custom_type === 'date') {
							$('#keypad').prop('data-field', custom_type)
							if (extra_data === 'informe') {
								let anio_antes = new Date()
								anio_antes.setFullYear(anio_antes.getFullYear() - 1)
								$('#dtBox').DateTimePicker({
									dateFormat: 'dd-mm-yyyy',
									language: 'es',
									minDate: anio_antes,
									maxDate: new Date()
								})
							} else {
								let min_fecha = new Date()
								min_fecha.setDate(min_fecha.getDate() + 1)
								let max_fecha = new Date()
								max_fecha.setDate(max_fecha.getDate() + 31)
								$('#dtBox').DateTimePicker({
									dateFormat: 'dd-mm-yyyy',
									language: 'es',
									defaultDate: min_fecha,
									minDate: min_fecha,
									maxDate: max_fecha
								})
							}
						}

						if (custom_type === 'time') {
							let empresa = JSON.parse(extra_data)

							$('#keypad').timepicker({'scrollDefault': 'now',
                                                  'step': 30,
                                                  'timeFormat': 'H:i',
                                                  'minTime': empresa[17],
                                                  'maxTime': empresa[16],
                                                  'useSelect': true
                                                })
							$('.ui-timepicker-select').addClass('form-control')
							$('.ui-timepicker-select').css('margin-left', '4%')
						}

						if (custom_type === 'select') {
							$('#keypad').hide()
							$('#keypad').after('<select id="keypad_select" class="form-control" style="margin-left: 4%"></select>')
							let csrfToken = getCookie('csrftoken')

							if (select_data === 'tipo_vivienda') {
								$('#keypad_select').html('<option value="CASA">CASA</option>' +
														 '<option value="DEPTO" selected>DEPTO</option>')
							}
							if (select_data === 'provincia') {
								$('#keypad_select').addClass(select_data)
								$.post('../listar_provincias/', {csrfmiddlewaretoken:csrfToken}, function (data) {
									$('#keypad_select').html(data)
								})
							}
							if (select_data === 'localidad') {
								$('#keypad_select').addClass(select_data)
								$.post('../listar_localidades/' + extra_data + '/', {csrfmiddlewaretoken:csrfToken},
									function (data) {
										$('#keypad_select').html(data)
									}
								)
							}

							$('#keypad').val($('#keypad_select option:selected').text())
						}

						if (custom_type === 'file') {
							$('#keypad').prop('accept', 'image/*')
							$('#keypad').prop('capture', 'capture')
						}
					}
				}
			}
			scrollToBottomOfResults()
			$('#keypad').focus()
		}
	}, 500)
}

// ------------------------------------------ Toggle chatbot -----------------------------------------------
$('#profile_div').click(function () {
	$('.profile_div').toggle()
	$('.widget').toggle()
	scrollToBottomOfResults()
	if ($('.chats').html().length <= 42) {
		send('/restart')
	}
})

$('.btn_ayuda').click(function () {
	$('.profile_div').toggle()
	$('.widget').toggle()
	scrollToBottomOfResults()
	if ($('.chats').html().length <= 42) {
		send('/restart')
	}
})

function resetKeypad() {
	$('.ui-timepicker-select').remove()
	$('#keypad_select').remove()
	let old_keypad = document.getElementById('keypad')
	let new_keypad = document.createElement('input')
	new_keypad.type = 'text'
	new_keypad.id = 'keypad'
	new_keypad.className = 'usrInput browser-default'
	new_keypad.placeholder = 'Escribe tu mensaje'
	new_keypad.autocomplete = 'off'
	old_keypad.parentNode.replaceChild(new_keypad, old_keypad)
	$('.keypad').show()
}

$('#close').click(function () {
	$('.profile_div').toggle()
	$('.widget').toggle()
})

$('#restart_bot').click(function () {
	send('/restart')
	$('.chats').html('')
	resetKeypad()
})

// ------------------------------------------ Suggestions -----------------------------------------------
function addSuggestion(textToAdd) {
	setTimeout(function () {
		let suggestions = textToAdd
		let suggLength = textToAdd.length
		$(' <div class="singleCard"> <div class="suggestions"><div class="menu"></div></div></diV>').appendTo('.chats').hide().fadeIn(750)

		for (let i = 0; i < suggLength; i++) {
			$('<div class="menuChips" data-payload=\''+(suggestions[i].payload)+'\'>' + suggestions[i].title + "</div>").appendTo(".menu")
		}
		scrollToBottomOfResults()
	}, 750)
}

$(document).on("click", ".menu .menuChips", function () {
	let text = this.innerText
	let payload= this.getAttribute('data-payload')
	console.log("button payload: ",this.getAttribute('data-payload'))
	setUserResponse(text)
	send(payload)
	$('.suggestions').remove()
})

function esMobile() {
	let hasTouchScreen
	if ("maxTouchPoints" in navigator) {
		hasTouchScreen = navigator.maxTouchPoints > 0
	} else if ("msMaxTouchPoints" in navigator) {
		hasTouchScreen = navigator.msMaxTouchPoints > 0
	} else {
		let mQ = window.matchMedia && matchMedia("(pointer:coarse)")
		if (mQ && mQ.media === "(pointer:coarse)") {
			hasTouchScreen = !!mQ.matches
		} else if ('orientation' in window) {
			hasTouchScreen = true
		} else {
			let UA = navigator.userAgent
			hasTouchScreen = (
				/\b(BlackBerry|webOS|iPhone|IEMobile)\b/i.test(UA) ||
				/\b(Android|Windows Phone|iPad|iPod)\b/i.test(UA)
			)
		}
	}
	return hasTouchScreen
}
/*
let wpp_link = ''
if (esMobile()) {
	wpp_link = "whatsapp://send?phone=" + nro_wpp
} else {
	wpp_link = "https://wa.me/" + nro_wpp
}
$('.link_wpp').prop('href', wpp_link)
*/

$('#keypad_select').change(function () {
	$('#keypad').val($('#keypad_select option:selected').text())
})

function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

function displaySize() {
    $("#js-width").text(window.innerWidth);
    $("#js-height").text(window.innerHeight);
}

$(function() {
    displaySize();

    $(window).resize(function() {
        displaySize();
    });
});
