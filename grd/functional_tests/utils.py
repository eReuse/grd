import os
import json

from django.core import management


def dump_grd_data(app_name="grd", filename="/tmp/grd_data.json"):
    """Dump test data to a file for debugging purposses."""
    with open(filename, 'w') as f:
        management.call_command('dumpdata', app_name, indent=4, stdout=f)


def load_json(filename):
    path = os.path.join(os.path.dirname(__file__), filename)
    with open(path) as request_file:
        data = json.load(request_file)
    return data
