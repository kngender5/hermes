/**
 * Self-Balancing Robot — ESP32-S3 Firmware Template
 * ===================================================
 * PlatformIO project. Adapt pin definitions and parameters for your robot.
 * 
 * Control loop: 200 Hz LQR + complementary filter
 * Telemetry: WiFi UDP broadcast at 50 Hz
 * 
 * Build: pio run
 * Upload: pio run --target upload
 * Monitor: pio device monitor -b 115200
 */

#include <Arduino.h>
#include <SPI.h>
#include <WiFi.h>
#include <WiFiUdp.h>

// ─── Pin Definitions ───
#define PIN_SPI_CLK       1
#define PIN_SPI_MOSI      2
#define PIN_SPI_MISO      3
#define PIN_CS_IMU        4
#define PIN_CS_ENCODER    8
#define PIN_CAN_TX        9
#define PIN_CAN_RX        10
#define PIN_PWM_SERVO     17
#define PIN_ESTOP         18
#define PIN_STATUS_LED    19
#define PIN_BUZZER        20
#define PIN_BTN_USER      35
#define PIN_VBAT_ADC      15

// ─── Physical Parameters ───
constexpr float MASS_BODY    = 8.0f;
constexpr float MASS_WHEEL   = 2.0f;
constexpr float CG_HEIGHT    = 0.25f;
constexpr float WHEEL_RADIUS = 0.203f;
constexpr float GRAVITY      = 9.81f;
constexpr float TAU_MAX      = 15.0f;
constexpr float DT           = 0.005f;

// ─── LQR Gains (from simulation) ───
constexpr float K[4] = {245.91f, 66.36f, 10.00f, 17.49f};

// ─── State ───
struct State {
    float theta, theta_dot, phi, phi_dot;
};

struct ControlOutput {
    float motor_torque;
    bool motor_enabled;
    bool alarm;
};

State state = {0};
ControlOutput control = {0};

// Complementary filter
float theta_hat = 0.0f;
float gyro_bias = 0.0f;
constexpr float CF_ALPHA = 0.98f;

// Timing
uint32_t last_control_us = 0;
constexpr uint32_t CONTROL_PERIOD_US = 5000;  // 200 Hz

// State machine
enum class RobotState { BOOT, SELF_TEST, BALANCING, FALL_DETECTED, EMERGENCY_STOP };
RobotState robot_state = RobotState::BOOT;

// ─── IMU Driver (ICM-42688-P) ───
class IMU {
    SPIClass& spi;
    uint8_t cs_pin;
public:
    IMU(SPIClass& spi_bus, uint8_t cs) : spi(spi_bus), cs_pin(cs) {}
    
    bool init() {
        pinMode(cs_pin, OUTPUT);
        digitalWrite(cs_pin, HIGH);
        uint8_t whoami = read_reg(0x75);
        if (whoami != 0x47) return false;
        write_reg(0x50, 0x06);  // ACCEL_CONFIG0: ±4g, 1kHz
        write_reg(0x4F, 0x06);  // GYRO_CONFIG0: ±1000°/s, 1kHz
        write_reg(0x53, 0x02);  // PWR_MGMT0: accel + gyro LN mode
        delay(10);
        return true;
    }
    
    void read(float& ax, float& ay, float& az, float& gx, float& gy, float& gz) {
        uint8_t buf[12];
        read_burst(0x1F, buf, 12);
        int16_t raw_ax = (buf[0] << 8) | buf[1];
        int16_t raw_ay = (buf[2] << 8) | buf[3];
        int16_t raw_az = (buf[4] << 8) | buf[5];
        int16_t raw_gx = (buf[6] << 8) | buf[7];
        int16_t raw_gy = (buf[8] << 8) | buf[9];
        int16_t raw_gz = (buf[10] << 8) | buf[11];
        constexpr float AS = 4.0f * 9.81f / 32768.0f;
        constexpr float GS = 1000.0f * DEG_TO_RAD / 32768.0f;
        ax = raw_ax * AS; ay = raw_ay * AS; az = raw_az * AS;
        gx = raw_gx * GS; gy = raw_gy * GS; gz = raw_gz * GS;
    }
    
private:
    uint8_t read_reg(uint8_t reg) {
        digitalWrite(cs_pin, LOW);
        spi.transfer(reg | 0x80);
        uint8_t val = spi.transfer(0x00);
        digitalWrite(cs_pin, HIGH);
        return val;
    }
    void write_reg(uint8_t reg, uint8_t val) {
        digitalWrite(cs_pin, LOW);
        spi.transfer(reg & 0x7F);
        spi.transfer(val);
        digitalWrite(cs_pin, HIGH);
    }
    void read_burst(uint8_t reg, uint8_t* buf, uint8_t len) {
        digitalWrite(cs_pin, LOW);
        spi.transfer(reg | 0x80);
        for (int i = 0; i < len; i++) buf[i] = spi.transfer(0x00);
        digitalWrite(cs_pin, HIGH);
    }
};

// ─── Encoder Driver (AS5047P) ───
class Encoder {
    SPIClass& spi;
    uint8_t cs_pin;
    float angle_offset = 0.0f;
    bool first_read = true;
public:
    Encoder(SPIClass& spi_bus, uint8_t cs) : spi(spi_bus), cs_pin(cs) {}
    
    bool init() {
        pinMode(cs_pin, OUTPUT);
        digitalWrite(cs_pin, HIGH);
        float a;
        if (read_angle(a)) { angle_offset = a; return true; }
        return false;
    }
    
    bool read_angle(float& angle) {
        uint16_t raw = read_reg(0x3FFF);
        if (raw & 0x4000) return false;
        angle = ((raw & 0x3FFF) / 16384.0f) * 2.0f * PI;
        if (first_read) { angle_offset = angle; first_read = false; }
        angle -= angle_offset;
        while (angle > PI) angle -= 2.0f * PI;
        while (angle < -PI) angle += 2.0f * PI;
        return true;
    }
    
private:
    uint16_t read_reg(uint16_t reg) {
        digitalWrite(cs_pin, LOW);
        uint8_t cmd[2] = {(uint8_t)(reg >> 8), (uint8_t)(reg & 0xFF)};
        uint8_t resp[2];
        spi.transferBytes(cmd, resp, 2);
        digitalWrite(cs_pin, HIGH);
        return (resp[0] << 8) | resp[1];
    }
};

// ─── LQR Controller ───
float lqr_compute(const State& s) {
    float u = -(K[0]*s.theta + K[1]*s.theta_dot + K[2]*s.phi + K[3]*s.phi_dot);
    return constrain(u, -TAU_MAX, TAU_MAX);
}

// ─── Global Objects ───
IMU imu(SPI, PIN_CS_IMU);
Encoder encoder(SPI, PIN_CS_ENCODER);

void setup() {
    Serial.begin(115200);
    delay(1000);
    Serial.println("Self-Balancing Robot — ESP32-S3");
    
    pinMode(PIN_STATUS_LED, OUTPUT);
    pinMode(PIN_ESTOP, INPUT_PULLUP);
    pinMode(PIN_BTN_USER, INPUT_PULLUP);
    analogReadResolution(12);
    analogSetAttenuation(ADC_11db);
    
    SPI.begin(PIN_SPI_CLK, PIN_SPI_MISO, PIN_SPI_MOSI);
    
    if (!imu.init()) { Serial.println("IMU FAIL"); while(1) delay(100); }
    if (!encoder.init()) { Serial.println("ENCODER FAIL"); while(1) delay(100); }
    
    Serial.println("Ready. Press button to start.");
    robot_state = RobotState::SELF_TEST;
    last_control_us = micros();
}

void loop() {
    uint32_t now = micros();
    
    // Emergency stop
    if (digitalRead(PIN_ESTOP) == LOW) {
        robot_state = RobotState::EMERGENCY_STOP;
        control.motor_enabled = false;
        digitalWrite(PIN_STATUS_LED, (millis() / 100) % 2);
        return;
    }
    
    // Control loop (200 Hz)
    if (now - last_control_us >= CONTROL_PERIOD_US) {
        last_control_us = now;
        
        // Read sensors
        float ax, ay, az, gx, gy, gz;
        imu.read(ax, ay, az, gx, gy, gz);
        
        float enc_angle;
        encoder.read_angle(enc_angle);
        
        // Complementary filter
        float accel_theta = atan2(-ax, sqrt(ay*ay + az*az));
        theta_hat = CF_ALPHA * (theta_hat + (gy - gyro_bias) * DT) + (1-CF_ALPHA) * accel_theta;
        if (abs(theta_hat) < 0.1f) gyro_bias += 0.001f * (accel_theta - theta_hat);
        
        // Estimate wheel velocity
        static float prev_phi = 0;
        static bool first = true;
        float phi_dot;
        if (first) { phi_dot = 0; prev_phi = enc_angle; first = false; }
        else {
            float d = enc_angle - prev_phi;
            if (d > PI) d -= 2*PI;
            if (d < -PI) d += 2*PI;
            phi_dot = d / DT;
            prev_phi = enc_angle;
        }
        
        state.theta = theta_hat;
        state.theta_dot = gy - gyro_bias;
        state.phi = enc_angle;
        state.phi_dot = phi_dot;
        
        // State machine
        switch (robot_state) {
            case RobotState::SELF_TEST:
                if (digitalRead(PIN_BTN_USER) == LOW) {
                    robot_state = RobotState::BALANCING;
                    control.motor_enabled = true;
                }
                break;
                
            case RobotState::BALANCING: {
                float tau = lqr_compute(state);
                // motor.set_torque(tau);  // implement with your motor driver
                control.motor_torque = tau;
                
                if (abs(state.theta) > 0.52f) {  // >30 deg
                    robot_state = RobotState::FALL_DETECTED;
                    control.motor_enabled = false;
                }
                break;
            }
                
            case RobotState::FALL_DETECTED:
                control.motor_enabled = false;
                if (abs(state.theta) < 0.05f && digitalRead(PIN_BTN_USER) == LOW) {
                    robot_state = RobotState::BALANCING;
                    control.motor_enabled = true;
                }
                break;
                
            case RobotState::EMERGENCY_STOP:
                control.motor_enabled = false;
                if (digitalRead(PIN_ESTOP) == HIGH && digitalRead(PIN_BTN_USER) == LOW) {
                    robot_state = RobotState::SELF_TEST;
                }
                break;
        }
        
        // Status LED
        digitalWrite(PIN_STATUS_LED, robot_state == RobotState::BALANCING ? HIGH : (millis()/500)%2);
    }
}
