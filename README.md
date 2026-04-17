# WebTRIS API Client

A Python project for retrieving and analyzing UK National Highways traffic data using the WebTRIS API. This application fetches daily traffic observations for a selected site, parses the API response into Python objects, and provides summary statistics such as average speed, total traffic volume, hourly records, and peak hour analysis. The repository currently includes `webtris_client.py`, `main.py`, and `test_webtris_client.py`. 

## Features

- Connects to the **WebTRIS API** through a dedicated client class
- Parses raw API rows into structured `TrafficObservation` objects
- Stores site-level daily data in a `Trafficsite` class
- Calculates:
  - average traffic speed
  - total traffic volume
  - records for a specific hour
  - average speed for a given hour
  - total volume for a given hour
  - peak traffic hour
- Includes automated tests using `pytest` and mocked API responses
- Handles API errors such as timeouts, HTTP errors, and missing response data. :contentReference[oaicite:1]{index=1}

## Project Structure

```bash
WebTRIS-API-Client/
├── main.py
├── webtris_client.py
└── test_webtris_client.py
