# Python concepts reference

## 1 — Variables are labels, not boxes

A variable doesn't _contain_ a value — it _points_ to an object in memory. Two variables can point to the same object.

```python
x = 5
y = x        # both point to the same integer object
id(x) == id(y)  # True
```

---

## 2 — Immutable vs mutable objects

**Immutable** objects (int, float, str, tuple) cannot be changed in place. **Mutable** objects (list, dict, set) can be.

```python
lst = [1, 2, 3]
lst.append(4)   # mutates the same object — id() unchanged

x = 5
x += 1          # creates a NEW object — id() changes
```

---

## 3 — Rebinding vs mutating

`x += 1` on an integer is shorthand for `x = x + 1` — it _rebinds_ the variable to a new object, it does not modify the old one.

```python
x = 5
print(id(x))   # e.g. 140234567
x += 1
print(id(x))   # e.g. 140234599 — different object!
```

---

## 4 — Rebinding doesn't affect other references

When you rebind a variable, any other variable still pointing to the old object is unaffected.

```python
x = 5
y = x       # y points to the same object as x
x += 1      # x is rebound to a new object
print(y)    # still 5 — y was not affected
```

---

## 5 — Function parameters: immutable (int)

Passing an integer creates a local variable pointing to the same object. Rebinding it inside the function doesn't touch the caller's variable.

```python
def increment(n):
    n += 1      # rebinds local n only

x = 5
increment(x)
print(x)        # still 5 — caller unaffected
```

---

## 6 — Function parameters: mutable (list)

Passing a list also points to the same object. But since lists are mutable, _mutating_ it inside the function affects the caller. _Rebinding_ it still does not.

```python
def mutate(lst):
    lst.append(4)   # mutates the shared object — caller sees this!

def rebind(lst):
    lst = [9, 9, 9] # rebinds local lst only — caller unaffected

nums = [1, 2, 3]
mutate(nums)
print(nums)         # [1, 2, 3, 4] — changed!

rebind(nums)
print(nums)         # [1, 2, 3, 4] — unchanged
```

---

## 7 — Generators and `yield`

A generator is a function that uses `yield` to pause and hand a value to the caller. Each `yield` has two jobs:

- **Outbound** — sends a value out to the caller when the generator pauses
- **Inbound** — receives a value in from the caller when the generator resumes

```python
value = yield total
#              ↑              ↑
#        [OUTBOUND]       [INBOUND]
#   sends `total` out   receives whatever
#   to the caller       the next send()/next() passes in
```

---

## 8 — Priming a generator

A freshly created generator hasn't started yet — it hasn't reached its first `yield`. You must call `next()` once first to advance it to the first `yield`. This is called **priming**.

- `next(acc)` is equivalent to `acc.send(None)`
- You cannot call `send(10)` as the very first call — Python raises a `TypeError` because the generator has no `yield` ready to receive the value yet

```python
acc = accumulator()
next(acc)       # primes — runs until first yield, pauses there
acc.send(10)    # resumes — 10 is assigned to value, runs until next yield
```

On the first `next()`, only the **outbound** half of `yield` fires. The **inbound** assignment (`value = ...`) happens on the next `send()` or `next()` call.

---

## 9 — `send()` vs `next()`

`next(acc)` and `acc.send(None)` are identical. The only difference is what value gets sent into the generator:

- `next(acc)` — sends `None` in, which gets assigned to `value`
- `acc.send(10)` — sends `10` in, which gets assigned to `value`

If you call `next()` when the generator has an `if value is None: break` guard, it will trigger the break — not because the generator is exhausted, but because `None` satisfies the condition.

---

## 10 — When does `StopIteration` get raised?

`StopIteration` is raised when the generator function has **no more code to execute** — it has nowhere left to go. This happens when:

```python
# 1. the function falls off the end
def gen():
    yield 1
    yield 2
    # nothing left — next() after this raises StopIteration

# 2. an explicit return statement
def gen():
    yield 1
    return      # raises StopIteration immediately

# 3. a break exits the last loop and the function ends
def gen():
    while True:
        value = yield
        if value is None:
            break
    # function ends here — StopIteration raised
```

`StopIteration` is not really an error — it's Python's signal that the generator is done. It's what `for` loops rely on internally to know when to stop iterating.

---

## 11 — Closing or stopping a generator

There are three ways to stop a generator:

**1. `gen.close()` — explicitly close it from outside**

Throws a `GeneratorExit` exception into the generator, which causes it to stop. Any subsequent `next()` or `send()` call will raise `StopIteration`.

```python
acc = accumulator()
next(acc)
acc.send(10)
acc.close()     # generator is now closed
acc.send(5)     # raises StopIteration
```

**2. `return` inside the generator — stop it from within**

When the generator hits a `return` statement (or a `break` that causes the function to end), it stops and raises `StopIteration` on the caller's end.

```python
def gen():
    while True:
        value = yield
        if value is None:
            return   # stops the generator from inside
```

**3. Abandoning it — let garbage collection handle it**

If you simply let the generator object go out of scope (no more references to it), Python's garbage collector will call `.close()` on it automatically.

```python
def use_generator():
    acc = accumulator()
    next(acc)
    acc.send(10)
    # acc goes out of scope here — Python closes it automatically
```

Of the three, `gen.close()` is the most explicit and is preferred when you need to stop a generator early from outside of it.

---

## 12 — `itertools.groupby()` groups consecutive elements

`groupby()` walks through data and starts a new group every time the key **changes**. It does not collect all elements with the same key from the entire list — it only groups consecutive runs.

```python
import itertools as it

# keys are consecutive — works as expected
data = [("a", 1), ("a", 2), ("b", 3)]
for key, group in it.groupby(data, key=lambda x: x[0]):
    print(key, list(group))
# a [('a', 1), ('a', 2)]
# b [('b', 3)]

# keys are NOT consecutive — "a" gets split into two groups
data = [("a", 1), ("b", 2), ("a", 3)]
for key, group in it.groupby(data, key=lambda x: x[0]):
    print(key, list(group))
# a [('a', 1)]    ← first run of "a"
# b [('b', 2)]
# a [('a', 3)]    ← second run of "a" — new group!
```

To get SQL-style grouping (all items with the same key together), sort by key first:

```python
data = sorted(data, key=lambda x: x[0])
```

Note: sorting only rearranges by the key — values within each group keep their original relative order (Python's `sorted()` is stable).

---

## 13 — `itertools.chain.from_iterable()` flattens one level

`chain.from_iterable()` takes a single iterable of iterables and concatenates them into one continuous sequence — one level of nesting only.

```python
import itertools as it

data = [[1, 2], [3, 4], [5, 6]]
list(it.chain.from_iterable(data))  # [1, 2, 3, 4, 5, 6]

# only flattens one level — inner lists stay intact
data = [[[1, 2], [3, 4]], [[5, 6]]]
list(it.chain.from_iterable(data))  # [[1, 2], [3, 4], [5, 6]]
```

`chain()` vs `chain.from_iterable()` — same result, different input style:

```python
it.chain([1, 2], [3, 4], [5, 6])              # separate arguments
it.chain.from_iterable([[1, 2], [3, 4], [5, 6]])  # one iterable of iterables
```

---

## 14 — `Counter` vs plain `dict` for counting

`Counter` is a dict subclass that automatically initializes missing keys to `0`, making it convenient for counting without needing to handle missing keys manually.

```python
from collections import Counter

# plain dict — raises KeyError on missing key
counts = {}
counts["a"] += 1  # KeyError!

# workaround with plain dict
counts["a"] = counts.get("a", 0) + 1

# Counter — just works
counts = Counter()
counts["a"] += 1  # defaults to 0, no error
```

`Counter` also comes with extras a plain dict doesn't have:

```python
counts.most_common(3)   # top 3 most frequent keys
counts.most_common()    # all keys sorted by frequency
```

---

## 15 — f-string alignment formatting

f-strings support alignment formatting to produce fixed-width columns, useful for displaying tabular data.

```python
f"{value:<20}"   # left-align in a field of 20 characters
f"{value:>12}"   # right-align in a field of 12 characters
f"{value:^10}"   # center in a field of 10 characters
```

Example — printing a table with consistent columns:

```python
for hour, count in sorted(hour_counts.items()):
    print(f"{hour:<20} {count:>12}")

# 2024-01-01 08:00                3
# 2024-01-01 09:00                7
# 2024-01-01 10:00               15
# 2024-01-01 11:00             1024
```

The right edge of the count column stays fixed regardless of how large the number grows. It only breaks if the value exceeds the field width, in which case Python just expands it without truncating.

---

## 16 — Why set membership check is O(1)

Sets are backed by a **hash table**. When you add an element, Python computes its **hash** — a fixed-size integer derived from the value — and uses it to determine where in memory to store the element. Lookup works the same way: compute the hash, jump directly to that location, done.

```python
my_set = {1, 2, 3, 4, 5}
3 in my_set   # doesn't scan 1, 2, 3... — jumps straight to where 3 lives

my_list = [1, 2, 3, 4, 5]
3 in my_list  # checks 1, then 2, then 3 — O(n)
```

**Hash collisions** — two different values can sometimes produce the same hash. Python handles this with a small extra step, but collisions are rare so average complexity stays O(1).

**Only hashable (immutable) objects** can be stored in a set. Python needs a stable hash, and mutable objects (like lists) can change — which would change their hash and break the lookup mechanism.

```python
{[1, 2, 3]}  # TypeError: unhashable type: 'list'
```

---

## 17 — `itertools.islice()` — lazy slicing for iterables

`islice()` slices an iterable without converting it to a list first. It works like regular list slicing but lazily — only processing elements as needed. Especially useful for generators and infinite sequences that don't support `[]` indexing.

```python
import itertools as it

data = [10, 20, 30, 40, 50, 60, 70]

list(it.islice(data, 3))         # [10, 20, 30]       — first 3 elements
list(it.islice(data, 2, 5))      # [30, 40, 50]       — index 2 to 4
list(it.islice(data, 0, 7, 2))   # [10, 30, 50, 70]   — every 2nd element

# works on infinite generators — regular slicing can't do this
def count_forever():
    n = 0
    while True:
        yield n
        n += 1

list(it.islice(count_forever(), 5))   # [0, 1, 2, 3, 4]
```

**Limitation:** does not support negative indices or steps — it processes elements one at a time and doesn't know the total length upfront.

```python
it.islice(data, -1)   # ValueError
```

**Time complexity:** O(n) where n is the stop index. It must walk through elements from the start — unlike list slicing which can jump to the start index in O(1).

---

## 18 — Generators are stateful

A generator object remembers where it left off between calls. Every `next()` or `send()` resumes from exactly where it paused — not from the beginning. The state it keeps track of includes:

- **execution position** — which `yield` line it paused on
- **local variables** — all variables inside the function retain their values between calls

```python
def counter():
    x = 0
    while True:
        yield x
        x += 1

gen = counter()
next(gen)   # 0 — x is 0, pauses
next(gen)   # 1 — resumes, x becomes 1, pauses
next(gen)   # 2 — resumes, x becomes 2, pauses
```

Compare to a regular function, which is **stateless** — starts fresh every call:

```python
def counter():
    x = 0
    return x + 1

counter()   # always 1
counter()   # always 1
```

A generator is also **not reusable** — once exhausted, its state is "finished". To start over, create a new generator object by calling the function again.

---

## 19 — `islice()` wraps the original generator — it doesn't copy it

`islice()` is a thin wrapper around the original generator. It doesn't buffer or copy elements — both the `islice` object and the generator point to the same underlying source. When `islice` consumes elements, the generator's position advances too.

```python
gen = count_forever()

list(it.islice(gen, 5))   # [0, 1, 2, 3, 4]
next(gen)                 # 5 — gen has advanced past 0-4
```

Think of `islice` as a gatekeeper in front of the generator:

```
you → islice (gatekeeper) → generator (source)
```

This means sharing a generator across multiple `islice` calls causes each one to pick up where the last left off:

```python
gen = count_forever()

list(it.islice(gen, 3))   # [0, 1, 2]
list(it.islice(gen, 3))   # [3, 4, 5] — not [0, 1, 2] again!
list(it.islice(gen, 3))   # [6, 7, 8]
```

This behavior is true for most of `itertools` — functions like `takewhile`, `dropwhile`, and `filterfalse` also wrap the original iterable rather than copying it, keeping memory usage efficient.

---

## 20 — `yield` vs `yield from`

`yield` yields a single value directly to the caller. `yield from` delegates to another iterable — yielding every item from it one by one.

```python
# yield — one value at a time
def gen():
    yield 1
    yield 2

# yield from — delegates to an iterable
def gen():
    yield from [1, 2]   # equivalent to: for x in [1, 2]: yield x
```

`yield from` is cleaner for delegating to sub-generators:

```python
def inner():
    yield 1
    yield 2

def outer():
    yield from inner()   # delegates directly
    yield 3

list(outer())   # [1, 2, 3]
```

**The deeper difference — two-way communication**

`yield from` doesn't just forward values outward — it also forwards `send()` values and exceptions back into the sub-generator transparently. A plain `for` + `yield` loop cannot do this.

```python
def inner():
    value = yield 1
    print(f"inner received: {value}")
    yield 2

def outer_manual():
    for x in inner():    # send() goes to outer, not inner — broken channel
        yield x

def outer_delegating():
    yield from inner()   # send() is forwarded directly into inner

gen = outer_delegating()
next(gen)        # 1
gen.send(99)     # inner received: 99 — send() reached inner directly
```

`yield from` creates a **transparent two-way tunnel** between the caller and the sub-generator — it is not just syntactic sugar for a loop.

---

## 21 — Decorators

A decorator is a function that takes another function, wraps it with extra behavior, and returns the wrapper. The `@` syntax is shorthand for reassigning the function to its wrapped version.

```python
def shout(func):
    def wrapper(*args, **kwargs):
        print(f"CALLING {func.__name__}")   # before
        result = func(*args, **kwargs)       # call the original
        print(f"DONE {func.__name__}")       # after
        return result
    return wrapper

@shout
def greet(name):
    print(f"hello {name}")

# @shout is exactly equivalent to:
greet = shout(greet)
```

**When does `shout()` return?**

`shout()` returns **immediately when the decorator is applied** — long before `greet("alice")` is ever called. The sequence is:

1. Python defines the original `greet` function
2. Python immediately calls `shout(greet)`, passing the original `greet` as `func`
3. `wrapper` is created and returned — `shout()` is now done, its stack frame is gone
4. `greet` is rebound to `wrapper`
5. Later, calling `greet("alice")` actually calls `wrapper("alice")`

---

## 22 — Closures

A closure is a **function bundled together with the variables it captured from its enclosing scope**. It is not just a function — it's the function plus its captured variables.

In the decorator example, `wrapper` is the closure — but more precisely, the closure is `wrapper` + the `func` variable it captured. Python stores captured variables in a `__closure__` attribute on the function object:

```python
greet.__closure__                    # (<cell object at 0x...>,)
greet.__closure__[0].cell_contents   # <function greet> — the captured func
```

Think of a closure as a function carrying a backpack of variables from where it was created:

```
wrapper (function)
└── __closure__ (backpack)
    └── func = <the original greet function>
```

Not every nested function is a closure — only if it references a variable from the enclosing scope:

```python
def outer():
    x = 10
    def inner():
        return x    # references x from outer — IS a closure
    return inner

def outer():
    x = 10
    def inner():
        return 42   # doesn't reference outer scope — NOT a closure
    return inner
```

**Why closures matter for decorators**

After `shout()` returns, its stack frame is gone — but `func` survives because `wrapper` closed over it. Python actively keeps a reference to `func` inside `wrapper`'s `__closure__`, preventing it from being garbage collected. Without this mechanism, `func` would disappear the moment `shout()` returned.

---

## 23 — Decorator use cases

A decorator is best used for **cross-cutting concerns** — behavior that applies to many functions but has nothing to do with what those functions actually do. The alternative without decorators is repeating the same boilerplate inside every function.

**Logging / tracing** — record every time a function is called:
```python
@log_calls
def process_payment(amount):
    ...
```

**Timing / performance** — measure how long a function takes:
```python
@timer
def run_report():
    ...
```

**Authentication / authorization** — check if a user is allowed before running. Heavily used in web frameworks like Flask and Django:
```python
@login_required
def dashboard(request):
    ...

@app.route("/")   # also a decorator — registers the function as a route handler
def index():
    ...
```

**Caching / memoization** — store results so the function doesn't recompute the same inputs:
```python
@functools.lru_cache
def fibonacci(n):
    ...
```

**Retry logic** — automatically retry a function if it fails:
```python
@retry(times=3)
def call_external_api():
    ...
```

**Validation** — check inputs before the function runs:
```python
@validate_input
def create_user(email, password):
    ...
```

The key insight: the wrapped functions don't know they're being decorated — the extra behavior is completely transparent to them. One decorator can apply the same logic across dozens of functions without any of them needing to be modified.

---

## 24 — `lru_cache` and `cached_property`

Both cache results to avoid recomputation, but operate in different contexts.

**`lru_cache` — caches function call results by arguments**

Stores results in a dictionary keyed by arguments. On repeated calls with the same arguments, skips the function entirely and returns the cached result. The **LRU** (Least Recently Used) eviction policy drops the least recently used entry when `maxsize` is hit, keeping memory bounded.

```python
@lru_cache(maxsize=128)
def fibonacci(n):
    if n < 2:
        return n
    return fibonacci(n-1) + fibonacci(n-2)

fibonacci(50)              # each value computed once, then reused
fibonacci.cache_info()     # CacheInfo(hits=48, misses=51, maxsize=128, currsize=51)
fibonacci.cache_clear()    # wipe the cache
```

Arguments must be **hashable** since they're used as dictionary keys:

```python
@lru_cache
def process(data):
    ...

process([1, 2, 3])   # TypeError — lists aren't hashable
```

**`cached_property` — caches a property on the instance itself**

On first access, computes the value and stores it directly in the instance's `__dict__`. On subsequent accesses, Python finds it in `__dict__` before even reaching the descriptor — the method is never called again.

```python
class Circle:
    def __init__(self, radius):
        self.radius = radius

    @cached_property
    def area(self):
        return 3.14159 * self.radius ** 2

c = Circle(5)
c.__dict__   # {} — empty before first access
c.area       # computes and stores result
c.__dict__   # {'area': 78.53975} — now stored on instance
c.area       # returns from __dict__ — method never called again
```

**Comparison:**

| | `lru_cache` | `cached_property` |
|---|---|---|
| context | standalone functions | class properties |
| cache lives on | the function itself | the instance `__dict__` |
| keyed by | arguments | nothing — once per instance |
| eviction | LRU when maxsize hit | never — lives until instance is deleted |
| arguments | yes | no |

---

## 25 — Does a decorator always contain a closure?

Not always — but most practical decorators do. A decorator only produces a closure if the wrapper references a variable from the enclosing scope. In practice this almost always happens because referencing `func` to call the original function is the whole point of a decorator — and that reference is what creates the closure.

The rare case with no closure is when the wrapper doesn't reference anything from the outer scope:

```python
def replace(func):
    def wrapper(*args, **kwargs):
        return 42   # completely ignores func — doesn't close over anything
    return wrapper

wrapper.__closure__   # None
```

This is contrived and not useful in practice.

---

## 26 — Is a closure always an inner function?

No — a closure is not always an inner function. What defines a closure is **a function that captures a variable from an enclosing scope that has already returned**. The inner function pattern is just the most common way to produce that situation.

A lambda can also be a closure:

```python
def make_multiplier(n):
    return lambda x: x * n   # lambda — captures n from enclosing scope

double = make_multiplier(2)
double(5)   # 10
```

A function referencing a **global** variable is NOT a closure — globals never disappear so they don't need to be captured:

```python
x = 10

def foo():
    return x   # references global x — NOT a closure

foo.__closure__   # None
```

| | closure? |
|---|---|
| inner function referencing enclosing variable | yes |
| lambda referencing enclosing variable | yes |
| function referencing a global variable | no |
| inner function not referencing enclosing scope | no |

---

## 27 — Enclosing scope and LEGB

An enclosing scope is the **local scope of the function that wraps your function** — the layer directly outside but not global. Python looks up variable names in LEGB order:

```
L — Local        (inside the current function)
E — Enclosing    (inside the outer function that wraps this one)
G — Global       (module level)
B — Built-in     (Python's built-ins like len, print, range)
```

```python
x = "global"

def outer():
    x = "enclosing"    # E — enclosing scope for inner

    def inner():
        x = "local"    # L — inner's own local scope
        print(x)       # finds "local" first — stops at L

def inner_only():
    print(x)           # no local, no enclosing — finds "global" at G
```

A variable is only in the enclosing scope when it lives in an **outer function's local scope** — not at the module level. This is what makes closures work: when `inner` references a variable from `outer`'s local scope, Python captures it before `outer`'s scope disappears. Globals don't need capturing because they never disappear.

---

## 28 — Exponential backoff in retry logic

Backoff is a strategy where you wait **longer and longer between each retry** instead of a fixed interval. The delay grows by multiplying by a backoff factor after each failure.

```python
current_delay = 1.0
backoff = 2.0

current_delay *= 2.0   # 2.0  — after attempt 1
current_delay *= 2.0   # 4.0  — after attempt 2
current_delay *= 2.0   # 8.0  — after attempt 3
```

The standard pattern is `current_delay *= backoff` — simpler than `delay * (backoff ** i)` and equivalent. The `** i` version requires tracking an index separately for no benefit, unless you need to jump to a specific attempt's delay without iterating.

`backoff=1.0` means no backoff at all (delay stays the same). Starting delay affects the scale but not the growth pattern:

```
delay=1: 1 → 2 → 4 → 8
delay=5: 5 → 10 → 20 → 40
```

Backoff matters in distributed systems — if many clients retry at fixed intervals, they keep hammering a struggling server. Exponential backoff spreads retries out over time, giving the server room to recover.

---

## 29 — Decorator stacking order matters

Decorators are applied **bottom up** — the one closest to the function wraps first. Given:

```python
@timed_log
@retry(times=3, delay=0.1, backoff=2.0)
@rate_limit(calls_per_second=2)
def fetch_user(self, user_id):
```

This is equivalent to:
```python
fetch_user = timed_log(retry(rate_limit(fetch_user)))
```

Call chain: `timed_log → retry → rate_limit → fetch_user`

Rate limiting is applied on **every retry attempt**. Swapping `retry` and `rate_limit`:

```python
@timed_log
@rate_limit(calls_per_second=2)
@retry(times=3)
def fetch_user(self, user_id):
```

Call chain: `timed_log → rate_limit → retry → fetch_user`

Now rate limiting is applied **once per outer call** — all retries fire inside without spacing. The original order is almost always correct — rate limiting inside retry prevents retries from overwhelming a struggling service.

---

## 30 — `rate_limit` decorator internals

A rate limiter enforces a minimum interval between calls using a timestamp, a lock, and `time.perf_counter()`.

```python
def rate_limit(calls_per_second=1.0):
    min_interval = 1.0 / calls_per_second   # e.g. 2/s → 0.5s between calls
    lock = threading.Lock()
    last_called = [0.0]

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            with lock:
                elapsed = time.perf_counter() - last_called[0]
                wait = min_interval - elapsed
                if wait > 0:
                    time.sleep(wait)
                last_called[0] = time.perf_counter()
            return func(*args, **kwargs)
        return wrapper
    return decorator
```

Each part:

- `min_interval` — converts calls/second to seconds/call (`2/s → 0.5s`)
- `lock` — prevents race conditions when multiple threads call simultaneously
- `last_called = [0.0]` — stores timestamp of last call as a list so the closure can mutate it
- `elapsed` — how long ago the last call was (`now - last_called`)
- `wait` — how much longer to wait (`min_interval - elapsed`); negative means no wait needed
- `if wait > 0` — only sleeps when the caller is moving faster than the rate limit allows
- `return func(...)` outside the lock — the actual function call doesn't need to hold the lock

`time.perf_counter()` is preferred over `time.time()` because it's monotonic — it never jumps backward if the system clock is adjusted.

---

## 31 — `threading.Lock()` and race conditions

A lock ensures only **one thread at a time** can execute the code inside `with lock`. Without it, two threads can read and update a shared variable simultaneously — a **race condition**:

```python
# without lock — two threads race:
thread 1: reads last_called[0] = 0.0
thread 2: reads last_called[0] = 0.0   # reads before thread 1 updates
thread 1: updates last_called[0] = 0.5
thread 2: updates last_called[0] = 0.5  # both fired — rate limit broken

# with lock — serialized:
thread 1: acquires lock → reads → updates → releases lock
thread 2: waits... → acquires lock → reads updated value → correct behavior
```

---

## 32 — Variable assignment under the hood

When you write `x = 10`, Python does three things:

1. **Creates the object** — allocates memory for the integer `10`, stores its value, type, and reference count
2. **Updates the namespace** — every scope has a namespace dictionary mapping names to objects
3. **Points the variable to the object** — the namespace entry stores the memory address, not the value

```python
x = 10
y = x    # y gets the same memory address — both point to the same object
id(x) == id(y)   # True

globals()   # the global namespace dictionary
locals()    # the local namespace dictionary
```

On reassignment, the namespace entry is updated to point to a new object — the old object is untouched and garbage collected if nothing else references it.

At compile time, Python scans a function body and marks any name that has an assignment (`=`) as a local variable (`co_varnames`). This is why reading a variable before assigning it in the same function raises `UnboundLocalError` — Python already decided it's local, finds nothing in local slots yet, and errors.

---

## 33 — `time.perf_counter()` — reading the current time

`perf_counter()` doesn't measure anything on its own — it just returns the **current timestamp** as a float. Elapsed time is computed by calling it twice and subtracting:

```python
start = time.perf_counter()   # snapshot 1
# ... code runs ...
end = time.perf_counter()     # snapshot 2
elapsed = end - start         # you compute the difference
```

Its absolute value is meaningless (it's a large float representing time since program or system start). What matters is the difference between two calls.

Preferred over `time.time()` for measuring intervals because it's **monotonic** — guaranteed to never move backward, even if the system clock is adjusted.

---

## 34 — Unpacking

Unpacking extracts values from an iterable and assigns them to variables in one line.

```python
a, b, c = [1, 2, 3]    # list
a, b, c = (1, 2, 3)    # tuple
a, b, c = "abc"         # string — any iterable works
```

**Star unpacking — capture the rest:**
```python
first, *rest = [1, 2, 3, 4, 5]       # first=1, rest=[2,3,4,5]
*init, last = [1, 2, 3, 4, 5]        # init=[1,2,3,4], last=5
first, *middle, last = [1, 2, 3, 4, 5]  # first=1, middle=[2,3,4], last=5
```

**Unpacking in function calls:**
```python
nums = [1, 2, 3]
add(*nums)            # same as add(1, 2, 3)

config = {"a": 1, "b": 2, "c": 3}
add(**config)         # same as add(a=1, b=2, c=3)
```

**Unpacking in function definitions:**
```python
def foo(*args):       # captures all positional args as a tuple
def bar(**kwargs):    # captures all keyword args as a dict
```

**Swapping variables — no temp variable needed:**
```python
a, b = 1, 2
a, b = b, a   # right side packed into tuple first, then unpacked
```

**Common use in loops:**
```python
for key, value in {"x": 10, "y": 20}.items():   # unpacks each tuple
    print(key, value)
```

This is exactly what `for key, group in groupby(...)` and `for hour, count in sorted(...)` do — unpacking each tuple as it comes out of the iterator.

---

## 35 — `@dataclass` — generating boilerplate automatically

`@dataclass` reads type-annotated properties and automatically generates `__init__`, `__repr__`, and `__eq__`. Eliminates writing every property name three times.

```python
# without @dataclass — repetitive
class Food:
    def __init__(self, name, protein_per_100g):
        self.name = name
        self.protein_per_100g = protein_per_100g

# with @dataclass — clean
from dataclasses import dataclass

@dataclass
class Food:
    name: str
    protein_per_100g: float
```

Rules:
- Required fields (no default) must come before optional fields (with default)
- Use `@dataclass(frozen=True)` to make the class immutable after creation

---

## 36 — `field(default_factory=...)` vs plain defaults

Three ways to set a default — only one is correct for mutable or dynamic values:

```python
# option 1 — calls date.today() once at class definition time — WRONG
logged_date: date = date.today()       # every instance gets the same hardcoded date

# option 2 — stores the function object as the value — WRONG
logged_date: date = date.today         # logged_date becomes a function, not a date

# option 3 — calls date.today() fresh on every instantiation — CORRECT
logged_date: date = field(default_factory=date.today)
```

`default_factory` stores a callable and calls it each time a new instance is created. Use it for any default that should be dynamic (dates, times) or mutable (lists, dicts).

```python
from dataclasses import dataclass, field
from datetime import date

@dataclass
class FoodEntry:
    weight_g: float
    logged_date: date = field(default_factory=date.today)  # fresh date each time
    tags: list = field(default_factory=list)               # fresh list each time
```

---

## 37 — `frozen=True` — immutable dataclasses

`frozen=True` makes a dataclass immutable after creation by overriding `__setattr__` and `__delattr__` to raise `FrozenInstanceError`. Use it for objects that represent historical records — things that should never be altered after creation.

```python
@dataclass(frozen=True)
class MacroGoal:
    calories: float
    protein_g: float

goal = MacroGoal(calories=2000, protein_g=150)
goal.calories = 1800   # FrozenInstanceError — cannot assign to field 'calories'
```

Under the hood, `frozen=True` generates:

```python
def __setattr__(self, name, value):
    raise FrozenInstanceError('cannot assign to field ' + name)

def __delattr__(self, name):
    raise FrozenInstanceError('cannot delete field ' + name)
```

If you need to set a computed field inside `__post_init__` on a frozen class, bypass the restriction with `object.__setattr__(self, 'field', value)`.

**When to use frozen:**
- Historical records that should never be altered (`MacroGoal`, `WeightEntry`)
- Value objects where identity is defined by content, not reference

**When not to use frozen:**
- Objects that legitimately change over time (`User`, `Food`, `FoodEntry`)

---

## 38 — `__post_init__` — running logic after `__init__`

`__post_init__` runs automatically right after the generated `__init__` finishes. Use it for validation, computed fields, or any setup logic.

```python
from nutritrack.core.exceptions import InvalidMacroError

@dataclass
class FoodEntry:
    food: Food
    weight_g: float

    def __post_init__(self):
        if self.weight_g <= 0:
            raise InvalidMacroError("weight_g", self.weight_g)
```

For multiple fields, loop over pairs instead of writing separate `if` statements:

```python
def __post_init__(self):
    for field_name, value in [
        ("protein_per_100g", self.protein_per_100g),
        ("carbs_per_100g", self.carbs_per_100g),
        ("fat_per_100g", self.fat_per_100g),
    ]:
        if value is not None and value < 0:
            raise InvalidMacroError(field_name, value)
```

**Frozen + `__post_init__`:** you can raise exceptions freely, but cannot assign to `self.field` — use `object.__setattr__` if needed.

---

## 39 — Custom exceptions

Custom exceptions give each error type its own identity, enabling precise error handling instead of catching generic `ValueError` or `Exception` everywhere.

```python
class FoodNotFoundError(Exception):
    def __init__(self, food_name: str):
        super().__init__(f"Food '{food_name}' was not found in the database")

class InvalidMacroError(Exception):
    def __init__(self, field_name: str, value: float):
        super().__init__(f"Invalid value {value} for '{field_name}'. Must be positive.")

class GoalNotSetError(Exception):
    def __init__(self):
        super().__init__("No macro goal has been set for today.")

class AIServiceError(Exception):
    def __init__(self, message: str):
        super().__init__(f"AI service error: {message}")
```

**Why custom over built-in:**

```python
# with generic exceptions — can't tell them apart
except ValueError:
    return 500   # which error was it?

# with custom exceptions — precise handling
except FoodNotFoundError:
    return 404
except InvalidMacroError:
    return 422
except GoalNotSetError:
    return 400
except AIServiceError:
    return 503
```

`super().__init__(message)` passes the message to the base `Exception` class — this is what makes it print readably in tracebacks.

---

## 40 — Object-oriented design — when to split into separate classes

A class should represent one distinct entity. Signs you need a separate class:

- The data changes independently over time (weight history, goal history)
- It has its own identity separate from the parent (a logged meal vs the food itself)
- Adding it to an existing class would mean storing multiple values or tracking change dates

**NutriTrack examples:**

| Entity | Why separate? |
|---|---|
| `Food` | Reference data — macros per 100g, doesn't change per user |
| `FoodEntry` | A logged event — ties a food to a user, weight, date, meal slot |
| `MacroGoal` | Changes over time — new goal = new object, preserving history |
| `WeightEntry` | Changes over time — each measurement is its own immutable record |
| `User` | The person — legitimately mutable (email, activity level can change) |

---

## 41 — Per 100g scaling

Food macros are stored per 100g as a standard reference. To get macros for any actual serving weight, scale by `weight_g / 100`:

```python
# protein for a specific serving
scaled_protein = protein_per_100g * (weight_g / 100)

# dimensional analysis — units cancel correctly:
# (31g protein / 100g food) × 62g food = 19.22g protein
```

This means the AI lookup only needs to happen once per food — store per 100g, then scale to any weight mathematically without another API call.

---

## 42 — Immutability of historical records

Historical records should never be altered — only appended to. If a record is wrong, delete it and create a correct one. This principle:

- Preserves a complete audit trail
- Makes the data trustworthy (no silent edits)
- Simplifies debugging (the past is always known)

In NutriTrack, `MacroGoal` and `WeightEntry` are `frozen=True` for this reason. If a user changes their goal, a new `MacroGoal` is created with a new `effective_date` — the old one is kept. This gives the app a full history of goal changes automatically.

---

## 43 — `@wraps` — preserving function identity through decoration

When you wrap a function without `@wraps`, Python loses the original function's metadata:

```python
def my_decorator(func):
    def wrapper(*args, **kwargs):
        return func(*args, **kwargs)
    return wrapper

@my_decorator
def greet(name: str) -> str:
    """Says hello."""
    return f"hello {name}"

print(greet.__name__)   # 'wrapper' — wrong!
print(greet.__doc__)    # None — lost!
```

`@wraps(func)` copies `__name__`, `__doc__`, and other metadata from the original function onto the wrapper:

```python
from functools import wraps

def my_decorator(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        return func(*args, **kwargs)
    return wrapper

print(greet.__name__)   # 'greet' — correct
print(greet.__doc__)    # 'Says hello.' — preserved
```

Always use `@wraps(func)` in decorators. FastAPI reads `__name__` and `__doc__` from route handlers to generate API documentation — without `@wraps`, every endpoint shows up as `wrapper`.

---

## 44 — Factory decorators — decorators that take arguments

A plain decorator takes only the function. A factory decorator takes configuration arguments and has an extra layer of nesting:

```python
# plain decorator — 2 layers
def timed_log(func: Callable) -> Callable:
    @wraps(func)
    def wrapper(*args, **kwargs):
        ...
    return wrapper

# factory decorator — 3 layers
def retry(times: int = 3, delay: float = 1.0):   # outer — takes config
    def decorator(func: Callable) -> Callable:    # middle — takes the function
        @wraps(func)
        def wrapper(*args, **kwargs):              # inner — runs on each call
            ...
        return wrapper
    return decorator
```

The extra layer exists because `times` and `delay` need to be captured in the closure before the function is known. Usage:

```python
@retry(times=3, delay=1.0)   # calls retry(3, 1.0) → returns decorator → wraps func
def fetch_data():
    ...
```

---

## 45 — `except Exception` with `isinstance` — filtering exception types

Python's `except` clause requires a literal type — you can't pass a variable as the exception type:

```python
my_exceptions = (ValueError, TypeError)
except my_exceptions as err:   # ❌ SyntaxError — variable not allowed here
```

The workaround — catch all exceptions, then check manually:

```python
except Exception as err:
    if not isinstance(err, exceptions):
        raise   # not one of ours — re-raise immediately
    # otherwise handle it
```

This pattern is used in `@retry` to only retry on the specified exception types and immediately re-raise anything else.

---

## 46 — `@retry` decorator — full implementation

```python
def retry(
    times: int = 3,
    delay: float = 1.0,
    backoff: float = 2.0,
    exceptions: tuple = (Exception,),
):
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            attempts = 0
            last_exception = None
            current_delay = delay        # initialize outside loop
            while attempts < times:
                try:
                    return func(*args, **kwargs)
                except Exception as err:
                    if not isinstance(err, exceptions):
                        raise            # not our exception — re-raise immediately
                    logger.warning(f"Attempt {attempts + 1}/{times} failed: {err}")
                    last_exception = err
                    time.sleep(current_delay)
                    current_delay *= backoff   # grows each iteration
                    attempts += 1
            raise last_exception         # all attempts exhausted
        return wrapper
    return decorator
```

Key decisions:
- `current_delay = delay` outside the loop so it carries across iterations
- `attempts + 1` in the log so humans see 1-based counting
- `isinstance(err, exceptions)` to filter which exceptions trigger a retry
- `raise last_exception` after the loop to surface the final failure

---

## 47 — `@rate_limit` decorator — full implementation

```python
def rate_limit(calls_per_second: float = 1.0) -> Callable:
    last_called = [0.0]
    interval_s = 1 / calls_per_second
    lock = threading.Lock()

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            with lock:
                elapsed = time.perf_counter() - last_called[0]
                if elapsed < interval_s:
                    time.sleep(interval_s - elapsed)
                last_called[0] = time.perf_counter()   # always update
            return func(*args, **kwargs)               # outside the lock
        return wrapper
    return decorator
```

Key decisions:
- `last_called[0]` updates on **every** call — not just when sleeping. If updated only on sleep, stale timestamps cause incorrect elapsed calculations on the next call.
- Function call is **outside** the lock — the lock only protects the timing check and timestamp update (microseconds). Holding it during the function call would block all threads for the full duration of the function.

---

## 48 — Python logging tree — why `basicConfig()` is needed

Python's logging system is a tree. Loggers pass messages up to the root logger, which is the one with the actual output handler.

```
root logger              ← basicConfig() configures this
└── nutritrack
    └── nutritrack.core
        └── nutritrack.core.utils   ← getLogger(__name__) creates this
```

`logging.getLogger(__name__)` creates a named logger for the current module. But without a handler on the root logger, messages travel up the tree and disappear.

```python
# in utils.py
logger = logging.getLogger(__name__)   # creates nutritrack.core.utils logger
logger.info("hello")                   # message disappears — no handler on root

# at app startup — configure once
import logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s')
logger.info("hello")   # now prints correctly
```

`basicConfig()` should be called **once at app startup** — in Phase 3 this goes in the FastAPI app entry point, so every logger across the entire application outputs correctly without per-module configuration.

---

## 49 — Circular imports — causes and fix

A circular import happens when two modules import each other:

```
models.py → imports utils.py → imports models.py → circular!
```

Python can't initialize either module because each depends on the other being ready first.

**Fix — separate concerns into a one-way dependency chain:**

```
exceptions.py  ← imports nothing from your package
utils.py       ← imports from exceptions only
models.py      ← imports from utils and exceptions
parsers.py     ← imports from models, utils, exceptions
```

Each layer only imports from layers below it — never above. Follow this rule and circular imports never happen.

In NutriTrack, `parse_food_csv()` and `daily_totals()` were moved from `utils.py` to `parsers.py` because they import `Food` and `FoodEntry` from `models.py` — which already imports from `utils.py`.

---

## 50 — Generator pipelines — `get_daily_totals()`

A generator pipeline chains lazy operations — each step processes one item at a time without loading everything into memory.

```python
def get_daily_totals(entries: list[FoodEntry]) -> Generator[dict, None, None]:
    # NOTE: sorting in memory — in production, pass pre-sorted entries from DB
    sorted_entries = sorted(entries, key=lambda e: e.logged_date, reverse=True)
    for logged_date, members in groupby(sorted_entries, key=lambda e: e.logged_date):
        day_entries = list(members)
        yield {
            "date": logged_date,
            "total_calories": sum(e.scaled_calories() for e in day_entries),
            "total_protein":  sum(e.scaled_protein()  for e in day_entries),
            "total_carbs":    sum(e.scaled_carbs()     for e in day_entries),
            "total_fat":      sum(e.scaled_fat()       for e in day_entries),
            "entry_count":    len(day_entries),
            "foods":          [e.food for e in day_entries],
        }
```

Key decisions:
- `reverse=True` — descending sort so first iteration = most recent day
- `list(members)` — materialize the group before iterating multiple times
- Generator expressions inside `sum()` — no intermediate list created
- In production, sort happens at the database level using an index — no in-memory sort needed

---

## 51 — `Counter` for frequency counting

`Counter` is a dict subclass that counts occurrences. Keys are items, values are counts. Best used when you need frequency analysis or top-N results.

```python
from collections import Counter

food_counter: Counter[str] = Counter()
food_counter["chicken breast"] += 1
food_counter["chicken breast"] += 1
food_counter["banana"] += 1

food_counter.most_common(2)   # [('chicken breast', 2), ('banana', 1)]
```

Type annotation `Counter[str]` tells mypy the keys are strings — required when initializing an empty Counter since mypy can't infer the type.

Use `food.name` (string) as the key rather than the `Food` object itself — non-frozen dataclasses are not hashable and can't be used as dict keys.

---

## 52 — Single-pass aggregation

When processing large datasets, do everything in one loop rather than multiple passes. Multiple passes over the same data multiplies execution time linearly.

```python
# two passes — O(2n)
totals = sum(e.scaled_calories() for e in entries)     # pass 1
counter = Counter(e.food.name for e in entries)        # pass 2

# one pass — O(n)
for entry in entries:
    total_calories += entry.scaled_calories()
    food_counter[entry.food.name] += 1
```

In `MacroAggregator`, a single pass through `get_daily_totals()` accumulates all totals and food counts simultaneously.

---

## 53 — Database indexes

An index is a separate data structure (B-tree) that keeps a column's values sorted for fast lookup. Without an index, every query does a full table scan — O(n). With an index, lookups are O(log n) and sorted retrievals are O(n) with no sorting cost.

```python
# SQLAlchemy — add index to a column
class FoodEntry(Base):
    id          = Column(Integer, primary_key=True)   # auto-indexed
    logged_date = Column(Date, index=True)             # manually indexed
    user_id     = Column(Integer, index=True)          # manually indexed
```

**Primary key vs index:**
- Primary key — uniquely identifies each row, automatically indexed, one per table
- Index — speeds up queries on any column, not necessarily unique, many per table

**Tradeoff:**
- Faster reads — queries on indexed columns skip full scans
- Slower writes — every INSERT/UPDATE also updates the index
- More storage — index takes disk space alongside the table

Index columns you query frequently: `user_id` (every request filters by user), `logged_date` (history queries always sort by date), `email` (login lookups).

---

## 54 — `Optional` vs kwarg with default

A kwarg with a default makes a parameter **optional to pass**. `Optional[T]` makes `None` an **explicitly valid value** that the code handles intentionally.

```python
# kwarg with default — fmt is always a str, None is not valid
def setup_logging(fmt: str = "%(asctime)s ...") -> None:
    formatter = logging.Formatter(fmt)   # always a string

# Optional — None is valid and handled explicitly
def setup_logging(fmt: Optional[str] = None) -> None:
    default = "%(asctime)s ..."
    formatter = logging.Formatter(fmt or default)   # handles None case
```

Use `Optional` when `None` is a meaningful signal that changes behavior. Use a plain default when the parameter always has a real value — simpler and more honest.

---

## 55 — Production logging setup

`basicConfig()` is fragile in production — it silently does nothing if the root logger already has handlers (e.g. set by a third-party library). Build `setup_logging()` manually for full control:

```python
def setup_logging(
    root_level: str = "DEBUG",
    stream_handler_level: str = "INFO",
    fmt: str = "%(asctime)s [%(levelname)s] %(name)s — %(message)s",
) -> None:
    formatter = logging.Formatter(fmt)
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(formatter)
    handler.setLevel(getattr(logging, stream_handler_level.upper()))

    root_logger = logging.getLogger()
    root_logger.handlers.clear()        # clear existing handlers — always wins
    root_logger.addHandler(handler)
    root_logger.setLevel(getattr(logging, root_level.upper()))
```

**Two-gate system:**
- Root logger level — drops messages before they reach any handler
- Handler level — filters what this specific handler outputs

Setting root to `DEBUG` and handler to `INFO` means the root captures everything, but only `INFO+` gets printed. Adding a `DEBUG` file handler later captures everything without touching the root level.

**`get_logger()` wrapper:**

```python
def get_logger(name: str) -> logging.Logger:
    return logging.getLogger(name)
```

Centralizes logger creation — if you swap Python's logging for `structlog` or `loguru` later, you only change `logger.py`, not every module.

Usage in every module:
```python
from nutritrack.core.logger import get_logger
logger = get_logger(__name__)   # __name__ = "nutritrack.core.utils"
```

Call `setup_logging()` once at app startup. Never call it per-module.

---

## 56 — `__name__` in modules

`__name__` inside a module resolves to the full dotted import path, not just the filename:

```python
# inside nutritrack/core/utils.py
__name__  →  "nutritrack.core.utils"

# inside nutritrack/core/parsers.py
__name__  →  "nutritrack.core.parsers"
```

This maps directly to the logger tree — `logging.getLogger(__name__)` places the logger in the correct position in the hierarchy automatically.

---

## 57 — NutriTrack Phase 1 file structure

```
nutritrack/
├── .venv/
├── data/
│   └── foods.csv              ← seed data for pre-populating food database
├── nutritrack/
│   ├── __init__.py
│   └── core/
│       ├── __init__.py
│       ├── models.py          ← Food, FoodEntry, MacroGoal, WeightEntry, User
│       ├── exceptions.py      ← FoodNotFoundError, InvalidMacroError, GoalNotSetError, AIServiceError
│       ├── utils.py           ← calculate_calories, calculate_macro_ratio + decorators
│       ├── parsers.py         ← parse_food_csv, get_daily_totals, MacroAggregator
│       └── logger.py          ← setup_logging, get_logger
├── .gitignore
└── requirements.txt
```

Dependency chain (one-way, no circular imports):
```
exceptions.py → utils.py → models.py → parsers.py
                                ↑
                           logger.py (standalone)
```

---

## 58 — `logging.Formatter`, `StreamHandler`, `getLogger`, `basicConfig` — what each does

**`logging.getLogger(name)`** — creates or retrieves a logger by name. Same name always returns the same object — it's a registry:

```python
logging.getLogger()                  # root logger — no name
logging.getLogger("nutritrack")      # named logger
logging.getLogger(__name__)          # named after current module
```

**`logging.Formatter`** — defines how a log message looks. Takes a format string:

```python
formatter = logging.Formatter("%(asctime)s [%(levelname)s] %(name)s — %(message)s")
# 2026-05-29 14:30:00 [INFO] nutritrack.core.utils — message here
```

Without a formatter, messages print with no timestamp, level, or module name.

**`logging.StreamHandler`** — defines where messages go. A handler is the output destination:

```python
logging.StreamHandler(sys.stdout)   # terminal
logging.StreamHandler(sys.stderr)   # error stream
logging.FileHandler("app.log")      # file
```

A logger can have multiple handlers simultaneously.

**`logging.basicConfig()`** — a convenience shortcut that creates a `StreamHandler`, attaches a `Formatter`, and sets it on the root logger in one call. Roughly equivalent to manually creating all three above.

---

## 59 — Why `basicConfig()` fails in production

`basicConfig()` silently does nothing if the root logger already has handlers:

```python
# Python's source code for basicConfig:
def basicConfig(**kwargs):
    if len(root.handlers) == 0:   # only runs if NO handlers exist
        ...
```

If a third-party library calls `basicConfig()` before your app does, your configuration is silently ignored. No error, no warning.

`setup_logging()` fixes this by explicitly clearing handlers first:

```python
root_logger.handlers.clear()   # always wins regardless of what ran before
root_logger.addHandler(handler)
```

---

## 60 — Why we need `basicConfig()` in the Python shell

The shell starts with a fresh Python process — no logging configuration, no handlers. Every new shell session starts from zero.

In a real app, `setup_logging()` is called once at startup and persists for the app's lifetime. In the shell there's no startup — you configure manually each session.

```
Real app: startup → setup_logging() once → all loggers work forever
Shell:    open → no setup → logger exists but silent → manually call setup_logging()
          close → everything gone → next session starts fresh
```

This is why Phase 3 wires `setup_logging()` into FastAPI's startup event — so it runs automatically every time the app starts.

---

## 61 — `setLevel()` on handler vs root logger — the two-gate system

A log message must pass two gates before being output:

```
message → gate 1: root logger level → gate 2: handler level → output
```

**Root logger level** — drops messages before they reach any handler:
```python
root_logger.setLevel(logging.INFO)
logger.debug("dropped here")    # never reaches any handler
logger.info("passes gate 1")    # moves to handler check
```

**Handler level** — filters what this specific handler outputs:
```python
stream_handler.setLevel(logging.INFO)   # terminal shows INFO+
file_handler.setLevel(logging.DEBUG)    # file captures everything
```

Setting root to `DEBUG` and handler to `INFO` means the root captures everything but only `INFO+` gets printed. Adding a `DEBUG` file handler later works without touching the root level — the root already passes everything through.

---

## 62 — `get_logger()` — why wrap `getLogger()`

`get_logger()` is a thin wrapper that centralizes logger creation:

```python
# without wrapper — every module imports logging directly
import logging
logger = logging.getLogger(__name__)

# with wrapper — every module imports from your package
from nutritrack.core.logger import get_logger
logger = get_logger(__name__)
```

Benefits:
- If you swap Python's `logging` for `structlog` or `loguru` later, change only `logger.py` — not every module
- Future extensibility — attach request context, custom filters, or correlation IDs in one place
- Consistency — enforces a single way of creating loggers across the codebase

---

## 63 — MacroGoal effective date — how the app finds today's goal

A new `MacroGoal` is only created when the user **changes** their goal — not every day. The app finds the active goal by querying the most recent one on or before today:

```sql
SELECT * FROM macro_goals
WHERE user_id = 42 AND effective_date <= today
ORDER BY effective_date DESC
LIMIT 1
```

This means:
- User registers → one `MacroGoal` created from TDEE calculation
- Never changed → same goal applies every day indefinitely
- Updated on Mar 15 → new `MacroGoal` created, applies from Mar 15 onward
- Old goal preserved → full history of goal changes available

`MacroAggregator` doesn't handle this lookup — by the time it receives a `MacroGoal`, the caller has already fetched the correct one for that day.

---

## 64 — TDEE and automatic goal calculation (Mifflin-St Jeor)

Instead of users manually entering calorie goals, the app calculates their TDEE (Total Daily Energy Expenditure) from body metrics:

```
BMR (men)   = (10 × weight_kg) + (6.25 × height_cm) - (5 × age) + 5
BMR (women) = (10 × weight_kg) + (6.25 × height_cm) - (5 × age) - 161
```

BMR × activity multiplier = TDEE:

```
Sedentary (desk job)        × 1.2
Lightly active (1-3x/week)  × 1.375
Moderately active (3-5x/week) × 1.55
Very active (6-7x/week)     × 1.725
```

Standard macro split from TDEE:
```
Protein: 30% of calories ÷ 4 kcal/g
Carbs:   40% of calories ÷ 4 kcal/g
Fat:     30% of calories ÷ 9 kcal/g
```

`calculate_tdee()` will be added to `utils.py` and called during user registration to auto-generate the first `MacroGoal`.

---

## Quick mental model

Think of variables as _sticky notes_ attached to objects. Reassigning moves the sticky note to a new object. Mutating changes the object itself — all sticky notes pointing to it see the change.
