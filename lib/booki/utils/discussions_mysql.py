import datetime
from booki.editor.models import DiscussionTheme
from booki.editor.models import DiscussionComment
from booki.editor.models import DiscussionCommentLike
from mysql_connect import Connect_BD
import time

# Function to get the last id from a elgg table
def Get_Last_Id(table):
   # database connect
   db = Connect_BD()
   cursor = db.cursor()
   sql = "SELECT MAX(guid) FROM " + table
   cursor.execute(sql)
   guid = cursor.fetchone()
   return guid

# Function to get a new object entity guid
def Get_Object_Entity():
   guid_array = Get_Last_Id('elgg_objects_entity')
   guid = guid_array[0] + 1
   return guid


# Function to get the elgg access from a Discussion Theme
def Get_Access(DiscussionTheme):
   # database connect
   db = Connect_BD()
   cursor = db.cursor()
   if DiscussionTheme.access == 'public':
     access = 2
   if DiscussionTheme.access == 'private':
     access = 0
   if DiscussionTheme.access == 'groupmembers':
     sql = "select id from elgg_access_collections where owner_guid = '"+ str(DiscussionTheme.book.group.id) + "'"
     cursor.execute(sql)
     result = cursor.fetchone()
     access = result[0]
   
   return access


# Function to save a Discussion Theme in Elgg
def Save_Discussion_Theme(DiscussionTheme):
   # database connect
   db = Connect_BD()
   cursor = db.cursor()
   
   # Modify objects_entity for title and description
   guid = str(DiscussionTheme.id)
   title = DiscussionTheme.title
   message = str(DiscussionTheme.message)
   sql = "insert into elgg_objects_entity (guid,title,description) values ('"+guid+"','"+title+"','"+message+"')"
   cursor.execute(sql)
   # Modify metastrings for labels
   labels = DiscussionTheme.labels
   labels.split(',')
   array_guid_labels = []
   for label in labels.split(','):      
      print label
      sql = "insert into elgg_metastrings (string) values ('"+label+"')"
      cursor.execute(sql)
      array_guid_labels.append(cursor.lastrowid)
   # Modify metadata to relationship discussion-labels and discussion-access
   user = DiscussionTheme.user
   access = Get_Access(DiscussionTheme)
   created = DiscussionTheme.created
   unix_created = time.mktime(created.timetuple())
   for label in array_guid_labels:
      sql = "insert into elgg_metadata (entity_guid, name_id, value_id, value_type, owner_guid, access_id, time_created, enabled) values ('"+guid+"','115','"+str(label)+"','text','"+str(user.id)+"','"+str(access)+"','"+str(unix_created)+"','yes')"
      cursor.execute(sql)
   
   # Modify entities to relationship discussion-writting_group
   sql = "insert into elgg_entities (guid, type, subtype, owner_guid, site_guid, container_guid, access_id, time_created, time_updated, last_action, enabled) values ('"+str(guid)+"','object','7','"+str(DiscussionTheme.user.id)+"','1','"+str(DiscussionTheme.book.group.id)+"','"+str(access)+"','"+str(unix_created)+"','"+str(unix_created)+"','"+str(unix_created)+"','yes')"
   cursor.execute(sql)

   return guid


# Function to update Discussion Theme
def Update_Discussion_Theme(DiscussionTheme):
   # database connect
   db = Connect_BD()
   cursor = db.cursor()
   guid = DiscussionTheme.id
   # Update title and description
   sql = "update elgg_objects_entity  set title = '"+DiscussionTheme.title+"', description = '"+str(DiscussionTheme.message)+"' where guid = '"+str(guid)+"'"
   cursor.execute(sql)
   # Delete from metadata old labels
   sql = "delete from elgg_metadata where entity_guid = '"+str(guid)+"' and name_id = '115' "
   cursor.execute(sql)
   # Insert new labels in metastrings
   labels = DiscussionTheme.labels
   labels.split(',')
   array_guid_labels = []
   for label in labels.split(','):      
      print label
      sql = "insert into elgg_metastrings (string) values ('"+label+"')"
      cursor.execute(sql)
      array_guid_labels.append(cursor.lastrowid)
   # Modify metadata to relationship update discussion-labels and update discussion-access
   user = DiscussionTheme.user
   access = Get_Access(DiscussionTheme)
   created = datetime.datetime.now()
   unix_created = time.mktime(created.timetuple())
   for label in array_guid_labels:
      sql = "insert into elgg_metadata (entity_guid, name_id, value_id, value_type, owner_guid, access_id, time_created, enabled) values ('"+str(guid)+"','115','"+str(label)+"','text','"+str(user.id)+"','"+str(access)+"','"+str(unix_created)+"','yes')"
      cursor.execute(sql)
   # Modify entities to update access, time updated and last action
   time_modified = datetime.datetime.now()
   unix_modified = time.mktime(time_modified.timetuple())
   sql = "update elgg_entities  set access_id= '"+str(access)+"', time_updated = '"+str(unix_modified)+"', last_action = '"+str(unix_modified)+"' where guid = '"+str(guid)+"'"
   
   return guid



# Function to save comment from discussion theme
def Save_Discussion_Comment(DiscussionComment):
   # database connect
   db = Connect_BD()
   cursor = db.cursor()
   
   Discussion = DiscussionComment.discussiontheme
   user = DiscussionComment.user
   
   # get access and created
   access = Get_Access(Discussion)
   created = DiscussionComment.created
   unix_created = time.mktime(created.timetuple())
   
   # insert comment into metastrings
   sql = "insert into elgg_metastrings (string) values ('"+DiscussionComment.comment+"')"
   cursor.execute(sql)
   guid_comment_metastring = cursor.lastrowid
   
   # insert comment into objects_entity
   guid_objects_entity = DiscussionComment.id
   sql = "insert into elgg_objects_entity (guid, title, description) values ('"+str(guid_objects_entity)+"','','')"
   cursor.execute(sql)
   
   # insert into entities relationship discussion-comment
   sql = "insert into elgg_entities (guid, type, subtype, owner_guid, site_guid, container_guid, access_id, time_created, time_updated, last_action, enabled) values ('"+str(guid_objects_entity)+"','object','13','"+str(DiscussionComment.user.id)+"','1','"+str(DiscussionComment.discussiontheme.id)+"','"+str(access)+"','"+str(unix_created)+"','"+str(unix_created)+"','"+str(unix_created)+"','yes')"
   cursor.execute(sql)
   
   # insert the comment into annotations
   sql = "insert into elgg_annotations (entity_guid, name_id, value_id, value_type, owner_guid, access_id, time_created, enabled) values ('"+str(DiscussionComment.discussiontheme.id)+"','189','"+str(guid_comment_metastring)+"','text','"+str(DiscussionComment.user.id)+"','"+str(access)+"','"+str(unix_created)+"','yes')"
   cursor.execute(sql)
   
   # insert into metadata
   sql = "insert into elgg_metadata (entity_guid, name_id, value_id, value_type, owner_guid, access_id, time_created, enabled) values ('"+str(guid_objects_entity)+"','269','"+str(guid_comment_metastring)+"','text','"+str(user.id)+"','"+str(access)+"','"+str(unix_created)+"','yes')"
   cursor.execute(sql)
   sql = "insert into elgg_metadata (entity_guid, name_id, value_id, value_type, owner_guid, access_id, time_created, enabled) values ('"+str(guid_objects_entity)+"','271','189','text','"+str(user.id)+"','"+str(access)+"','"+str(unix_created)+"','yes')"
   cursor.execute(sql)
   sql = "insert into elgg_metadata (entity_guid, name_id, value_id, value_type, owner_guid, access_id, time_created, enabled) values ('"+str(guid_objects_entity)+"','272','29','text','"+str(user.id)+"','"+str(access)+"','"+str(unix_created)+"','yes')"
   cursor.execute(sql)
   sql = "insert into elgg_metadata (entity_guid, name_id, value_id, value_type, owner_guid, access_id, time_created, enabled) values ('"+str(guid_objects_entity)+"','273','626','integer','"+str(user.id)+"','"+str(access)+"','"+str(unix_created)+"','yes')"
   cursor.execute(sql)
   
   return True



# Function to like a comment
def Like_Discussion_Comment(CommentLike):
   # database connect
   db = Connect_BD()
   cursor = db.cursor()
   
   Comment = CommentLike.discussioncomment
   Discussion = Comment.discussiontheme
   user = CommentLike.user
   
   # get access and created
   access = Get_Access(Discussion)
   created = datetime.datetime.now()
   unix_created = time.mktime(created.timetuple())
   
   # insert like into objects_entity
   guid_objects_entity = CommentLike.id
   sql = "insert into elgg_objects_entity (guid, title, description) values ('"+str(guid_objects_entity)+"','','')"
   cursor.execute(sql)
   
   # insert into entities relationship like-comment
   sql = "insert into elgg_entities (guid, type, subtype, owner_guid, site_guid, container_guid, access_id, time_created, time_updated, last_action, enabled) values ('"+str(guid_objects_entity)+"','object','13','"+str(user.id)+"','1','"+str(Comment.id)+"','"+str(access)+"','"+str(unix_created)+"','"+str(unix_created)+"','"+str(unix_created)+"','yes')"
   cursor.execute(sql)
   
   # insert into annotations
   sql = "insert into elgg_annotations (entity_guid, name_id, value_id, value_type, owner_guid, access_id, time_created, enabled) values ('"+str(guid_objects_entity)+"','61','4','text','"+str(user.id)+"','"+str(access)+"','"+str(unix_created)+"','yes')"
   cursor.execute(sql)
   guid_like_annotations = cursor.lastrowid
   
   # insert into metastrings
   sql = "insert into elgg_metastrings (string) values ('"+str(guid_like_annotations)+"')"
   cursor.execute(sql)
   guid_like_metastring = cursor.lastrowid
   
   # insert into metadata
   sql = "insert into elgg_metadata (entity_guid, name_id, value_id, value_type, owner_guid, access_id, time_created, enabled) values ('"+str(guid_objects_entity)+"','269','4','text','"+str(user.id)+"','"+str(access)+"','"+str(unix_created)+"','yes')"
   cursor.execute(sql)
   sql = "insert into elgg_metadata (entity_guid, name_id, value_id, value_type, owner_guid, access_id, time_created, enabled) values ('"+str(guid_objects_entity)+"','271','61','text','"+str(user.id)+"','"+str(access)+"','"+str(unix_created)+"','yes')"
   cursor.execute(sql)
   sql = "insert into elgg_metadata (entity_guid, name_id, value_id, value_type, owner_guid, access_id, time_created, enabled) values ('"+str(guid_objects_entity)+"','273','"+str(guid_like_metastring)+"','integer','"+str(user.id)+"','"+str(access)+"','"+str(unix_created)+"','yes')"
   cursor.execute(sql)
   
   return True
   


# Function to unlike a comment
def Unlike_Discussion_Comment(CommentLike):
   # database connect
   db = Connect_BD()
   cursor = db.cursor()
   
   Comment = CommentLike.discussioncomment
   Discussion = Comment.discussiontheme
   user = CommentLike.user
   
   # get guid from like
   guid = CommentLike.id
   
   # delete from metadata
   sql = "delete from elgg_metadata where entity_guid = '"+str(guid)+"'"
   cursor.execute(sql)
   
   # delete from entities the relationships
   sql = "delete from elgg_entities where guid = '"+str(guid)+"'"
   cursor.execute(sql)
   
   # delete from objects_entity the object
   sql = "delete from elgg_objects_entity where guid = '"+str(guid)+"'"
   cursor.execute(sql)
   
   return True


# Function to delete a comment from discussion theme
def Delete_Discussion_Comment(DiscussionComment):
   # database connect
   db = Connect_BD()
   cursor = db.cursor()
   
   guid = DiscussionComment.id
   Likes = DiscussionCommentLike.objects.filter(discussioncomment = DiscussionComment)
   
   # delete the likes from comment
   for like in Likes:
     Unlike_Discussion_Comment(like)
   
   # get the metastring id of comment from metadata
   sql = "select value_id from elgg_metadata where entity_guid = '"+str(DiscussionComment.id)+"' and name_id = '269'"
   cursor.execute(sql)
   result = cursor.fetchone()
   metastring_id = result[0]
   
   # delete the comment from metadata
   sql = "delete from elgg_metadata where entity_guid = '"+str(guid)+"'"
   cursor.execute(sql)
      
   # delete from annotations
   sql = "delete from elgg_annotations where value_id = '"+str(metastring_id)+"'"
   cursor.execute(sql)
   
   # delete from entities
   sql = "delete from elgg_entities where guid = '"+str(guid)+"'"
   cursor.execute(sql)
   
   # delete the object from objects_entity
   sql = "delete from elgg_objects_entity where guid = '"+str(guid)+"'"
   cursor.execute(sql)
   
   return True



# Function to delete a discussion theme
def Delete_Discussion_Theme(DiscussionTheme):
   # database connect
   db = Connect_BD()
   cursor = db.cursor()
   
   # guid from discussion
   guid = DiscussionTheme.id
  
   # delete comments from discussion
   comment_list = DiscussionComment.objects.filter(discussiontheme = DiscussionTheme)
   for comment in comment_list:
     # delete likes from comment
     like_list = DiscussionCommentLike.objects.filter(discussioncomment = comment)
     for like in like_list:
        Unlike_Discussion_Comment(like)
     Delete_Discussion_Comment(comment)
   
   # delete relationship discussion-writting_group
   sql = "delete from elgg_entities where guid = '"+str(guid)+"'"
   cursor.execute(sql)
   
   # delete labels and access from metadata
   sql = "delete from elgg_metadata where entity_guid = '"+str(guid)+"'"
   cursor.execute(sql)
   
   # delete title and description from objects_entity
   sql = "delete from elgg_objects_entity where guid = '"+str(guid)+"'"
   cursor.execute(sql)
   
   return True
   
 
 