# dnssink v1.0

from flask import Flask
from flask_restful import Resource, Api, reqparse
import pandas as pd
import ast


app = Flask(__name__)
api = Api(app)

class alert(Resource):
	def get(self):
		return 200


class upstairs(Resource):
	def get(self):
		return 200

class downstairs(Resource):
	def get(self):
		return 200

class check(Resource):
    def get(self):
        return 10001

@app.route("/")
def home():
    page = """
<html>
<head></head>
<body>
<h1><center>The furnace is in Deep Maintenance Mode</center></h1>
<h2><center>The API will act as a sink</center></h2>
</body>
</html>
"""
    return page

@app.route("/advanced")
def advanced():
    page = """
<html>
<head></head>
<body>
<h1><center>The furnace is in Deep Maintenance Mode</center></h1>
<h2><center>The API will act as a sink</center></h2>
</body>
</html>
"""
    return page

api.add_resource(downstairs, '/DOWNSTAIRS')
api.add_resource(upstairs, '/UPSTAIRS')
api.add_resource(alert, '/alert')
api.add_resource(check, '/check')


if __name__ == '__main__':
	app.run("0.0.0.0", port=5000)
