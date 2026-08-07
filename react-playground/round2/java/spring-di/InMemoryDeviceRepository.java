package com.cisco.iot.device;

import org.springframework.stereotype.Repository;

import java.util.ArrayList;
import java.util.List;
import java.util.Map;
import java.util.Optional;
import java.util.concurrent.ConcurrentHashMap;

/**
 * A concrete implementation of the repository contract.
 *
 * @Repository marks it as a Spring-managed BEAN. At startup Spring creates ONE
 * instance and, because DeviceService's constructor asks for a DeviceRepository,
 * Spring injects THIS bean automatically. Swap it for a JpaDeviceRepository and
 * nothing else changes — that's the payoff of coding to the interface.
 */
@Repository
public class InMemoryDeviceRepository implements DeviceRepository {

    private final Map<String, Device> store = new ConcurrentHashMap<>();

    @Override
    public List<Device> findAll() {
        return new ArrayList<>(store.values());
    }

    @Override
    public Optional<Device> findById(String id) {
        return Optional.ofNullable(store.get(id));
    }

    @Override
    public Device save(Device device) {
        store.put(device.getId(), device);
        return device;
    }
}
