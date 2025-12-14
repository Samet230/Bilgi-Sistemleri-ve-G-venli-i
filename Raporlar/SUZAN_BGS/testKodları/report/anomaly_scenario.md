# Anomaly Scenario: Frequent & Irregular Energy Pricing Changes

## Description
This scenario simulates manipulations in energy pricing where the tariff changes frequently and irregularly
without expected grid events or peak-hour justification.

## Injected Values
- Rapid changes: 0.20 → 0.85 → 0.18 → 0.95
- Invalid values: -0.30 (negative), 5.50 (extremely high)

## Expected Impact (Security/Business)
- Incorrect billing / financial manipulation risk
- Loss of trust and potential regulatory issues

## Expected System Reaction
- Generate warnings in logs for out-of-bounds values
- Provide a clear summary of detected anomalies
