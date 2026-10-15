import ee

# 1. Initialize Earth Engine (Replace with your actual GCP project ID)
ee.Initialize(project='your-gcp-project-id')

# 2. Define Region of Interest (e.g., Islamabad, Pakistan bounding box or point)
# Here we create a small region around Islamabad
pakistan_region = ee.Geometry.Rectangle([73.00, 33.60, 73.15, 33.75])

# 3. Load ECMWF ERA5 Daily Aggregates Dataset
# This dataset provides daily aggregates for temperature, precipitation, and wind
era5_collection = (
    ee.ImageCollection('ECMWF/ERA5/DAILY')
    .filterBounds(pakistan_region)
    .filterDate('2025-07-01', '2025-08-01')  # Example peak monsoon window
    .select(
        [
            'mean_2m_air_temperature',
            'total_precipitation',
            'u_component_of_wind_10m',
            'v_component_of_wind_10m',
        ]
    )
)

print(
    f'Total daily records retrieved: {era5_collection.size().getInfo()} days'
)


# 4. Define a function to process values (e.g., convert temperature Kelvin to Celsius)
def process_climate_data(image):
  # Extract bands
  temp_k = image.select('mean_2m_air_temperature')
  temp_c = temp_k.subtract(273.15).rename('temp_celsius')

  precip_m = image.select('total_precipitation')
  # Convert precipitation from meters to millimeters (mm)
  precip_mm = precip_m.multiply(1000.0).rename('precip_mm')

  u_wind = image.select('u_component_of_wind_10m')
  v_wind = image.select('v_component_of_wind_10m')

  # Calculate horizontal wind speed (m/s) using Pythagorean theorem
  wind_speed = u_wind.hypot(v_wind).rename('wind_speed_ms')

  return image.addBands([temp_c, precip_mm, wind_speed]).copyProperties(
      image, ['system:time_start']
  )


processed_collection = era5_collection.map(process_climate_data)

# 5. Compute regional means across the Islamabad bounding box for the first day in the collection
sample_day = ee.Image(processed_collection.first())
stats = sample_day.reduceRegion(
    reducer=ee.Reducer.mean(),
    geometry=pakistan_region,
    scale=27830,  # ERA5 native resolution (~28km grid)
    maxPixels=1e9,
).getInfo()

print('\n--- Sample Daily Climate Metrics for Islamabad Region ---')
print(f"Mean Temperature (°C): {stats.get('temp_celsius', 0):.2f}")
print(f"Total Precipitation (mm): {stats.get('precip_mm', 0):.2f}")
print(f"Mean Wind Speed (m/s): {stats.get('wind_speed_ms', 0):.2f}")