from __init__ import *

class Supervisory_Organization(object):
    def __init__(self, line_no, org_id, effective_date, name, availability_date, parent_org_id, location_id, org_subtype):
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
        self._manager = None
        self._seq = Seq_Generator().id
        self._children = []
        self._traversed = False
        return

    def add_manager(self, manager):
        self._manager = manager
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
                        text(" {} {}".format(self._manager, self.location))
            if self._children:
                with tag("div", id="{}".format(self.id), klass="panel-collapse collapse"):
                    with tag("ul", klass="list_group"):
                        for c in self._children:
                            with tag("li", klass="list-group-item"):
                                doc.asis(c.to_html())
        return doc.getvalue()

    def __repr__(self):
        return "{} ({})".format(self.name, self.id)



class Location(object):
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

class Manager(object):
    def __init__(self, position_id, emp_id=None, name=None):
        self._pos_id = position_id
        self._emp_id = emp_id
        self._name = name
        return

    @property
    def position(self): return self._pos_id
    @property
    def employee_id(self): return self._emp_id
    @employee_id.setter
    def employee_id(self, emp_id): self._emp_id = emp_id
    @property
    def name(self): return self._name
    @name.setter
    def name(self, name):
        self._name = name
        return

    def __repr__(self):
        return "{} ({})".format(self.name, self._emp_id)
