#!/usr/bin/env python

import csv
import sys
import argparse
import datetime as dt
from supervisory_organization import Location, Supervisory_Organization, Manager
from __init__ import *

ORG_ID_INDEX = 5
EFFECTIVE_DATE_INDEX = 6
NAME_INDEX = 9
AVAIL_DATE_INDEX = 13
ORG_SUBTYPE_INDEX = 25
PARENT_ID_INDEX = 28
LOCATION_ID_INDEX = 35
LOCATION_FILE_REF_ID_INDEX = 6
LOCATION_FILE_NAME_INDEX = 8
MANAGER_FILE_SUP_ORG_INDEX =  5
MANAGER_FILE_POS_ID_INDEX = 14
MANAGER_FILE_ROLE_INDEX = 11
NAME_FILE_FNAME_INDEX = 19
NAME_FILE_LNAME_INDEX = 21
NAME_FILE_EMP_ID_INDEX = 5
JOB_CHANGE_FILE_EMP_ID_INDEX = 16
JOB_CHANGE_FILE_POS_ID_INDEX = 33
ROW_NO_INDEX = 1

def parse_command_line(args):
    parser = argparse.ArgumentParser()
    parser.add_argument("sup_org_file", metavar="Supervisory Org File with Dependencies")
    parser.add_argument("-l", "--location", metavar="Location iLoad file", action="append", help="Location file (names and ref ids)")
    parser.add_argument("-m", "--manager", metavar="Role Based Security Assignment iLoad file", action="append", help="Manager file (name and ref id)") # Assumes entire file is managers only
    parser.add_argument("-j", "--job-change", metavar="Job Change iLoad file(s)", action="append", help="Job change file (Position id to emp id)")
    parser.add_argument("-p", "--pre-hire", metavar="Pre-hire iLoad file(s)", action="append", help="Pre-hire file (Emp name and id)")
    return parser.parse_args(args[1:])

def main(argv):
    global args

    debug("Beginning program")
    args = parse_command_line(argv)

    location_dict = {} # Key is location id, value is Location object
    sup_org_dict = {} # Key is org id, value is Sup Org object
    manager_dict = {} # Key is position id, value is Manager object
    emp_dict = {} # Key is emp id, value is position id
    top_level_sup_orgs = []
    ctr = 0

    # Process sup org file
    with open(args.sup_org_file, "rU") as csvfile:
        debug("Processing supervisory organization file {}".format(args.sup_org_file))
        reader = csv.reader(csvfile)
        # go through each row of data and create necessary data structures
        for row in reader:
            # Skip if we are not on a "valid" row with a row number (iLoad format)
            try:
                int(row[ROW_NO_INDEX])
            except ValueError:
                continue

            ctr += 1

            d = dt.datetime.strptime(row[EFFECTIVE_DATE_INDEX], "%m/%d/%y").date()

            lid = row[LOCATION_ID_INDEX]
            if lid not in location_dict:
                location_dict[lid] = Location(lid, lid)
            loc = location_dict[lid]

            sup_org_id = row[ORG_ID_INDEX]
            so = Supervisory_Organization(ctr, sup_org_id, d, row[NAME_INDEX], row[AVAIL_DATE_INDEX],
                    row[PARENT_ID_INDEX], row[LOCATION_ID_INDEX], row[ORG_SUBTYPE_INDEX])
            sup_org_dict[sup_org_id] = so
            so.location = loc
            if so.is_top_level:
                top_level_sup_orgs.append(so)

    # Now go through and populate the parent relationships
    for so in sup_org_dict.values():
        if not so.is_top_level:
            so.parent = sup_org_dict[so.parent_id]

    # Do a cycle check
    for so in top_level_sup_orgs:
        so.cycle_check(list())
    for so in sup_org_dict.values(): # Needed to find missing top level orgs
        # Every org should have been touched above. If there is a cycle there weill be orgs
        # that have not yet been traversed
        if not so.traversed:
            so.cycle_check(list())

    # Now get location names if given
    if args.location:
        for filename in args.location:
            debug("Processing location file {}.".format(filename))
            with open(filename, "rU") as csvfile:
                reader = csv.reader(csvfile)
                for row in reader:
                    try:
                        int(row[ROW_NO_INDEX])
                    except ValueError:
                        continue
                    lid = row[LOCATION_FILE_REF_ID_INDEX]
                    if lid in location_dict:
                        location_dict[lid].name = row[LOCATION_FILE_NAME_INDEX]

    if args.manager:
        for filename in args.manager:
            debug("Processing manager file {}.".format(filename))
            with open(filename, "rU") as csvfile:
                reader = csv.reader(csvfile)
                for row in reader:
                    try:
                        int(row[ROW_NO_INDEX])
                    except ValueError:
                        continue
                    org = row[MANAGER_FILE_SUP_ORG_INDEX]
                    if not row[MANAGER_FILE_ROLE_INDEX] == "Manager":
                        continue
                    if org in sup_org_dict:
                        position = row[MANAGER_FILE_POS_ID_INDEX]
                        manager = Manager(position)
                        sup_org_dict[org].add_manager(manager)
                        manager_dict[position] = manager

    if args.job_change:
        for filename in args.job_change:
            debug("Processing job change file {}.".format(filename))
            with open(filename, "rU") as csvfile:
                reader = csv.reader(csvfile)
                for row in reader:
                    try:
                        int(row[ROW_NO_INDEX])
                    except ValueError:
                        continue
                    position = row[JOB_CHANGE_FILE_POS_ID_INDEX]
                    if position in manager_dict:
                        emp_id = row[JOB_CHANGE_FILE_EMP_ID_INDEX]
                        manager_dict[position].employee_id = emp_id
                        emp_dict[emp_id] = position

    if args.pre_hire and args.job_change:
        for filename in args.pre_hire:
            debug("Processing pre-hire file {}.".format(filename))
            with open(filename, "rU") as csvfile:
                reader = csv.reader(csvfile)
                for row in reader:
                    try:
                        int(row[ROW_NO_INDEX])
                    except ValueError:
                        continue
                    emp_id = row[NAME_FILE_EMP_ID_INDEX][2:] # Remove the A- of applicatant ID
                    if not emp_id in emp_dict:
                        continue
                    fname = row[NAME_FILE_FNAME_INDEX]
                    lname = row[NAME_FILE_LNAME_INDEX]
                    position = emp_dict[emp_id]
                    manager_dict[position].name = "{} {}".format(fname, lname)

    # Now print
    doc, tag, text = Doc().tagtext()
    doc.asis("<!DOCTYPE html>")
    with tag("html"):
        with tag("head"):
            doc.asis('<meta name="viewport" content="width=device-width, initial-scale=1">',
                    '<link rel="stylesheet" href="https://maxcdn.bootstrapcdn.com/bootstrap/3.3.7/css/bootstrap.min.css">',
                    '<script src="https://ajax.googleapis.com/ajax/libs/jquery/3.2.1/jquery.min.js"></script>',
                    '<script src="https://maxcdn.bootstrapcdn.com/bootstrap/3.3.7/js/bootstrap.min.js"></script>',
                     '<style>.list_group { padding: 20px 40px; } .list-group-item { border: 0 none !important; } </style>')
        with tag("body"):
            with tag("div", klass="container"):
                with tag("h2"):
                    text("Supervisory Organizations")
                with tag("div", klass="panel-group"):
                    for tlo in top_level_sup_orgs:
                        doc.asis(tlo.to_html())
    print(doc.getvalue())


    return


if __name__ == "__main__":

    main(sys.argv)