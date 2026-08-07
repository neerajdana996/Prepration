package com.cisco.iot.device;

/**
 * Domain exception. A @RestControllerAdvice (see README) maps this to HTTP 404
 * so controllers stay clean and don't repeat error handling.
 */
public class DeviceNotFoundException extends RuntimeException {
    public DeviceNotFoundException(String id) {
        super("Device not found: " + id);
    }
}
