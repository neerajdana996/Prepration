package com.cisco.iot.oops;

import java.util.List;

/**
 * Shows polymorphism + programming to interfaces.
 */
public class Demo {
    public static void main(String[] args) {
        // A heterogeneous fleet held as the ABSTRACT type.
        List<Device> fleet = List.of(
                new Router("R1", "core-router", "16.9.1"),
                new Sensor("S1", "temp-sensor", "C")
        );

        for (Device d : fleet) {
            d.poll();                          // POLYMORPHISM: each type's own poll() runs
            System.out.println(d.describe());  // concrete method from the base class

            // Act on CAPABILITIES via interfaces, not concrete types:
            if (d instanceof Monitorable m) {
                System.out.println("  healthy? " + m.isHealthy());   // default method
            }
            if (d instanceof Rebootable r) {   // only the Router qualifies
                r.reboot();
                System.out.println("  rebooted → " + d.getStatus());
            }
        }
    }
}
