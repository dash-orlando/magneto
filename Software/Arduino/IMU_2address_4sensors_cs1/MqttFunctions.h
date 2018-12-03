/*
 * MQTT Functions such as: Connect to WiFi, subscribe, publish, etc...
 */

#include <WiFi.h>                                             // WiFi Library
#include "Adafruit_MQTT.h"
#include "Adafruit_MQTT_Client.h"

/************************* WiFi Access Point *********************************/
#define WLAN_SSID             "pd3d_magneto"                   // Wi-Fi SSID
#define WLAN_PASS             "pd3d@ist"                      // Wi-Fi Password
//#define WLAN_SSID             "pd3d"                          // Wi-Fi SSID
//#define WLAN_PASS             "n3w.pas."                      // Wi-Fi Password

/************************* MQTT Server Setup *********************************/
#define MQTT_SERVER           "192.168.42.1"                  // URL to the RPi running MQTT
#define MQTT_SERVERPORT       1883                            // Use 8883 for SSL

/************************* MQTT Topic  Setup *********************************/
#define MQTT_ID               "MAGNETICTRACKING-"             // Identifier to MQTT broker
#define QOS                   1                               // QOS1 == deliver at least once
#define SENSOR01_PUB          "magfield"                      // Topic

String                  ID        = "ID - ";
String                  mqttID( MQTT_ID );

WiFiClient espClient;                                         // Use WiFiClientSecure for SSL

////  Requires: '#include "WifiFunctions.h"' in main program
////  before:   '#include "MqttFunctions.h"'.
Adafruit_MQTT_Client    mqtt( &espClient, MQTT_SERVER, MQTT_SERVERPORT );
Adafruit_MQTT_Publish   devOutput = Adafruit_MQTT_Publish(   &mqtt, SENSOR01_PUB, QOS );


String WiFiErrorCode( int );                                  // Function prototype

// =========================     Setup WiFi     ========================
void setup_WiFi( ) {

  int     cnt       =  0;                                     // Counter for reset

  delay( 10 );                                                // Delay for stability
  Serial.print( "\nConnecting to " );                         // [INFO] ...
  Serial.println( WLAN_SSID );                                // [INFO] ...
  WiFi.disconnect();                                          // NOTE: For some reason we need this
  WiFi.begin( WLAN_SSID, WLAN_PASS );                         // Connect to WiFi

  while ( WiFi.status() != WL_CONNECTED )                     // Wait while we connect
  {
    delay( 500 );
    Serial.print( "." );
    if ( ++cnt % 20 == 0 ) Serial.println();                  // Print new-line every 10sec

    if ( cnt == 40 )                                          // cnt==40 for 20 seconds
    {
      int s = WiFi.status();                                  // Get error message
      Serial.print( "\nTimed out. Resetting!\n" );            // [INFO] ...
      Serial.print( "WiFi status = " );                       // [INFO] ...
      Serial.println( WiFiErrorCode( s ) );                   // [INFO] ...
      WiFi.begin( WLAN_SSID, WLAN_PASS );                     // Re-issue connect to WiFi command
      cnt = 0;                                                // Reset counter
    }

  }
  Serial.print( "\nWiFi connected - ESP IP address: " );
  Serial.println( WiFi.localIP() );
}

// ===================   WiFi Error Codes Translator  ==================
String WiFiErrorCode( int n )
{
  String s = "";
  switch ( n )
  {
    case WL_IDLE_STATUS     : s = "WL_IDLE_STATUS";           //   0
      break;
    case WL_NO_SSID_AVAIL   : s = "WL_NO_SSID_AVAIL";         //   1
      break;
    case WL_SCAN_COMPLETED  : s = "WL_SCAN_COMPLETED";        //   2
      break;
    case WL_CONNECTED       : s = "WL_CONNECTED";             //   3
      break;
    case WL_CONNECT_FAILED  : s = "WL_CONNECT_FAILED";        //   4
      break;
    case WL_CONNECTION_LOST : s = "WL_CONNECTION_LOST";       //   5
      break;
    case WL_DISCONNECTED    : s = "WL_DISCONNECTED";          //   6
      break;
    case WL_NO_SHIELD       : s = "WL_NO_SHIELD";             // 255
      break;
  }
  return s;
}

// ===========================  MQTT Connect  ==========================
// Function to connect and reconnect as necessary;
// ...run from loop()
void MQTT_connect( int blockingTime )
{ 
  int8_t rc;

  if ( mqtt.connected() )                                     // If already connected...
  {
    mqtt.processPackets( blockingTime );
    if ( !mqtt.ping() )
      mqtt.disconnect();
  }
  else
  {
    Serial.println( "Connecting to MQTT..." );

    uint8_t retries = 3;
    while ( (rc = mqtt.connect()) != 0 )                      // connect will return 0 for connected
    {
      Serial.println( mqtt.connectErrorString( rc ) );
      Serial.println( F("Retrying MQTT connection in 5s...") );
      mqtt.disconnect();                                      // Disconnect from MQTT server
      delay( 5000 );                                          // wait 5 seconds
      retries--;                                              // We are one attempt less
      if ( retries == 0 ) while ( true );                     // Basically die and wait for WDT to reset.
    }
    Serial.println( "MQTT Connected." );
    Serial.print( "MQTT ID: " ); Serial.println( mqttID );
  }
}
