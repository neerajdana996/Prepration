package com.cisco.iot.oops;

/**
 * A CAPABILITY interface. Not every device can reboot (a passive sensor can't),
 * so we keep it separate — Interface Segregation: clients depend only on what they use.
 */
public interface Rebootable {
    void reboot();
}
