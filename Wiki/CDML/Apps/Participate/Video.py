#!/usr/bin/env python

import os.path

# import sys ; sys.path.append("/srv/www/sites/bicker.kamaelia.org/cgi/app/")
# import CookieJar
# 
# from model.Record import EntitySet
# 
# EntitySet.data = "/srv/www/sites/bicker.kamaelia.org/cgi/app/data"
# Registrations = EntitySet("registrations", key="regid")
# Contacts      = EntitySet("contacts", key="contactid")
# 
# def set_cookie(env, thecookie, value):
#     env["context"]["newcookies"][thecookie] = value

playerscript = """\
<script type="text/javascript" src="/flvplayer/swfobject.js"></script>

<script type="text/javascript">
    var flashvars = {};
                // The following 3 things should change for the content
                flashvars.contentpath = "http://bicker.kamaelia.org/%(path_to_player)s";
                flashvars.video = "%(filename)s";
                flashvars.preview = "%(preview)s";

                // Following needs to change for other sites
                flashvars.playerpath = "http://bicker.kamaelia.org/flvplayer";

                // You could change these. I wouldn't, but you could.
                flashvars.skin = "skin-applestyle.swf";
                flashvars.skincolor = "0xaaddaa";
                flashvars.skinscalemaximum = "1";

                // If you change these, you'll need to change other things
                flashvars.autoscale = "false";
                flashvars.videowidth = "466";
                flashvars.videoheight = "350";

                var params = {};
                        params.scale = "noscale";
                        params.allowfullscreen = "true";
                        params.salign = "tl";

                var attributes = {};
                        attributes.align = "left";

        swfobject.embedSWF("/flvplayer/flvplayer.swf",
                           "videoPlayer",
                           "466", "380",
                           "9.0.28",
                           "/flvplayer/expressInstall.swf",
                           flashvars, params, attributes);
</script>
"""

player = """\
<div class="divide"></div>
        <div  class="column oneC"> &nbsp; </div>
        <div id="videoPlayer" class="column sixC">
            <p>This content requires the Adobe Flash Player.</p>
                <p><a href="http://www.adobe.com/go/getflashplayer"><img src="http://www.adobe.com/images/shared/download_buttons/get_flash_player.gif" alt="Get Adobe Flash player" /></a>
            </p>
        </div>
        <div  class="column oneC"> &nbsp; </div>
<div class="divide"></div>
"""

class tagHandler(object):
      def doVideoPlayerScript(bunch, text, env):
          return env["context"].get("video.headeritems", "")
          
      def doVideoPlayer(bunch, text, env):
          args = {
             "path_to_player" : "videos/user/",
             "filename" : bunch.get("video", text)+".flv",
             "preview" : "preview.jpg",
          }
          env["context"]["video.headeritems"] = playerscript % args
          return player

      mapping = {
           "videoplayerscript" : doVideoPlayerScript,
           "videoplayer" : doVideoPlayer,
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
