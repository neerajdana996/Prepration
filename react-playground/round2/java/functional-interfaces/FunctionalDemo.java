package com.cisco.iot.functional;

import java.util.List;
import java.util.function.*;
import java.util.stream.Collectors;

/**
 * The four built-in functional interfaces + a custom one, used the way you
 * actually use them: composing a stream pipeline over a list of devices.
 */
public class FunctionalDemo {

    // A CUSTOM functional interface: exactly ONE abstract method.
    // @FunctionalInterface makes the compiler enforce that (and documents intent).
    @FunctionalInterface
    interface DeviceAlerter {
        String alert(Device device);
    }

    record Device(String id, String name, String status, int cpu) {}

    public static void main(String[] args) {
        List<Device> devices = List.of(
                new Device("R1", "core-router", "online",   82),
                new Device("R2", "edge-gw",     "offline",   0),
                new Device("R3", "temp-sensor", "degraded", 55)
        );

        // Predicate<T>  : T -> boolean   (a test → filter)
        Predicate<Device> isUnhealthy = d -> !d.status().equals("online");

        // Function<T,R> : T -> R         (a transform → map)
        Function<Device, String> toSummary = d -> d.name() + " [" + d.status() + "]";

        // Consumer<T>   : T -> void      (a side effect → forEach)
        Consumer<String> log = System.out::println;               // method reference

        // Supplier<T>   : () -> T        (produce a value lazily → default)
        Supplier<String> noneMsg = () -> "all devices healthy";

        // Custom functional interface
        DeviceAlerter alerter = d -> "ALERT " + d.name() + " cpu=" + d.cpu() + "%";

        // Compose them: filter (Predicate) → map (Function) → collect
        List<String> unhealthy = devices.stream()
                .filter(isUnhealthy)
                .map(toSummary)
                .collect(Collectors.toList());

        if (unhealthy.isEmpty()) log.accept(noneMsg.get());        // Supplier
        else unhealthy.forEach(log);                               // Consumer

        // custom FI + method reference in a pipeline
        devices.stream()
                .filter(d -> d.cpu() > 80)
                .map(alerter::alert)
                .forEach(log);

        // Function composition: andThen / compose
        Function<Device, String> summaryUpper = toSummary.andThen(String::toUpperCase);
        log.accept(summaryUpper.apply(devices.get(0)));            // CORE-ROUTER [ONLINE]

        // BiFunction<T,U,R> : (T,U) -> R
        BiFunction<Device, String, String> tag = (d, t) -> d.name() + "#" + t;
        log.accept(tag.apply(devices.get(0), "prod"));
    }
}
