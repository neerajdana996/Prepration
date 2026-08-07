package com.cisco.iot.oops;

import java.util.Map;

/**
 * Another concrete device — but a Sensor implements ONLY Monitorable.
 * It is NOT Rebootable or FirmwareUpgradable, so it doesn't implement them.
 * That's Interface Segregation in action: it only takes the capabilities it has.
 */
public class Sensor extends Device implements Monitorable {

    private final String unit;
    private double reading;

    public Sensor(String id, String name, String unit) {
        super(id, name);
        this.unit = unit;
        this.status = "online";
    }

    @Override
    public void poll() {
        this.reading = 42.0; // a real sensor would read hardware here
    }

    @Override
    public Map<String, Object> metrics() {
        return Map.of("status", status, "reading", reading, "unit", unit);
    }
}
