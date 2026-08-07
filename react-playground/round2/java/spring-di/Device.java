package com.cisco.iot.device;

/**
 * Plain domain model. In a real app this could be a JPA @Entity.
 * Kept simple so the DI wiring is the focus.
 */
public class Device {
    private final String id;
    private String name;
    private String status; // "online" | "offline" | "degraded" | "rebooting"

    public Device(String id, String name, String status) {
        this.id = id;
        this.name = name;
        this.status = status;
    }

    public String getId() { return id; }
    public String getName() { return name; }
    public String getStatus() { return status; }
    public void setStatus(String status) { this.status = status; }
}
