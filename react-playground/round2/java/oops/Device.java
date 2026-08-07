package com.cisco.iot.oops;

/**
 * ABSTRACT base class.
 *
 * Use an abstract class when related types share STATE and some behavior:
 *   - it holds fields (id, name, status) — an interface can't hold instance state
 *   - it has a constructor
 *   - it mixes CONCRETE methods (describe) with ABSTRACT ones (poll)
 *   - it cannot be instantiated on its own
 */
public abstract class Device {

    private final String id;
    private final String name;
    protected String status = "unknown"; // shared, protected so subclasses can update

    protected Device(String id, String name) {
        this.id = id;
        this.name = name;
    }

    public String getId() { return id; }
    public String getName() { return name; }
    public String getStatus() { return status; }

    // Concrete: shared by every device type.
    public String describe() {
        return name + " (" + id + ") — " + status;
    }

    // Abstract: every concrete device MUST define how it is polled.
    public abstract void poll();
}
