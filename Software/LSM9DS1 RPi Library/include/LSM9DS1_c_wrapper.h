#ifndef __SparkFunLSM9DS1_C_WRAPPER_H__
#define __SparkFunLSM9DS1_C_WRAPPER_H__

#include "LSM9DS1.h"

extern "C" {
    LSM9DS1* create(uint8_t xgAddr, uint8_t mAddr);
    void begin(LSM9DS1* obj);
    void calibrate(LSM9DS1* obj);
    void calibrateMag(LSM9DS1* obj);
    void setMagScale(LSM9DS1* obj, uint8_t mScl);
    // Chack imu
    int gyroAvailable(LSM9DS1* obj);
    int accelAvailable(LSM9DS1* obj);
    int magAvailable(LSM9DS1* obj);
    // Read data
    void readGyro(LSM9DS1* obj);
    void readAccel(LSM9DS1* obj);
    void readMag(LSM9DS1* obj);
    // Get data
    float getGyroX(LSM9DS1* obj);
    float getGyroY(LSM9DS1* obj);
    float getGyroZ(LSM9DS1* obj);
    float getAccelX(LSM9DS1* obj);
    float getAccelY(LSM9DS1* obj);
    float getAccelZ(LSM9DS1* obj);
    float getMagX(LSM9DS1* obj);
    float getMagY(LSM9DS1* obj);
    float getMagZ(LSM9DS1* obj);
    // Compute data
    float calcGyro(LSM9DS1* obj, float gyro);
    float calcAccel(LSM9DS1* obj, float accel);
    float calcMag(LSM9DS1* obj, float mag);
}

#endif /* __SparkFunLSM9DS1_C_WRAPPER_H__ */
