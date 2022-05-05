<%@ page language="java" contentType="text/html; charset=ISO-8859-1"
    pageEncoding="ISO-8859-1"
    import="java.util.*"%>
<!DOCTYPE html>
<html>
<head>

<meta charset="ISO-8859-1">
<meta name='apple-mobile-web-app-capable' content='yes' />
<meta name='apple-mobile-web-app-status-bar-style' content='black-translucent' />
<title>Controllo Caldaia</title>
</head>

<body style = 'background-color:#000000; color:white;'>
<h1>ESP8266 - Controllo Elettrico Caldaia</h1>
<hr/><hr>
<br><br>
<%= (long)Math.ceil(System.currentTimeMillis()/1000) %>
<form>
<p>Seleziona modalità di visualizzazione</p>
<div>
	<input type="radio" id="basic" name="view" value="basic" checked>
	<label for="basic">SEMPLICE</label>
</div>
	
<div>
	<input type="radio" id="advanced" name="view" value="advanced">
	<label for="advanced">AVANZATO</label>
</div>

<div>
    <button type="submit">Submit</button>
  </div>
</form>

<% if("basic".equals(request.getParameter("view"))) { %>
<br><br>
<h2>Comandi</h2>
Accensione Manuale
<a href='furnOn.jsp'><button>Accendi Caldaia</button></a>
<a href='furnOff.jsp'><button>Spegni Caldaia</button></a>
<a href='automatic.jsp'><button>Ritorna in Automatico</button></a>

<%
}else{}
%>

<br><br>


<br><br>
<br><br>
<br><br>


<!--  <a href='/advanced.jsp -->

</body>
</html>