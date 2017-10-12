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


class Auto_Number(Enum):
    def __new__(cls):
        value = len(cls.__members__) + 1
        obj = object.__new__(cls)
        obj._value_ = value
        return obj

class Org_Types(Auto_Number):
    COMPANY = ()
    COST_CENTER = ()
    HR_VISIBILTY = ()
    SEGMENT = ()
    AVAYA_LOCATIONS = ()
    CAREER_SUB_FUNCTION = ()
    CURRENT_SUB_FUNCTION = ()
    OPERATING_UNIT = ()
    COMPENSATION_PAY_VISIBILITY = ()
    CAREER_FUNCTION = ()
    CURRENT_FUNCTION = ()
    MANAGEMENT_LEVEL_FOR_SECURITY = ()
    DNU_JOINT_VENTURE_HIERARCHY = ()
    EXTERNAL_PAYROLL = ()
    CAREER_DESIGNATION_HIERARCHY = ()
    CAREER_DESIGNATION = ()
    GLOBAL_SERVICES__CAPABILITIES = ()
    GRANDFATHER_VACATION = ()
    JOINT_VENTURE = ()
    INDIA_HOLIDAY_CALENDAR_INDIA_FOODS_USE_ONLY = ()
    REGION = ()

    def __lt__(self, other):
        return self.name < other.name

class Roles(Auto_Number):
    Manager = ()
    HR_Business_Support_Supervisory = ()
    HR_Business_Partner_Supervisory = ()
    Compensation_COE_Partner = ()
    Executive_Comp_Leader = ()
    Executive_Compensation = ()
    Global_Mobility_Partner = ()
    HR_Direct_HR_Partner_by_Supervisory_Org = ()
    Organization_Partner = ()
    Stock_Partner = ()
    Talent_Partner = ()
    Succession_Partner = ()
    ASSIGNABLE_ROLE_6_127 = ()
    ASSIGNABLE_ROLE_6_129 = ()
    ASSIGNABLE_ROLE_6_130 = ()
    Primary_Recruiter = ()
    HD_Operations_Leadership = ()



