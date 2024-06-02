$(document).ready(() => {

	// set visitor name
	let $userName = "";
	let $urlBase="https://localhost:8000"
	let $app_name="test_app"
	let $app_key="CyLang-9da11944-2fb0-462d-a79d-d586cf2f1625"
	let $session_id="";

	// start chatbox
	$("#form-start").on("submit", (event) => {
		
		event.preventDefault();
		$userName = $("#username").val();
		$("#landing").slideUp(300);
		setTimeout(() => {
			$("#start-chat").html("Continue chat")
		}, 300);

		// get contexts
		$.ajax({
			url: $urlBase+'/contexts',
			headers: {
				'app-name':$app_name,
				'app-key':$app_key
			},
			type: "GET", 
			dataType: "json",
			data: {
			},
			success: function (result) {
				console.log(result);
				$.each( result, function( i ,item ) {
					console.log(item.id)
					$('#sel_contexts').append($('<option>', { 
						value: item.id,
						text : item.name +" [embs="+item.embeddings_model_name+";type="+item.context_type_name
						+";history="+item.history
						+"]"
					}));
				  });

				$('#sel_llms').empty()

				// get session_id
				$.ajax({
					url: $urlBase+'/sessions',
					headers: {
						'app-name':$app_name,
						'app-key':$app_key
					},
					type: "GET", 
					dataType: "json",
					data: {
					},
					success: function (result) {
						$session_id=result
					},
					error: function () {
						postBotReply("Sorry, there are some problems. Try later.")
					}
				});

				// get llm
				$.ajax({
					url: $urlBase+'/llms/'+$('#sel_contexts').val(),
					headers: {
						'app-name':$app_name,
						'app-key':$app_key	
					},
					type: "GET", 
					dataType: "json",
					data: {
					},
					success: function (result) {
						console.log(result);
						$.each( result, function( i ,item ) {
							if (item.model_name==null)
								item.model_name=''
							if (item.task==null)
								item.task=''
							
							$('#sel_llms').append($('<option>', { 
								value: item.name,
								text : item.name +" [LLM="+item.llm_type_name+
								";model="+item.model_name+";task="+item.task+
								";local="+item.local+";pipeline="+item.pt_pipeline+"]"
							}));
						});
						
					},
					error: function () {
						postBotReply("Sorry, there are some problems. Try later.")
					}
				});	
				 
			},
			error: function () {
				postBotReply("Sorry, there are some problems. Try later.")
			}
		});	


		
		
	});

	// context selection
	$("#sel_contexts").change(function(){
		$('#sel_llms').empty()

		// get session_id
		$.ajax({
			url: $urlBase+'/sessions',
			headers: {
				'app-name':$app_name,
				'app-key':$app_key	
			},
			type: "GET", 
			dataType: "json",
			data: {
			},
			success: function (result) {
				$session_id=result
			},
			error: function () {
				postBotReply("Sorry, there are some problems. Try later.")
			}
		});

		$.ajax({
			url: $urlBase+'/llms/'+$('#sel_contexts').val(),
			headers: {
				'app-name':$app_name,
				'app-key':$app_key	
			},
			type: "GET", 
			dataType: "json",
			data: {
			},
			success: function (result) {
				console.log(result);
				$.each( result, function( i ,item ) {
					if (item.model_name==null)
						item.model_name=''
					if (item.task==null)
						item.task=''	

					$('#sel_llms').append($('<option>', { 
						value: item.name,
						text : item.name +" [LLM="+item.llm_type_name+
						";model="+item.model_name+";task="+item.task+
						";local="+item.local+";pipeline="+item.pt_pipeline+"]"
					}));
				  });
				 
			},
			error: function () {
				postBotReply("Sorry, there are some problems. Try later.")
			}
		});	
    });
	
	
	// Post a message to the board
	function $postMessage() {
		$("#message").find("br").remove();
		let $message = $("#message").html().trim(); // get text from text box
		$message = $message.replace(/<div>/, "<br>").replace(/<div>/g, "").replace(/<\/div>/g, "<br>").replace(/<br>/g, " ").trim();
		if ($message) { // if text is not empty
			const html = `<div class="post post-user">${"["+$userName+"] "+$message + timeStamp()}</span></div>`; // convert post to html
			$("#message-board").append(html); // add post to board
			$scrollDown(); // stay at bottom of chat
			botReply($message);
		};
		$("#message").empty();
	};

	// Chat input
	$("#message").on("keyup", (event) => {
		if (event.which === 13) $postMessage(); // Use enter to send
	}).on("focus", () => {
		$("#message").addClass("focus");
	}).on("blur", () => {
		$("#message").removeClass("focus");
	});
	$("#send").on("click", $postMessage);


	//  Reply
	function botReply(userMessage) {
		console.log("userMessage="+userMessage);
		
		$.ajax({
			contentType: 'application/json',
			headers: {
				'app-name':$app_name,
				'app-key':$app_key	
			},
			data: JSON.stringify({ "query": userMessage,"context_id":$('#sel_contexts').val(),llm_name:$('#sel_llms').val(),
				askdata_output_fmt:'html',session_id: $session_id}),
			dataType: 'json',
			success: function(reply){
				if (typeof reply === "string") postBotReply(reply);
				else 
					reply.forEach((str) => postBotReply(str));
			},
			error: function(error){
				postBotReply("Sorry, there are some problems. Try later.")
			},
			processData: false,
			type: 'POST',
			url: $urlBase+'/llm-query/'
		});
		
		
	};

	

	function postBotReply(reply) {
		const html = `<div class="post post-bot">${"[AI] "+reply + timeStamp()}</div>`;
		const timeTyping = 500 + Math.floor(Math.random() * 2000);
		$("#message-board").append(html);
		$scrollDown();
	};



	/******************/
	/*** TIMESTAMPS ***/
	/******************/


	function timeStamp() {
		const timestamp = new Date();
		const hours = timestamp.getHours();
		let minutes = timestamp.getMinutes();
		if (minutes < 10) minutes = "0" + minutes;
		const html = `<span class="timestamp">${hours}:${minutes}</span>`;
		return html;
	};




	/***************/
	/*** CHAT UI ***/
	/***************/


	// Back arrow button
	$("#back-button").on("click", () => {
		$("#landing").show();
	});


	// Menu - navigation
	$("#nav-icon").on("click", () => {
		$("#nav-container").show();
	});

	$("#nav-container").on("mouseleave", () => {
		$("#nav-container").hide();
	});

	$(".nav-link").on("click", () => {
		$("#nav-container").slideToggle(200);
	});

	// Clear history
	$("#clear-history").on("click", () => {
		$("#message-board").empty();
		$("#message").empty();
	});

	// Sign out
	$("#sign-out").on("click", () => {
		$("#message-board").empty();
		$("#message").empty();
		$("#landing").show();
		$("#username").val("");
		$("#start-chat").html("Start chat");
	});




	/*********************/
	/*** SCROLL TO END ***/
	/*********************/


	function $scrollDown() {
		const $container = $("#message-board");
		const $maxHeight = $container.height();
		const $scrollHeight = $container[0].scrollHeight;
		if ($scrollHeight > $maxHeight) $container.scrollTop($scrollHeight);
	}




	/***************/
	/*** EMOIJIS ***/
	/***************/


	// toggle emoijis
	$("#emoi").on("click", () => {
		$("#emoijis").slideToggle(300);
		$("#emoi").toggleClass("fa fa-grin far fa-chevron-down");
	});

	// add emoiji to message
	$(".smiley").on("click", (event) => {
		const $smiley = $(event.currentTarget).clone().contents().addClass("fa-lg");
		$("#message").append($smiley);
		$("#message").select(); // ==> BUG: message field not selected after adding smiley !! 
	});




});