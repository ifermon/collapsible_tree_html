# -*- coding: utf-8 -*-
import logging
from enum import Enum
from yattag import Doc, indent
import sys
reload(sys)
sys.setdefaultencoding('utf8')

# Configure logging for everyone
logging.basicConfig(datefmt="%H:%M:%S", format="%(asctime)s %(message)s")
l = logging.getLogger()
l.setLevel(logging.DEBUG)
debug = l.info
info = l.info
error = l.error

import itertools
class Seq_Generator():
    newid = itertools.count().next
    def __init__(self):
        self.id = Seq_Generator.newid()

class Org_Types(Enum):
    COMPANY = "Company"
    COST_CENTER = "Cost Center"
    HR_VISIBILTY = "HR Visibilty"
    SEGMENT = "Segment"
    AVAYA_LOCATIONS = "Avaya Locations"
    CAREER_SUB_FUNCTION = "Career Sub Function"
    CURRENT_SUB_FUNCTION = "Current Sub Function"
    OPERATING_UNIT = "Operating Unit"
    COMPENSATION_PAY_VISIBILITY = "Compensation Pay Visibility"
    CAREER_FUNCTION = "Career Function"
    CURRENT_FUNCTION = "Current Function"
    MANAGEMENT_LEVEL_FOR_SECURITY = "Management Level For Security"
    EXTERNAL_PAYROLL = "External Payroll"
    CAREER_DESIGNATION_HIERARCHY = "Career Designation Hierarchy"
    CAREER_DESIGNATION = "Career Designation"
    GLOBAL_SERVICES__CAPABILITIES = "Global Services Capabilities"
    GRANDFATHER_VACATION = "Grandfather Vacation"
    JOINT_VENTURE = "Joint Venture"
    INDIA_HOLIDAY_CALENDAR_INDIA_FOODS_USE_ONLY = "India Holiday Calendar India Foods Use Only"
    REGION = "Region"

    def __lt__(self, other):
        return self.name < other.name

class Roles(Enum):
    Manager = "Manager"
    HR_Business_Support_Supervisory = "HR_Business_Support_Supervisory"
    HR_Business_Partner_Supervisory = "HR_Business_Partner_Supervisory"
    Compensation_COE_Partner = "Compensation_COE_Partner"
    Executive_Comp_Leader = "Executive_Comp_Leader"
    Executive_Compensation = "Executive_Compensation"
    Global_Mobility_Partner = "Global_Mobility_Partner"
    HR_Direct_HR_Partner_by_Supervisory_Org = "HR_Direct_HR_Partner_by_Supervisory_Org"
    Organization_Partner = "Organization_Partner"
    Stock_Partner = "Stock_Partner"
    Talent_Partner = "Talent_Partner"
    Succession_Partner = "Succession_Partner"
    ASSIGNABLE_ROLE_6_127 = "ASSIGNABLE_ROLE_6_127"
    ASSIGNABLE_ROLE_6_129 = "ASSIGNABLE_ROLE_6_129"
    ASSIGNABLE_ROLE_6_130 = "ASSIGNABLE_ROLE_6_130"
    Primary_Recruiter = "Primary_Recruiter"
    HD_Operations_Leadership = "HD_Operations_Leadership"



