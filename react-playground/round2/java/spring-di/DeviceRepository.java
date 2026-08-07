package com.cisco.iot.device;

import java.util.List;
import java.util.Optional;

/**
 * The data-access CONTRACT (an interface).
 *
 * DeviceService depends on THIS interface — not on any concrete class — so the
 * implementation (JPA, in-memory, a mock in tests) can be swapped without
 * touching the service. That "depend on abstractions" is the heart of DI/IoC.
 */
public interface DeviceRepository {
    List<Device> findAll();
    Optional<Device> findById(String id);
    Device save(Device device);
}
