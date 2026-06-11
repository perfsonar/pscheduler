import json
import pathlib

from .data import data

from flask import Flask, redirect, url_for, request, Response

app = Flask(__name__)

# Arg evaluation

def arg_boolean(name):
    """Determine if a boolean argument is part of a request.  The
    argument is considered true if it is 'true', 'yes' or '1' or if it
    is present but has no value.  Otherwise it is considered False."""
    argval = request.args.get(name)
    if argval is None:
        return False;
    argval = argval.lower()
    if argval in [ '', 'true', 'yes', '1' ]:
        return True
    return False

# Responses

def ok(message='OK', mimetype=None):
    return Response(message + '\n',
                    status=200,
                    mimetype=mimetype)

def ok_json(data=None, sanitize=True):
    return Response(json.dumps(data) + '\n',
                    status=200,
                    mimetype='application/json')

def not_found(message='Resource not found.', mimetype="text/plain"):
    return Response(message + "\n",
                    status=404,
                    mimetype="text/plain")

@app.route('/')
def root():
    return ok('Hello, enumerated world!')

@app.route('/pscheduler')
def pscheduler():
    return ok('This is not really pScheduler.')

@app.route('/pscheduler/<plugin>')
def pscheduler_plugin(plugin):
    try:
        if arg_boolean('expanded'):
            return ok_json(data[plugin])
        else:
            result = []
            for item in data[plugin]:
                result.append(f'''{request.url}/{item['name']}''')
            return ok_json(result)
    except KeyError:
        return not_found()

@app.route('/pscheduler/<plugin>/<name>')
def pscheduler_plugin_name(plugin, name):
    try:
        for item in data[plugin]:
            if item['name'] == name:
                return ok_json(item)
        return not_found()
    except KeyError:
        return not_found()

    

def main():
    app.run(port=21044, debug=False, use_reloader=False)
