package com.cisco.iot.oops;

import java.util.Map;

/**
 * A capability interface with a DEFAULT method (Java 8+): shared behavior with
 * no state, so implementers get isHealthy() for free but can override it.
 */
public interface Monitorable {
    Map<String, Object> metrics();

    default boolean isHealthy() {
        return !"offline".equals(String.valueOf(metrics().get("status")));
    }
}
