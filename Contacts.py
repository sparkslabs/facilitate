#!/usr/bin/python
"""
This script handles user registrations
"""
import md5                          # for hexdigest
import random                       # for confirmation codes
import time                         # to check age
import pprint                       # for dumping errors

import CookieJar
import Cookie
from model.Record import EntitySet  # For access to the temporary DB
import Interstitials


def new_contacts(**argd):
    rec = {
      # --------------------------------------------------------- Required to create a new record
        'dob.day'          : argd.get("dob.day", ""),
        'dob.month'        : argd.get("dob.month", ""),
        'dob.year'         : argd.get("dob.year", ""),
        'email'            : argd.get("email", ""),
        'password'         : argd.get("password", ""),
        'passwordtwo'      : argd.get("passwordtwo", ""),
        'screenname'       : argd.get("screenname", ""),
        'side'             : argd.get("side", ""),
    }
    # --------------------------------------------------------- Sprinkle with default metadata
    rec["confirmed"] = False
    rec["confirmationcode"] = generate_confirmation_code()
    rec["personrecord"] = ""

    # -------------------------------------------- Validations... (lots of these)

    validate_record(rec) # Seperated out to a seperate function to make logic clearer

    # ---------------------------------------------------------  TRANSFORMS FOR STORAGE
    #    One way hash for security reasons before storage
    #    NOTE: This means we always check the digest, not the value
    #          This also means we can do a password reset, not a password reminder
    #
    if rec["password"] != "":
        rec["password"] = md5.md5(rec["password"]).hexdigest()

    if rec["passwordtwo"] != "":
        rec["passwordtwo"] = md5.md5(rec["passwordtwo"]).hexdigest()

    # --------------------------------------------------------- Actual storage
    stored_rec = Registrations.new_record(rec)
    return stored_rec


def page_logic(json, **argd):
    if argd.get("action", "") == "addcontact":
        contact   = argd.get("contact", None)
        contactof = argd.get("contactof", None)        
        if contact is None:
            return [
                      "error",
                      {
                        "message" : "Need to have contact to add to",
                        "record" : "",
                        "problemfield" : "contact",
                      }
                   ]

        if contactof is None:
            return [
                      "error",
                      {
                        "message" : "Need to know who to add this as a contact of...",
                        "record" : "",
                        "problemfield" : "contactof",
                      }
                   ]
        
        contacts = Contacts.read_database()
        for rec in contacts:
            if rec["contactof"] == contactof:
                break # Found the record
        else:
            rec = { "contactof" : contactof, "contacts" : [ ] }
            
        if contact not in rec["contacts"]:
            rec["contacts"].append( contact )
        else:
            return [
                      "error",
                      {
                        "message" : "You've already added this person as a contact! <a href='/BrowseParticipants'> more </a>",
                        "record" : "",
                        "problemfield" : "contactof",
                      }
                   ]


        if rec.get("contactid", None):
            stored_rec = Contacts.store_record(rec)
        else:
            stored_rec = Contacts.new_record(rec)


        return [
                  "error",
                  {
                    "message" : "OK, Adding contacts isn't quite implemented yet... <a href='/BrowseParticipants'> more </a>",
                    "record" : "",
                    "problemfield" : "",
                  }
               ]
        try:

            R = reg_new(**argd) # This internally validates the record before creating it. This thefore means a possible crash at this point
            return [ 
                     "new",  
                     { "message" : "Thank you for signing up. Just need to confirm your registration now!",
                       "record" : R,
                     }
                   ]

        except ValueError, e:
            try:
                (R, field, Reason) = e.args
            except ValueError:
                raise e
            return [ 
                     "error",  
                     { "message" : Reason,
                       "record" : R,
                       "problemfield" : field,
                     }
                   ]
        # end of action=new ------------------------------------------------------------------------

    if argd.get("action", "") == "dump":
        env = argd.get("__environ__")
        cookie = env["bbc.cookies"].get("sessioncookie",None)
        if cookie:
            try:
                userid = CookieJar.getUser(cookie)
            except CookieJar.NoSuchUser:
               return [ "error",
                 { "message" : "Can't find your registration associated with your cookie"+repr(cookie),
                   "record" : {},
                   "problemfield" : "regid",
                   "setcookies" : {"sessioncookie" : ";path=/"},
                  }
               ]

            try:
                R = Registrations.get_record(userid)
            except IOError: # probably means the db has been deleted/zapped
               CookieJar.wipePairing(cookie, userid)
               return [ "error",
                 { "message" : "Can't find your registration associated with your cookie - maybe it was deleted?",
                   "record" : {},
                   "problemfield" : "regid",
                   "setcookies" : {"sessioncookie" : ";path=/"},
                  }
               ]
                   
                 
        else:
            return [ "error",
                 { "message" : "Can't dump anything since you don't have a session cookie - please try registering :)",
                   "record" : {},
                   "problemfield" : "",                 
                   "setcookies" : {"sessioncookie" : ";path=/"},
                 }
                ]
            
        return [ "error",
                 { "message": "nearly implemented!",# + pprint.pformat(R),
                   "record" : R,
                   "problemfield" : ""
                 }
               ]

    if argd.get("action", "") == "confirmcode":
        if argd.get("regid",None) == None:
             return [ "error",
                      { "Message" : "Sorry, I can't confirm your registration without a registration id",
                        "record" : {},
                        "problemfield" : "regid",
                      }
                    ]

        if argd.get("confirmationcode",None) == None:
             return [ "error",
                      { "Message" : "Sorry, I can't confirm your registration without a confirmation code",
                        "record" : {},
                        "problemfield" : "confirmationcode",
                      }
                    ]
            
        registration = Registrations.get_record(argd.get("regid",""))
        if registration["confirmationcode"] == argd.get("confirmationcode",""):
             registration["confirmed"] = True
             Registrations.store_record(registration)
             cookie = CookieJar.getCookie(argd["regid"])
             
             return [ "confirmed",
                      { "message" : "Thank you for confirming your registration. Your account is now active.",
                        "sessioncookie" : cookie,
                        "record" : registration }
                    ]
        else:
             return [ "error",
                      { "Message" : "There's an error with the confirmation code you're using",
                      }
                    ]
             
        # end of action=confirmcode ------------------------------------------------------------------------

    return [ 
             "__default__",  
             { "message" : "Hello World"+pprint.pformat(argd),
               "record" : {}
             }
           ]

# import MailConfirmCode

def MakeHTML( structure ):

    if structure[0] == "__default__":
        return [], notdirect

    if structure[0] == "new":
        app = "http://bicker.kamaelia.org/cgi-bin/app/register?action=confirmcode&"
        app_args =  "regid=%(regid)s&confirmationcode=%(confirmcode)s" % {
                                  "regid" : structure[1]["record"]["regid"],
                                  "confirmcode" : structure[1]["record"]["confirmationcode"],
                           }
        confirm_url = app + app_args

        page = Interstitials.registration_success % {
                       "body" : pprint.pformat(structure),
                       "confirmationcode" : structure[1]["record"]["confirmationcode"],
                       "regid"       : structure[1]["record"]["regid"],
                       "email"       : structure[1]["record"]["email"],
                       "screenname"  : structure[1]["record"]["screenname"],
                       "dob.day"     : structure[1]["record"]["dob.day"],
                       "dob.month"   : structure[1]["record"]["dob.month"],
                       "dob.year"    : structure[1]["record"]["dob.year"],
                       "side"        : structure[1]["record"]["side"],
                   }
        return [], page

    if structure[0] == "confirmed":

        sessioncookie = structure[1]["sessioncookie"]
        expirytime = time.gmtime(time.time()+31000000) # approx 1 year
        formatteddate = time.strftime("%a, %d-%b-%Y %H:%M:%S %Z", expirytime)

        headers = [("Set-Cookie", "sessioncookie=%s; path=/; expires=%s"  % ( sessioncookie, formatteddate))]

        return headers, Interstitials.confirmed_template

    if structure[0] == "error":
        structure[1]["record"] = pprint.pformat( structure[1]["record"] )
        page = Interstitials.error % structure[1]
        headers = []        
        if structure[1].get("setcookies", False):
            cookies = structure[1]["setcookies"]
            for cookie in cookies:
                headers.append( ("Set-Cookie", "%s=%s" % ( cookie, cookies[cookie]) ) )

        return headers, page

    return [], Interstitials.failback % { "body" : pprint.pformat(structure) }
    

def page_render_html(json, **argd):
    extra_headers, page = MakeHTML( page_logic(json, **argd) )
    status = "200 OK"
    headers = [('Content-type', "text/html")]
    return status, headers+extra_headers, page

Registrations = EntitySet("registrations", key="regid")
Contacts      = EntitySet("contacts",      key="contactid")

if __name__ == "__main__":
     pass
