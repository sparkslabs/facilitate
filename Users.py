#!/usr/bin/env python

from Cheetah.Template import Template
from model.Record import EntitySet

UsersDatabase = EntitySet("users",key="userid")

def store_new_user(the_user): return UsersDatabase.new_record(the_user)
def read_database(): return UsersDatabase.read_database()
def store_user(user): return UsersDatabase.store_record(user)
def get_user(user): return UsersDatabase.get_record(user)
def delete_user(user): return UsersDatabase.delete_record(user)

#
# Map web request to data layer
#

def make_user(stem="form", **argd):
    new_user = {
        "username" : argd.get(stem + ".username",""),
        "loggedin" : argd.get(stem + ".loggedin","pending"), # we create the user in the pending | loggedoff  state ?
        "personid" : argd.get(stem + ".personid",""),        # a user is a person?
    }
    new_user = store_new_user(new_user)
    return new_user

#
# Map web request to data layer
#

def update_user(stem="form", **argd):
    the_user = {
        "userid" : argd.get(stem + ".userid",""),
        "username" : argd.get(stem + ".username",""),
        "loggedin" : argd.get(stem + ".loggedin",""),      # state = "yes", "no", "pending"
        "personid" : argd.get(stem + ".personid",""),      # a user is a person?
    }
    store_user(the_user)
    return the_user

def dummy_user(stem="form", **argd):                       # a blank user to pass around
    the_user = {
        "userid" : argd.get(stem + ".userid",""),
        "username" : argd.get(stem + ".username",""),
        "loggedin" : argd.get(stem + ".loggedin","no"),    # state = "yes", "no", "pending"
        "personid" : argd.get(stem + ".personid",""),      # a user is a person?
    }
    return the_user

class RecordRender(object):
    record_listview_template = 'templates/Users.View.tmpl'
    record_editget_template = 'templates/User.Edit.tmpl'
    record_view_template = 'templates/User.View.tmpl'
    record_user_login_template = 'templates/User.Login.tmpl'
    record_editpost_template = 'templates/Form.tmpl'         # Actually to do with a configured form isn't it...
    page_template = 'templates/UserPage.tmpl'

    def __init__(self, environ,**argd):
        self.environ = environ
        self.__dict__.update(argd)

    def rendered_record_list(self, addresses):
        users = Template ( file = self.record_listview_template,
                            searchList = [self.environ, {"users": addresses}] )
        return users

    def rendered_record_entry_form(self, item):
        dataentry = Template ( file = self.record_editget_template,
                               searchList = [self.environ, item] )
        return dataentry

    def rendered_user_login_form(self, item):
        dataentry = Template ( file = self.record_user_login_template,
                               searchList = [self.environ, item] )
        return dataentry

    def rendered_record(self, item):
        dataentry = Template ( file = self.record_view_template,
                               searchList = [self.environ, item] )
        return dataentry

    def render_configured_form(self, pre_filled_data_entry,
                               nextstep="create_new",
                               submitlabel="Add Item"):

        configured_form = Template ( file = self.record_editpost_template,
                                     searchList = [
                                         self.environ, {
                                           "formbody":pre_filled_data_entry,
                                           "formtype":nextstep,
                                           "submitlabel": submitlabel,
                                                  }]
                                   )
        return configured_form

    def render_page(self, content="", extra="", dataentry=""):
        return str(Template ( file = self.page_template,
                             searchList = [
                                  self.environ,
                                  {
                                    "extra": extra ,
                                    "content" : content,
                                    "dataentry" : dataentry,
                                  }
                              ] ))

    def user_exists(self):
        return 


#
# Actually User Life Cycle Logic
#

def page_render_html(json, **argd):
    action = argd.get("formtype","overview")
    R = RecordRender(argd["__environ__"])
    if action == "overview":
        # Show the database & a few options
        addresses = read_database()
        users                = R.rendered_record_list(addresses)
        return R.render_page(content=users,extra={"user":"None"})

    #if action == "user_greet":
    #    dummy_content = "<B> User Landing Page </B>. next state is  user_login "
    #    return R.render_page(content=dummy_content)

    if action == "user_login":
        this_user = dummy_user(stem="form", **argd)
        dummy_content = "<B> User Login Page </B>. get login details next state is user_verify "  # Real content is new template to get username and password
        pre_filled_data_entry = R.rendered_user_login_form(this_user)
        configured_form       = R.render_configured_form(pre_filled_data_entry,
                                                       nextstep="user_verify",
                                                       )
        
        return R.render_page(content=dummy_content, dataentry=configured_form, extra={"user":"None"})

    if action == "user_verify":
        if R.user_exists():
            pass
        else:
            pass
        dummy_content = "<B>  User Verify  </B>. if valid update user record, state next state is user_view else user_challenge"
        return R.render_page(content=dummy_content,extra={"user":"None"})

    if action == "user_view":
        dummy_content = "<B> User View </B>. whatever this user can view or edit determined by owns and can view relations"
        return R.render_page(content=dummy_content)

    if action == "user_challenge":
        dummy_content = "<B> User Challenge </B>. if lost password/username  next state is user_lost_password else user_create_new else bog off"  
        return R.render_page(content=dummy_content)

    if action == "user_verify":
        dummy_content = "<B> User Challenge </B>. user_createnew"
        return R.render_page(content=dummy_content)

    if action == "user_create_new":
        dummy_content = "<B> User Create New</B>. Create new  user in state pending "
        return R.render_page(content=dummy_content)

    if action == "user_validate_new":
        dummy_content = "<B> Validate New  </B>.  next state is user_pending" 
        return R.render_page(content=dummy_content)

    if action == "user_logout":
        dummy_content = "<B> Logout Page </B> if logout update user record  next state is user greet"
        return R.render_page(content=dummy_content,extra={"user":"None"})

    if action == "user_lostpassword":
        dummy_content = "<B> User lost password  </B>. user enters email ddress if valid send login else bog off"
        return R.render_page(content=dummy_content)
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
  
    
 # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
 #                     original ms users below here                       #
 # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    if action == "edit_new":
        # Show the database & a form for creating a new user
        addresses = read_database()
        users           = R.rendered_record_list(addresses)
        empty_data_entry = R.rendered_record_entry_form({})
        configured_form  = R.render_configured_form(empty_data_entry)

        return R.render_page(content=users, dataentry=configured_form)

    if action == "create_new":
        # Take the data sent to us, and use that to fill out an edit form
        # Note: This is actually filling in an *edit* form at that point, not a *new* user form
        # If they submit the new form, the surely they should be viewed to be updating the form?
        # yes...
        #
        new_user = make_user(stem="form", **argd) # This also stores them in the database

        addresses = read_database()
        users                = R.rendered_record_list(addresses)
        pre_filled_data_entry = R.rendered_record_entry_form(new_user)
        configured_form       = R.render_configured_form(pre_filled_data_entry,
                                                       nextstep="update_user",
                                                       )
        return R.render_page(content=users, dataentry=configured_form)

    if action == "view_user":
        # Show the database & a few options
        user = get_user(argd["userid"])
        addresses = read_database()
        users                = R.rendered_record_list(addresses)
        user_rendered = R.rendered_record(user)

        return R.render_page(content=users, dataentry=user_rendered)

    if action == "edit_user":
        user = get_user(argd["userid"])

        addresses = read_database()
        users                = R.rendered_record_list(addresses)
        pre_filled_data_entry = R.rendered_record_entry_form(user)
        configured_form       = R.render_configured_form(pre_filled_data_entry,
                                                       nextstep="update_user",
                                                       )
        return R.render_page(content=users, dataentry=configured_form)

    if action == "update_user":
        # Take the data sent to us, and use that to fill out an edit form
        #
        # Note: This is actually filling in an *edit* form at that point, not a *new* user form
        # If they submit the new form, the surely they should be viewed to be updating the form?
        # yes...
        #
        theuser = update_user(stem="form", **argd)

        addresses = read_database()
        users                = R.rendered_record_list(addresses)
        pre_filled_data_entry = R.rendered_record_entry_form(theuser)
        configured_form       = R.render_configured_form(pre_filled_data_entry,nextstep="update_user")

        return R.render_page(content=users, dataentry=configured_form)

    if action == "delete_user":
        # Take the data sent to us, and use that to fill out an edit form
        #
        # Note: This is actually filling in an *edit* form at that point, not a *new* user form
        # If they submit the new form, the surely they should be viewed to be updating the form?
        # yes...
        #
        # Show the database & a few options
        user = get_user(argd["userid"])
        addresses = read_database()
        users                = R.rendered_record_list(addresses)
        user_rendered = R.rendered_record(user)
        user_rendered = "<h3> Are you sure you wish to delete this user?</h3><ul>" + str(user_rendered)

        delete_action = "<a href='/cgi-bin/app/users?formtype=confirm_delete_user&userid=%s'>%s</a>" % (user["userid"], "Delete this user")
        cancel_action = "<a href='/cgi-bin/app/users?formtype=view_user&userid=%s'>%s</a>" % (user["userid"], "Cancel deletion")
        user_rendered += "</ul><h3> %s | %s </h3>" % (delete_action, cancel_action)

        return R.render_page(content=users, dataentry=user_rendered)

    if action == "confirm_delete_user":
        # Show the database & a few options
        user = get_user(argd["userid"])
        delete_user(argd["userid"])

        addresses = read_database()
        users          = R.rendered_record_list(addresses)
        user_rendered = R.rendered_record(user)

        return R.render_page(content=users, dataentry="<h1> %s Deleted </h1>" % user["user"])


    return str(Template ( file = 'templates/Page.tmpl', 
                         searchList = [
                            argd["__environ__"],
                              {
                                "extra": "" ,
                                "content" : "Sorry, got no idea what you're on!",
                                "dataentry" : "",
                                "banner" : "Not found", # should send back a 404 status then? Or similar?
                              }
                          ] ))

if __name__ == "__main__":

    print "Content-Type: text/html"
    print

    print page_render_html({})
