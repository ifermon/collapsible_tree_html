from __init__ import *
from weakref import WeakSet
import operator
"""
    A note about Organization vs. Supervisory Organization. Supervisory Organization is the "master". Organization
    is just an attribute. Organizations are things like Company, Cost Center, Segment, Region, etc
    Defaults are those orgs association as a default for a supervisory org.
    
    Example
    Sup Org 123 has a default company of ABC
    
    Organization ABC is of org type Company, and is a default value for sup org 123 (it 
    might also be a default for other sup orgs)
    
    Example Roles:
    A sup org has roles (e.g. manager, HR partner, etc).
    
    So sup org 123 has a manager with a position ID of 567-pos. That "Role" is of type Manger, 
    position 567-pos, and the position is assigned to worker W123 whose name is John Doe.
    And sup org 123 has 2 HR partners, so one role (HR Partner), two positions (pos 456 and pos 987), with
    workers assigned to each of those positions
"""

class base(object):
    def __new__(cls, *args, **kwargs):
        instance = object.__new__(cls, *args, **kwargs)
        if "instances" not in cls.__dict__:
            cls.instances = WeakSet()
        cls.instances.add(instance)
        return instance


class Supervisory_Organization(base):
    """
        This object is populated by either the Supervisory Org with Superiors file (iLoad) or by a "super" file
        generated through query.
    """

    @classmethod
    def by_id(cls): return {so.org_id: so for so in cls.instances}

    def __init__(self, line_no, org_id, effective_date, name, availability_date, parent_org_id, location_id, org_subtype):
        """
            :param line_no: Used for debugging. Typically the line number in the input file
            :param org_id: ID of the supervisory org. Typically a number
            :param effective_date: Effective date of sup org. Not currenlly used.
            :param name: User friendly name of sup org
            :param availability_date:  Not currently used
            :param parent_org_id: Org id of the parent supervisory org. *NOT* the object
            :param location_id: Location ref id. *NOT* the object
            :param org_subtype: Text string of org subtype. Not currently used
        """
        self._line_no = line_no
        self._org_id = org_id
        self._effective_date = effective_date
        self._name = name
        self._availability_date = availability_date
        self._parent_org_id = parent_org_id
        if not parent_org_id:
            self._is_top_level = True
        else:
            self._is_top_level = False
        self._parent = None
        self._location_id = location_id
        self._location = None
        self._subtype = org_subtype
        self._role_list = []
        self._seq = Seq_Generator().id
        self._children = []
        self._traversed = False
        self._default_orgs_dict = {}
        self._manager = None
        return

    def propagate_custom_orgs(self):
        """ Go through my parent's default orgs. If I have a value, use it. If I don't then use my parent's value """
        if self._parent: # Make sure I have a parent
            for org_type, def_org in self._parent.get_default_orgs().iteritems():
                if org_type not in self._default_orgs_dict:
                    self.add_default(def_org.org, True)
        for c in self._children:
            c.propagate_custom_orgs()
        return

    def add_default(self, default_org, inherited=False):
        if type(default_org) != Organization:
            error("Inavlid organization passed to add_default")
            raise TypeError
        do = Default_Organization(self, default_org, inherited)
        self._default_orgs_dict[default_org.org_type] = do
        return

    def add_role(self, role):
        if type(role) != Role:
            error("Invalid role_type type passed")
            raise TypeError
        if role in self._role_list:  # Dup roles are an issue if using "super" file. Remove existing and replace
            self._role_list.remove(role)
        self._role_list.append(role)
        return

    def add_child(self, sup_org):
        self._children.append(sup_org)
        return

    def cycle_check(self, stack):
        if self._traversed:
            error("Found cyclic error. Print stack")
            for so in stack:
                error(so)
            sys.exit()
        else:
            stack.append(self)
            self._traversed = True
            for c in self._children:
                c.cycle_check(stack)
            stack.pop()
        return

    def set_manager(self, role):
        self._manager = role

    @property
    def traversed(self): return self._traversed
    @property
    def is_top_level(self): return self._is_top_level
    @property
    def subtype(self): return self._subtype
    @property
    def location_id(self): return self._location_id
    @property
    def location(self): return self._location
    @location.setter
    def location(self, location):
        self._location = location
        return
    @property
    def id(self): return self._org_id
    @property
    def name(self): return self._name
    @property
    def parent(self): return self._parent
    @property
    def parent_id(self): return self._parent_org_id
    @parent.setter
    def parent(self, parent):
        self._parent = parent
        parent.add_child(self)
        return

    def get_default_orgs(self):
        return self._default_orgs_dict

    def to_html_collapse_table_w_roles(self):
        doc, tag, text = Doc().tagtext()
        with tag("div", klass="panel panel-default"):
            with tag("div", klass="panel-heading", display="inline"):
                with tag("p"):
                    with tag("a", ("data-toggle","collapse"), href="#{}".format(self.id)):
                        with tag("b", klass="panel-title"):
                            text("{} ({})".format(self.name, self.id))
                    with tag("span", style="font-size:0.8em", klass="panel-title"):
                        with tag("strong"):
                            text(" Manager: ")
                        if self._manager:
                            text(" {} ".format(self._manager.get_workers()[0]))
                        else:
                            text("No Manager Assigned")
                        with tag("strong"):
                            text("  Location: ")
                        text(" {} ".format(self._location))
                        doc.stag("br")
                        with tag("table"):
                            with tag("tr"):
                                with tag("th"):
                                    with tag("a", ("data-toggle","collapse"), href="#Roles{}".format(self.id)):
                                        text("Roles:")
                                with tag("th"):
                                    with tag("a", ("data-toggle","collapse"), href="#Defaults{}".format(self.id)):
                                        text("Organization Defaults:")
                            with tag("tr"):
                                with tag("td"):
                                    with tag("div", id="Roles{}".format(self.id), klass="panel-collapse collapse"):
                                        if self._role_list:
                                            with tag("table", border=".5"):
                                                for r in self._role_list:
                                                    with tag("tr"):
                                                        with tag("td"):
                                                            text(r.name)
                                                        with tag("td"):
                                                            w_list = r.get_workers()
                                                            for w in w_list:
                                                                text(str(w))
                                                                doc.stag("br")
                                with tag("td"):
                                    with tag("div", id="Defaults{}".format(self.id), klass="panel-collapse collapse"):
                                        with tag("table"):
                                            with tag("tr"):
                                                for col_heading in ["Organization Type", "Organization Name", "Inherited (T/F)"]:
                                                    with tag("th"):
                                                        text(col_heading)
                                            for k, v in sorted(self._default_orgs_dict.items(), key=operator.itemgetter(0)):
                                                with tag("tr"):
                                                    for txt in [k.name, v.org, v.inherited]:
                                                        with tag("td"):
                                                            text(str(txt))
            if self._children:
                with tag("div", id="{}".format(self.id), klass="panel-collapse collapse"):
                    with tag("ul", klass="list_group"):
                        for c in self._children:
                            with tag("li", klass="list-group-item"):
                                doc.asis(c.to_html_collapse_table_w_roles())
        return doc.getvalue()

    def to_html_collapse_table(self):
        doc, tag, text = Doc().tagtext()
        with tag("div", klass="panel panel-default"):
            with tag("div", klass="panel-heading", display="inline"):
                with tag("p"):
                    with tag("a", ("data-toggle","collapse"), href="#{}".format(self.id)):
                        with tag("b", klass="panel-title"):
                            text("{} ({})".format(self.name, self.id))
                            doc.asis("<br>")
                    with tag("span", style="font-size:0.8em", klass="panel-title"):
                        with tag("strong"):
                            text("Manager:")
                        text(" {} ".format(self._role_list.worker))
                        if self._role_list.inherited:
                            text("[Inherited]")
                        with tag("strong"):
                            text("Location: ")
                        text(" {} ".format(self._location))
                        if len(self._default_orgs_dict):
                            doc.stag("br")
                            with tag("strong"):
                                with tag("a", ("data-toggle","collapse"), href="#Defaults{}".format(self.id)):
                                    text("Defaults: ")
                            with tag("div", id="Defaults{}".format(self.id), klass="panel-collapse collapse"):
                                with tag("table"):
                                    with tag("tr"):
                                        for col_heading in ["Organization Type", "Organization Name", "Inherited (T/F)"]:
                                            with tag("th"):
                                                text(col_heading)
                                    #for k, v in self._default_orgs.iteritems():
                                    for k, v in sorted(self._default_orgs_dict.items(), key=operator.itemgetter(0)):
                                        with tag("tr"):
                                            for txt in [k.name, v.org, v.inherited]:
                                                with tag("td"):
                                                    text(str(txt))
            if self._children:
                with tag("div", id="{}".format(self.id), klass="panel-collapse collapse"):
                    with tag("ul", klass="list_group"):
                        for c in self._children:
                            with tag("li", klass="list-group-item"):
                                doc.asis(c.to_html_collapse_table())
        return doc.getvalue()

    def to_html_collapse(self):
        doc, tag, text = Doc().tagtext()
        with tag("div", klass="panel panel-default"):
            with tag("div", klass="panel-heading", display="inline"):
                with tag("p"):
                    with tag("a", ("data-toggle","collapse"), href="#{}".format(self.id)):
                        with tag("b", klass="panel-title"):
                            text("{} ({})".format(self.name, self.id))
                            doc.asis("<br>")
                    with tag("span", style="font-size:0.8em", klass="panel-title"):
                        with tag("strong"):
                            text("Manager:")
                        text(" {} ".format(self._role_list.worker))
                        if self._role_list.inherited:
                            text("[Inherited]")
                        with tag("strong"):
                            text("Location: ")
                        text(" {} ".format(self._location))
                        if len(self._default_orgs_dict):
                            doc.stag("br")
                            with tag("strong"):
                                with tag("a", ("data-toggle","collapse"), href="#Defaults{}".format(self.id)):
                                    text("Defaults: ")
                            with tag("div", id="Defaults{}".format(self.id), klass="panel-collapse collapse"):
                                with tag("ul", klass="list-group"):
                                    for k, v in self._default_orgs_dict.iteritems():
                                        with tag("li", klass="list-group-item", style="white-space: pre;margin-left: 10px; font-size:0.8em; padding-top:0px; padding-bottom:0px"):
                                            text("{:30}  {}".format(k.name, v))

            if self._children:
                with tag("div", id="{}".format(self.id), klass="panel-collapse collapse"):
                    with tag("ul", klass="list_group"):
                        for c in self._children:
                            with tag("li", klass="list-group-item"):
                                doc.asis(c.to_html_collapse())
        return doc.getvalue()

    def to_html(self):
        doc, tag, text = Doc().tagtext()
        with tag("div", klass="panel panel-default"):
            with tag("div", klass="panel-heading", display="inline"):
                with tag("p"):
                    with tag("a", ("data-toggle","collapse"), href="#{}".format(self.id)):
                        with tag("b", klass="panel-title"):
                            text("{} ({})".format(self.name, self.id))
                            doc.asis("<br>")
                    with tag("span", style="font-size:0.8em", klass="panel-title"):
                        with tag("strong"):
                            text("Manager:")
                        text(" {} ".format(self._role_list.worker))
                        if self._role_list.inherited:
                            text("[Inherited]")
                        with tag("strong"):
                            text("Location: ")
                        text(" {} ".format(self._location))
                        if len(self._default_orgs_dict):
                            doc.stag("br")
                            with tag("strong"):
                                text("Defaults: ")
                            for k, v in self._default_orgs_dict.iteritems():
                                text(" {}:{}  ".format(k.name, v))
            if self._children:
                with tag("div", id="{}".format(self.id), klass="panel-collapse collapse"):
                    with tag("ul", klass="list_group"):
                        for c in self._children:
                            with tag("li", klass="list-group-item"):
                                doc.asis(c.to_html())
        return doc.getvalue()

    def to_Assignment_Restrictions_and_Defaults_iLoad(self):
        row = ["", "Organization_Reference_ID", "", self._org_id]
        ctr = 1
        for default_org in self._default_orgs_dict.values():
            org = default_org.org
            row += [ctr, "Organization_Type_ID", "", org.org_type.value] + [""] * 6 + ["Organization_Reference_ID", "", org.ref_id]
            yield row
            ctr += 1
            row = [""] * 4

    def __repr__(self):
        return "{} ({})".format(self.name, self.id)


class Location(base):
    """
        Simple object to hold the name and ID of a location, and control the look of the output
    """
    def __init__(self, reference_id, name):
        self._ref_id = reference_id
        self._name = name
        self._seq = Seq_Generator().id
        return

    @property
    def name(self): return self._name
    @name.setter
    def name(self, name):
        if name:
            self._name = name
        return
    @property
    def ref_id(self): return self._ref_id

    def __repr__(self):
        return "{} ({})".format(self.name, self.ref_id)


class Position(base):
    """
        This object represents the manager of a given supervisory org. It is position specific, meaning that
        it is specific to the supervisory org. So if one worker is manager for more than one org, they will have
        multiple Manager objects each with it's own position
    """
    def __init__(self, position_id, supervisory_org, role, worker=None):
        self._pos_id = position_id
        self._inherited = False
        if type(role) != Role:
            error("Invalid type for role_type passed to position")
            raise TypeError
        self._role = role
        if type(supervisory_org) != Supervisory_Organization:
            error("Invalid org_type passed to Manager __init__")
            raise TypeError
        self._org = supervisory_org  # Object, not ID
        if worker:
            self.assign_worker(worker)
        else:
            self._worker = Worker("UNKNOWN", position_id)
        return

    def assign_worker(self, worker):
        if type(worker) != Worker:
            error("Invalid org_type passed to assign_worker.")
            raise TypeError
        self._worker = worker
        return

    @property
    def inherited(self): return self._inherited
    @inherited.setter
    def inherited(self, inherited):
        self._inherited = inherited
        return
    @property
    def position(self): return self._pos_id
    @property
    def worker(self): return self._worker

    def __repr__(self):
        ret_str = "Position ID: {} Worker: {} Inherited: {}".format(self._pos_id, self._worker, self._inherited)
        return ret_str


class Role(base):
    def __init__(self, role_type, sup_org):
        if type (role_type) != Roles:
            error("Invalid role_type type passed")
            raise TypeError
        if type(sup_org) != Supervisory_Organization:
            error("Invalid sup org type send to Role")
            raise TypeError
        self._position_list = []
        self._sup_org = sup_org
        self._role = role_type
        if role_type == Roles.Manager:
            sup_org.set_manager(self)
        return

    def add_position(self, position):
        if type(position) != Position:
            error("Invalid position passed to add_position")
            raise TypeError
        self._position_list.append(position)
        return

    @property
    def role_type(self): return self._role
    @property
    def name(self): return self._role.name

    def get_workers(self):
        ret_list = []
        for p in self._position_list:
            ret_list.append(p.worker)
        return ret_list

    def __eq__(self, other):
        return self.role_type == other.role_type


class Default_Organization(base):
    """
        This object represents those organizations specified as "defaults" for a given supervisory organization
        It points to both the supervisory org that it belongs to and to the referenced org.
        This really exists because the inherited flag is specific to the sup org, not to the org
   """
    def __init__(self, sup_org, org, inherited=False):
        if type(sup_org) != Supervisory_Organization:
            error("Invalid org_type for supervisory org in Default Organization")
            raise TypeError
        if type(org) != Organization:
            error("Invalid org_type for organization in Default Organization")
            raise TypeError
        self._sup_org = sup_org
        self._org = org
        self._inherited = inherited
        return

    @property
    def org(self): return self._org
    @property
    def inherited(self): return self._inherited
    @inherited.setter
    def inherited(self, inherit):
        self._inherited = inherit
        return
    @property
    def org_type(self): return self._org.org_type

    def __repr__(self):
        if self._inherited:
            ret_str = "{}[Inherited]".format(self._org)
        else:
            ret_str = "{}".format(self._org)
        return ret_str


class Worker(base):
    def __init__(self, name, emp_id):
        self._name = name
        self._emp_id = emp_id
        self._positions = []
        return

    @property
    def name(self): return self._name
    @name.setter
    def name(self, name):
        self._name = name
    @property
    def emp_id(self): return self._emp_id

    def add_position(self, position):
        self._positions.append(position)
        return

    def __repr__(self):
        return "{} ({})".format(self._name, self._emp_id)


class Organization(base):
    def __init__(self, name, ref_id, org_type):
        self._name = name
        self._ref_id = ref_id
        self._type = org_type
        return

    @property
    def name(self): return self._name
    @name.setter
    def name(self, name):
        self._name = name
        return
    @property
    def ref_id(self): return self._ref_id
    @property
    def org_type(self): return self._type

    def __repr__(self):
        return "{} ({})".format(self._name, self._ref_id)
