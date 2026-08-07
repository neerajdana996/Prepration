package com.cisco.iot.device;

import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.List;

/**
 * REST layer.
 *
 * @RestController = @Controller + @ResponseBody → every handler returns DATA
 * (serialized to JSON), not a view name. Perfect for a JSON API.
 *
 * It depends on DeviceService, which Spring injects via the constructor — same
 * DI pattern as the service→repository layer. The chain is:
 *   DeviceController → DeviceService → DeviceRepository (InMemoryDeviceRepository)
 * and Spring wires all three beans together at startup.
 */
@RestController
@RequestMapping("/api/devices")
public class DeviceController {

    private final DeviceService service;

    public DeviceController(DeviceService service) {
        this.service = service;
    }

    @GetMapping
    public List<Device> list() {
        return service.listDevices();
    }

    @GetMapping("/{id}")
    public ResponseEntity<Device> get(@PathVariable String id) {
        // ResponseEntity lets you control status + headers + body.
        return ResponseEntity.ok(service.getDevice(id));
    }

    @PostMapping("/{id}/reboot")
    public ResponseEntity<Device> reboot(@PathVariable String id) {
        return ResponseEntity.ok(service.reboot(id));
    }
}
