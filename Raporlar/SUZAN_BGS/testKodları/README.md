# Energy Pricing Anomaly Test (OCPP-oriented)

This repository contains a minimal test environment to simulate **frequent & irregular energy pricing changes**
and generate reproducible logs for reporting.

## Structure
- `src/` : simulator code
- `logs/` : generated log file
- `report/` : test environment + scenario + results docs

## Run
```bash
cd src
python anomaly_simulator.py
