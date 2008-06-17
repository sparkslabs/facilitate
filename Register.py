#!/usr/bin/python
"""
This script handles user registrations
"""
import md5                          # for hexdigest
import random                       # for confirmation codes
import time                         # to check age
import pprint                       # for dumping errors

from model.Record import EntitySet  # For access to the temporary DB

def generate_confirmation_code():
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
    }
    # --------------------------------------------------------- Sprinkle with default metadata
    rec["confirmed"] = False
    rec["confirmationcode"] = generate_confirmation_code()
    rec["personrecord"] = ""

    # -------------------------------------------- Validations...

    # Minimally validate email. (check for "@")
    # passwords typed must equal passwordtwo and not be ""
    if "@" not in rec["email"]:
        raise ValueError(rec, "email",
                         "Email looks wrong - doesn't contain a '@' symbol. (got: %s)" % rec["email"] )

    # Validate password
    # password typed must equal passwordtwo
    if (rec["password"] != rec["passwordtwo"]) or (rec["password"] == ""):
        raise ValueError(rec, "password",
                         "Passwords provided do not match"
                        )
    # password must not be null
    if rec["password"] == "":
        raise ValueError(rec, "password",
                         "Passwords must not be blank!"
                        )

    # Email address must not match any other record in the database
    R = Registrations.read_database()
    uniquefield = "email"
    for r in R:
       if r[uniquefield] == rec[uniquefield]:
           raise ValueError(rec, uniquefield,
                            "Users are are identified as unique by %s - record already exists (got %s)" % (uniquefield, rec[uniquefield])
                           )


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
        raise ValueError(rec, "dob.year",
                         "Year age restriction not met. Must be minimum %d years. (Got: %d)" % (min_age, year_age)
                        )

    # Application logic validation
    if rec["side"] == "":
        raise ValueError(rec, "side",
                         "'side' is empty - you must pick sides! (Got: %s)" % rec["side"]
                        )

    OKValues = ["eve", "isambard"]
    if rec["side"] not in OKValues:
        raise ValueError(rec, "side",
                         "'side' must be one of the valid values: %s. (Got: %s)" %
                            (repr(OKValues), repr(rec["side"]))
                        )

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

        except ValueError, (R, field, Reason):
            return [ 
                     "error",  
                     { "message" : Reason,
                       "record" : R,
                       "problemfield" : field,
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

Registrations = EntitySet("registrations", key="regid")

if __name__ == "__main__":
    if 0:
        print "WARNING, running this test will zap your local store"
        print "press return to continue, control-c to not continue"
        raw_input()
    Registrations.Zap("registrations","regid")
    testcases = [
             [ "new", 
                "should succeed",
               "Can create new record in new database",
               {
                  'action' : 'new',
                  'dob.day': '30',
                  'dob.month': 'June',
                  'dob.year': '1980',
                  'email': 'ms@cerenity.org',
                  'password': 'password',
                  'passwordtwo': 'password',
                  'screenname': 'Michael',
                  'side': 'eve',
               }],
             [ "error", 
               "email",
               "Can't recreate same record in existing database",
               {
                  'action' : 'new',
                  'dob.day': '30',
                  'dob.month': 'June',
                  'dob.year': '1980',
                  'email': 'ms@cerenity.org',
                  'password': 'password',
                  'passwordtwo': 'password',
                  'screenname': 'Michael',
                  'side': 'eve',
               }],
             [ "error", 
               "dob.day",
               "Can't create record with bogus day for month",
               {
                  'action' : 'new',
                  'dob.day': '31',
                  'dob.month': 'June',
                  'dob.year': '1980',
                  'email': 'ma@cerenity.org',
                  'password': 'password',
                  'passwordtwo': 'password',
                  'screenname': 'Michael',
                  'side': 'eve',
               }],
             [ "error", 
               "dob.month",
               "Can't create record with bogus month",
               {
                  'action' : 'new',
                  'dob.day': '30',
                  'dob.month': 'June...',
                  'dob.year': '1980',
                  'email': 'ma@cerenity.org',
                  'password': 'password',
                  'passwordtwo': 'password',
                  'screenname': 'Michael',
                  'side': 'eve',
               }],
             [ "error", 
               "dob.year",
               "Can't create user who is younger than 18",
               {
                  'action' : 'new',
                  'dob.day': '30',
                  'dob.month': 'June',
                  'dob.year': '2000',
                  'email': 'ma@cerenity.org',
                  'password': 'password',
                  'passwordtwo': 'password',
                  'screenname': 'Michael',
                  'side': 'eve',
               }],
             [ "error", 
               "email",
               "user's emails must contain an @ as a sanity check on the email",
               {
                  'action' : 'new',
                  'dob.day': '30',
                  'dob.month': 'June',
                  'dob.year': '2000',
                  'email': 'ms at cerenity.org',
                  'password': 'password',
                  'passwordtwo': 'password',
                  'screenname': 'Michael',
                  'side': 'eve',
               }],
             [ "error", 
               "password",
               "Passwords provided by the user must match",
               {
                  'action' : 'new',
                  'dob.day': '30',
                  'dob.month': 'June',
                  'dob.year': '1980',
                  'email': 'ma@cerenity.org',
                  'password': 'password',
                  'passwordtwo': 'passwordtwo',
                  'screenname': 'Michael',
                  'side': 'eve',
               }],
             [ "error", 
               "password",
               "Password must not be null",
               {
                  'action' : 'new',
                  'dob.day': '30',
                  'dob.month': 'June',
                  'dob.year': '1980',
                  'email': 'ma@cerenity.org',
                  'password': '',
                  'passwordtwo': '',
                  'screenname': 'Michael',
                  'side': 'eve',
               }],
             [ "error", 
               "side",
               "User must pick a side",
               {
                  'action' : 'new',
                  'dob.day': '30',
                  'dob.month': 'June',
                  'dob.year': '1980',
                  'email': 'ma@cerenity.org',
                  'password': 'password',
                  'passwordtwo': 'password',
                  'screenname': 'Michael',
                  'side': '',
               }],
             [ "error", 
               "side",
               "User must pick a side which is one of the permitted values",
               {
                  'action' : 'new',
                  'dob.day': '30',
                  'dob.month': 'June',
                  'dob.year': '1980',
                  'email': 'ma@cerenity.org',
                  'password': 'password',
                  'passwordtwo': 'password',
                  'screenname': 'Michael',
                  'side': 'not eve or isambard',
               }],
    ]
    print "RUNNING TEST SUITE"
    print "------------------"
    for testcase in testcases:
        testdata = testcase[-1]
        result = page_logic(None, **testdata)
        print testcase[2],
        assert result[0] == testcase[0], ( "testcase return code mismatch %s != %s" % (repr(result[0]), repr(testcase[0])) )
        if result[0] == "error":
            assert testcase[1] == result[1]["problemfield"], "Testcase return field mismatch %s %s" % (repr(result[1]["problemfield"]), repr(testcase[1]))
        print "PASSED"        
