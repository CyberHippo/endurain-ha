# Endurain Home Assistant Integration

A custom Home Assistant integration for [Endurain](https://codeberg.org/endurain-project/endurain), a self-hosted fitness tracking application.

## Features

- Last activity details (name, type, distance, duration, heart rate, speed, elevation, calories)
- Weekly and monthly distances by sport (run, bike, swim)
- Body composition metrics (weight, body fat, muscle mass) — requires Garmin Connect sync
- Daily steps — requires Garmin Connect sync
- Sleep metrics (duration, score, resting heart rate) — requires Garmin Connect sync

## Installation

### HACS (recommended)

1. Add this repository as a custom HACS repository (category: **Integration**)
2. Install **Endurain** from HACS
3. Restart Home Assistant

### Manual

Copy `custom_components/endurain/` into your Home Assistant `config/custom_components/` directory and restart.

## Configuration

1. Go to **Settings → Devices & Services → Add integration**
2. Search for **Endurain**
3. Enter your instance URL (e.g. `http://192.168.1.100:8000`), username, and password

## Sensors

| Entity | Description | Unit |
|--------|-------------|------|
| Last activity name | Name of the most recent activity | — |
| Last activity type | Sport type | — |
| Last activity distance | Distance | m |
| Last activity duration | Elapsed time | s |
| Last activity avg. heart rate | Average HR | bpm |
| Last activity avg. speed | Average speed | km/h |
| Last activity elevation gain | Elevation gain | m |
| Last activity calories | Calories burned | kcal |
| Weekly run/bike/swim distance | Distance this week | m |
| Monthly run/bike/swim distance | Distance this month | m |
| Weight | Latest body weight | kg |
| Body fat | Latest body fat | % |
| Muscle mass | Latest muscle mass | kg |
| Steps | Latest daily step count | steps |
| Sleep duration | Total sleep | s |
| Sleep score | Overall sleep score | score |
| Resting heart rate | Resting HR from sleep | bpm |

## Poll interval

Data is refreshed every 5 minutes by default. To override, change `DEFAULT_SCAN_INTERVAL` in `const.py`.
