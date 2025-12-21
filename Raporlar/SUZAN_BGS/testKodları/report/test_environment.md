# Test Environment

## Platform
- Operating System: Ubuntu 22.04 (VM) / Windows host
- Language Runtime: Python 3.x
- Test Output: `logs/pricing_anomaly.log`

## Components
- Charge Point (Simulated): Python script
- Scenario: Energy Pricing Anomaly (Frequent & Irregular Changes)
- Detection Rule: flag prices outside [0.05, 1.50] EUR/kWh or negative values
