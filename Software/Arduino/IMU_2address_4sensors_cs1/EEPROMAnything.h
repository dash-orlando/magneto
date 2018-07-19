#include <EEPROM.h>                                           // Access EEPROM
#include <Arduino.h>                                          // For type definitions

#define EEPROM_SIZE                   1024                    // I'm just guessing EEPROM SIZE here

// Define a struct to store data to
struct config_t
{
  double    sensors_offsets[NSENS][NAXES];
  boolean   Calibrated;
} calibration;

// =========================  Write EEPROM  =========================
template <class T> int EEPROM_writeAnything(int ee, const T& value)
{
    const byte* p = (const byte*)(const void*)&value;
    unsigned int i;
    for (i = 0; i < sizeof(value); i++)
          EEPROM.write(ee++, *p++);
    return i;
}

// =========================  Read  EEPROM  =========================
template <class T> int EEPROM_readAnything(int ee, T& value)
{
    byte* p = (byte*)(void*)&value;
    unsigned int i;
    for (i = 0; i < sizeof(value); i++)
          *p++ = EEPROM.read(ee++);
    return i;
}

// ================  Read  EEPROM & print to Serial  ================
void read_EEPROM()
{
  Serial.println( F("******************************") );

  EEPROM_readAnything( 0, calibration );                      // Read in the data from the EEPROM
  delay(100);                                                 // Pause a little just in case

  /* Print calibration/offset data from the EEPROM */
  Serial.print( F("FORMAT: (offset_X, offset_Y, offset_Z)\n") );
  for ( uint8_t i = 0; i < NSENS; i++ ) {
    for ( uint8_t j = 0; j < NAXES; j++) {
      Serial.print( calibration.sensors_offsets[i][j], 5 );
      Serial.print( ',' );
    } Serial.println();
  }

  Serial.print( F("Calibrated: ") );
  Serial.print( calibration.Calibrated );
  Serial.println();

  Serial.println("******************************");
}
