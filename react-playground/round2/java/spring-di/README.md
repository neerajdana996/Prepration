# Spring MVC + Dependency Injection

A realistic 3-layer REST slice for managing IoT devices:

```
HTTP → DeviceController (@RestController)   ← returns JSON
          → DeviceService (@Service)        ← business logic, @Transactional
             → DeviceRepository (interface) ← data-access contract
                └ InMemoryDeviceRepository (@Repository)  ← the concrete bean
```

## What DI / IoC actually is
- **IoC (Inversion of Control):** *you don't create your dependencies* — the framework does. You declare "I need a `DeviceRepository`" and Spring hands you one.
- **DI (Dependency Injection):** the *mechanism* — Spring passes beans into your constructor.
- **Why it matters:** each class depends on an **interface**, not a concrete class → swap `InMemoryDeviceRepository` for a `JpaDeviceRepository` and nothing else changes; and tests just pass a mock into the constructor. Loose coupling + testability.

## Key annotations
| Annotation | Role |
|---|---|
| `@RestController` | `@Controller` + `@ResponseBody` → methods return JSON data |
| `@Service` | business-logic bean |
| `@Repository` | data-access bean |
| `@RequestMapping` / `@GetMapping` / `@PostMapping` | route mapping |
| `@PathVariable` | bind a URL segment to a parameter |
| `@Transactional` | run in a transaction; roll back on runtime exception |

## Constructor injection > field injection
```java
private final DeviceRepository repository;              // final, required, testable
public DeviceService(DeviceRepository repository) { ... } // no @Autowired needed (single ctor)
```
Field injection (`@Autowired` on a field) hides dependencies and can't be `final` — avoid it.

## Clean error handling (mention this)
```java
@RestControllerAdvice
public class GlobalExceptionHandler {
    @ExceptionHandler(DeviceNotFoundException.class)
    @ResponseStatus(HttpStatus.NOT_FOUND)
    public String handle(DeviceNotFoundException ex) { return ex.getMessage(); }
}
```
Centralizes error→HTTP mapping so controllers stay thin.

**Soundbite:** *"Each layer depends on an interface and Spring injects the implementation via the constructor — that's IoC/DI: loose coupling and easy testing. `@RestController` returns JSON, `@Transactional` gives me atomic writes, and a `@RestControllerAdvice` centralizes error handling."*
