//Libraries
#include <ESP8266WiFi.h>//https://github.com/esp8266/Arduino/blob/master/libraries/ESP8266WiFi/src/ESP8266WiFi.h
#include <ESP8266HTTPClient.h>
#include <WiFiClient.h>
#include "variables.h"

//Constants
#define LED BUILTIN_LED
#define UPDATE_TIME 25
#define furnace 5
//Parameters
String nom = "FURNACE";
//Variables
//String command;
//int wait = 0;
bool state = false;
int lastcheck;
int exit_code;
int keepalive = 60000;

//Objects
WiFiClient master;
String checkURL = "http://192.168.1.7:5000/check";
String alarmURL = "http://192.168.1.7:5000/alarm";

// mail stuff
#include <Arduino.h>
#include <ESP_Mail_Client.h>
SMTPSession smtp;

void smtpCallback(SMTP_Status status);

const char rootCACert[] PROGMEM = "-----BEGIN CERTIFICATE-----\n"
                                  "-----END CERTIFICATE-----\n";
// end mail stuff

void setup() {
  Serial.begin(9600);
  Serial.println(F("Init"));
  // Init WiFi
  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(F("."));
  }
  Serial.print(nom);
  Serial.print(F(" connected to WiFi! IP Address : ")); Serial.println(WiFi.localIP());
  pinMode(LED, OUTPUT);
  pinMode(furnace, OUTPUT);
  furnOff();
  //mail stuff

}

void loop() {
  exit_code = requestStatus();
  checkCode(exit_code);
  delay(5000);
}

void checkCode(int code){
  /* Elenco codici: 1000 caldaia in accensione da valvole
   *                400 caldaia in spegnimento da valvole
   *                3141 caldaia in accensione da manuale
   *                314 caldaia in spegnimento da manuale
   *                10001 temporaneamente non connesso
   *
   *                0-999 caldaia spenta
   *                1000-9999 caldaia accesa
  */
  if (cod == 10001){
      Serial.println("Waiting...");
      return;
  }
  if (code >= 1000 && code < 9999){
      if (state != true){
        Serial.println("La Caldaia va accesa");
        furnOn();
        state = true;
        //wait = 0;
        lastcheck = millis();
      } else {
        lastcheck = millis();
      }
  } else if (code < 1000) {
      if (state != false){
        Serial.println("La Caldaia va spenta");
        furnOff();
        state = false;
        //wait = wait + 1;
        lastcheck = millis();
      }
      else {
        lastcheck = millis();
      }
  } else if (code == 9999) {
    Serial.println("Maintenance");
    checkURL = "http://192.168.1.22:5000/check";
    alarmURL = "http://192.168.1.22:5000/alarm";
  } else if (code = 10000) {
    Serial.println("Out of Maintenance");
    checkURL = "http://192.168.1.7:5000/check";
    alarmURL = "http://192.168.1.7:5000/alarm";
  }
}

int requestStatus(){
  HTTPClient http;
  http.begin(master,checkURL);
  int httpCode = http.GET();
  //Serial.println(httpCode);
  if (httpCode == 200){
    String payload = http.getString();
    int code = payload.toInt();
    http.end();
    return code;
  } else {
    Serial.println("No Connection");
    if ((millis() - lastcheck) > keepalive) {
      Serial.println("Sending message to DNS!");
      alert_API();
      Serial.println("Sending email to administrator!");
      mail();
      lastcheck = millis();
      http.end();
      return 3141;
    }
    return 10001;
  }
}

void alert_API(){
  HTTPClient http;
  http.begin(master,"http://192.168.1.7:5000/alert");
  int httpCode = http.GET();
  Serial.println(httpCode);
}

void mail(){
  smtp.debug(0);
  smtp.callback(smtpCallback);
  ESP_Mail_Session session;
  session.server.host_name = SMTP_HOST;
  session.server.port = SMTP_PORT;
  session.login.email = AUTHOR_EMAIL;
  session.login.password = AUTHOR_PASSWORD;
  session.login.user_domain = SMTP_DOMAIN;
  session.time.ntp_server = "pool.ntp.org,time.nist.gov";
  session.time.gmt_offset = 1;
  session.time.day_light_offset = 0;
  SMTP_Message message;
  message.sender.name = "ESP";
  message.sender.email = AUTHOR_EMAIL;
  message.subject = "Furnace Control requires your attention";
  message.addRecipient("admin", ADMIN_EMAIL);
  String textMsg = "There is no connection to local DNS.";
  message.text.content = textMsg.c_str();
  message.addHeader("Message-ID: <administrator>");
  if (!smtp.connect(&session)){
    return;
  }
  if (!MailClient.sendMail(&smtp, &message)){
    Serial.println("Error sending email, " +smtp.errorReason());
  }
}

void furnOff(){
  digitalWrite(LED,HIGH);
  digitalWrite(furnace,LOW);
}

void furnOn(){
  digitalWrite(LED,LOW);
  digitalWrite(furnace,HIGH);
}



void smtpCallback(SMTP_Status status)
{
  /* Print the current status */
  Serial.println(status.info());

  /* Print the sending result */
  if (status.success())
  {
    Serial.println("----------------");
    ESP_MAIL_PRINTF("Message sent success: %d\n", status.completedCount());
    ESP_MAIL_PRINTF("Message sent failled: %d\n", status.failedCount());
    Serial.println("----------------\n");
    struct tm dt;

    for (size_t i = 0; i < smtp.sendingResult.size(); i++)
    {
      /* Get the result item */
      SMTP_Result result = smtp.sendingResult.getItem(i);
      time_t ts = (time_t)result.timestamp;
      localtime_r(&ts, &dt);

      ESP_MAIL_PRINTF("Message No: %d\n", i + 1);
      ESP_MAIL_PRINTF("Status: %s\n", result.completed ? "success" : "failed");
      ESP_MAIL_PRINTF("Date/Time: %d/%d/%d %d:%d:%d\n", dt.tm_year + 1900, dt.tm_mon + 1, dt.tm_mday, dt.tm_hour, dt.tm_min, dt.tm_sec);
      ESP_MAIL_PRINTF("Recipient: %s\n", result.recipients);
      ESP_MAIL_PRINTF("Subject: %s\n", result.subject);
    }
    Serial.println("----------------\n");

    //You need to clear sending result as the memory usage will grow up as it keeps the status, timstamp and
    //pointer to const char of recipients and subject that user assigned to the SMTP_Message object.

    //Because of pointer to const char that stores instead of dynamic string, the subject and recipients value can be
    //a garbage string (pointer points to undefind location) as SMTP_Message was declared as local variable or the value changed.

    smtp.sendingResult.clear();
  }
}
