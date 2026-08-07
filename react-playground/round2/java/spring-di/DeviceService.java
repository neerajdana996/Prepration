package com.cisco.iot.device;

import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.List;

/**
 * Business layer. Depends on the DeviceRepository INTERFACE.
 *
 * CONSTRUCTOR INJECTION (the preferred style):
 *   - The dependency is a `final` field, set once in the constructor → immutable,
 *     obviously required, and trivial to unit-test (just pass a mock in `new`).
 *   - With a single constructor, Spring 4.3+ injects it WITHOUT needing @Autowired.
 *   - Prefer this over field injection (@Autowired on a field), which hides
 *     dependencies and can't be made final.
 */
@Service
public class DeviceService {

    private final DeviceRepository repository;

    public DeviceService(DeviceRepository repository) {
        this.repository = repository;
    }

    public List<Device> listDevices() {
        return repository.findAll();
    }

    public Device getDevice(String id) {
        return repository.findById(id)
                .orElseThrow(() -> new DeviceNotFoundException(id));
    }

    /**
     * @Transactional: run inside a DB transaction. If the method throws a runtime
     * exception, Spring rolls the whole thing back — so partial writes never persist.
     */
    @Transactional
    public Device reboot(String id) {
        Device device = getDevice(id);
        device.setStatus("rebooting");
        return repository.save(device);
    }
}
