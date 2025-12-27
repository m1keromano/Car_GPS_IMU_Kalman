# Car_GPS_IMU_Kalman

Recorded telemetry data on iPhone using Sensor Logger App in accordance with ISO 8855

    +X	Forward (correlates with right of screen)
    +Y	Left (correlates with top of screen)
    +Z	Up (correlates with above phone)

Exported this as .zip containing all sensor data

Created .csv and .mat files combining all sensors, and processing data

    Utilized a nearest-neighbor asynchronous merge between GPS (1Hz) and inertial sensors (100Hz)

    Performed calculation to move from raw coordinate GPS data to NED convention






