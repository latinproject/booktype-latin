           /* MODIFICATION UCSP */
	   
	   
	   /*************************************************************************************
	    * FUNCTIONS 
	    *************************************************************************************/
	   
	   /***
	    * Function to get text from html format
	    */
	   function strip(html)
	   {
		    var tmp = document.createElement("DIV");
		    tmp.innerHTML = html;
		    return tmp.textContent || tmp.innerText || "";
	   }  
	   
	   
           /***
	    *Function to Add Comment to Discussion
	    */
           function addCommenttoTheme(item, theme){
		        $.booki.ui.notify($.booki._('add_comment_to_theme', 'Add Comment to Theme'));
			$.booki.sendToChannel("/booki/book/discussion/"+$.booki.currentBookID+"/"+$.booki.currentVersion+"/", {"command": "add_comment_to_theme", "comment": strip(item), "theme": theme}, function(data) {
						    if(data.created) {
							$.booki.ui.notify();
							var lcomment, luser, lcreated, liden
							var comment_list = $("#discussioncommentlist");
							$.each(data.comment, function(i, elem) {
							      lcomment = elem.comment;
							      luser = elem.user;
							      lcreated = elem.created;
							      liden = elem.iden;
							      llikes = elem.likes;
							      lunix_created = elem.unix_created;
							      
							      var en = $.booki.ui.getTemplate('commnetlist');
							      $.booki.ui.fillTemplate(en, {"entryComment": strip(lcomment), "entryUser": luser, "entryCreated": lcreated, "entryCountLiked":llikes});
							      comment_list.append(en);
							      
							      en.find('.buttonlikecomment').show();
							      en.find('.buttonunlikecomment').hide();
							      en.find('.buttonremovecomment').show();
							      en.find(".buttonlikecomment").attr('title',$.booki._('like', 'Like'));
							      en.find(".buttonremovecomment").attr('title',$.booki._('remove_comment', 'Remove Comment'));
							      
							      en.find(".buttonlikecomment").click(function(){
								var comment = lcomment;
								var func = 'add';
								addLiketoComment(theme,comment,func,luser,lunix_created);
								en.find('.buttonlikecomment').hide();
								en.find('.buttonunlikecomment').show();
								en.find(".buttonunlikecomment").attr('title',$.booki._('unlike', 'Unlike'));
							      });
							      
							      en.find(".buttonunlikecomment").click(function(){
								var comment = lcomment;
								var func = 'remove';
								addLiketoComment(theme,comment,func,luser,lunix_created);
								en.find('.buttonlikecomment').show();
								en.find('.buttonunlikecomment').hide();
								en.find(".buttonlikecomment").attr('title',$.booki._('like', 'Like'));
							      });
							      
							      en.find(".buttonremovecomment").click(function(){
								    var comment = lcomment;
								    var user = luser;
								    
								    if(confirm($.booki._('confirm_delete', 'Really do you want delete this comment?')))
								    {
								       deleteCommentfromTheme(theme,comment,user);
								    }
								    else{
								       en.find('.buttonremovecomment').show();
								    }
							      });
							      
							      
							      
							      
							});
							$("#valcommenttheme").val('')
							$("#formaddcomment").removeClass('show');
							$("#formaddcomment").addClass('hide');
							$("#formaddcomment").slideUp('fast');
						    } else {
							$.booki.ui.notify();
							alert($.booki._('can_not_add_comment', 'Can not add comment to discussion.'));
							$("#valcommenttheme").val('')
							$("#formaddcomment").removeClass('show');
							$("#formaddcomment").addClass('hide');
							$("#formaddcomment").slideUp('fast');
						    }
						    		
						});	      
	   }
	   
	   /***
	    * Function to delete comment from discussion
	    */
	   function deleteCommentfromTheme(theme, comment, user){
	            $.booki.sendToChannel("/booki/book/discussion/"+$.booki.currentBookID+"/"+$.booki.currentVersion+"/", {"command": "delete_comment_from_theme", "comment": comment, "user": user}, function(data) {
						  if(data.deleted == 1) {
						      $.booki.ui.notify();
						      getCommentList(theme);
						  } else if(data.deleted == 0){
						      $.booki.ui.notify();
						      alert($.booki._('can_not_delete_comment', "Can't delete comment from discussion."));
						  }
						  else if (data.deleted == 2){
						      $.booki.ui.notify();
						      alert($.booki._('can_not_get_comment_from_discussion', "Can't delete comment from discussion. The comment may have been removed."));
						  
						  }
						  		
					      });
	  }
	   
	   
	   /***
	    * Function to add like/unlike to comment
	    */
	   function addLiketoComment(theme, comment, func, user, unix_created){
	            $.booki.sendToChannel("/booki/book/discussion/"+$.booki.currentBookID+"/"+$.booki.currentVersion+"/", {"command": "update_like_to_comment", "comment": comment, "function": func, "theme": theme, "user": user, "unix_created": unix_created}, function(data) {
						  if(data.updated == 1) {
						      $.booki.ui.notify();
						      var liden, lcomment, lnext_func, llike, ltitle
						      var en = $.booki.ui.getTemplate('discussionlist');
						      $.each(data.like, function(i, elem) {
							      liden = elem.iden;
							      lcomment = elem.comment;
							      lnext_func = elem.next_func;
							      llike = elem.like;
							      ltitle = elem.discussion;
						      });
						      
						      getCommentList(ltitle);
						      
						      /* Is like already*/
						      if(llike == 1) {
							  $('#buttonlike'+liden).attr('func',lnext_func);
							  en.find('.buttonlikecomment').hide();
							  en.find('.buttonunlikecomment').show();
						      }
						      /* Or is unlike */
						      else if(llike == 0){
							  $('#buttonlike'+liden).attr('func',lnext_func);
							  en.find('.buttonlikecomment').show();
							  en.find('.buttonunlikecomment').hide();
						      } 
						  } 
						  else if(data.updated == 0){
							$.booki.ui.notify();
							alert($.booki._('can_not_update_like_comment', "Can't update like to comment."));
						  }
						  
						  else if(data.updated == 2){
							$.booki.ui.notify();
							alert($.booki._('can_not_get_comment_to_like', "Can't update like to comment. The comment may have been removed."));
						  }
						  
						  		
					      });
	   }
	   
	  
	   /***
	    * Function to show Create Discussion Dialog
	    */
	    function showCreateDiscussionDialog(){
		    $("#newdiscussion").dialog({
			bgiframe: true,
			autoOpen: true,
			height: 500,
		        width: 600, 
			modal: true,
			title: $.booki._('new_discussion', 'New Discussion Theme'),
			buttons: [
				  { text: $.booki._('create_discussion', 'Create discussion'),
				    click: function() {
				          var content = tinyMCE.activeEditor.getContent();
					  content = $.trim(content);
					  var message_length = content.length;
					  
					  if($.trim($("#newdiscussion INPUT[name=title]").val())=='' && $.trim(content=='')){
					     alert("Titulo y Descripcion deben ser llenados"); 
					     return;
					  }
					  
					  var title = $("#newdiscussion INPUT[name=title]").val();
					  title = $.trim(title);
					  var title_length = title.length;
					  
					  var labels = $("#newdiscussion INPUT[name=labels]").val();
					  labels = $.trim(labels);
					  var labels_length = labels.length;
					  
					  if(title_length > 2500)
					  {
					     $("#errortammaxtitle").show(); 
					     return;
					  }
					  if(message_length > 10000)
					  {
					      $("#errortammaxmessage").show(); 
					      return;
					  }
					  if(labels_length > 200)
					  {
					      $("#errortammaxlabels").show(); 
					      return;
					  }
					  $.booki.ui.notify($.booki._('creating_discussion', 'Creating discussion'));
				
					  $.booki.sendToChannel("/booki/book/discussion/"+$.booki.currentBookID+"/"+$.booki.currentVersion+"/", {"command": "create_discussion", "discussion": $("#newdiscussion INPUT[name=title]").val(),
					                                                                                                                              "message": content,
					                                                                                                                              "labels": $("#newdiscussion INPUT[name=labels]").val(),
																				      "access": $("#access option:selected").val()}, function(data) {
						  if(data.created) {
						      $.booki.ui.notify();
						      var his = $("#discussionlist");
						      $.each(data.discussion, function(i, elem) {
							    var en = $.booki.ui.getTemplate('discussionlist');
							    $.booki.ui.fillTemplate(en, {"entryTitle": elem.title, "entryMessage": elem.message, "entryUser": elem.user, "entryCreated": elem.created});
							    his.append(en);
							
							    $.booki.current_discussiontheme = elem.title;
							    showDiscussionDetail(elem.title);
							    	    
							    /* link to discussion detail */
							    en.find(".linkdiscussiontheme").click(function(){
								  $.booki.current_discussiontheme = elem.title;
								  showDiscussionDetail(elem.title);
							    });
							  
						      });		      
						  } else {
						      $.booki.ui.notify();
						      alert($.booki._('can_not_create_discussion', 'Can not create discussion theme.'));
						  }
						  			
					      });
					  $(this).dialog('close');
				      }
				  },
				  { text: $.booki._('cancel', 'Cancel'),
				    click: function() {
					  $(this).dialog('close');
				      }
				  }
			],
			open: function(event,ui) {
			    $("#newdiscussion INPUT[name=title]").val('');
			    $("#newdiscussion TEXTAREA[name=message]").val('');
			    $("#newdiscussion INPUT[name=labels]").val('');
			    $("#newdiscussion SELECT[name=access] OPTION[value=public]").attr('selected','selected'); 
			    $("#newdiscussion TEXTAREA[name=message]").tinymce(window.EVIL_TINY_OPTIONS);			    
			},
			close: function() {
			    tinyMCE.activeEditor.remove();
			    $("#errortammaxtitle").hide();
			    $("#errortammaxmessage").hide();
			    $("#errortammaxlabels").hide();
			}
		    });   
	     
	     
	   }
	   
	   
	   /***
	    * Function to show Edit Discussion Dialog
	    */
	   function showEditDiscussionDialog(title, message, labels, access){
	            $("#newdiscussion").dialog({
			bgiframe: true,
			autoOpen: true,
			height: 500,
		        width: 600, 
			modal: true,
			title: $.booki._('edit_discussion_theme', 'Edit Discussion Theme'),
			buttons: [
				  { text: $.booki._('save_changes', 'Save Changes'),
				    click: function() {
				          var content = tinyMCE.activeEditor.getContent();
					  if (content == ''){
					    content = document.getElementById('discussiondetailheadmessage').innerHTML;
					  }
					  content = $.trim(content);
					  var message_length = content.length;
					  
					  if($.trim($("#newdiscussion INPUT[name=title]").val())=='' && $.trim(content=='')){
					     alert("Titulo y Descripcion deben ser llenados"); 
					     return;
					  }
					  
					  var old_title = document.getElementById('discussiondetailheadtitle').innerHTML;
					  var title = $("#newdiscussion INPUT[name=title]").val();
					  title = $.trim(title);
					  var title_length = title.length;
					  
					  var labels = $("#newdiscussion INPUT[name=labels]").val();
					  labels = $.trim(labels);
					  var labels_length = labels.length;
					  
					  if(title_length > 2500)
					  {
					     $("#errortammaxtitle").show(); 
					     return;
					  }
					  if(message_length > 10000)
					  {
					      $("#errortammaxmessage").show(); 
					      return;
					  }
					  if(labels_length > 200)
					  {
					      $("#errortammaxlabels").show(); 
					      return;
					  }
					  
					  $.booki.ui.notify($.booki._('editing_discussion', 'Editing discussion'));
					  $.booki.sendToChannel("/booki/book/discussion/"+$.booki.currentBookID+"/"+$.booki.currentVersion+"/", {"command": "edit_discussion", "old_title": old_title,
																				      "new_title": $("#newdiscussion INPUT[name=title]").val(),
					                                                                                                                              "new_message": content,
					                                                                                                                              "new_labels": $("#newdiscussion INPUT[name=labels]").val(),
																				      "new_access": $("#access option:selected").val()}, function(data) {
						  if(data.edited) {
						      $.booki.ui.notify();
						      
						      var htitle,hmessage,hlabels,haccess;
						      $.each(data.discussion, function(i, elem) {
							    htitle = elem.title;
							    hmessage = elem.message;
							        
							    document.getElementById('discussiondetailheadtitle').innerHTML= htitle;
							    document.getElementById('discussiondetailheadmessage').innerHTML= hmessage;
							 
						      });
						      showDiscussionDetail(htitle);
						      
						  } else {
						      $.booki.ui.notify();
						      alert($.booki._('can_not_edit_discussion', 'Can not edit discussion theme.'));
						  }
						  			
					      });
					  $(this).dialog('close');
				      }
				  },
				  { text: $.booki._('cancel', 'Cancel'),
				    click: function() {
					  $(this).dialog('close');
				      }
				  }
			],
			open: function(event,ui) {
			      $("#newdiscussion INPUT[name=title]").val(title);
			      $("#newdiscussion TEXTAREA[name=message]").val(message);
			      $("#newdiscussion INPUT[name=labels]").val(labels);
			      $('#newdiscussion SELECT[name=access] OPTION[value='+access+']').attr('selected','selected'); 
			      $("#newdiscussion TEXTAREA[name=message]").tinymce(window.EVIL_TINY_OPTIONS);
			      tinymce.activeEditor.setContent(message);
			},
			close: function() {
			     tinymce.activeEditor.remove();
			     $("#errortammaxtitle").hide();
			     $("#errortammaxmessage").hide();
			     $("#errortammaxlabels").hide();
			}
		    });
	   }
	   
	   
	   
	   /***
	    * Function to show Discussion Detail Page
	    */
	   function showDiscussionDetail(title) {
		    $("#discussionthemecontent").hide();
		    $("#discussioncommentcontent").show();
		    $.booki.ui.notify($.booki._('getting_discussion_detail', 'Getting Discussion Detail'));
		    $.booki.sendToChannel("/booki/book/discussion/"+$.booki.currentBookID+"/"+$.booki.currentVersion+"/", {"command": "get_discussion_detail", "title": title}, function(data) {
						  if(data.get) {
						      $.booki.ui.notify();
						      
						          $("#discussioncommenthead").empty()
							  $("#discussioncommentlist").empty()
							  $("#searchtag").hide()
							  $("#valcommenttheme").val('')
							  $("#formaddcomment").removeClass('show');
							  $("#formaddcomment").addClass('hide');
							  $("#formaddcomment").slideUp('fast');
							  $("#errortammaxcomment").hide();
							  
							  var htitle,huser,hmessage,hcreated,hlabels,haccess;
							  var his = $("#discussioncommenthead");
							  var en = $.booki.ui.getTemplate('discussionhead');
							  en.find(".buttonbacktodiscussiontheme").attr('title',$.booki._('back', 'Back'));
							  /* Detail */
							  $.each(data.head, function(i, elem) {
							      htitle = elem.title;
							      huser = elem.user;
							      hmessage = elem.message;
							      hcreated = elem.created;
							      hlabels = elem.labels;
							      haccess = elem.access;
							      his_owner = elem.is_owner;
							     
							      $.booki.ui.fillTemplate(en, {"entryTitle": htitle, "entryMessage": hmessage, "entryUser": huser, "entryCreated": hcreated});
							      his.append(en);
							      
							      if(his_owner == "false"){
								 en.find('.buttoneditdiscussiontheme').hide();
								 en.find('.buttonremovediscussiontheme').hide();
							      }
							      else if(his_owner == "true"){
								 en.find(".buttoneditdiscussiontheme").attr('title',$.booki._('edit_discussion', 'Edit Discussion'));
								 en.find(".buttonremovediscussiontheme").attr('title',$.booki._('remove_discussion', 'Remove Discussion'));
							      }
							      
							      
							  });
							  
							  /* Labels */
							  en.find(".labelicon").attr('title',$.booki._('labels', 'Labels'));
							  $.each(data.labels, function(i, elem) {
							      en.find(".labelsheadmessage").append("<a class='labeltag' val='"+elem.label+"' style='font-size:10px'>"+elem.label+"</a><a> <strong>,</strong> </a>");
							  });
							  
							  /* Comment List */
							  getCommentList(title);
							  
						          /* label tag click */
							  $(".labeltag").click(function(){
							      var label = $(this).attr('val')
							      $("#discussioncommentcontent").hide();
							      $("#searchtag").show();
							      $(".buttonbacksearchtag").attr('title',$.booki._('back', 'Back'));
							      getDiscussionListByLabel(label);
							    
							  });
							  
							  /* button back */
							  $(".buttonbacktodiscussiontheme").click(function(){
							      $("#discussioncommentcontent").hide();
							      $("#discussionthemecontent").show();
							      getDiscussionList();
							    
							  });
							  
							  /* button edit */
							  $(".buttoneditdiscussiontheme").click(function(){
							      htitle = document.getElementById('discussiondetailheadtitle').innerHTML;
						              hmessage = document.getElementById('discussiondetailheadmessage').innerHTML;
							      showEditDiscussionDialog(htitle,hmessage,hlabels,haccess);
							      
							  });
							  
							  /* button remove theme */
							  $(".buttonremovediscussiontheme").click(function(){
							      if(confirm($.booki._('confirm_delete_discussion', 'Really do you want delete this discussion?'))){
								removeDiscussionTheme(htitle, huser);
							      }
							  });
							  
							  /* link commentate */
							  $(".buttonaddcommenttheme").click(function(){
							      addCommenttoTheme();
							  });
							  
						  } else {
						      $.booki.ui.notify();
						      alert($.booki._('can_not_get_comments', 'Can not get comments.'));
						  }
						  			
					      });
		}
		
		
	   
	        /***
		* Function to get and show the discussion list
		*/
		function getDiscussionList(){
			    $.booki.ui.notify($.booki._('get_discussion_list', 'Get Discussion List'));
			    $.booki.sendToChannel("/booki/book/discussion/"+$.booki.currentBookID+"/"+$.booki.currentVersion+"/", {"command": "get_discussion_list"}, function(data) {
							if(data.get) {
							    $.booki.ui.notify();
							    $("#discussionlist").empty()
							    var his = $("#discussionlist");
							    
							    $.each(data.discussions, function(i, elem) {
							          var en = $.booki.ui.getTemplate('discussionlist');
							          if(elem.state=='1'){
								      var mess = strip(elem.message);
								      /* if discussion title length > 500 substring to show in the list */
								      if(mess.length > 500)
								      {
									 mess = mess.substring(0,500);
									 mess = mess + " ........";
								      }
								      $.booki.ui.fillTemplate(en, {"entryTitle": elem.title, "entryMessage": strip(mess), "entryUser": elem.user, "entryCreated": elem.created});
								      his.prepend(en);
								      $.booki.current_discussiontheme = elem.title;
								  }
								  
								  /* Go to discussion detail */
								  en.find(".linkdiscussiontheme").click(function(){
								    $("#discussionthemecontent").hide();
								    $("#discussioncommentcontent").show();
								    var item = elem.title;
								    $.booki.current_discussiontheme = item;
								    showDiscussionDetail(item);
								  });  
								  
							    });
							    
							} else {
							    $.booki.ui.notify();
							    alert($.booki._('can_not_get_discussion_list', 'Can not get discussion list.'));
							}
										
						    });
		}
		
		
		/***
		* Function to get and show the discussion list search by label
		*/
		function getDiscussionListByLabel(label){
			    $.booki.ui.notify($.booki._('get_discussion_list', 'Get Discussion List'));
			    $.booki.sendToChannel("/booki/book/discussion/"+$.booki.currentBookID+"/"+$.booki.currentVersion+"/", {"command": "get_discussion_list_by_label", "label": label}, function(data) {
							if(data.get) {
							    $.booki.ui.notify();
							    $("#discussionlisttag").empty()
							    var his = $("#discussionlisttag");
							    $.each(data.discussions, function(i, elem) {
							          var en = $.booki.ui.getTemplate('discussionlist');
							          if(elem.state=='1'){
								      var mess = strip(elem.message);
								      /* if discussion title length > 500 substring to show in the list */
								      if(mess.length > 500)
								      {
									 mess = mess.substring(0,500);
									 mess = mess + " ........";
								      }
								      $.booki.ui.fillTemplate(en, {"entryTitle": elem.title, "entryMessage": strip(mess), "entryUser": elem.user, "entryCreated": elem.created});
								      his.prepend(en);
								      $.booki.current_discussiontheme = elem.title;
								  }
								  
								  /* Go to discussion detail */
								  en.find(".linkdiscussiontheme").click(function(){
								    $("#discussionthemecontent").hide();
								    $("#discussioncommentcontent").show();
								    var item = elem.title;
								    $.booki.current_discussiontheme = item;
								    showDiscussionDetail(item);
								  });  
								  
							    });
							   
							    /* Button Back*/
							    $(".buttonbacksearchtag").click(function(){
							          $("#searchtag").hide();
							          $("#discussioncommentcontent").show();
								  $("#valcommenttheme").val('')
								  $("#formaddcomment").removeClass('show');
								  $("#formaddcomment").addClass('hide');
								  $("#formaddcomment").slideUp('fast');
								  $("#errortammaxcomment").hide();
							    });
							    
							    
							} else {
							    $.booki.ui.notify();
							    alert($.booki._('can_not_get_discussion_list', 'Can not get discussion list.'));
							}
									
						    });
		}
		
		
		/***
		 * Function to get and show the comment list from a discussion
		 */
		function getCommentList(title){
			    $.booki.ui.notify($.booki._('get_comment_list', 'Get Comment List'));
			    $.booki.sendToChannel("/booki/book/discussion/"+$.booki.currentBookID+"/"+$.booki.currentVersion+"/", {"command": "get_comment_list", "title": title}, function(data) {
							if(data.get) {
							    $.booki.ui.notify();
							    $("#discussioncommentlist").empty()
							    var comment_list = $("#discussioncommentlist");
							    
							    $.each(data.comments, function(i, elem) {
							          var cuser = elem.user;
								  var ccomment = strip(elem.comment);
								  var ccreated = elem.created;
								  var cid = elem.id;
								  var clikes = parseInt(elem.likes,10);
								  var cunix_created = elem.unix_created; 
								  var like_next_func = elem.like_next_func;
								 
								  var en = $.booki.ui.getTemplate('commnetlist');
								  $.booki.ui.fillTemplate(en, {"entryComment": ccomment, "entryUser": cuser, "entryCreated": ccreated, "entryCountLiked":clikes});
								  comment_list.append(en);
								  
								  
								  if(like_next_func == 'add'){
								    en.find('.buttonlikecomment').show();
								    en.find('.buttonunlikecomment').hide();
								    en.find(".buttonlikecomment").attr('title',$.booki._('like', 'Like'));
								  }
								  else if(like_next_func == 'remove'){
								    en.find('.buttonlikecomment').hide();
								    en.find('.buttonunlikecomment').show();
								    en.find(".buttonunlikecomment").attr('title',$.booki._('unlike', 'Unlike'));
								  }
								  
								  if(elem.can_remove == 1){
								    en.find('.buttonremovecomment').show();
								    en.find(".buttonremovecomment").attr('title',$.booki._('remove_comment', 'Remove Comment'));
								  }
								  
								  /* Like */
								  en.find(".buttonlikecomment").click(function(){
								    var comment = ccomment;
								    var func = 'add';
								    addLiketoComment(title,comment,func, cuser,cunix_created);
								    en.find('.buttonlikecomment').hide();
								    en.find('.buttonunlikecomment').show();
								    en.find(".buttonunlikecomment").attr('title',$.booki._('unlike', 'Unlike'));
								  });
								  
								  /* Unlike */
								  en.find(".buttonunlikecomment").click(function(){
								    var comment = ccomment;
								    var func = 'remove';
								    addLiketoComment(title,comment,func,cuser,cunix_created);
								    en.find('.buttonlikecomment').show();
								    en.find('.buttonunlikecomment').hide();
								    en.find(".buttonlikecomment").attr('title',$.booki._('like', 'Like'));
								  });
								  
								  /* Button Remove */
								  en.find(".buttonremovecomment").click(function(){
								    var comment = ccomment;
								    var user = cuser;
								    if(confirm($.booki._('confirm_delete', 'Really do you want delete this comment?')))
								    {
								       deleteCommentfromTheme(title,comment,user);
								    }
								  });
							    });
							    
							} else {
							    $.booki.ui.notify();
							    alert($.booki._('can_not_get_comment_list', 'Can not get comment list.'));
							}
										
						    });
		}
		
		
		/***
	         * Function to delete a discusion theme
	         */
		function removeDiscussionTheme(title, user){
		            $.booki.ui.notify($.booki._('delete_discussion_theme', 'Delete Discussion Theme'));
			    $.booki.sendToChannel("/booki/book/discussion/"+$.booki.currentBookID+"/"+$.booki.currentVersion+"/", {"command": "delete_themediscussion", "title": title, "user": user}, function(data) {
							if(data.deleted == 1) {
							    $.booki.ui.notify();
							    $("#discussioncommentcontent").hide();
							    $("#discussionthemecontent").show();
							    getDiscussionList();
							    
							} else if(data.deleted == 0){
							    $.booki.ui.notify();
							    alert($.booki._('can_not_delete_discussion_theme', "Can't delete discussion theme."));
							}
							else if(data.deleted == 2){
							    $.booki.ui.notify();
							    alert($.booki._('can_not_get_discussion_theme', "Can't delete discussion theme. The discussion may have been removed."));
							}
									
						    });
		}
		
		
		/*************************************************************************************
		 * EVENTS 
		 *************************************************************************************/
                 $(function() {		
		    /* Button New Discussion Theme */
		    $(".buttonadddiscussiontheme").click(function(){
		      showCreateDiscussionDialog();
		    });
		    
		    /* Link of Discussion Theme Title */
		    $(".linkdiscussiontheme").click(function(){
		      $("#discussionthemecontent").hide();
		      $("#discussioncommentcontent").show();
		      var item = $(this).attr("val");
		      $.booki.current_discussiontheme = item;
		      showDiscussionDetail(item);
		    });
		    
		    /* Link to Commentate */
		    $("#linkaddcomment").click(function(){
		      if($("#formaddcomment").hasClass('hide')) {
			      $("#formaddcomment").removeClass('hide');
			      $("#formaddcomment").addClass('show');
			      $("#formaddcomment").slideDown('fast');
		      } else {
			      $("#formaddcomment").removeClass('show');
			      $("#formaddcomment").addClass('hide');
			      $("#formaddcomment").slideUp('fast');
		      }
		    });
		    
		    /* Button Public Comment */
		    $("#buttonaddcommenttheme").click(function(){
			var item = $("#valcommenttheme").val();
			if(item.length > 1500){ 
			   $("#errortammaxcomment").show();
			   return;
			}
			else{
			  var theme = $.booki.current_discussiontheme;
			  addCommenttoTheme(item,theme);
			  $("#errortammaxcomment").hide();
			}
		    });
  
	        });
