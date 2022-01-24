# dnsapi_bleeding v2.0

from flask import Flask
from flask_restful import Resource, Api, reqparse
import pandas as pd
import ast
import time
import datetime
from pushbullet import Pushbullet
from decouple import config
from lib.homepage import homepage
import threading

upState = False
downState = False
manual = False
lastUp = 0
lastDown = 0
payload = 0
#schedule = 0

app = Flask(__name__)
api = Api(app)
pb_api = config('pb_api')
device = config('dev')
server_info = config('server_info')
user_info = config('user_info')
passw_info = config('passw_info')
receiver_info = config('receiver_info')

def what_time_is_it():
	today = datetime.date.today()
	now = time.time() - time.mktime(today.timetuple())
	return now

class alert(Resource):
	def get(self):
		print("Alert!!!")
		alert("Generic Error from Valve")
		#data = time.strftime("%H,%M,%S",time.gmtime())
		return 200

class timer(Resource):
	def get(self):
		ssm = what_time_is_it()
		return int(ssm)

class upstairs(Resource):
	def get(self):
		global lastUp
		lastUp = what_time_is_it()
		global upState
		upState = True
		return 200

class downstairs(Resource):
	def get(self):
		global lastDown
		lastDown = what_time_is_it()
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
		global last_check
		if (payload == 9999 or payload == 10000):
			return payload
		resetTime = 240
		now = what_time_is_it()
		last_check = now
		#if any(lower <= int(now) <= upper for (lower,upper) in schedule):
		#	payload = 1414
		#	return payload
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

class maintenanceOn(Resource):
	def get(self):
		global payload
		payload = 9999
		return 200

class maintenanceOff(Resource):
	def get(self):
		global payload
		payload = 10000
		return 200

class furnOn(Resource):
	def get(self):
		global manual
		global payload
		manual = True
		payload = 3141
		#return 200

class furnOff(Resource):
	def get(self):
		global manual
		global payload
		manual = True
		payload = 314
		return 200

@app.route("/")
def home():
	"""
def home():
	page = \"""<!DOCTYPE HTML>
	<html>
	<head>
	<meta name='apple-mobile-web-app-capable' content='yes' />
	<meta name='apple-mobile-web-app-status-bar-style' content='black-translucent' />
	<meta charset=\"utf-8\" />
	</head>
	<body style = ' background-color:#000000; color:white;'>
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
	</body>
	</html>\"""
	return page
""" 
	return homepage()


@app.route("/advanced")
def advanced():
	global upState
	global downState
	global manual
	page = """ <!DOCTYPE HTML>
 <html>
 <head>
 <meta name='apple-mobile-web-app-capable' content='yes' />
 <meta name='apple-mobile-web-app-status-bar-style' content='black-translucent' />
 <meta http-equiv=\"refresh\" content=\"1; url=/advanced\">
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
	maint = "<a href='/maintenanceOff.html'><button>Esci da modalità manutenzione</button></a>"
	maint = maint + "<a href='/maintenanceOn.html'><button>Entra in modalità manutenzione</button></a>"
	page += maint
	ending = """
</center>
</body>
</html>"""
	page += ending
	return page


api.add_resource(maintenanceOn, '/maintenanceOn.html')
api.add_resource(maintenanceOff, '/maintenanceOff.html')
api.add_resource(downstairs, '/DOWNSTAIRS')
api.add_resource(upstairs, '/UPSTAIRS')
api.add_resource(alert, '/alert')
api.add_resource(timer, '/timer')
api.add_resource(check, '/check')
api.add_resource(furnOn, '/furnOn.html')
api.add_resource(furnOff, '/furnOff.html')
api.add_resource(automatic, '/automatic.html')


def alert(source, case):
	try:
		pb = Pushbullet(pb_api)
		dev = pb.get_device(device)
		push = dev.push_note("APIFC message from ", str(source), "Error with " + str(case))
	except:
		print("Sending mail")
		mailing(source, case)
		

def checking(stop, reset_time):
	global last_check
	while True:
		if stop():
			print("dead")
			break
		now = what_time_is_it()
		delay = int(now) - int(last_check)
		if delay >= reset_time:
			print("delay")
			alert("DNS","Furnace not checking in with DNS")
			#alerting += 1  # still undecided if having a counter to stop overreacting and overloading pushbullet or mail sending
			#time.sleep(4)  # this sould be not necessary
		time.sleep(4)

def mailing(source, case):
	import os, sys
	import smtplib
	from email.mime.text import MIMEText
	from email.mime.multipart import MIMEMultipart
	from email.mime.base import MIMEBase
	from email import encoders
	
	subject = "APIFC message from "
	subject += str(source)
	body = "There was a problem catched by the furnace API. The case of the problem is: "
	body = body + str(case)
	
	# imported via config: server_info, user_info, passw_info, receiver_info
	server = smtplib.SMTP(str(server_info), 587)
	server.ehlo()
	server.starttls()
	# Login
	user = str(user_info)
	passw = str(passw_info)
	server.login(user, passw)
	
	msg = MIMEMultipart()
	msg['Subject'] = subject
	msg['From'] = 'Furnace API'
	receivers = receiver_info
	msg['To'] = receivers
	msg.attach(MIMEText(body, 'plain'))
	# Send email
	server.sendmail(user, receivers, msg.as_string())
	server.quit()

if __name__ == '__main__':
	#mailing("crap") # for testing purposes
	stop_threads = False # Yet to implement the stopping condition for the checking thread
	last_check = what_time_is_it()
	error_time = 12
	t1 = threading.Thread(target = checking, args =(lambda : stop_threads, error_time))
	t1.start()
	app.run("0.0.0.0", port=5000)
