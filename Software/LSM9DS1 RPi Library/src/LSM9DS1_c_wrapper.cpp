#include "LSM9DS1_c_wrapper.h"
#include "LSM9DS1.h"

LSM9DS1* create(uint8_t xgAddr, uint8_t mAddr) {
    return new LSM9DS1(IMU_MODE_I2C, xgAddr, mAddr);
}

void begin(LSM9DS1* obj) {
    obj->begin();
}

void calibrate(LSM9DS1* obj) {
    obj->calibrate();
}

void calibrateMag(LSM9DS1* obj) {
    obj->calibrateMag();
}

void setMagScale(LSM9DS1* obj, uint8_t mScl) {
	obj->setMagScale(mScl);
}

int gyroAvailable(LSM9DS1* obj) {
    return obj->gyroAvailable();
}

int accelAvailable(LSM9DS1* obj) {
    return obj->accelAvailable();
}

int magAvailable(LSM9DS1* obj) {
    return obj->magAvailable();
}

void readGyro(LSM9DS1* obj) {
    obj->readGyro();
}

void readAccel(LSM9DS1* obj) {
    obj->readAccel();
}

void readMag(LSM9DS1* obj) {
    obj->readMag();
}

float getGyroX(LSM9DS1* obj) {
    return obj->gx;
}
float getGyroY(LSM9DS1* obj) {
    return obj->gy;
}
float getGyroZ(LSM9DS1* obj) {
    return obj->gz;
}

float getAccelX(LSM9DS1* obj) {
    return obj->ax;
}
float getAccelY(LSM9DS1* obj) {
    return obj->ay;
}
float getAccelZ(LSM9DS1* obj) {
    return obj->az;
}

float getMagX(LSM9DS1* obj) {
    return obj->mx;
}
float getMagY(LSM9DS1* obj) {
    return obj->my;
}
float getMagZ(LSM9DS1* obj) {
    return obj->mz;
}

float calcGyro(LSM9DS1* obj, float gyro) {
    return obj->calcGyro(gyro);
}
float calcAccel(LSM9DS1* obj, float accel) {
    return obj->calcAccel(accel);
}
float calcMag(LSM9DS1* obj, float mag) {
    return obj->calcMag(mag);
}
