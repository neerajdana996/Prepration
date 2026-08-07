# Functional interfaces

See [`FunctionalDemo.java`](FunctionalDemo.java).

A **functional interface** = an interface with exactly **one abstract method**, so it can be implemented by a **lambda** or a **method reference**. `@FunctionalInterface` makes the compiler enforce the single-method rule.

## The four you must know
| Interface | Shape | Use |
|---|---|---|
| `Predicate<T>` | `T -> boolean` | test / **filter** |
| `Function<T,R>` | `T -> R` | transform / **map** |
| `Consumer<T>` | `T -> void` | side effect / **forEach** |
| `Supplier<T>` | `() -> T` | produce / lazy default |

Also handy: `BiFunction<T,U,R>`, `UnaryOperator<T>` (a `Function<T,T>`), `BinaryOperator<T>`.

## Extras shown
- **Method references** — `System.out::println`, `String::toUpperCase`, `alerter::alert`.
- **Composition** — `f.andThen(g)` (run f, then g) and `f.compose(g)` (run g, then f).
- **Custom `@FunctionalInterface`** — `DeviceAlerter` implemented by a lambda.

**Soundbite:** *"A functional interface has one abstract method, so a lambda satisfies it. I use Predicate to filter, Function to map, Consumer for side effects, Supplier for lazy values — composed in a stream pipeline, with method references where they read cleaner."*
