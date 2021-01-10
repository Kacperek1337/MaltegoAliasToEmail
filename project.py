import sys

from maltego_trx.handler import handle_run
from maltego_trx.registry import (register_transform_classes,
                                  register_transform_function)
from maltego_trx.server import app, application

import transforms

# register_transform_function(transform_func)
register_transform_classes(transforms)

handle_run(__name__, sys.argv, app)
