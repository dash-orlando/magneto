/*
 * Configure all aspects of the IMU sensor array
 */

// Define sensor address, for the setup.
#define LSM9DS1_M_HIGH             	0x1E                    	// SDO_M on these IMU's are HIGH
#define LSM9DS1_AG_HIGH            	0x6B                   		// SDO_AG on these IMU's are HIGH 
#define LSM9DS1_M_LOW              	0x1C                    	// SDO_M on these IMU's are LOW
#define LSM9DS1_AG_LOW             	0x6B                 		// SDO_AG on these IMU's are HIGH [PINS NOT GROUNDED]***

// =========================    Setup IMU       ========================
void setupIMU()
{

  // ---------------------------------------- HIGH IMU Setup ---------------------------------------
  
  imuHI.settings.device.commInterface = IMU_MODE_I2C;          	//
  imuHI.settings.device.mAddress      = LSM9DS1_M_HIGH;        	// Load IMU settings
  imuHI.settings.device.agAddress     = LSM9DS1_AG_HIGH;       	//

  imuHI.settings.gyro.enabled         = false;                 	// Disable gyro
  imuHI.settings.accel.enabled        = false;                 	// Disable accelerometer
  imuHI.settings.mag.enabled          = true;                  	// Enable magnetometer
  imuHI.settings.temp.enabled         = true;                  	// Enable temperature sensor

  imuHI.settings.mag.scale            = 12;                   	// Set mag scale to +/-12 Gs
  imuHI.settings.mag.sampleRate       = 7;                     	// Set sampling rate to 80Hz
  imuHI.settings.mag.tempCompensationEnable = true;            	// Enable temperature compensation (good stuff!)

  imuHI.settings.mag.XYPerformance    = 3;                     	// 0 = Low || 1 = Medium || 2 = High || 3 = Ultra-high
  imuHI.settings.mag.ZPerformance     = 3;                     	// Ultra-high performance

  imuHI.settings.mag.lowPowerEnable   = false;                 	// Disable low power mode
  imuHI.settings.mag.operatingMode    = 0;                     	// 0 = Continuous || 1 = Single || 2 = OFF

  // ---------------------------------------- LOW IMU Setup ----------------------------------------

  imuLO.settings.device.commInterface = IMU_MODE_I2C;           //
  imuLO.settings.device.mAddress      = LSM9DS1_M_LOW;          // Load IMU settings
  imuLO.settings.device.agAddress     = LSM9DS1_AG_LOW;         //

  imuLO.settings.gyro.enabled         = false;                  // Disable gyro
  imuLO.settings.accel.enabled        = false;                  // Disable accelerometer
  imuLO.settings.mag.enabled          = true;                   // Enable magnetometer
  imuLO.settings.temp.enabled         = true;                   // Enable temperature sensor

  imuLO.settings.mag.scale            = 12;                    	// Set mag scale to +/-12 Gs
  imuLO.settings.mag.sampleRate       = 7;                      // Set sampling rate to 80Hz
  imuLO.settings.mag.tempCompensationEnable = true;             // Enable temperature compensation (good stuff!)

  imuLO.settings.mag.XYPerformance    = 3;                      // 0 = Low || 1 = Medium || 2 = High || 3 = Ultra-high
  imuLO.settings.mag.ZPerformance     = 3;                      // Ultra-high performance

  imuLO.settings.mag.lowPowerEnable   = false;                  // Disable low power mode
  imuLO.settings.mag.operatingMode    = 0;                      // 0 = Continuous || 1 = Single || 2 = OFF
}
