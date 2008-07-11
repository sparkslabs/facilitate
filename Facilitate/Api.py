#!/usr/bin/python

from Facilitate.model.Record import EntitySet

Images        = None
Registrations = None
Contacts      = None
Videos        = None

def initApi(basedir):
    EntitySet.data = basedir

    global Images
    global Registrations
    global Contacts
    global Videos

    Images        = EntitySet("images", key="imageid")
    Registrations = EntitySet("registrations", key="regid")
    Contacts      = EntitySet("contacts", key="contactid")
    Videos        = EntitySet("videos", key="imageid")

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

def getUserVideos(userid):
    videos = Videos.read_database()
    user_videos = []
    for video in videos:
        if video["userid"] == userid:
            user_videos.append(video)
    return user_videos



