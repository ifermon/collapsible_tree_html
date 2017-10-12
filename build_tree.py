#!/usr/bin/env python
"""
    Supervisory Organization with Superiors file:
        sup org ref id
        sup org name
        sup org superior sup org id (parent)
        location ref id
        effective date
        availablity date
    Worker file (pre hire):
        emp id
        worker name
    Location file:
        location ref id
        location name
    Manager file (role_type based security):
        position id
        sup org ref id
        role_type (Manager)
    Default Organization file:
        sup org ref id
        org ref id
        org org_type
    Organization file(s) [companies, cost centers, cust orgs, etc]:
        org ref id
        org name
        org org_type
    Job Change file [maps worker to position]:
        emp id
        position id

    "Super" file from Mark (still needs org file(s) for org names, default org file(s) for defaults not comp or cost ctr
        sup org ref id
        sup org name
        location ref id
        location name
        manager emp id
        manager name
        inherited flag
        sup org superior sup org id (parent)
        company ref id
        cost center ref id


"""
import csv
import argparse
import datetime as dt
from supervisory_organization import Location, Supervisory_Organization, Position, Default_Organization, Worker, Organization, Role
from __init__ import *

ORG_ID_I = 5
EFFECTIVE_DATE_I = 6
NAME_I = 9
AVAIL_DATE_I = 13
ORG_SUBTYPE_I = 25
PARENT_ID_I = 28
LOCATION_ID_I = 35
LOCATION_FILE_REF_ID_I = 6
LOCATION_FILE_NAME_I = 8
ROLES_FILE_SUP_ORG_I =  8
ROLES_FILE_POS_ID_I = 17
ROLES_FILE_ROLE_I = 14
NAME_FILE_FNAME_I = 19
NAME_FILE_LNAME_I = 21
NAME_FILE_EMP_ID_I = 5
JOB_CHANGE_FILE_EMP_ID_I = 16
JOB_CHANGE_FILE_POS_ID_I = 33
ROW_NO_I = 1

# Indicies for Superfile
SUPER_ORG_ID_I = 0
SUPER_ORG_NAME_I = 1
SUPER_LOCATION_ID_I = 2
SUPER_LOCATION_NAME_I = 3
SUPER_MGR_ID_I = 4
SUPER_MGR_NAME_I = 5
SUPER_MGR_INHERITED_I = 6
SUPER_PARENT_ID_I = 7
SUPER_DATA_SOURCE_I = 8
SUPER_DEF_COMP_ID_I = 9
SUPER_DEF_COST_CTR_ID_I = 10

# Indicies for Company, Cost Center and Custom Org files (name, ref id, org_type)
COMP_NAME_I = 0
COMP_REF_ID_I = 1
CC_NAME_I = 0
CC_REF_ID_I = 1
REGION_NAME_I = 0
REGION_REF_ID_I = 1
CUST_NAME_I = 0
CUST_REF_ID_I = 1
CUST_TYPE_I = 2

# Indices for Custom Organization Default file
CUST_ORG_DEF_SUP_ORG_ID_I = 5
CUST_ORG_DEF_DEF_CUST_ORG_ID_I = 18
CUST_ORG_DEF_CUST_ORG_TYPE_I = 9


def parse_command_line(args):
    parser = argparse.ArgumentParser()
    parser.add_argument("sup_org_file", nargs="+", metavar="Supervisory Org File with Dependencies")
    parser.add_argument("-l", "--location", metavar="Location iLoad file", action="append", help="Location file (names and ref ids)")
    parser.add_argument("--roles", metavar="Role Based Security Assignment iLoad file", action="append", help="Role based security file (name and ref id)")
    parser.add_argument("--job-change", metavar="Job Change iLoad file(s)", action="append", help="Job change file (Position id to emp id)")
    parser.add_argument("--pre-hire", metavar="Pre-hire iLoad file(s)", action="append", help="Pre-hire file (Emp name and id)")
    parser.add_argument("-company", help="Company names and reference ids")
    parser.add_argument("-region", help="Region names and reference ids")
    parser.add_argument("-cost-center", help="Cost center names and reference ids")
    parser.add_argument("-custom-organization", help="Custom organization names, reference ids and types")
    parser.add_argument("-custom-org-defaults", help="Custom organization defaults Kate iLoad")
    parser.add_argument("-s", "--super", action="store_true", help="Use one or more file(s) that have everything but custom org defaults, default org names and location names")
    parser.add_argument("-propagate-custom-orgs", action="store_true", help="Propogate custom orgs down the hierarchy.")
    return parser.parse_args(args[1:])

def convert_custom_org_type_to_enum(org_type_str):
    try:
        ot = Org_Types[org_type_str.upper().replace(" ", "_").translate(None, "&()").replace("-", "_")]
    except KeyError:
        error("Invalid org org_type {}".format(org_type_str))
        sys.exit()
    return ot

def convert_role_name_to_enum(role_name_str):
    try:
        rname = role_name_str.replace(" ", "_").replace("-", "_")
        r = Roles[rname]
    except KeyError:
        error("Invalid role_type {}".format(rname))
        sys.exit()
    return r

def main(argv):
    global args

    info("Beginning program")
    args = parse_command_line(argv)

    location_dict = {} # Key is location id, value is Location object
    sup_org_dict = {} # Key is org id, value is Sup Org object
    position_dict = {} # Key is position id, value is Manager object
    worker_dict = {} # Key is emp id, value is position id
    org_dict = {} # Key is org id, value is Default_Organization object

    top_level_sup_orgs = []
    ctr = 0

    # Process sup org file(s)
    for f in args.sup_org_file:
        with open(f, "rU") as csvfile:
            info("Processing supervisory organization file {}".format(args.sup_org_file))
            reader = csv.reader(csvfile)
            # go through each row of data and create necessary data structures
            for row in reader:
                ctr += 1 # Keep track of line number for debugging purposes
                if args.super: # Not iLoads, summary files provided by Mark
                    try: # skip header rows, look for number
                        int(row[SUPER_ORG_ID_I])
                    except ValueError:
                        continue
                    pass

                    # Get location ref id and name
                    lid = row[SUPER_LOCATION_ID_I]
                    if lid not in location_dict:
                        location_dict[lid] = Location(lid, row[SUPER_LOCATION_NAME_I])
                    loc = location_dict[lid]

                    # Create supervisory org and link to location
                    sup_org_id = row[SUPER_ORG_ID_I]
                    so = Supervisory_Organization(ctr, sup_org_id, None, row[SUPER_ORG_NAME_I], None,
                            row[SUPER_PARENT_ID_I], row[SUPER_LOCATION_ID_I], None)
                    sup_org_dict[sup_org_id] = so
                    so.location = loc
                    if so.is_top_level:  # Set on creation of org if parent exists
                        top_level_sup_orgs.append(so)

                    # Create worker, link to position and sup org
                    #worker = Worker(row[SUPER_MGR_NAME_I], row[SUPER_MGR_ID_I])
                    #manager = Position(None, so, Role.MANAGER, worker)
                    #so.add_role(manager)
                    #if row[SUPER_MGR_INHERITED_I] == "No":
                    #    manager.inherited = False
                    #else:
                    #    manager.inherited = True

                    # process defaults, may not exist if NON-SAP file
                    if len(row) > SUPER_DEF_COMP_ID_I:
                        cost_ctr_id = row[SUPER_DEF_COST_CTR_ID_I]
                        company_id = row[SUPER_DEF_COMP_ID_I]
                        if cost_ctr_id:
                            try:
                                cc = org_dict[cost_ctr_id]
                            except KeyError:
                                cc = Organization(None, cost_ctr_id, Org_Types.COST_CENTER)
                                org_dict[cost_ctr_id] = cc
                            so.add_default(cc)
                        if company_id:
                            try:
                                comp = org_dict[company_id]
                            except KeyError:
                                comp = Organization(None, company_id, Org_Types.COMPANY)
                                org_dict[company_id] = comp
                            so.add_default(comp)


                else: # iLoad files
                    try: # skip header rows, look for number
                        int(row[ROW_NO_I])
                    except ValueError:
                        continue
                    d = dt.datetime.strptime(row[EFFECTIVE_DATE_I], "%m/%d/%y").date()

                    lid = row[LOCATION_ID_I]
                    if lid not in location_dict:
                        location_dict[lid] = Location(lid, lid)
                    loc = location_dict[lid]

                    sup_org_id = row[ORG_ID_I]
                    so = Supervisory_Organization(ctr, sup_org_id, d, row[NAME_I], row[AVAIL_DATE_I],
                            row[PARENT_ID_I], row[LOCATION_ID_I], row[ORG_SUBTYPE_I])
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
            info("Processing location file {}.".format(filename))
            with open(filename, "rU") as csvfile:
                reader = csv.reader(csvfile)
                for row in reader:
                    try:
                        int(row[ROW_NO_I])
                    except ValueError:
                        continue
                    lid = row[LOCATION_FILE_REF_ID_I]
                    if lid in location_dict:
                        location_dict[lid].name = row[LOCATION_FILE_NAME_I]

    if args.roles: # Get all the roles for sup orgs (iLoad)
        """ 
            This file is a pain. With multiple rows per supervisory org, and multiple
            rows per security role_type (i.e. multiple HR Partners per org
        """
        for filename in args.roles:
            info("Processing security roles file {}.".format(filename))
            record_no = None
            record_skip = None
            with open(filename, "rU") as csvfile:
                reader = csv.reader(csvfile)
                for row in reader:
                    # First get values from the current line
                    try:
                        current_record_no = int(row[ROW_NO_I])
                    except ValueError:
                        continue
                    current_sup_org_id = row[ROLES_FILE_SUP_ORG_I]
                    current_position_id = row[ROLES_FILE_POS_ID_I]
                    current_role_name = row[ROLES_FILE_ROLE_I]

                    # Skip this line if we are skipping this record or no position to assign
                    if current_record_no == record_skip or not current_position_id:
                        continue

                    if record_no != current_record_no:  # Processing new record (org)
                        record_no = current_record_no
                        if current_sup_org_id not in sup_org_dict:  # All kinds of orgs in this file
                            record_skip = record_no
                            continue
                        so = sup_org_dict[current_sup_org_id]

                    # At this point we should have a valid supervisory org and so should be defined
                    # If current_role_name has a value, then we process it. If not, we use the last one
                    if current_role_name:
                        role_type = convert_role_name_to_enum(current_role_name)
                    role = Role(role_type, so)
                    so.add_role(role)
                    if current_position_id not in position_dict:
                        position = Position(current_position_id, so, role)
                        if current_position_id == "72027620":
                            debug("Adding position to dict")
                        position_dict[current_position_id] = position
                    role.add_position(position_dict[current_position_id])


    if args.job_change and args.job_change: # Process job change file if given
        for filename in args.job_change:
            info("Processing job change file {}.".format(filename))
            with open(filename, "rU") as csvfile:
                reader = csv.reader(csvfile)
                for row in reader:
                    try:
                        int(row[ROW_NO_I])
                    except ValueError:
                        continue
                    position_id = row[JOB_CHANGE_FILE_POS_ID_I]
                    if position_id not in position_dict:
                        continue
                    emp_id = row[JOB_CHANGE_FILE_EMP_ID_I]
                    if position_id == "72027620":
                        debug("found her position")
                    if emp_id not in worker_dict:
                        if emp_id == "10249":
                            debug("adding her to worker dict")
                        worker = Worker(None, emp_id)
                        worker_dict[emp_id] = worker
                    position_dict[position_id].assign_worker(worker_dict[emp_id])

    if args.pre_hire and args.job_change: # Get manager names
        for filename in args.pre_hire:
            info("Processing pre-hire file {}.".format(filename))
            with open(filename, "rU") as csvfile:
                reader = csv.reader(csvfile)
                for row in reader:
                    try:
                        int(row[ROW_NO_I])
                    except ValueError:
                        continue
                    emp_id = row[NAME_FILE_EMP_ID_I][2:] # Remove the A- of applicatant ID
                    if emp_id == "10249":
                        debug("Found her in pre hire")
                    if emp_id not in worker_dict:
                        continue
                    fname = row[NAME_FILE_FNAME_I]
                    lname = row[NAME_FILE_LNAME_I]
                    worker_dict[emp_id].name = "{} {}".format(fname, lname)
                    if emp_id == "10249":
                        debug("Found her in pre hire")
                        debug("{}".format(worker_dict[emp_id]))

    if args.custom_org_defaults: # Get the custom org defaults (e.g. SEGMENT)
        with open(args.custom_org_defaults, "rU") as csvfile:
            reader = csv.reader(csvfile)
            for row in reader:
                try:
                    int(row[ROW_NO_I])
                except ValueError:
                    continue
                sup_org_id = row[CUST_ORG_DEF_SUP_ORG_ID_I]
                cust_org_id = row[CUST_ORG_DEF_DEF_CUST_ORG_ID_I]
                cust_org_type_str = row[CUST_ORG_DEF_CUST_ORG_TYPE_I]
                cust_org_type = convert_custom_org_type_to_enum(cust_org_type_str)
                try:
                    cust_org = org_dict[cust_org_id]
                except KeyError:
                    cust_org = Organization(None, cust_org_id, cust_org_type)
                    org_dict[cust_org_id] = cust_org
                try:
                    sup_org_dict[sup_org_id].add_default(cust_org)
                except KeyError:
                    info("Invalid supervisory org {} found while loading custom defaults.".format(sup_org_id))

    if args.company: # Get company names by ref id
        info("Processing company name + reference ID file {}".format(args.company))
        with open(args.company, "rU") as csvfile:
            reader = csv.reader(csvfile)
            for row in reader:
                # We will only update companies that already exist by ref id
                try:
                    dorg = org_dict[row[COMP_REF_ID_I]]
                    dorg.name = row[COMP_NAME_I]
                except KeyError:
                    continue
    if args.cost_center: # Get cost center names by ref id
        info("Processing cost center name + reference ID file {}".format(args.cost_center))
        with open(args.cost_center, "rU") as csvfile:
            reader = csv.reader(csvfile)
            for row in reader:
                # We will only update companies that already exist by ref id
                try:
                    dorg = org_dict[row[CC_REF_ID_I]]
                    dorg.name = row[CC_NAME_I]
                except KeyError:
                    continue
    if args.custom_organization: # Get custom org names by ref id
        info("Processing custom organization name + reference ID + org_type file {}".format(args.custom_organization))
        with open(args.custom_organization, "rU") as csvfile:
            reader = csv.reader(csvfile)
            for row in reader:
                # We will only update companies that already exist by ref id
                try:
                    dorg = org_dict[row[CUST_REF_ID_I]]
                    dorg.name = row[CUST_NAME_I]
                except KeyError:
                    continue
    if args.region: # Get region names by ref id
        info("Processing region name + reference ID + org_type file {}".format(args.region))
        with open(args.region, "rU") as csvfile:
            reader = csv.reader(csvfile)
            for row in reader:
                # We will only update regions that already exist by ref id
                try:
                    dorg = org_dict[row[REGION_REF_ID_I]]
                    dorg.name = row[REGION_NAME_I]
                except KeyError:
                    continue

    # Propogate custom org inheritenance - needs to come after we've loaded the defaults
    if args.propagate_custom_orgs:
        for so in top_level_sup_orgs:
            so.propagate_custom_orgs()

    # Now print
    doc, tag, text = Doc().tagtext()
    doc.asis("<!DOCTYPE html>")
    with tag("html"):
        with tag("head"):
            doc.asis('<meta name="viewport" content="width=device-width, initial-scale=1">',
                    '<link rel="stylesheet" href="https://maxcdn.bootstrapcdn.com/bootstrap/3.3.7/css/bootstrap.min.css">',
                    '<script src="https://ajax.googleapis.com/ajax/libs/jquery/3.2.1/jquery.min.js"></script>',
                    '<script src="https://maxcdn.bootstrapcdn.com/bootstrap/3.3.7/js/bootstrap.min.js"></script>',
                     '<style>.list_group { padding: 20px 40px; } .list-group-item { border: 0 none !important; } table th, table td { padding: 0 10px 0 0; } table { margin-left: 10px; font-size: 0.8em; } </style>')
        with tag("body"):
            with tag("div", klass="container"):
                with tag("h2"):
                    text("Supervisory Organizations")
                with tag("div", klass="panel-group"):
                    for tlo in top_level_sup_orgs:
                        doc.asis(tlo.to_html_collapse_table_w_roles())
    print(doc.getvalue())

    return


if __name__ == "__main__":

    main(sys.argv)