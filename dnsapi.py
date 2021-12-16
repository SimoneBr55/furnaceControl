from flask import Flask
from flask_restful import Resource, Api, reqparse
import pandas as pd
import ast
import time
import datetime
from pushbullet import Pushbullet
from decouple import config
upState = False
downState = False
manual = False
lastUp = 0
lastDown = 0
payload = 0
schedule = [(12600,13200)]

app = Flask(__name__)
api = Api(app)
pb_api = config('pb_api')
device = config('dev')
class alert(Resource):
	def get(self):
		print("Alert!!!")
		alert()
		#data = time.strftime("%H,%M,%S",time.gmtime())
		return 200

class timer(Resource):
	def get(self):
		today = datetime.date.today()
		ssm = time.time() - time.mktime(today.timetuple())
		return int(ssm)

class upstairs(Resource):
	def get(self):
		global lastUp
		today = datetime.date.today()
		lastUp = time.time() - time.mktime(today.timetuple())
		global upState
		upState = True
		return 200

class downstairs(Resource):
	def get(self):
		global lastDown
		today = datetime.date.today()
		lastDown = time.time() - time.mktime(today.timetuple())
		global downState
		downState = True
		return 200

class check(Resource):
	def get(self):
		global upState
		global downState
		global lastUp
		global lastDown
		global manual
		global payload
		global schedule
		if (payload == 9999):
			return payload
		resetTime = 240
		today = datetime.date.today()
		now = time.time() - time.mktime(today.timetuple())
		if any(lower <= int(now) <= upper for (lower,upper) in schedule):
			payload = 1414
			return payload
		if (manual != True):
			if( (int(now) - lastUp) >= resetTime):
				upState = False
			if( (int(now) - lastDown) >= resetTime):
				downState = False
			if(upState or downState):
				payload = 1000 #accensione da valvol*
			else:
				payload = 400
		return payload

class automatic(Resource):
	def get(self):
		global manual
		manual = False
		return 200

class maintenance(Resource):
	def get(self):
		global payload
		if (payload == 9999):
			payload == 3140
		else:
			payload = 9999
		return 200

class furnOn(Resource):
	def get(self):
		global manual
		global payload
		manual = True
		payload = 3141
		return 200

class furnOff(Resource):
	def get(self):
		global manual
		global payload
		manual = True
		payload = 314
		return 200

@app.route("/")
def home():
	global upState
	global downState
	global manual
	page = """ <!DOCTYPE HTML>
 <html>
 <head>
 <meta name='apple-mobile-web-app-capable' content='yes' />
 <meta name='apple-mobile-web-app-status-bar-style' content='black-translucent' />
 <meta http-equiv=\"refresh\" content=\"1; url=/\">
 <meta charset=\"utf-8\" />
 </head>
 <body style = ' background-color:#000000; color:white;'>
 <hr/><hr>
 <h1><center> ESP8266 - Controllo Elettrico Caldaia </center></h1>
 <hr/><hr>
 <br><br>
 <br><br>
 <h2> Comandi </h2>
 <center>
 Accensione Manuale
 <a href='/furnOn.html'><button>Accendi Caldaia</button></a>
 <a href='/furnOff.html'><button>Spegni Caldaia</button></a><br />
 <a href='/automatic.html'><button>Ritorna in Automatico</button></a>
 </center>
 <br><br>
 <br><br>
 <h2> Status </h2>
 <center>
 <table border='5'>
 <tr>
"""
	if manual:
		status_furnace = "<td>La Caldaia è Accesa</td>"
	else:
		if upState or downState:
			status_furnace = "<td>La Caldaia è Accesa</td>"
		else:
			status_furnace = "<td>La Caldaia è Spenta</td>"
	page += status_furnace
	page += "<br />"
	if manual:
		regime = "<td>La Caldaia è in funzionamento Manuale</td>"
	else:
		regime = "<td>La Caldaia è in funzionamento Automatico</td>"
	page += regime
	page += "</tr>"
	page += "<tr>"
	if upState:
		statusUp = "<td>La Termovalvola1 è Accesa</td>"
	else:
		statusUp = "<td>La Termovalvola1 è Spenta</td>"
	page += statusUp
	page += "<br />"
	if downState:
		statusDown = "<td>La Termovalvola2 è Accesa</td>"
	else:
		statusDown = "<td>La Termovalvola2 è Spenta</td>"
	page += statusDown
	waitforit = """</tr>
</table>
</center>
<br><br>
<br><br>
<center>
"""
	page += waitforit
	if (payload == 9999):
		maint = "<a href='/maintenance.html'><button>Esci da modalità manutenzione</button></a>"
	else:
		maint = "<a href='/maintenance.html'><button>Entra in modalità manutenzione</button></a>"
	page += maint
	ending = """
</center>
</body>
</html>"""
	page += ending
	return page

api.add_resource(maintenance, '/maintenance.html')
api.add_resource(downstairs, '/DOWNSTAIRS')
api.add_resource(upstairs, '/UPSTAIRS')
api.add_resource(alert, '/alert')
api.add_resource(timer, '/timer')
api.add_resource(check, '/check')
api.add_resource(furnOn, '/furnOn.html')
api.add_resource(furnOff, '/furnOff.html')
api.add_resource(automatic, '/automatic.html')


def alert():
	pb = Pushbullet(pb_api)
	dev = pb.get_device(device)
	push = dev.push_note("Titolo di Prova", "Stop")


if __name__ == '__main__':
	app.run("0.0.0.0", port=5000)
