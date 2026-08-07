package com.cisco.iot.oops;

import java.util.Map;

/**
 * Concrete class extending the abstract base AND implementing MULTIPLE interfaces.
 * A router is monitorable, rebootable, and firmware-upgradable — so it opts into
 * all three capabilities. (Single class inheritance, but many interfaces.)
 */
public class Router extends Device implements Monitorable, Rebootable, FirmwareUpgradable {

    private String firmware;

    public Router(String id, String name, String firmware) {
        super(id, name);
        this.firmware = firmware;
        this.status = "online";
    }

    @Override
    public void poll() {           // implements the abstract method its own way
        this.status = "online";
    }

    @Override
    public Map<String, Object> metrics() {
        return Map.of("status", status, "firmware", firmware);
    }

    @Override
    public void reboot() {
        this.status = "rebooting";
    }

    @Override
    public void upgradeFirmware(String version) {
        this.firmware = version;
    }
}
