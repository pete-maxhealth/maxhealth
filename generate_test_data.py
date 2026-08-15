"""
generate_test_data.py — realistic synthetic Garmin export data, matching the
exact schemas confirmed against Pete's real examples (both the wellness JSON
and the activities CSV). Used only to build and validate the merge logic
before the real 24-48hr bulk export arrives — not meant to be mistaken for
real data anywhere downstream.
"""

import json
import csv

# 5 days of synthetic wellness data (unofficial get_user_summary schema —
# the one Pete will actually get from a personal export/script)
wellness_days = [
    {"userProfileId": 111, "calendarDate": "2026-07-05", "steps": 8420, "distanceInMeters": 6540.0,
     "activeCalories": 410, "bmrCalories": 1850, "totalCalories": 2260,
     "minHeartRate": 52, "maxHeartRate": 158, "restingHeartRate": 55,
     "moderateIntensityDurationInSeconds": 2100, "vigorousIntensityDurationInSeconds": 900,
     "averageStressLevel": 30, "maxStressLevel": 80, "floorsClimbed": 6},
    {"userProfileId": 111, "calendarDate": "2026-07-06", "steps": 5200, "distanceInMeters": 3900.0,
     "activeCalories": 180, "bmrCalories": 1850, "totalCalories": 2030,
     "minHeartRate": 53, "maxHeartRate": 140, "restingHeartRate": 54,
     "moderateIntensityDurationInSeconds": 600, "vigorousIntensityDurationInSeconds": 0,
     "averageStressLevel": 25, "maxStressLevel": 65, "floorsClimbed": 3},
    {"userProfileId": 111, "calendarDate": "2026-07-07", "steps": 12100, "distanceInMeters": 9200.0,
     "activeCalories": 640, "bmrCalories": 1850, "totalCalories": 2490,
     "minHeartRate": 50, "maxHeartRate": 174, "restingHeartRate": 53,
     "moderateIntensityDurationInSeconds": 1800, "vigorousIntensityDurationInSeconds": 1500,
     "averageStressLevel": 28, "maxStressLevel": 88, "floorsClimbed": 10},
    {"userProfileId": 111, "calendarDate": "2026-07-08", "steps": 6800, "distanceInMeters": 5100.0,
     "activeCalories": 220, "bmrCalories": 1850, "totalCalories": 2070,
     "minHeartRate": 52, "maxHeartRate": 145, "restingHeartRate": 54,
     "moderateIntensityDurationInSeconds": 900, "vigorousIntensityDurationInSeconds": 0,
     "averageStressLevel": 32, "maxStressLevel": 70, "floorsClimbed": 4},
    {"userProfileId": 111, "calendarDate": "2026-07-09", "steps": 9600, "distanceInMeters": 7300.0,
     "activeCalories": 520, "bmrCalories": 1850, "totalCalories": 2370,
     "minHeartRate": 51, "maxHeartRate": 158, "restingHeartRate": 52,
     "moderateIntensityDurationInSeconds": 1500, "vigorousIntensityDurationInSeconds": 600,
     "averageStressLevel": 27, "maxStressLevel": 82, "floorsClimbed": 8},
]

with open('test_garmin_wellness.json', 'w') as f:
    json.dump(wellness_days, f, indent=2)

# 3 days with a real recorded activity — matching Pete's actual CSV format,
# including his exact column set and a realistic date spread that overlaps
# with the wellness days above, so the merge has real matches to work with.
activities_rows = [
    ["Activity Type","Date","Title","Distance","Calories","Time","Avg HR","Max HR","Avg Pace","Best Pace","Elevation Gain","Elevation Loss","Avg Cadence","Max Cadence","Strokes","Training Effect"],
    ["Running","07-Jul-2026 07:30 AM","Morning 5K Run","5.02","320","00:24:15","152","174","04:50","04:15","45","42","162","175","","3.2"],
    ["Walking","06-Jul-2026 12:10 PM","Lunch Walk","3.10","145","00:38:40","98","112","12:28","10:50","8","8","","","",""],
    ["Cycling","09-Jul-2026 05:45 PM","Evening Ride","18.30","390","00:52:00","128","150","21.1 mph","28.0 mph","95","90","78","88","","2.4"],
]
with open('test_garmin_activities.csv', 'w', newline='') as f:
    writer = csv.writer(f)
    writer.writerows(activities_rows)

print("Generated test_garmin_wellness.json (5 days) and test_garmin_activities.csv (3 activities)")
