#!/usr/bin/env python

import os.path

import sys ; sys.path.append("/srv/www/sites/bicker.kamaelia.org/cgi/app/Facilitate")
import CookieJar

from model.Record import EntitySet

EntitySet.data = "/srv/www/sites/bicker.kamaelia.org/cgi/app/data"

Images        = EntitySet("images", key="imageid")
Registrations = EntitySet("registrations", key="regid")

loggedout = False

def loggedIn(env):
    if loggedout:
        return False

    cookies = env.get("cookies", None)
    if not cookies:
        return False

    sessioncookie_raw = cookies.get("sessioncookie", None)
    if not sessioncookie_raw:
        return False

    sessioncookie = sessioncookie_raw.value

    try:
        userid = CookieJar.getUser(sessioncookie)
    except CookieJar.NoSuchUser:
        return False

    user = Registrations.get_record(userid)
    if user["confirmed"]:
        return userid
    else:
        return False

upload_form = """\
<form action="http://bicker.kamaelia.org/cgi-bin/app/images" method="POST"
enctype="multipart/form-data">
<input type="hidden" name="action" value="upload" />

Upload file: <input type="file" name="upload.filename" value="" size="30"/>

<input type="submit" value="submit" />

</form>
"""

class tagHandler(object):
      def doUploadForm(bunch, text, env):
          return upload_form

      def doUserImages(bunch, text, env):
          userid = loggedIn(env)
          if userid:
              images = Images.read_database()
              user_images = []
              for image in images:
                  if image["userid"] == userid:
                      user_images.append(image)
              Y = [ x["unique_name"] for x in user_images]
              images = []
              for image in user_images:
                  image = "<img class='column twoC button' src='/images/user/%(unique_name)s/thumb.jpg'>" % image
                  images.append(image)
              return "".join(images)+ '<div class="divide"></div>'
              return repr(Y)
          else:
              return "can't give you images, you're not logged in"
          
      mapping = {
           "uploadone_form" : doUploadForm,
           "userimages" : doUserImages,
      }

mapping = tagHandler.mapping

if __name__ == "__main__":
   print "TAG HANDLER", tagHandler
   print "MAPPING", tagHandler.mapping
   print "HMM", tagHandler.mapping["w"]({"location":"bingle"}, "hello world", {})



   if 0:
          if loggedIn(env):
              myid = loggedIn(env)
              for rec in Contacts.read_database():
                  if rec["contactof"] == myid:
                      break
              else:
                  return text

              users = ["<ul>"]
              for contactid in rec["contacts"]:
                  user = Registrations.get_record(contactid)
                  user["email"] = user["email"][user["email"].find("@")+1:]
                  users.append( "<li> <B>%(screenname)s</b> ( %(email)s )" % user )
              users.append("</ul>")
              
              return "\n".join(users)
          else:
              return "Sorry, in order to have a contact/friends list, you must be logged in!"
