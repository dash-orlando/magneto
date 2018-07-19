/*
 * Configure all aspects of the IMU sensor array
 */

// Define sensor address, for the setup.
#define LSM9DS1_M_HIGH                0x1E                    // SDO_M on these IMU's are HIGH
#define LSM9DS1_AG_HIGH               0x6B                    // SDO_AG on these IMU's are HIGH 
#define LSM9DS1_M_LOW                 0x1C                    // SDO_M on these IMU's are LOW
#define LSM9DS1_AG_LOW                0x6B                    // SDO_AG on these IMU's are HIGH [PINS NOT GROUNDED]***

// =========================    Setup IMU       ========================
void setupIMU() {

  // ---------------------------------------- HIGH IMU Setup ---------------------------------------
  
  high.settings.device.commInterface = IMU_MODE_I2C;          //
  high.settings.device.mAddress      = LSM9DS1_M_HIGH;        // Load IMU settings
  high.settings.device.agAddress     = LSM9DS1_AG_HIGH;       //

  high.settings.gyro.enabled         = false;                 // Disable gyro
  high.settings.accel.enabled        = false;                 // Disable accelerometer
  high.settings.mag.enabled          = true;                  // Enable magnetometer
  high.settings.temp.enabled         = true;                  // Enable temperature sensor

  high.settings.mag.scale            = 4;                     // Set mag scale to +/-12 Gs
  high.settings.mag.sampleRate       = 7;                     // Set sampling rate to 80Hz
  high.settings.mag.tempCompensationEnable = true;            // Enable temperature compensation (good stuff!)

  high.settings.mag.XYPerformance    = 3;                     // 0 = Low || 1 = Medium || 2 = High || 3 = Ultra-high
  high.settings.mag.ZPerformance     = 3;                     // Ultra-high performance

  high.settings.mag.lowPowerEnable   = false;                 // Disable low power mode
  high.settings.mag.operatingMode    = 0;                     // 0 = Continuous || 1 = Single || 2 = OFF

  // ---------------------------------------- LOW IMU Setup ----------------------------------------

  low.settings.device.commInterface = IMU_MODE_I2C;           //
  low.settings.device.mAddress      = LSM9DS1_M_LOW;          // Load IMU settings
  low.settings.device.agAddress     = LSM9DS1_AG_LOW;         //

  low.settings.gyro.enabled         = false;                  // Disable gyro
  low.settings.accel.enabled        = false;                  // Disable accelerometer
  low.settings.mag.enabled          = true;                   // Enable magnetometer
  low.settings.temp.enabled         = true;                   // Enable temperature sensor

  low.settings.mag.scale            = 4;                      // Set mag scale to +/-12 Gs
  low.settings.mag.sampleRate       = 7;                      // Set sampling rate to 80Hz
  low.settings.mag.tempCompensationEnable = true;             // Enable temperature compensation (good stuff!)

  low.settings.mag.XYPerformance    = 3;                      // 0 = Low || 1 = Medium || 2 = High || 3 = Ultra-high
  low.settings.mag.ZPerformance     = 3;                      // Ultra-high performance

  low.settings.mag.lowPowerEnable   = false;                  // Disable low power mode
  low.settings.mag.operatingMode    = 0;                      // 0 = Continuous || 1 = Single || 2 = OFF
}
