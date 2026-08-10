WITH station_aoi AS (
  SELECT
    observstation,
    atmostransparency * (1.0 - humidityrate / 100.0) * (1.0 - 0.02 * windspeedms) AS aoi,
    lunarstage,
    lunardistdeg,
    solarstatus,
    CASE
      WHEN atmostransparency * (1.0 - humidityrate / 100.0) * (1.0 - 0.02 * windspeedms) > 0.85
       AND lunarstage IN ('New', 'First Quarter')
       AND lunardistdeg > 45
       AND solarstatus IN ('Low', 'Moderate')
      THEN 1 ELSE 0
    END AS meets_oow
  FROM observatories
)
SELECT
  CASE WHEN meets_oow = 1 THEN TRUE ELSE FALSE END AS meets_oow,
  COUNT(*) AS station_count,
  ROUND(AVG(aoi), 3) AS avg_aoi,
  json_group_array(
    json_object(
      'station', observstation,
      'aoi', ROUND(aoi, 3),
      'lunar_factors', json_object('stage', lunarstage, 'distance', lunardistdeg),
      'solar_status', solarstatus
    )
  ) AS station_details
FROM station_aoi
GROUP BY meets_oow
ORDER BY meets_oow DESC;
