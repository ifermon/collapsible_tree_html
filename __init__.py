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
    COMPANY = "COMPANY"
    COST_CENTER = "COST_CENTER"
    HR_VISIBILTY = "HR_VISIBILTY"
    SEGMENT = "SEGMENT"
    AVAYA_LOCATIONS = "AVAYA_LOCATIONS"
    CAREER_SUB_FUNCTION = "CAREER_SUB_FUNCTION"
    CURRENT_SUB_FUNCTION = "CURRENT_SUB_FUNCTION"
    OPERATING_UNIT = "OPERATING_UNIT"
    COMPENSATION_PAY_VISIBILITY = "COMPENSATION_PAY_VISIBILITY"
    CAREER_FUNCTION = "CAREER_FUNCTION"
    CURRENT_FUNCTION = "CURRENT_FUNCTION"
    MANAGEMENT_LEVEL_FOR_SECURITY = "MANAGEMENT_LEVEL_FOR_SECURITY"
    DNU_JOINT_VENTURE_HIERARCHY = "DNU_JOINT_VENTURE_HIERARCHY"
    EXTERNAL_PAYROLL = "EXTERNAL_PAYROLL"
    CAREER_DESIGNATION_HIERARCHY = "CAREER_DESIGNATION_HIERARCHY"
    CAREER_DESIGNATION = "CAREER_DESIGNATION"
    GLOBAL_SERVICES__CAPABILITIES = "GLOBAL_SERVICES__CAPABILITIES"
    GRANDFATHER_VACATION = "GRANDFATHER_VACATION"
    JOINT_VENTURE = "JOINT_VENTURE"
    INDIA_HOLIDAY_CALENDAR_INDIA_FOODS_USE_ONLY = "INDIA_HOLIDAY_CALENDAR_INDIA_FOODS_USE_ONLY"
    REGION = "REGION"

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



