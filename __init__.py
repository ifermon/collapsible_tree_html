import logging
from yattag import Doc, indent

# Configure logging for everyone
logging.basicConfig(datefmt="%H:%M:%S", format="%(asctime)s %(message)s")
l = logging.getLogger()
l.setLevel(logging.DEBUG)
debug = l.debug
info = l.info
error = l.error

import itertools
class Seq_Generator():
    newid = itertools.count().next
    def __init__(self):
        self.id = Seq_Generator.newid()
