#include <ESP8266WiFi.h>
#include <ESP8266HTTPClient.h>
#include <WiFiClient.h>

//Constants
const char* ssid="ssid";
const char* password="password";
String nom="UPSTAIRS";
#define LED LED_BUILTIN

int keepalive = 60000;
int lastcheck;

//mail stuff
#include <Arduino.h>
#include <ESP_Mail_Client.h>
#define SMTP_HOST "mailserver"
#define SMTP_PORT 465
#define AUTHOR_EMAIL "email"
#define AUTHOR_PASSWORD "password"
#define SMTP_DOMAIN "domain"
#define ADMIN_EMAIL "emailto"
SMTPSession smtp;
void smtpCallback(SMTP_Status status);

const char rootCACert[] PROGMEM = "-----BEGIN CERTIFICATE-----\n"
                                  "-----END CERTIFICATE-----\n";
// end mail stuff

WiFiClient slave;

void setup() {
  Serial.begin(9600);
  Serial.println(F("Client v1.0"));
  Serial.println(F("Init"));
  //init wifi
  WiFi.begin(ssid,password);
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.println(F("."));
  }
  Serial.print(nom);
  Serial.print(F(" connected to Wifi! IP address : ")); Serial.println(WiFi.localIP()); // Print the IP address
  pinMode(LED,OUTPUT);
}

void loop() {
  flash(100);
  alive(nom);
  delay(900);
}

int alive(String order){
 HTTPClient http;
 http.begin(slave, "http://192.168.1.7:5000/"+order);
 int httpCode = http.GET();
 Serial.println(httpCode);
 if (httpCode == -1){
  if(millis() - lastcheck > keepalive){
    Serial.println("Sending email to administrator!");
    mail();
    lastcheck = millis();
    http.end();
    return httpCode;
  }
  http.end();
  return httpCode;
 }
 lastcheck = millis();
 http.end();
 return httpCode;
}

void LED_ON(){
  digitalWrite(LED,LOW);
}

void LED_OFF(){
  digitalWrite(LED,HIGH);
}

void flash(int timing){
  digitalWrite(LED,HIGH);
  delay(timing);
  digitalWrite(LED,LOW);
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
  message.sender.name = "UPSTAIRS";
  message.sender.email = AUTHOR_EMAIL;
  message.subject = "Furnace Control requires your attention";
  message.addRecipient("admin", ADMIN_EMAIL);
  String textMsg = "I am UPSTAIRS. There is no connection to local DNS.";
  message.text.content = textMsg.c_str();
  message.addHeader("Message-ID: <administrator>");
  if (!smtp.connect(&session)){
    return;
  }
  if (!MailClient.sendMail(&smtp, &message)){
    Serial.println("Error sending email, " +smtp.errorReason());
  }
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
