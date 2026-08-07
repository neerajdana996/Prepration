package com.cisco.iot.oops;

/** Another capability — only devices with firmware implement it. */
public interface FirmwareUpgradable {
    void upgradeFirmware(String version);
}
