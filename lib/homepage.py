def homepage():
	page = """<!DOCTYPE HTML>
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
	</html>"""
	return page
