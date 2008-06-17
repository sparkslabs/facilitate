#!/usr/bin/python
"""
This script handles user registrations
"""
import pprint

from model.Record import EntitySet

class UniquenessConstraint(Exception): pass
class SamenessConstraint(Exception): pass
class NotNull(Exception): pass


Registrations = EntitySet("registrations", key="regid")

import md5
import random
import time

def generate_confrimation_code():
    return md5.md5(str(random.randint(100000000000,1000000000000))).hexdigest()

def reg_new(**argd):
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

      # --------------------------------------------------------- Independently createable
        'confirmed'        : False,
        'confirmationcode' : generate_confrimation_code(),
        'personrecord'     : "",
    }

    # -------------------------------------------- Validations...

    # Minimally validate email. (check for "@")
    # passwords typed must equal passwordtwo and not be ""
    if "@" not in rec["email"]:
        raise ValueError(rec, "email",
                         "Email looks wrong - doesn't contain a '@' symbol. (got: %s)" % rec["email"] )

    # Validate password
    # passwords typed must equal passwordtwo and not be ""
    if (rec["password"] != rec["passwordtwo"]) or (rec["password"] == ""):
        raise SamenessConstraint("password")

    # Email address must not match any other record in the database
    R = Registrations.read_database()
    for r in R:
       if r["email"] == rec["email"]:
           raise UniquenessConstraint(r)


    # Validate month
    if rec["dob.month"] not in [ "January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December" ]:
        raise ValueError(rec, 
                         "dob.month",
                         "Month doesn't match options - should be full word, capitalised (got: %s)" % repr(rec["dob.month"])
                        ) 

    # Validate day is within range for given month
    m2d = {
         "January" : 31,
         "February" : 28,
         "March" : 31,
         "April": 30,
         "May" : 31,
         "June" : 30,
         "July" : 31,
         "August" : 31,
         "September" : 30,
         "October" : 31,
         "November" : 30,
         "December" : 31
    }
    days = m2d[rec["dob.month"]]
    if (int(rec["dob.year"]) % 4) == 0:
        if days == 28:
            days +=1
     
    if (int(rec["dob.day"]) < 1) or int(rec["dob.day"]) > days:
        raise ValueError(rec,
                         "dob.day",
                         "Day in month falling on a day not in that month? (got: %s %s)" % (repr(rec["dob.day"]), repr(rec["dob.month"]))
                        )

    # "yearage" >= 18
    # FIXME: This is actually excludes many 18 year olds...
    year_age = (time.localtime(time.time())[0] - int(rec["dob.year"]))
    min_age = 18

    if year_age < min_age: 
        raise ValueError(rec, "dob.year"
                         "Year age restriction not met. Must be minimum %d years. (Got: %d)" % (min_age, year_age)
                        )

    # Application logic validation
    if rec["side"] == "":
        raise ValueError(rec, "side"
                         "'side' is empty - you must pick sides! (Got: %s)" % rec["side"]
                        )

    if rec["side"] not in ["eve", "isambard"]:
        raise ValueError("side")

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
    if argd.get("action", "") == "new":
        try:
            R = reg_new(**argd) # This internally validates the record before creating it. This thefore means a possible crash at this point
            return [ 
                     "new",  
                     { "message" : "NEW USER",
                       "record" : R,
                     }
                   ]

        except UniquenessConstraint, e:
            R = e.args[0]
            return [ 
                     "new_fail_unique",  
                     { "message" : "EXISTING USER",
                       "record" : R,
                     }
                   ]

        except SamenessConstraint, e:
            R = e.args[0]
            return [ 
                     "new_fail_password",  
                     { "message" : "OTHER ERROR",
                       "record" : R,
                     }
                   ]

        except ValueError, (R, field, Reason):
            return [ 
                     "error",  
                     { "message" : Reason,
                       "record" : R,
                     }
                   ]

    return [ 
             "__default__",  
             { "message" : "Hello World"+pprint.pformat(argd),
               "record" : {}
             }
           ]

failback = """<html>
<body>
<pre>
%(body)s
</pre>
</body>
</html>"""

error = """<html>
<body>
<P><B>ERROR: %(message)s
<P> Record
<pre>
%(record)s
</pre>
</body>
</html>"""

def MakeHTML( structure ):
    structure[1]["record"]["password"] = "****"
    structure[1]["record"]["passwordtwo"] = "****"
    if structure[0] == "__default__":
        return failback % structure[1]

    if structure[0] == "new":
        return failback % structure[1]

    if structure[0] == "new_fail_unique":
        return failback % structure[1]
    
    if structure[0] == "new_fail_password":
        return failback % structure[1]
    
    if structure[0] == "error":
        structure[1]["record"] = pprint.pformat( structure[1]["record"] )
        return error % structure[1]
    
    return failback % { "body" : repr(structure) }
    

def page_render_html(json, **argd):
    return MakeHTML( page_logic(json, **argd) )


if __name__ == "__main__":
    testcase = {
              'action' : 'new',
              'dob.day': '31',
              'dob.month': 'June',
              'dob.year': '1980',
              'email': 'ms@cerenity.org',
              'password': 'password',
              'passwordtwo': 'password',
              'screenname': 'Michael',
              'side': 'eve',
             }


    pprint.pprint(
        page_logic(None, **testcase)
    )
