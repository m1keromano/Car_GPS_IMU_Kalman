import pandas as pd
import numpy as np
from scipy.io import savemat

# 1. Load the CSVs
accel = pd.read_csv('Ride_2/Accelerometer.csv')
gyro = pd.read_csv('Ride_2/Gyroscope.csv')
mag = pd.read_csv('Ride_2/Magnetometer.csv')
gps = pd.read_csv('Ride_2/Location.csv')

# 2. Select and Rename (Mapping Z,Y,X to X,Y,Z for ISO 8855)
acc = accel[['seconds_elapsed', 'x', 'y', 'z']].rename(columns={'x':'ax', 'y':'ay', 'z':'az'}).sort_values('seconds_elapsed')
gyr = gyro[['seconds_elapsed', 'x', 'y', 'z']].rename(columns={'x':'gx', 'y':'gy', 'z':'gz'}).sort_values('seconds_elapsed')
mag_data = mag[['seconds_elapsed', 'x', 'y', 'z']].rename(columns={'x':'mx', 'y':'my', 'z':'mz'}).sort_values('seconds_elapsed')
gps_data = gps[['seconds_elapsed', 'latitude', 'longitude', 'speed', 'bearing', 'horizontalAccuracy']].sort_values('seconds_elapsed')

# 3. Step-by-Step Merge (The "Inertial Backbone")
# Merge Gyro to Accel
imu = pd.merge_asof(acc, gyr, on='seconds_elapsed', direction='nearest')
# Merge Magnetometer to the IMU stream
imu = pd.merge_asof(imu, mag_data, on='seconds_elapsed', direction='nearest')

# 4. Asynchronous GPS Merge (1Hz into 100Hz)
df = pd.merge_asof(imu, gps_data, on='seconds_elapsed', direction='nearest', tolerance=0.05)

# Decompose GPS Speed into North/East Velocity Vectors
df['v_north'] = df['speed'] * np.cos(np.deg2rad(df['bearing']))
df['v_east'] = df['speed'] * np.sin(np.deg2rad(df['bearing']))

# Convert Lat/Lon to North/East meters (WGS-84 approximation)
R_earth = 6378137.0
lat0 = gps_data['latitude'].iloc[0]
lon0 = gps_data['longitude'].iloc[0]
df['north_meters'] = np.deg2rad(df['latitude'] - lat0) * R_earth
df['east_meters'] = np.deg2rad(df['longitude'] - lon0) * R_earth * np.cos(np.deg2rad(lat0))

# 5. Clear non-GPS rows (Keep it "Truthful")
gps_timestamps = gps_data['seconds_elapsed'].values
mask = df['seconds_elapsed'].apply(lambda x: any(np.isclose(x, gps_timestamps, atol=0.005)))
df.loc[~mask, ['latitude', 'longitude', 'speed', 'bearing', 'v_north', 'v_east', 'horizontalAccuracy', 'north_meters', 'east_meters']] = 0

# 6. Final Export
# Columns: 1:Time, 2-4:Acc, 5-7:Gyro, 8-10:Mag, 11:Lat, 12:Lon, 13:Speed, 14:Bearing, 15:V_North, 16:V_East, 17:HorizAcc, 18:North, 19:East
export_cols = ['seconds_elapsed', 'ax', 'ay', 'az', 'gx', 'gy', 'gz', 
               'mx', 'my', 'mz', 'latitude', 'longitude', 'speed', 'bearing', 'v_north', 'v_east', 'horizontalAccuracy', 'north_meters', 'east_meters']
sim_input = df[export_cols].values.T

savemat('combined_sensor_data.mat', {'ekf_data': sim_input})
df[export_cols].to_csv('combined_sensor_data.csv', index=False)

print("Success! Saved to combined_sensor_data.mat and combined_sensor_data.csv")