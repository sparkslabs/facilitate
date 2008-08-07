#!/usr/bin/env python

import Facilitate.model.Record as Record

import sys

import unittest

class Test_Record_new_record(unittest.TestCase):
    def setUp(self):
        self.key = "personid"

        Record.EntitySet.Zap(name="People", key=self.key)
        self.X = Record.EntitySet(name="People", key=self.key)

    # --------------------------------------------------------------

    def test_new_record(self):
        "Record.new_record - Adding a record should result in us being given the record back, preserving our values and with an id added "
        newrec = self.X.new_record({"name": "bob", "age": 30})
        self.assertEqual(newrec["name"], "bob")
        self.assertEqual(newrec["age"], 30)

    def test_new_record_personid_startsZero(self):
        "Record.new_record - records returned contain key values that start at 0 upwards - keys returned are strings"
        newrec = self.X.new_record({"name": "bob", "age": 30})
        self.assertEqual(newrec["personid"], "0")

    def test_new_record_personid_DuplicatesAllowedStoredSeperately(self):
        "Record.new_record - creating new records, even duplicating existing content, creates a new record"
        newrec1 = self.X.new_record({"name": "John Smith", "age": 30})
        newrec2 = self.X.new_record({"name": "John Smith", "age": 30}) # Because there can easily be two John Smiths aged 30
        self.assertNotEqual(newrec1["personid"], newrec2["personid"])

    def test_new_record_personid_startZeroIncreasing(self):
        "Record.new_record - keys returned increase numerically from 0 upwards"
        newrec = self.X.new_record({"name": "bob", "age": 1})
        self.assertEqual(newrec["personid"], "0")
        newrec = self.X.new_record({"name": "bob", "age": 1})
        self.assertEqual(newrec["personid"], "1")
        newrec = self.X.new_record({"name": "bob", "age": 1})
        self.assertEqual(newrec["personid"], "2")
        newrec = self.X.new_record({"name": "bob", "age": 1})
        self.assertEqual(newrec["personid"], "3")

    def test_new_record_DifferingRecordsDiffer(self):
        "Record.new_record - storing different records, remain different"
        rec_raws = [
                      {"name": "alice",   "age": "30"},
                      {"name": "bob",     "age": "31"},
                      {"name": "charlie", "age": "32"},
                      {"name": "dan",     "age": "33"},
                  ]
        newrecs = []

        for source in rec_raws:
            newrec = self.X.new_record( source )
            newrecs.append( newrec )

        for left,right in zip(rec_raws, newrecs):
            self.assertEqual( left["name"], right["name"] )
            self.assertEqual( left["age"], right["age"] )

    


if __name__=="__main__":
    # Next line invokes voodoo magic that causes all the testcases above to run.
    unittest.main()
      


if 0:

      if 1:
#          # common tests
#          rec_raw = [
#                      {"name": "michael", "age": "34"},
#                      {"name": "polina", "age": "35"},
#                      {"name": "sam", "age": "5"},
#                      {"name": "nat", "age": "4"},
#                    ]
#          recs_new = [ ]
#
#          for rec in rec_raw:
#              newrec = X.new_record(rec)
#              print newrec
#              recs_new.append(newrec)
#
#          print recs_new
#
#          print recs_new[2]

          recs_new[2]["name"] = "sam sparks"
          X.store_record(recs_new[2])

          print recs_new

          record = X.get_record("3")

          print "Record","3", record

          for myrec in X.read_database():
              print "R", myrec


