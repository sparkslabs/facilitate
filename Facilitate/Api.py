#!/usr/bin/python

from Facilitate.model.Record import EntitySet

Images        = None
Registrations = None
Contacts      = None

def initApi(basedir):
    EntitySet.data = basedir

    global Images
    global Registrations
    global Contacts

    Images        = EntitySet("images", key="imageid")
    Registrations = EntitySet("registrations", key="regid")
    Contacts      = EntitySet("contacts", key="contactid")

def getRegistration(userid):
    user = Registrations.get_record(userid)
    return user

def ContactsImages(contacts):
    images = Images.read_database()
    user_images = []
    userids = []
    for image in images:
        userids.append(image["userid"])
        if image["userid"] in contacts:
            user_images.append(image)
    return user_images

def getContacts(userid):
    for rec in Contacts.read_database():
        if rec["contactof"] == userid:
            return rec["contacts"]
    else:
        return None

def getAllImages():
    return Images.read_database()

def getUserImages(userid):
    images = Images.read_database()
    user_images = []
    for image in images:
        if image["userid"] == userid:
            user_images.append(image)
    return user_images

def getAllUsers():
    return Registrations.read_database()

def getRegistrations(users):
    R = []
    for user in users:
        R.append(getRegistration(user))
    return R
