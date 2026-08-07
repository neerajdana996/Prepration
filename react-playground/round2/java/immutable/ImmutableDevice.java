package com.cisco.iot.immutable;

import java.util.ArrayList;
import java.util.Collections;
import java.util.List;
import java.util.Objects;

/**
 * A proper immutable value object.
 *
 * The five ingredients:
 *   1. `final` class          → nobody can subclass and add mutable state
 *   2. all fields `private final`
 *   3. no setters
 *   4. set everything in the constructor
 *   5. DEFENSIVE-COPY mutable fields (a List is mutable) both IN and OUT
 *
 * Result: the object's state can never change after construction → inherently
 * thread-safe, and safe to use as a Map/Set key.
 */
public final class ImmutableDevice {

    private final String id;
    private final String name;
    private final List<String> tags; // List is mutable → must be defended

    public ImmutableDevice(String id, String name, List<String> tags) {
        this.id = id;
        this.name = name;
        // defensive copy IN: if we stored the caller's list directly, they could
        // keep a reference and mutate our internals later.
        this.tags = new ArrayList<>(tags == null ? List.of() : tags);
    }

    public String getId() { return id; }
    public String getName() { return name; }

    // defensive copy / unmodifiable view OUT: caller can't mutate our internal list
    public List<String> getTags() {
        return Collections.unmodifiableList(tags);
    }

    /**
     * "Wither": to "change" an immutable object you return a NEW instance.
     * The original is never touched.
     */
    public ImmutableDevice withName(String newName) {
        return new ImmutableDevice(this.id, newName, this.tags);
    }

    // Value equality + the hashCode/equals contract (equal objects → equal hashCodes)
    @Override
    public boolean equals(Object o) {
        if (this == o) return true;
        if (!(o instanceof ImmutableDevice other)) return false;
        return id.equals(other.id) && name.equals(other.name) && tags.equals(other.tags);
    }

    @Override
    public int hashCode() {
        return Objects.hash(id, name, tags);
    }

    @Override
    public String toString() {
        return "ImmutableDevice{id=" + id + ", name=" + name + ", tags=" + tags + "}";
    }
}
