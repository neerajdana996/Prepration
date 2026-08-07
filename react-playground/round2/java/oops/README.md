# OOP — abstract class + multiple interfaces + polymorphism

A realistic IoT-device model (not `Animal`/`Shape`):

```
abstract Device  (id, name, status; concrete describe(); abstract poll())
   ├─ Router  extends Device  implements Monitorable, Rebootable, FirmwareUpgradable
   └─ Sensor  extends Device  implements Monitorable
```

## The four OOP pillars, shown here
- **Abstraction** — `Device` defines *what* a device does (`poll()`) without the *how*.
- **Encapsulation** — fields are private/protected with accessors; state isn't exposed raw.
- **Inheritance** — `Router`/`Sensor` reuse `Device`'s state + `describe()`.
- **Polymorphism** — a `List<Device>` where each element's own `poll()` runs (runtime dispatch).

## Abstract class vs interface (the interview question)
| | Abstract class | Interface |
|---|---|---|
| State (fields) | ✅ yes | ❌ no instance state |
| Constructor | ✅ | ❌ |
| Inherit how many | **one** | **many** |
| Use for | related types sharing code + state ("is-a") | a capability many (even unrelated) types provide ("can-do") |

## Multiple interfaces + Interface Segregation
- `Router` opts into **three** capabilities (`Monitorable`, `Rebootable`, `FirmwareUpgradable`).
- `Sensor` opts into **only** `Monitorable` — a sensor can't reboot or take firmware, so it doesn't implement those. Clients depend only on what they use.
- `Monitorable.isHealthy()` is a **default method** — shared behavior with no state.

## Program to the interface, not the class
`Demo` checks `instanceof Monitorable` / `Rebootable` — it acts on **capabilities**, so new device types just implement the relevant interfaces and everything keeps working.

**Soundbite:** *"Abstract class for shared state + common code (single inheritance); interfaces for capabilities a type can opt into (many). Router implements three, Sensor only one — interface segregation — and I program to the interface so polymorphism and new device types just work."*
