from lxml import etree, html
import sputnik
from django.db import transaction
from booki.editor import models
from booki.utils.misc import bookiSlugify
from django.conf import settings
from booki.utils import config

from booki.utils import discussions_mysql

try:
    OBJAVI_URL = settings.OBJAVI_URL
except AttributeError:
    OBJAVI_URL = constants.OBJAVI_URL

try:
    THIS_BOOKI_SERVER = settings.THIS_BOOKI_SERVER
except AttributeError:
    THIS_BOOKI_SERVER = constants.THIS_BOOKI_SERVER


###
 # MODIFICATION UCSP
 # Function to creation and integration of discussion theme module
 
def remote_create_discussion(request, message, bookid, version):
    """ 
    Function to create the discussion theme in the model
    """
    import datetime
    book = models.Book.objects.get(id=bookid)
    user = request.user
    url_title = bookiSlugify(message["discussion"])
    title = message["discussion"]
    lmessage = message["message"]
    state = "1"
    labels = message["labels"]
    access = message["access"]
    
    try:
      # Elgg Integration
      guid = discussions_mysql.Get_Object_Entity()
      #
      discussiontheme = models.DiscussionTheme(id = int(guid),
			      book = book,
			      user = user,
			      url_title = url_title,
			      title = title,
			      message = lmessage,
			      state = state,
			      labels = labels,
			      access = access,
			      created = datetime.datetime.now())

      discussiontheme.save()
      # Elgg Integration
      elgg = discussions_mysql.Save_Discussion_Theme(discussiontheme)
    except:
      transaction.rollback()
      return {"created": False}
    else:
      transaction.commit()
    
    
    
    discussion = []
    discussion.append({"title": discussiontheme.title,
		 "message": discussiontheme.message,
		 "user": discussiontheme.user.username,
		 "created": discussiontheme.created.strftime("%d %b. %Y, %H:%M")})
     
    return {"created": True, "discussion": discussion}


def remote_edit_discussion(request, message, bookid, version):
    """ 
    Function to edit the discussion theme in the model
    """
    import datetime
     
    discussiontheme = models.DiscussionTheme.objects.get(title = message["old_title"])
    
    discussiontheme.title = message["new_title"]
    url_title = bookiSlugify(message["new_title"])
    discussiontheme.url_title = url_title
    discussiontheme.message = message["new_message"]
    discussiontheme.labels = message["new_labels"]
    discussiontheme.access = message["new_access"]
    
    try:
      # Elgg Integration
      elgg = discussions_mysql.Update_Discussion_Theme(discussiontheme)
      #
      discussiontheme.save()
    except:
      transaction.rollback()
      return {"edited": False}
    else:
      transaction.commit()
      
    discussion = []
    discussion.append({"title": discussiontheme.title,
		 "message": discussiontheme.message,
		 "labels": discussiontheme.labels,
		 "access": discussiontheme.access,
		 "user": discussiontheme.user.username,
		 "created": discussiontheme.created.strftime("%d %b. %Y, %H:%M")})
     
    return {"edited": True, "discussion": discussion}



def remote_get_discussion_list(request, message, bookid, version):
    """
    Function to get the discussion list
    """
    book = models.Book.objects.get(id=bookid)
    discussion_list = models.DiscussionTheme.objects.filter(book = book).order_by('created')
    group = book.group
    members = group.members.all()
    is_member = request.user in members
    
    
    discussions = []
    
    try:
      for discussion in discussion_list:
	if discussion.access == 'public' or discussion.access == 'groupmembers' and is_member or discussion.access == 'private' and discussion.user == request.user:
	    discussions.append({"title": discussion.title,
				  "message": discussion.message,
				  "labels": discussion.labels,
				  "access": discussion.access,
				  "state": discussion.state,
				  "user": discussion.user.username,
				  "created": discussion.created.strftime("%d %b. %Y, %H:%M")})
    except:
      transaction.rollback()
      return {"get":False}
    else:
      transaction.commit()
      
    return {"get": True, "discussions": discussions}


def remote_get_discussion_list_by_label(request, message, bookid, version):
    """
    Function to get the discussion list search by label
    """
    book = models.Book.objects.get(id=bookid)
    discussion_list = models.DiscussionTheme.objects.filter(book = book).order_by('created')
    group = book.group
    members = group.members.all()
    is_member = request.user in members
    
    
    discussions = []
    lab_array = []
    
    
    try:
      for discussion in discussion_list:
	labels = discussion.labels
	for label in labels.split(','):
	  if(label.strip() == message['label'].strip()):
	    lab_array.append({"label": label.strip()})
	    if discussion.access == 'public' or discussion.access == 'groupmembers' and is_member or discussion.access == 'private' and discussion.user == request.user:
		discussions.append({"title": discussion.title,
				      "message": discussion.message,
				      "labels": discussion.labels,
				      "access": discussion.access,
				      "state": discussion.state,
				      "user": discussion.user.username,
				      "created": discussion.created.strftime("%d %b. %Y, %H:%M")})
    except:
      transaction.rollback()
      return {"get":False}
    else:
      transaction.commit()
      
    return {"get": True, "discussions": discussions, "lab_array": lab_array}



def remote_get_comment_list(request, message, bookid, version):
    """
    Function to get the commnet list from a discussion theme
    """
    discussion_title = message['title']
    discussion = models.DiscussionTheme.objects.get(title = discussion_title)
    comment_list = models.DiscussionComment.objects.filter(discussiontheme = discussion).order_by('created')
    likes_list = models.DiscussionCommentLike.objects.filter(user = request.user)
    
    comments = []
    
    import time
    import datetime
    
    try:
      for comment in comment_list:
	# Check if user can remove comment : Only comment owner or discussion owner can remove comment
	can_remove = 0
	if request.user == comment.user or request.user == discussion.user:
	  can_remove = 1
	# Get the created time in unix format
	created = comment.created
        unix_created = time.mktime(created.timetuple())*1e3 + created.microsecond/1e3

	# Check if the comment is liked or no by the user
	comment_is_like = 0
	for like in likes_list:
	    if like.discussioncomment == comment:
	      comment_is_like = 1
	      break
	if comment_is_like == 1: 	    
	      comments.append({"user": comment.user.username,
				"comment": comment.comment,
				"id": comment.id,
				"created": comment.created.strftime("%d %b. %Y, %H:%M"),    
				"like_next_func":'remove',
				"likes": comment.nro_likes,
				"unix_created": unix_created,
				"can_remove": can_remove})
	else:
	      comments.append({"user": comment.user.username,
				"comment": comment.comment,
				"id": comment.id,
				"created": comment.created.strftime("%d %b. %Y, %H:%M"),
				"like_next_func":'add',
				"likes": comment.nro_likes,
				"unix_created": unix_created,
				"can_remove": can_remove})
    except:
      transaction.rollback()
      return {"get": False}
    else:
      transaction.commit()
      
    return {"get": True, "comments": comments}
    
    
    

def remote_get_discussion_detail(request, message, bookid, version):
    """
    Function to get the discussion detail
    """
    discussion_title = message['title']
    try:
      discussion = models.DiscussionTheme.objects.get(title = discussion_title)
    except:
      return {"get": False}
    else:
      transaction.commit()
    
    # Check if user is discussion owner
    if request.user == discussion.user:
      is_owner = 'true'
    else:
      is_owner = 'false'
    
    head = []
    head.append({"title": discussion.title,
		 "message": discussion.message,
		 "labels": discussion.labels,
		 "access": discussion.access,
		 "user": discussion.user.username,
		 "created": discussion.created.strftime("%d %b. %Y, %H:%M"),
		 "is_owner": is_owner})
    
    labels = []
    labels_array = discussion.labels
    labels_array.split(',')
    tam = len(labels_array)
    
    # Get the labels
    for label in labels_array.split(','):
      labels.append({'label':label})
    
    return {"get": True, "head": head, "labels": labels}


def remote_add_comment_to_theme(request, message, bookid, version):
    """
    Function to add comment to discussion theme
    """
    import datetime
    theme_title = message['theme']
    theme = models.DiscussionTheme.objects.get(title = theme_title)
    user = request.user
    comment = message['comment']
    nro_likes = 0
    
    book = models.Book.objects.get(id=bookid)
    group = book.group
    members = group.members.all()
    is_member = request.user in members
    
    access = theme.access
    
    if access == 'public' or access == 'groupmembers' and is_member or access == 'private' and theme.user == user:
	try:
	    # Elgg Integration
            guid = discussions_mysql.Get_Object_Entity()
	    commenttheme = models.DiscussionComment(id = int(guid),
				  discussiontheme = theme,
				  user = user,
				  comment = comment,
				  nro_likes = nro_likes,
				  created = datetime.datetime.now())

	    commenttheme.save()
	    # Elgg Integration
	    elgg = discussions_mysql.Save_Discussion_Comment(commenttheme)
	except:
	  transaction.rollback()
	  return {"created": False}
	else:
	  transaction.commit()
    else:
       return {"created": False}
    import time
    import datetime  
    created = commenttheme.created
    unix_created = time.mktime(created.timetuple())*1e3 + created.microsecond/1e3
    comm = []
    comm.append({"comment": commenttheme.comment,
		 "user": commenttheme.user.username,
		 "created": commenttheme.created.strftime("%d %b. %Y, %H:%M"),
		 "likes": commenttheme.nro_likes,
		 "unix_created": unix_created,
		 "iden": commenttheme.id})
    
    return {"created": True, "comment": comm}



def remote_update_like_to_comment(request, message, bookid, version):
    """
    Function to like/unlike comment
    """
    import time
    import datetime  
    unix_created = message['unix_created']
    unix_created = unix_created
    time_created = datetime.datetime.fromtimestamp(unix_created/1000.0)
    
    
    like = []
    if message['function'] == 'add':
        try: 
	  comment = models.DiscussionComment.objects.get(comment = message['comment'], discussiontheme__title = message['theme'], user__username = message['user'], created = time_created)
	except:
	  transaction.rollback()
	  return {"updated":2}
	else:
	  transaction.commit()
	  
	user = request.user
	value = 1
	
        
        is_like = models.DiscussionCommentLike.objects.filter(discussioncomment = comment, user = user).count()
        if is_like > 0:
	   return {"updated":0}
        
        try:
	  # Elgg Integration
          guid = discussions_mysql.Get_Object_Entity()
	  commentlike = models.DiscussionCommentLike( id = int(guid),
						      discussioncomment = comment,
						      user = user,
						      value = value)
	  commentlike.save() 
	  comment.nro_likes = comment.nro_likes + value
	  comment.save()
	  # Elgg Integration
	  elgg_comm = discussions_mysql.Like_Discussion_Comment(commentlike)
	except:
	  transaction.rollback()
	  return {"updated":0}
	else:
	  transaction.commit()
	  
	like.append({"iden": comment.id,
		     "comment": comment.comment,
		     "next_func": 'remove',
		     "discussion": comment.discussiontheme.title,
		     "like": 1})
	
    if message['function'] == 'remove':
	try:
	  comment = models.DiscussionComment.objects.get(comment = message['comment'], discussiontheme__title = message['theme'], user__username = message['user'], created = time_created)
	except:
	  transaction.rollback()
	  return {"updated": 2}
	else:
	  transaction.commit()
	
	try:
	  commentlike = models.DiscussionCommentLike.objects.get(discussioncomment = comment, user = request.user)
	  # Elgg Integration
	  elgg_comm = discussions_mysql.Unlike_Discussion_Comment(commentlike)
	  commentlike.delete()
	  value = 1
	  comment.nro_likes = comment.nro_likes - value
	  comment.save()
	except:
	  transaction.rollback()
	  return {"updated": 0}
	else:
	  transaction.commit()
	
	like.append({"iden": comment.id,
		     "comment": comment.comment,
		     "next_func": 'add',
		     "discussion": comment.discussiontheme.title,
		     "like": 0})
      
    return {"updated": 1, "like": like}


def remote_delete_all_likes_from_comment(request, message, bookid, version):
    """
    Function to delete all likes from a comment
    """
    comment = models.DiscussionComment.objects.get(comment = message['comment'])
    likes_list = models.DiscussionCommentLike.objects.filter(discussioncomment = comment)
    for like in likes_list:
      like.delete()
    
    comment.nro_likes = 0
    comment.save()
    
    return {"deleted": True}


def remote_delete_all_comments_from_theme(request, message, bookid, version):
    """
    Function to delete all comments from a discussion theme
    """
    theme = models.DiscussionTheme.objects.get(title = message['title'])
    comments_list = models.DiscussionComment.objects.filter(discussiontheme = theme)
    for comment in comments_list:
      mes = []
      mes.append({"comment":comment.comment})
      remote_delete_all_likes_from_comment(request, mes, bookid, version)
      comment.delete()
    
    return {"deleted": True}


def remote_delete_comment_from_theme(request, message, bookid, version):
    """
    Function to delete comment from a discussion theme
    """
    try: 
      comment = models.DiscussionComment.objects.get(comment = message['comment'], user__username = message['user'])
    except:
      transaction.rollback()
      return {"deleted": 2}
    else:
      transaction.commit()
    
    try:
      # Elgg Integration
      elgg = discussions_mysql.Delete_Discussion_Comment(comment)
      #
      likes_list = models.DiscussionCommentLike.objects.filter(discussioncomment = comment)
      for like in likes_list:
	like.delete()
      comment.delete()
    except:
      transaction.rollback()
      return {"deleted": 0}
    else:
      transaction.commit()
      
    return {"deleted": 1}
 

def remote_delete_themediscussion(request, message, bookid, version):
    """
    Function to delete discussion theme
    """
    try:
      theme = models.DiscussionTheme.objects.get(title = message['title'])
    except:
      transaction.rollback()
      return {"deleted": 2}
    else:
      transaction.commit()
      
    try:  
	comments_list = models.DiscussionComment.objects.filter(discussiontheme = theme)
	elgg = discussions_mysql.Delete_Discussion_Theme(theme)
	for comment in comments_list:
	  likes_list = models.DiscussionCommentLike.objects.filter(discussioncomment = comment)
	  for like in likes_list:
	    like.delete()
	  comment.delete()
	theme.state = "0"
	theme.save()
	# Elgg Integration
	elgg = discussions_mysql.Delete_Discussion_Theme(theme)
    except:
      transaction.rollback()
      return {"deleted": 0}
      
    return {"deleted": 1}
    