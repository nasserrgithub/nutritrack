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

## 65 — SQLAlchemy — engine vs session

The engine is the connection pool manager — created once at app startup and lives for the app's lifetime. The session is a unit of work — short-lived, one per request.

```python
# engine — created once, never recreated
engine = create_engine("postgresql://user:pass@localhost/nutritrack")

# session — opened, used, closed per operation
session = Session()
session.add(food)
session.commit()
session.close()
```

Analogy: engine = a pool of database connections (shared, long-lived). Session = one conversation with the database (short-lived, per request).

In Phase 3, FastAPI creates one session per HTTP request and closes it when the request is done. The engine stays alive the whole time.

---

## 66 — `get_session()` context manager

Wraps session lifecycle so cleanup always happens — even if an exception occurs:

```python
@contextmanager
def get_session() -> Generator[Session, None, None]:
    session = SessionLocal()
    try:
        yield session
        session.commit()    # commits on clean exit
    except Exception as err:
        session.rollback()  # rolls back on exception — releases DB locks
        raise err
    finally:
        session.close()     # always closes — prevents connection leaks
```

Without rollback on exception — the transaction stays open, database holds row locks, other requests block. Without close in finally — connection leak exhausts the connection pool.

The caller never manages cleanup:

```python
with get_session() as session:
    session.add(food)
    # no manual commit needed — context manager handles it
```

---

## 67 — SQLAlchemy ORM models

ORM models map Python classes to database tables. All models inherit from `Base` (a `DeclarativeBase` subclass):

```python
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, Float, Integer, ForeignKey, func, DateTime
from nutritrack.db.base import Base

class FoodModel(Base):
    __tablename__ = "foods"

    id:               Mapped[int]           = mapped_column(Integer, primary_key=True, autoincrement=True)
    name:             Mapped[str]           = mapped_column(String(255), nullable=False, index=True)
    protein_per_100g: Mapped[float]         = mapped_column(Float, nullable=False)
    fiber_per_100g:   Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    created_at:       Mapped[datetime]      = mapped_column(DateTime, server_default=func.now())

    food_entries: Mapped[list["FoodEntryModel"]] = relationship(back_populates="food")
```

Key column options:
- `primary_key=True` — uniquely identifies each row, auto-indexed
- `autoincrement=True` — database assigns ID automatically on insert
- `nullable=False` — column required, cannot be NULL
- `index=True` — creates a B-tree index for fast lookups
- `server_default=func.now()` — database sets timestamp on insert
- `unique=True` — enforces uniqueness (e.g. email)

`Mapped[Optional[float]]` + `nullable=True` — must match. `Optional` is the Python type, `nullable` is the database constraint.

---

## 68 — SQLAlchemy relationships and `back_populates`

Relationships let you navigate between related objects without writing SQL joins:

```python
# without relationship — manual query needed
entries = session.query(FoodEntryModel).filter(FoodEntryModel.user_id == user.id).all()

# with relationship — SQLAlchemy does the join
entries = user.food_entries
```

`back_populates` creates a two-way link — must be defined on both sides, each referencing the attribute name on the other:

```python
class UserModel(Base):
    food_entries: Mapped[list["FoodEntryModel"]] = relationship(back_populates="user")

class FoodEntryModel(Base):
    user: Mapped["UserModel"] = relationship(back_populates="food_entries")
```

**Naming convention:**
- Foreign key column → `{model}_id` (e.g. `user_id`, `food_id`) — stores the integer
- Relationship attribute → `{model}` (e.g. `user`, `food`) — stores the Python object

**List vs single:**
- "One" side (user has many entries) → `Mapped[list["FoodEntryModel"]]`
- "Many" side (entry belongs to one user) → `Mapped["UserModel"]`

Relationships are optional — foreign keys alone are enough for the database to enforce the link. Relationships are a Python-level convenience.

---

## 69 — Foreign keys vs primary keys vs indexes

| | Primary key | Foreign key | Index |
|---|---|---|---|
| Purpose | Uniquely identifies a row | References another table's primary key | Speeds up queries |
| Unique? | Always | Not required | Optional |
| Per table | One | Many | Many |
| Auto-indexed? | Yes | No (add manually) | N/A |

```python
class FoodEntryModel(Base):
    id:      Mapped[int] = mapped_column(Integer, primary_key=True)          # PK
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True) # FK + index
    food_id: Mapped[int] = mapped_column(ForeignKey("foods.id"), index=True) # FK + index
```

Always index foreign key columns — every query filters by them, and without an index it's a full table scan.

---

## 70 — `Base` in its own file — avoiding circular imports

`Base` must be importable by both `models.py` and `database.py`. Putting it in `database.py` risks circular imports if `database.py` ever needs to import from `models.py`. Solution — give `Base` its own file:

```python
# nutritrack/db/base.py
from sqlalchemy.orm import DeclarativeBase

class Base(DeclarativeBase):
    pass
```

Then import from it everywhere:

```python
# database.py
from nutritrack.db.base import Base  # noqa: F401 — imported for Alembic

# models.py
from nutritrack.db.base import Base
```

`# noqa: F401` — tells linters not to flag `Base` as unused in `database.py`. It's imported there so Alembic can find all models through one entry point.

One-way dependency chain to prevent all circular imports:

```
base.py → nothing
exceptions.py → nothing
utils.py → exceptions
models.py (core) → utils, exceptions
db/base.py → nothing
db/models.py → db/base
db/database.py → db/base
db/repositories.py → db/models, db/database, core/exceptions
db/schemas.py → nothing (pure Pydantic)
db/seed.py → all of the above
```

---

## 71 — Alembic migrations — setup and usage

Alembic tracks database schema changes as versioned migration scripts. Each script has `upgrade()` and `downgrade()` so you can move forward or backward without losing data.

**One-time setup:**

```bash
# 1. initialize alembic (run from project root)
alembic init alembic

# 2. edit alembic.ini — leave sqlalchemy.url blank
sqlalchemy.url =

# 3. edit alembic/env.py — add at the top:
from dotenv import load_dotenv
import os
load_dotenv()
config.set_main_option("sqlalchemy.url", os.getenv("DATABASE_URL", ""))

# import Base and all models so Alembic can detect them
from nutritrack.db.base import Base
from nutritrack.db import models  # noqa: F401
target_metadata = Base.metadata
```

**Daily usage:**

```bash
# generate a migration from ORM model changes
alembic revision --autogenerate -m "add timezone to users"

# apply all pending migrations
alembic upgrade head

# roll back one migration
alembic downgrade -1

# see migration history
alembic history

# see current version
alembic current
```

**How it works:** `alembic_version` table in the database tracks which migrations have been applied. Each migration file has a `revision` ID and a `down_revision` pointing to its parent — forming a chain.

```
migration 001 (down_revision=None)    ← first migration
migration 002 (down_revision=001)
migration 003 (down_revision=002)     ← head
```

**PostgreSQL permissions needed:**

```sql
GRANT ALL PRIVILEGES ON DATABASE nutritrack TO nutritrack_user;
GRANT ALL ON SCHEMA public TO nutritrack_user;
ALTER DATABASE nutritrack OWNER TO nutritrack_user;
```

---

## 72 — Repository pattern

Repositories create an abstraction layer between application logic and database queries. Each model gets one repository that owns all its queries.

```python
class FoodRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def create(self, name: str, ...) -> FoodModel:
        food = FoodModel(name=name, ...)
        self.session.add(food)
        self.session.flush()   # assigns id without committing
        return food

    def get_by_id(self, food_id: int) -> FoodModel:
        food = self.session.get(FoodModel, food_id)
        if not food:
            raise FoodNotFoundError(str(food_id))
        return food

    def get_by_name(self, name: str) -> Optional[FoodModel]:
        return self.session.query(FoodModel)\
            .filter(FoodModel.name.ilike(f"%{name}%"))\
            .first()
```

Benefits:
- Single place for all queries — easy to find, debug, and change
- Testable — swap real repository for a fake in tests
- Readable — `food_repo.get_by_name("chicken")` vs raw SQLAlchemy query

Usage:

```python
with get_session() as session:
    repo = FoodRepository(session)
    food = repo.get_by_name("chicken breast")
```

---

## 73 — `session.get()` vs `session.query()`

| | `session.get()` | `session.query()` |
|---|---|---|
| Lookup by | primary key only | any column |
| Returns | one object or None | query builder |
| Cache check | yes — identity map | no |
| Use when | you have the ID | filtering/sorting/joining |

```python
# session.get — primary key lookup, checks identity map cache
food = session.get(FoodModel, 42)

# session.query — flexible filtering
food = session.query(FoodModel)\
    .filter(FoodModel.name.ilike("%chicken%"))\
    .first()

# .first() — returns first result or None, never raises
# .all()   — returns list of all results
# .one()   — returns exactly one, raises if 0 or more than 1
```

---

## 74 — `session.flush()` vs `session.commit()`

```python
session.flush()   # writes SQL to DB within current transaction — assigns auto-generated IDs
                  # not yet permanent — can still be rolled back

session.commit()  # makes all changes permanent — cannot be rolled back
```

Use `flush()` when you need the auto-generated `id` immediately (e.g. to log it or use it in another insert) but want to keep everything in one transaction.

---

## 75 — Return type design — `Optional` vs exception

```python
def get_by_id(self, food_id: int) -> FoodModel:        # raises FoodNotFoundError if missing
def get_by_name(self, name: str) -> Optional[FoodModel]: # returns None if missing
```

Rule of thumb:
- `Optional` return — absence is expected and normal (food might not exist yet — trigger AI lookup)
- Exception — absence is unexpected (you have an ID, it should exist)

The return type tells the caller what to expect. mypy catches cases where you use the result without checking for `None`.

---

## 76 — Pydantic schemas — three data shapes

The same entity has three different shapes:

```
Request  (what comes IN)   — user-provided fields only, no id, no created_at
Database (what's STORED)   — everything including id, timestamps, relationships
Response (what goes OUT)   — controlled subset, no sensitive fields
```

```python
class FoodCreate(BaseModel):         # request — what user sends
    name: str = Field(..., min_length=1, max_length=255)
    protein_per_100g: float = Field(..., ge=0)
    ...

class FoodResponse(BaseModel):       # response — what user receives
    id: int
    name: str
    protein_per_100g: float
    created_at: datetime
    model_config = {"from_attributes": True}
```

`user_id` never appears in request schemas — it comes from the JWT token. `id` and `created_at` never appear in create schemas — the database assigns them.

---

## 77 — Pydantic `Field()` constraints

```python
from pydantic import BaseModel, Field

class FoodCreate(BaseModel):
    name: str           = Field(..., min_length=1, max_length=255)  # required, length limits
    protein_per_100g: float = Field(..., ge=0)    # required, >= 0
    weight_g: float     = Field(..., gt=0)        # required, > 0 (strictly positive)
    age: int            = Field(..., ge=1, le=120) # required, 1-120
    source: str         = Field(default="manual") # optional with default
    logged_date: date   = Field(default_factory=date.today)  # dynamic default
```

- `...` — required, no default
- `ge` — greater than or equal (numbers)
- `gt` — greater than (numbers)
- `le` — less than or equal (numbers)
- `lt` — less than (numbers)
- `min_length`, `max_length` — string length limits
- `default` — static default value
- `default_factory` — callable called fresh on each instantiation

---

## 78 — `@field_validator` — custom validation logic

Use when `Field()` constraints aren't expressive enough:

```python
from pydantic import field_validator

class UserCreate(BaseModel):
    email: str

    @field_validator("email")
    @classmethod
    def validate_email(cls, v: str) -> str:
        if "@" not in v:
            raise ValueError("Invalid email — must contain @")
        return v   # must return the value
```

Rules:
- Must be `@classmethod`
- Must return the value (can transform it too e.g. `return v.lower()`)
- Can validate multiple fields: `@field_validator("protein_g", "carbs_g", "fat_g")`

Use `Field()` constraints for simple rules. Use `@field_validator` for logic that can't be expressed as a simple constraint.

---

## 79 — `model_config = {"from_attributes": True}`

Tells Pydantic to read from object attributes, not just dict keys. Required on response schemas that convert SQLAlchemy objects to Pydantic models:

```python
class FoodResponse(BaseModel):
    id: int
    name: str
    model_config = {"from_attributes": True}

food_model = session.get(FoodModel, 1)         # SQLAlchemy object
response = FoodResponse.model_validate(food_model)  # reads food_model.id, food_model.name
```

Without it — `model_validate()` only works with dicts, not SQLAlchemy objects.

Only needed on response schemas — request schemas receive plain JSON dicts from FastAPI.

---

## 80 — `model_validate()` and `model_dump()`

```python
# model_validate — create Pydantic model from dict or object
food_data = {"id": 1, "name": "chicken breast"}
response = FoodResponse.model_validate(food_data)

food_orm = session.get(FoodModel, 1)
response = FoodResponse.model_validate(food_orm)   # needs from_attributes: True

# model_dump — convert Pydantic model back to dict
food_create = FoodCreate(name="chicken", protein_per_100g=31.0, ...)
food_create.model_dump()
# {"name": "chicken", "protein_per_100g": 31.0, ...}
```

Full API flow in NutriTrack:

```
POST /foods {"name": "chicken", ...}
    ↓
FoodCreate.model_validate(request_body)   # validate incoming JSON
    ↓
FoodRepository.create(**food_create.model_dump())  # save to DB
    ↓
FoodResponse.model_validate(food_model)   # convert DB object to response
    ↓
{"id": 1, "name": "chicken", "created_at": "..."}
```

---

## 81 — Why Pydantic AND SQLAlchemy constraints

Both serve different purposes — neither replaces the other:

```
Layer 1 — Pydantic     ← catches bad data at API boundary, fast, user-friendly errors
Layer 2 — SQLAlchemy   ← type mapping
Layer 3 — PostgreSQL   ← last resort safety net
```

Pydantic fails fast — bad data is rejected before any DB round trip. PostgreSQL constraint errors are cryptic; Pydantic errors are clean JSON the frontend can display. PostgreSQL constraints protect data integrity even if something bypasses the API (seed scripts, direct inserts, other services).

Response schemas have no constraints — data coming out of the database has already been validated twice on the way in.

---

## 82 — Database seeding and idempotency

A seed script pre-populates the database with initial data. Must be **idempotent** — running it multiple times produces the same result as running it once. Check before inserting:

```python
def seed_foods():
    csv_path = Path(__file__).parent.parent.parent / "data" / "foods.csv"
    with get_session() as session:
        fr = FoodRepository(session)
        for food in parse_food_csv(csv_path):
            if fr.get_by_name(food.name):
                logger.info(f"Skipping {food.name} — already exists")
                continue
            fr.create(name=food.name, ...)

if __name__ == "__main__":
    seed_foods()
```

Run with: `python -m nutritrack.db.seed`

One session for the entire operation — not one per food. Batch inserts are one transaction, one commit, much faster than N separate transactions.

---

## 83 — `Path(__file__)` — file-relative paths

`__file__` holds the absolute path of the current file. Use `.parent` to navigate up the directory tree, `/` to join path segments:

```python
from pathlib import Path

# inside nutritrack/db/seed.py
Path(__file__)                           # nutritrack/db/seed.py
Path(__file__).parent                    # nutritrack/db/
Path(__file__).parent.parent             # nutritrack/
Path(__file__).parent.parent.parent      # project root
Path(__file__).parent.parent.parent / "data" / "foods.csv"  # project root/data/foods.csv
```

Safer than relative paths like `"data/foods.csv"` — relative paths depend on where you run the script from. `Path(__file__)` always knows where the file itself lives.

---

## 84 — YAGNI — You Aren't Gonna Need It

Only add code when there is a real use case for it. Don't build `get_by_food_id()` on `FoodEntryRepository` just because it might be useful someday — add it when a feature actually needs it.

Benefits: less code to maintain, less surface area for bugs, cleaner codebase. If a feature needs it in a later phase, add it then.

Applied in NutriTrack: `FoodEntryRepository` only has `get_by_user()` and `get_by_user_and_date()` — the two queries the dashboard actually needs.

---

## 85 — NutriTrack Phase 2 file structure

```
nutritrack/
├── data/
│   └── foods.csv              ← seed data (stays at project root, not in package)
├── alembic/
│   ├── env.py                 ← configured to load DATABASE_URL from .env
│   └── versions/
│       └── 2a6551a59786_initial_tables.py
├── alembic.ini                ← sqlalchemy.url left blank (loaded from .env)
├── nutritrack/
│   ├── core/                  ← Phase 1 (unchanged)
│   └── db/
│       ├── __init__.py
│       ├── base.py            ← DeclarativeBase — own file to avoid circular imports
│       ├── database.py        ← engine, SessionLocal, get_session()
│       ├── models.py          ← SQLAlchemy ORM models for all 5 tables
│       ├── repositories.py    ← FoodRepository, UserRepository, FoodEntryRepository
│       ├── schemas.py         ← Pydantic request/response schemas
│       └── seed.py            ← idempotent seed script
└── .env                       ← DATABASE_URL (never committed to git)
```

---

## 86 — REST — Representational State Transfer

REST is a set of conventions for designing APIs that use HTTP in a predictable, consistent way. Everything is a resource, and you interact with resources using standard HTTP methods.

```
GET    /foods          → read all foods
GET    /foods/1        → read food with id=1
POST   /foods          → create a new food
PUT    /foods/1        → update food with id=1
DELETE /foods/1        → delete food with id=1
```

HTTP status codes carry meaning:
```
200 OK           → success
201 Created      → resource created
400 Bad Request  → malformed request
401 Unauthorized → not logged in
403 Forbidden    → logged in but not allowed
404 Not Found    → resource doesn't exist
422 Unprocessable → validation failed
500 Server Error → something broke on the server
503 Service Unavailable → external service down
```

Before REST, APIs used RPC-style — action-based URLs with no consistency:
```
GET /getAllFoods
POST /createNewFood
POST /deleteFood?id=1   ← POST for a delete? confusing
```

REST improved predictability — a developer who knows REST conventions can guess your API's endpoints without documentation.

---

## 87 — FastAPI basics

FastAPI is a Python web framework for building REST APIs. A Python function becomes an HTTP endpoint by decorating it with `@app.get()`, `@app.post()`, etc.:

```python
from fastapi import FastAPI

app = FastAPI(
    title="NutriTrack API",
    description="Food calorie and macro tracker",
    version="0.1.0",
)

@app.get("/health")
def health_check():
    return {"status": "ok"}
```

FastAPI automatically:
- Parses and validates request bodies using Pydantic
- Serializes responses to JSON
- Generates interactive API docs at `/docs`
- Returns 422 for validation errors

Run with uvicorn:
```bash
uvicorn nutritrack.api.main:app --reload
```

`--reload` restarts the server on file changes — essential during development.

---

## 88 — FastAPI routers

Routers group related endpoints. Instead of defining everything in one file, split by feature:

```python
# foods.py
from fastapi import APIRouter
router = APIRouter()

@router.get("/")
def get_foods(): ...

@router.post("/")
def create_food(): ...
```

```python
# main.py
from nutritrack.api.routers import foods

app.include_router(foods.router, prefix="/foods", tags=["foods"])
# prefix="/foods" → all routes in foods.router get /foods prepended
# tags=["foods"]  → groups endpoints in /docs
```

`GET /` in `foods.py` + `prefix="/foods"` = `GET /foods/`

---

## 89 — FastAPI lifespan — startup and shutdown

`lifespan` runs code at app startup (before `yield`) and shutdown (after `yield`):

```python
from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    setup_logging()                        # startup
    logger.info("API starting up")
    yield
    logger.info("API shutting down")       # shutdown

app = FastAPI(lifespan=lifespan)
```

Use for: initializing logging, connecting to services, loading models. Replaces the deprecated `@app.on_event("startup")` pattern.

---

## 90 — Dependency injection with `Depends()`

`Depends()` tells FastAPI to call a function and inject its result as a parameter. Used for shared logic like session management and authentication:

```python
from fastapi import Depends

def get_db_session():
    session = SessionLocal()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()

@router.get("/foods")
def get_foods(session: Session = Depends(get_db_session)):
    #                             ↑ FastAPI calls get_db_session() and injects result
    return FoodRepository(session).get_all()
```

Dependencies can depend on other dependencies — FastAPI resolves the chain automatically. Write logic once, inject everywhere.

Unused dependencies (gate-only) use underscore prefix:
```python
def create_food(_user: UserModel = Depends(get_current_user), ...):
    # _user just validates the token — value not needed in function body
```

---

## 91 — JWT authentication

JWT (JSON Web Token) is stateless authentication — the server never stores session state.

**Flow:**
```
1. user logs in → server creates signed token containing user_id
2. server returns token to client
3. client sends token in every request header: Authorization: Bearer <token>
4. server validates signature → knows who the user is
```

**Token structure — three parts separated by dots:**
```
header.payload.signature
eyJhbGciOiJIUzI1NiJ9.eyJzdWIiOiI0MiJ9.abc123
```

- Header — algorithm used (`HS256`)
- Payload — your data (`{"sub": "42", "exp": 1234567890}`) — base64 encoded, NOT encrypted
- Signature — `HMAC(header + payload, SECRET_KEY)` — proves it wasn't tampered with

**Why stateless scales better:**
- Traditional sessions store state on the server — all servers must share session state (Redis)
- JWT is self-validating — any server recomputes the signature using `SECRET_KEY` and verifies it matches
- No shared state needed — add servers freely without coordination

**Security:** only the server knows `SECRET_KEY`. Client carries the token but can't forge it without the key. Never put sensitive data in the payload — it's readable by anyone (base64, not encrypted).

```python
from jose import jwt
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)

def create_access_token(user_id: int) -> str:
    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    payload = {"sub": str(user_id), "exp": expire}
    return jwt.encode(payload, SECRET_KEY, algorithm="HS256")
    # jwt.encode() builds header automatically, computes HMAC signature
```

Use `datetime.now(timezone.utc)` not deprecated `datetime.utcnow()`.

---

## 92 — `get_current_user()` dependency

Validates JWT and returns the authenticated user. Injected into any protected endpoint:

```python
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

security = HTTPBearer()

def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    session: Session = Depends(get_db_session),
) -> UserModel:
    token = credentials.credentials   # extract raw token string
    user_id = decode_access_token(token)
    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid token")
    user = session.get(UserModel, user_id)
    if not user or not user.is_active:
        raise HTTPException(status_code=401, detail="User not found or inactive")
    return user
```

`HTTPBearer` reads `Authorization: Bearer <token>` header automatically. `credentials.credentials` extracts the raw token string.

---

## 93 — HTTP status codes in FastAPI

```python
from fastapi import status

@router.post("/", status_code=status.HTTP_201_CREATED)   # 201 for creates
@router.get("/")                                          # 200 default for reads
```

Using `status.HTTP_201_CREATED` instead of `201` is more readable and avoids magic numbers. Common ones:

```
HTTP_200_OK
HTTP_201_CREATED
HTTP_400_BAD_REQUEST
HTTP_401_UNAUTHORIZED
HTTP_403_FORBIDDEN
HTTP_404_NOT_FOUND
HTTP_422_UNPROCESSABLE_ENTITY
HTTP_500_INTERNAL_SERVER_ERROR
HTTP_503_SERVICE_UNAVAILABLE
```

---

## 94 — `response_model` vs return type hint

```python
@router.get("/foods", response_model=list[FoodResponse])
def get_foods(...) -> list[FoodResponse]:
```

Both look similar but serve different purposes:

- `-> list[FoodResponse]` — tells mypy and IDE the return type (static analysis)
- `response_model=list[FoodResponse]` — tells FastAPI to validate and serialize the response, and shows the correct schema in `/docs`

Without `response_model` — FastAPI doesn't validate the output and `/docs` shows no response schema. Always include both.

---

## 95 — Global exception handlers

Register once on the `app` object — catches exceptions from any endpoint automatically:

```python
from fastapi import Request
from fastapi.responses import JSONResponse

@app.exception_handler(FoodNotFoundError)
async def food_not_found_handler(request: Request, exc: FoodNotFoundError):
    return JSONResponse(status_code=404, content={"detail": str(exc)})

@app.exception_handler(GoalNotSetError)
async def goal_not_set_handler(request: Request, exc: GoalNotSetError):
    return JSONResponse(status_code=404, content={"detail": str(exc)})

@app.exception_handler(InvalidMacroError)
async def invalid_macro_handler(request: Request, exc: InvalidMacroError):
    return JSONResponse(status_code=422, content={"detail": str(exc)})

@app.exception_handler(AIServiceError)
async def ai_service_handler(request: Request, exc: AIServiceError):
    return JSONResponse(status_code=503, content={"detail": str(exc)})
```

**Each handler must have a unique function name** — Python overwrites duplicate names, leaving only the last one active.

Without global handlers — every endpoint needs try/except. With them — endpoints are clean, exceptions propagate naturally:

```python
# clean endpoint — no try/except needed
@router.get("/{food_id}")
def get_food(food_id: int, session = Depends(get_db_session)):
    food = FoodRepository(session).get_by_id(food_id)   # raises FoodNotFoundError
    return FoodResponse.model_validate(food)             # global handler catches it → 404
```

---

## 96 — Middleware

Middleware wraps every request and response — runs before the endpoint and after it returns:

```
request → middleware (before) → endpoint → middleware (after) → response
```

Use for cross-cutting concerns: logging, CORS, rate limiting, compression.

```python
import time
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request as StarletteRequest

class RequestLoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: StarletteRequest, call_next: RequestResponseEndpoint):
        start = time.perf_counter()
        response = await call_next(request)   # passes request to next layer/endpoint
        duration = time.perf_counter() - start
        logger.info(f"{request.method} {request.url.path} → {response.status_code} ({duration:.3f}s)")
        return response

app.add_middleware(RequestLoggingMiddleware)
```

`call_next` — injects by Starlette, passes the request to the next middleware or endpoint. Without it, the request never reaches the endpoint. Must be `await`ed since it's async.

`BaseHTTPMiddleware` requires overriding exactly one method — `dispatch` — with `(self, request, call_next)` signature. Any other methods are regular class methods.

---

## 97 — CORS middleware

CORS (Cross-Origin Resource Sharing) is a browser security mechanism that blocks requests from a different domain. When React on `localhost:3000` calls FastAPI on `localhost:8000`, the browser sees different origins and blocks it.

CORS middleware adds headers to every response telling the browser which origins are allowed:

```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],        # allow all origins (development)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

In production, restrict to the frontend's domain:
```python
allow_origins=["https://nutritrack.yourdomain.com"]
```

CORS is browser-only — it doesn't affect Postman, curl, or Python requests.

---

## 98 — Starlette

FastAPI is built on top of Starlette. Starlette handles the core HTTP mechanics — routing, requests, responses, middleware, WebSockets.

```
Your code
    ↓
FastAPI        ← Pydantic validation, dependency injection, auto docs
    ↓
Starlette      ← HTTP handling, routing, middleware, requests, responses
    ↓
Uvicorn        ← server that listens for connections
```

When you use `Request`, `JSONResponse`, or `BaseHTTPMiddleware` — those come from Starlette. FastAPI re-exports most of them, but for middleware `BaseHTTPMiddleware` is imported directly from Starlette.

---

## 99 — pydantic-settings — centralized config

`pydantic-settings` reads environment variables and `.env` files, validates and types them:

```python
from pydantic_settings import BaseSettings
from functools import lru_cache

class Settings(BaseSettings):
    database_url: str = ""             # reads DATABASE_URL from .env
    secret_key: str = "changeme"       # reads SECRET_KEY from .env
    access_token_expire_minutes: int = 60 * 24
    environment: str = "development"

    model_config = {"env_file": ".env"}

@lru_cache
def get_settings() -> Settings:
    return Settings()
```

`@lru_cache` — caches the `Settings` instance so `.env` is only read once at startup, not on every call. Fields with no default are required — app raises `SettingsError` immediately at startup if missing (fail fast). Fields with defaults are optional.

`database_url: str = ""` — empty string satisfies mypy (which can't see `.env`) while the real value comes from the environment at runtime.

---

## 100 — ORM to dataclass conversion

SQLAlchemy ORM objects need to be converted to Phase 1 dataclasses for computation (e.g. `MacroAggregator`). Use SQLAlchemy relationships to access related data:

```python
def orm_to_food_entry(entry: FoodEntryModel) -> FoodEntry:
    food = Food(
        name=entry.food.name,              # entry.food uses SQLAlchemy relationship
        protein_per_100g=entry.food.protein_per_100g,
        carbs_per_100g=entry.food.carbs_per_100g,
        fat_per_100g=entry.food.fat_per_100g,
        fiber_per_100g=entry.food.fiber_per_100g,
        source=entry.food.source,
    )
    return FoodEntry(
        food=food,
        weight_g=entry.weight_g,
        logged_date=entry.logged_date,
        meal_slot=entry.meal_slot,
    )
```

`entry.food` — SQLAlchemy automatically loads the related `FoodModel` when accessed. No extra query needed.

Skip `FoodEntryResponse` as an intermediate step — convert directly from ORM to dataclass. Response schemas are only for API output, not for internal data transformation.

---

## 101 — Read operations vs write operations — auth requirements

Standard REST security pattern:

```
GET    → public (reading data, no harm if unauthenticated)
POST   → auth required (creates a record)
PUT    → auth required (updates a record)
DELETE → auth required (deletes a record)
```

`user_id` never comes from the request body — it comes from the JWT token via `get_current_user()`. This prevents a user from logging food for another user.

---

## 102 — `FoodNotFoundError` in endpoint vs repository

The repository raises a Python exception. The endpoint maps it to an HTTP response. Two separate layers:

```
repository raises FoodNotFoundError   ← Python layer
    ↓
global exception handler catches it
    ↓
returns HTTP 404 to client            ← HTTP layer
```

Without the handler — FastAPI returns 500. With it — client receives meaningful 404. The repository's job is raising the right exception. The endpoint/handler's job is translating it to HTTP.

---

## 103 — async/await and the event loop

`async def` marks a function as a coroutine — it can pause at `await` and let other code run while waiting.

```python
# sync — blocks everything while waiting
def get_food():
    food = database.query(...)   # blocks 30ms — nothing else runs
    return food

# async — pauses and lets other requests run while waiting
async def get_food():
    food = await database.query(...)   # pauses 30ms — other requests run
    return food
```

**The event loop** is a single loop that manages all async operations:
```
event loop:
    check: any tasks ready to resume?
    yes → resume task, run until next await
    no  → wait for I/O to complete
    repeat forever
```

Like a restaurant manager moving between tables during waiting periods — not doing multiple things simultaneously, but making progress on all of them during waits.

**Concurrency vs parallelism:**
```
Concurrency  — one worker switching between tasks during waits (async/await)
Parallelism  — multiple workers truly doing things simultaneously (threading/multiprocessing)
```

Async gives concurrency — enough for most web servers where most time is waiting for I/O.

---

## 104 — When to use `async def` vs `def` in FastAPI

```
sync library (SQLAlchemy, psycopg2)  → use def
async library (httpx, aiohttp)       → use async def
middleware                           → always async def (Starlette requires it)
exception handlers                   → always async def (FastAPI requires it)
utility functions (pure computation) → def
```

FastAPI runs `def` endpoints in a thread pool — they don't block the event loop. Using `async def` with synchronous SQLAlchemy would actually block the event loop — worse performance.

The rule: **a function should be `async def` if it needs to `await` something inside it.**

```python
# needs async def — calls await
async def get_macros_from_ai(food_name: str):
    async with httpx.AsyncClient() as client:
        response = await client.post(...)
    return response.json()

# plain def — no await needed
def get_food(session: Session):
    return session.query(FoodModel).all()
```

---

## 105 — Concurrency and web servers

Concurrency — dealing with multiple requests at the same time without doing them strictly sequentially.

**Without async (sync thread pool):**
```
FastAPI default thread pool: ~40 threads
1000 concurrent requests → 40 handled, 960 queue up
response times grow as queue grows
```

**With async (event loop):**
```
1000 concurrent requests → all start immediately
each pauses at await, letting others progress
total time ≈ time for one request
```

**Real NutriTrack example — dashboard load (3 simultaneous requests):**
```
sync:   request 1 (30ms) + request 2 (30ms) + request 3 (30ms) = 90ms
async:  all 3 start simultaneously, all pause at DB query, all respond = ~30ms
```

**Where async matters most in NutriTrack — AI calls (Phase 4):**
```
sync:  40 threads tied up for 800ms AI call = 40 AI requests max in flight
async: 1000 AI requests in flight, event loop serves other users during 800ms wait
```

While one user waits 800ms for the AI, all other users get instant responses.

---

## 106 — NutriTrack Phase 3 file structure

```
nutritrack/
└── nutritrack/
    └── api/
        ├── __init__.py
        ├── main.py           ← app, routers, CORS, lifespan, exception handlers, middleware
        ├── dependencies.py   ← get_db_session(), get_current_user()
        ├── auth_utils.py     ← JWT creation/validation, bcrypt password hashing
        ├── settings.py       ← pydantic-settings config class
        └── routers/
            ├── __init__.py
            ├── auth.py       ← POST /auth/register, POST /auth/login
            ├── foods.py      ← GET /foods, GET /foods/{id}, POST /foods
            ├── logs.py       ← POST /log, GET /log/{date}
            ├── goals.py      ← POST /goals, GET /goals/active
            └── summary.py    ← GET /summary/{date} — wires MacroAggregator
```

Key dependencies used from previous phases:
- Phase 1: `MacroAggregator`, `Food`, `FoodEntry`, `MacroGoal` dataclasses, `setup_logging()`
- Phase 2: all repositories, all Pydantic schemas, `get_db_session()`

---

## 107 — Prompt engineering — getting structured output from AI

The quality of the AI's response depends entirely on how well you write the prompt. For structured data, you must be explicit — tell the AI exactly what format to return and what not to include.

**Bad prompt:**
```
"What are the macros for chicken adobo?"
→ AI returns: "Chicken adobo is a Filipino dish. Per 100g it contains approximately 18-20g of protein..."
```
Unparseable — too much text, ranges instead of numbers, no structure.

**Good prompt:**
```
"You are a nutrition database. Return ONLY raw JSON with no markdown, no code fences, no backticks, no explanation.
The response must start with { and end with }.
Return macros per 100g for: chicken adobo
Required format: {"protein_per_100g": <float>, ...}
If the food is unknown, return: {"error": "unknown_food"}"
```
Returns clean, parseable JSON every time.

Key principles:
- Be explicit about format — show the exact JSON structure
- Say what NOT to do — "no markdown, no code fences, no explanation"
- Handle edge cases — tell the AI what to return for unknown inputs
- Use `f-strings` with `{{}}` for literal braces inside f-strings

---

## 108 — Markdown fence stripping

Even with explicit "no markdown" instructions, some AI models wrap responses in code fences:

```
```json
{"protein_per_100g": 18.5, ...}
```
```

Strip defensively — extract it into a helper:

```python
def _strip_markdown_fences(text: str) -> str:
    text = text.strip()
    if text.startswith("```"):
        text = text.split("```")[1]
        if text.startswith("json"):
            text = text[4:]
        text = text.strip()
    return text
```

Call before `json.loads()` in every AI client function. If the AI returns clean JSON, the function is a no-op. If it wraps in fences, it strips them.

---

## 109 — Anthropic async client

```python
import anthropic
from anthropic.types import TextBlock

client = anthropic.AsyncAnthropic(api_key=settings.anthropic_api_key)

response = await client.messages.create(
    model="claude-sonnet-4-5",
    max_tokens=256,
    messages=[{"role": "user", "content": prompt}],
)

block = response.content[0]
if not isinstance(block, TextBlock):
    raise AIServiceError(f"Unexpected response block type: {type(block)}")
text = block.text
```

`response.content[0]` can be many block types (`TextBlock`, `ToolUseBlock`, etc.) — mypy requires an `isinstance` check before accessing `.text`. Without the check, mypy raises a union-attr error.

`await` applies only to the coroutine — chain attribute access after:
```python
# ❌ wrong — can't chain after await
response = await client.messages.create(...).content[0].text

# ✅ correct — await the coroutine, then access attributes
response = await client.messages.create(...)
text = response.content[0].text
```

---

## 110 — `max_tokens` in AI API calls

`max_tokens` limits the length of the AI's response in tokens (roughly 1 token per word). If the response would exceed this limit, it gets cut off mid-response.

```python
max_tokens=256    # ~200 words — fine for a single JSON object
max_tokens=1024   # ~800 words — needed for lists with reason strings
```

Choose based on expected response size:
- Single JSON object (macro lookup) → 256 is enough
- JSON array with descriptions (suggestions, natural language) → use 1024+

---

## 111 — DB-first AI caching strategy

AI calls are expensive — avoid calling the API for the same food multiple times. Check the database first:

```python
food = food_repo.get_by_name(food_entry.food_name)

if not food:
    # only call AI if not in DB
    macros = await lookup_food_macros(food_entry.food_name)
    food = food_repo.create(
        name=food_entry.food_name,
        source="ai_lookup",
        **macros
    )
# food is now in DB — next lookup finds it without AI call
```

Result: AI called exactly once per unique food name ever. The `source="ai_lookup"` field tracks which foods came from AI vs CSV vs manual entry.

---

## 112 — Natural language meal parsing

One AI call can extract multiple foods from free text, estimate weights, and return macros — all at once:

```
Input: "I had oatmeal with banana and two eggs for breakfast"
Output: [
    {"food_name": "oatmeal", "weight_g": 80, "protein_per_100g": 17.0, ...},
    {"food_name": "banana", "weight_g": 118, "protein_per_100g": 1.1, ...},
    {"food_name": "whole egg", "weight_g": 120, "protein_per_100g": 13.0, ...}
]
```

One API call instead of three — cheaper and faster. The endpoint then loops through results, checks DB for each food, creates if missing, and creates a `FoodEntry` per food.

---

## 113 — `asyncio.run()` — running async code from sync context

In a synchronous context (shell, script, test), use `asyncio.run()` to run a coroutine:

```python
import asyncio

# can't call async function directly from sync code
result = lookup_food_macros("chicken breast")   # ❌ returns coroutine, not result

# asyncio.run() creates event loop, runs coroutine, returns result
result = asyncio.run(lookup_food_macros("chicken breast"))   # ✅
```

For testing async functions — write a `tester.py` script at project root rather than using the interactive shell (Git Bash doesn't support arrow key history in Python shell).

---

## 114 — Error handling in AI clients — exception ordering

When catching exceptions in AI client functions, always re-raise known exceptions before the catch-all:

```python
try:
    ...
    raise FoodNotFoundError(food_name)   # known exception
    ...
except FoodNotFoundError:
    raise                                # re-raise as-is — don't wrap it
except Exception as exc:
    raise AIServiceError(str(exc))       # wrap unknown exceptions
```

Without the specific `except FoodNotFoundError` — it gets caught by `except Exception` and wrapped as `AIServiceError`, losing the original exception type. The global exception handler maps `FoodNotFoundError` → 404 and `AIServiceError` → 503 — so the distinction matters.

---

## 115 — AI suggestions — context-aware prompts

For suggestions, the prompt must include the user's current state as context. The AI reads remaining macros and goal totals, then suggests specific foods with portions and reasons:

```python
def daily_suggestions_prompt(remaining: dict, goal: dict) -> str:
    return f"""You are a nutrition database. Return ONLY raw JSON...
    
The remaining macros are {remaining} and the goal is {goal}.
Give 3-5 food suggestions that help hit the remaining macros.
Each suggestion: {{"food_name": ..., "weight_g": ..., "reason": ...}}
Return as a JSON array.""".strip()
```

The AI uses `remaining` to understand the gap and suggests foods specifically targeting that gap — not generic recommendations.

---

## 116 — `model_validate()` with plain dicts

`model_validate()` works with both SQLAlchemy objects and plain dicts:

```python
# from dict (AI response)
suggestion = SuggestionResponse.model_validate({
    "food_name": "chicken breast",
    "weight_g": 150,
    "reason": "High protein"
})

# from SQLAlchemy object (needs from_attributes: True)
response = FoodResponse.model_validate(food_orm_object)
```

Response schemas that only receive dicts (like `SuggestionResponse`) don't need `model_config = {"from_attributes": True}` — that's only needed when reading from ORM objects.

---

## 117 — Path parameters in FastAPI — no defaults allowed

Path parameters are part of the URL — they are always required. You cannot give them default values:

```python
# ❌ wrong — path parameters can't have defaults
@router.get("/{summary_date}/suggestions")
async def get_suggestions(summary_date: date = date.today()):

# ✅ correct — required path parameter
@router.get("/{summary_date}/suggestions")
async def get_suggestions(summary_date: date):
```

If you want an optional date that defaults to today, use a **query parameter** instead:

```python
@router.get("/suggestions")
async def get_suggestions(summary_date: date = Query(default_factory=date.today)):
```

Query parameters appear after `?` in the URL: `/suggestions?summary_date=2026-06-11`

---

## 118 — JWT token expiry and re-authentication

Tokens expire after the configured duration (`ACCESS_TOKEN_EXPIRE_MINUTES`). When expired:
- `decode_access_token()` returns `None` (the `JWTError` catches expiry)
- `get_current_user()` raises `HTTP 401 Unauthorized`
- Client must call `POST /auth/login` again to get a fresh token

Two common patterns:

```
Pattern 1 — Single token (NutriTrack):
access_token expires in 24h → user logs in again
Simple but worse UX for long sessions

Pattern 2 — Refresh tokens:
access_token expires in 15min
refresh_token expires in 30 days
client silently refreshes access_token using refresh_token
Better UX — user never sees login screen
```

NutriTrack uses Pattern 1 — 24 hours is reasonable for a daily tracking app.

---

## 119 — NutriTrack Phase 4 file structure

```
nutritrack/
└── nutritrack/
    └── ai/
        ├── __init__.py
        ├── client.py      ← async Anthropic API calls with fence stripping and error handling
        └── prompts.py     ← prompt template functions
```

New endpoints added to Phase 3 routers:
```
POST /log              ← updated: AI fallback when food not in DB
POST /log/natural      ← new: natural language meal logging
GET  /summary/{date}/suggestions  ← new: AI food suggestions
```

New schemas added to `schemas.py`:
```
NaturalMealLog         ← text, meal_slot, logged_date
SuggestionResponse     ← food_name, weight_g, reason
```

---

## 120 — Triple-quoted strings and f-strings for prompts

Triple-quoted strings preserve newlines and indentation — ideal for prompts:

```python
prompt = f"""
Return ONLY a JSON object for: {food_name}
No markdown, no explanation.
Format: {{"protein_per_100g": <float>}}
""".strip()
```

Inside f-strings, `{{` and `}}` are literal curly braces (not format placeholders). `.strip()` removes leading/trailing whitespace from the triple-quoted string.

Three ways to write multiline strings:
```python
# triple quotes — preserves newlines
prompt = """line one
line two"""

# implicit concatenation — no newlines
prompt = ("line one "
          "line two")

# backslash continuation — no newlines
prompt = "line one " \
         "line two"
```

Use triple quotes for prompts — the structure is readable in code exactly as the AI sees it.

---

## 121 — Why `field(default_factory=date.today)` and not `date.today()` — deeper explanation

Three options and what actually happens at class definition time:

```python
# option 1 — calls date.today() ONCE when Python loads the class
logged_date: date = date.today()
# Result: every instance ever created shares the same hardcoded date

# option 2 — stores the function object as the value, never calls it
logged_date: date = date.today
# Result: logged_date becomes the function itself, not a date

# option 3 — correct: stores the function, calls it fresh on each instantiation
logged_date: date = field(default_factory=date.today)
# Result: date.today() called fresh every time a new instance is created
```

`default_factory` is the instruction to CALL the function — not just hold it. Same rule applies to mutable defaults like lists — never `tags: list = []`, always `tags: list = field(default_factory=list)`.

---

## 122 — How Python decides if a variable is local — compile-time scoping

Python decides a variable's scope for the **entire function** at compile time based on whether any assignment to that name exists anywhere in the function body:

```python
x = 10

def foo():
    print(x)   # UnboundLocalError — even though x=10 exists outside!
    x = 20     # this assignment makes Python treat x as local EVERYWHERE in foo
```

Python sees `x =` on line 2 and marks `x` as local for the entire function — including line 1. At runtime, line 1 tries to read `x` from local scope, finds nothing, and raises `UnboundLocalError`.

Without the assignment:
```python
def foo():
    print(x)   # works fine — no assignment, so Python looks in enclosing/global scope
```

This is why the list trick works for closures — `last_called[0] = value` mutates the list contents without reassigning `last_called` itself, so Python never marks it as local.

---

## 123 — Why `validate_macros` decorator checks `endswith("_g")` not `endswith("_per_100g")`

A subtle gotcha tested in practice:

```python
"protein_per_100g".endswith("_g")     # False — ends with "0g" not "_g"
"protein_per_100g".endswith("_per_100g")  # True
"protein_g".endswith("_g")            # True
```

The string `"protein_per_100g"` ends with `"0g"` — the last two characters are `0` and `g`, not `_` and `g`. So `endswith("_g")` does NOT catch `_per_100g` fields.

The correct check needs both conditions:
```python
if macro_type.endswith("_g") or macro_type.endswith("_per_100g"):
```

Always verify string operations in the Python shell before assuming — `"protein_per_100g".endswith("_g")` returning `False` is counterintuitive but correct.

---

## 124 — `current_delay = delay` must be outside the retry loop

A common bug — placing `current_delay = delay` inside the loop resets it on every iteration, defeating exponential backoff:

```python
# ❌ wrong — resets every iteration
while attempts < times:
    try:
        ...
    except Exception:
        current_delay = delay       # reset to original every time
        time.sleep(current_delay)
        current_delay *= backoff    # multiplied but immediately reset next iteration

# ✅ correct — initialized once, grows across iterations
current_delay = delay               # outside the loop
while attempts < times:
    try:
        ...
    except Exception:
        time.sleep(current_delay)
        current_delay *= backoff    # grows: 1 → 2 → 4 → 8
        attempts += 1
```

---

## 125 — Why `last_called[0]` updates on every call, not just when sleeping

In `@rate_limit`, the timestamp must update whether or not a sleep occurred:

```python
with lock:
    elapsed = time.perf_counter() - last_called[0]
    if elapsed < interval_s:
        time.sleep(interval_s - elapsed)
    last_called[0] = time.perf_counter()   # ← always update, outside the if
```

If `last_called[0]` only updates inside the `if` (when sleeping), then calls that don't need to sleep never update the timestamp. The next call then calculates elapsed against a stale value and may fire too early.

---

## 126 — `ilike` in SQLAlchemy — case-insensitive search

```python
session.query(FoodModel).filter(FoodModel.name.ilike(f"%{name}%")).first()
```

`ilike` — case-insensitive LIKE. Searching "chicken" matches "Chicken Breast", "CHICKEN", "chicken breast". The `%` wildcards match any characters before and after the search term.

Used in `FoodRepository.get_by_name()` so users can type "Chicken" and find "chicken breast" without exact case matching.

---

## 127 — `session.flush()` — get auto-generated ID without committing

```python
self.session.add(food)
self.session.flush()   # writes SQL, assigns id, stays in transaction
logger.info(f"Created food: {food.name} (id={food.id})")  # id is now available
return food
```

Without `flush()` — `food.id` is `None` because the database hasn't assigned it yet. With `flush()` — the INSERT runs within the current transaction, the database assigns the ID, and it's available in Python. The transaction can still be rolled back — `flush()` is not permanent.

---

## 128 — Why the function call is OUTSIDE the lock in `@rate_limit`

```python
with lock:
    # timing check and timestamp update only — microseconds
    elapsed = time.perf_counter() - last_called[0]
    if elapsed < interval_s:
        time.sleep(interval_s - elapsed)
    last_called[0] = time.perf_counter()
# lock released here

return func(*args, **kwargs)   # actual function call — outside lock
```

If the function call is inside the lock:
- Thread 1 acquires lock → sleeps 0.5s → calls func (800ms AI call) → lock held for 800ms
- Thread 2 waits 800ms just to get to the timing check — blocked by func, not rate limiting

The lock's only job is protecting `last_called[0]` from race conditions — a microsecond operation. Holding it during the actual function call blocks all threads for the full function duration unnecessarily.

---

## 129 — Python logging tree — why modules don't need to call `basicConfig()`

Every module creates its own named logger with `getLogger(__name__)`. Messages travel up the logger tree to the root logger which has the output handler:

```
nutritrack.core.utils logger → nutritrack.core → nutritrack → root logger → stdout
```

`setup_logging()` configures the root logger once at app startup. All child loggers automatically output correctly — no per-module configuration needed.

In the Python shell, there's no app startup — you must call `setup_logging()` manually each session. This is why shell testing requires it but the running app doesn't.

---

## 130 — `deactivate()` — why `.update()` returns int, not the object

```python
# ❌ wrong — .update() returns number of rows affected, not the object
deactivated_user = session.query(UserModel).filter(...).update({...})
return deactivated_user   # returns 1, not a UserModel

# ✅ correct — fetch first, mutate attribute, flush
def deactivate(self, user_id: int) -> UserModel:
    user = self.get_by_id(user_id)   # raises UserNotFoundError if missing
    user.is_active = False
    self.session.flush()
    return user
```

This approach also reuses `get_by_id()` — no duplicate lookup logic. If the user doesn't exist, `UserNotFoundError` is raised before any update attempt.

---

## 131 — Why `FoodEntryCreate` uses `food_name` not `food_id`

The user never knows or provides `food_id` — that's an internal database concept. They just type a food name. The backend resolves it:

```
user provides: food_name="chicken adobo", weight_g=200
    ↓
backend checks DB for "chicken adobo"
    ↓
found? use existing food_id
not found? call AI → save food → get food_id
    ↓
create FoodEntry with resolved food_id
```

Similarly, `user_id` never comes from the request body — it comes from the JWT token. This prevents a user from logging food for another user's account.

---

## 132 — Swagger UI (`/docs`) for API testing during development

FastAPI auto-generates interactive API documentation at `/docs`. Standard workflow:

1. Start server: `uvicorn nutritrack.api.main:app --reload`
2. Open `http://127.0.0.1:8000/docs`
3. Call `POST /auth/login` → copy the `access_token`
4. Click **Authorize** (top right) → paste token in HTTPBearer field
5. All protected endpoints now send the token automatically
6. Use **Try it out** on any endpoint to test with real data

The `/docs` page reads `response_model`, `status_code`, tags, and docstrings from your code — keeping documentation always in sync with the implementation.

---

## 133 — bcrypt version compatibility — passlib and bcrypt

Passlib's bcrypt handler reads `bcrypt.__about__.__version__` which no longer exists in newer bcrypt versions. This causes a `ValueError: password cannot be longer than 72 bytes` error even for short passwords.

Fix — pin bcrypt to a compatible version:
```bash
pip install bcrypt==4.0.1
```

The error message is misleading — the real issue is passlib failing to detect the bcrypt backend version, not actual password length.

---

## 134 — `OAuth2PasswordBearer` vs `HTTPBearer` in FastAPI

`OAuth2PasswordBearer` — designed for OAuth2 password flow. The `/docs` Authorize button shows a username/password form and calls the token URL automatically. But it expects form data (`username`/`password`), not JSON.

`HTTPBearer` — simpler, reads `Authorization: Bearer <token>` header. The `/docs` Authorize button shows a raw token field — paste your JWT directly. Works with JSON login endpoints.

For NutriTrack, `HTTPBearer` is cleaner since the login endpoint accepts JSON. After logging in via `POST /auth/login`, copy the token and paste it in the Authorize dialog.

```python
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

security = HTTPBearer()

def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    ...
) -> UserModel:
    token = credentials.credentials   # the raw JWT string
```

The type hint `HTTPAuthorizationCredentials` is required — without it, mypy can't determine the type of `credentials` and `credentials.credentials` fails.

---

## 135 — Flask vs FastAPI — key differences

Both are Python web frameworks but optimized for different use cases:

```
FastAPI                          Flask
────────────────────             ────────────────────
returns JSON by default          returns HTML or JSON
Pydantic validation built-in     manual validation
async native                     sync by default
auto /docs generation            no auto docs
dependency injection             no DI system
type hints first-class           optional
best for: REST APIs              best for: server-rendered HTML, admin panels
```

Flask's `render_template()` generates complete HTML pages — the browser reloads on every navigation. FastAPI's endpoints return JSON consumed by a frontend (React). Both can do either, but each is optimized for its primary use case.

---

## 136 — Flask app factory pattern

Wraps app creation in a function for testability and configurability:

```python
def create_app(config: str = "production") -> Flask:
    app = Flask(__name__, template_folder="templates")
    app.config["SECRET_KEY"] = settings.secret_key

    from nutritrack.admin.routes import bp
    app.register_blueprint(bp)

    return app
```

Benefits over module-level creation:
- Pass different configs for testing vs production
- Create fresh isolated app instances in tests
- Defer configuration until needed

Import blueprint inside the function to avoid circular imports — the blueprint imports from the same package.

---

## 137 — Flask blueprints

Equivalent of FastAPI routers — groups related routes:

```python
# routes.py
from flask import Blueprint, render_template
bp = Blueprint("admin", __name__, url_prefix="/admin")

@bp.route("/")              # GET /admin/
def dashboard(): ...

@bp.route("/users")         # GET /admin/users
def users(): ...

@bp.route("/login", methods=["GET", "POST"])  # GET and POST /admin/login
def login(): ...
```

```python
# app.py
app.register_blueprint(bp)
```

Flask uses `.route()` not `.router()`. `methods=["GET"]` is optional for GET-only routes — Flask defaults to GET. Specify methods when accepting POST or multiple methods.

---

## 138 — Jinja2 templates

Flask's templating engine — HTML with Python-like expressions:

```html
{{ variable }}              — output a variable
{% for item in items %}     — loop
{% if condition %}          — conditional
{% extends "base.html" %}   — inherit from base template
{% block content %}         — define/fill a content block
{{ value | round(2) }}      — apply a filter (round to 2 decimal places)
```

Template inheritance — `base.html` defines the layout, child templates fill in blocks:

```html
<!-- base.html -->
<nav>...</nav>
{% block content %}{% endblock %}

<!-- dashboard.html -->
{% extends "admin/base.html" %}
{% block content %}
<h2>Dashboard</h2>
{{ user_count }} users
{% endblock %}
```

`render_template("admin/dashboard.html", user_count=42)` — passes keyword arguments as template variables.

---

## 139 — DetachedInstanceError — SQLAlchemy objects after session closes

SQLAlchemy objects become "detached" when their session closes. Accessing attributes on detached objects raises `DetachedInstanceError`:

```python
# ❌ wrong — session closes before template accesses attributes
with get_session() as session:
    users = session.query(UserModel).all()
# session closed here — users are detached

return render_template("users.html", users=users)
# template accesses user.email → DetachedInstanceError
```

Fix — convert to plain dicts before session closes:

```python
# ✅ correct — plain dicts never detach
with get_session() as session:
    users = [{
        "id": u.id,
        "email": u.email,
        "activity_level": u.activity_level,
    } for u in session.query(UserModel).all()]

return render_template("users.html", users=users)
```

Plain Python values (strings, ints, dicts) are copied out of SQLAlchemy immediately — they're never detached. This is also better production practice — keeps business logic (DB queries) separate from view logic (templates).

---

## 140 — Celery — task queue architecture

Three processes running simultaneously:

```
Web app (Flask/FastAPI)    Redis (broker)         Celery worker
────────────────────       ──────────────         ─────────────
task.delay(args)      →    stores task       →    picks up task
returns immediately        in queue               executes it
                                                  stores result
```

**Celery app setup:**

```python
from celery import Celery

celery_app = Celery(
    "nutritrack",
    broker=settings.redis_url,       # where tasks are sent
    backend=settings.redis_url,      # where results are stored
    include=["nutritrack.worker.tasks"],  # where to find tasks
    broker_connection_retry_on_startup=True,
)
```

**Task definition:**

```python
@celery_app.task
def generate_weekly_report(user_id: int) -> dict:
    # runs in worker process, not in web app
    ...
    return result
```

**Dispatching — `.delay()` sends to queue without waiting:**

```python
task = generate_weekly_report.delay(user_id=1)
# returns immediately
print(task.id)      # unique task ID
print(task.status)  # PENDING — not done yet
```

**Calling directly (not queued):**

```python
result = generate_weekly_report(user_id=1)  # runs immediately, blocks
```

Use `.delay()` for background work. Call directly when you need the result immediately (e.g. calling from inside another task).

---

## 141 — Redis vs RabbitMQ as Celery broker

Both work as Celery message brokers:

```
Redis                          RabbitMQ
────────────────────           ────────────────────
primary: in-memory cache       primary: message broker
brokering is secondary         built for message queuing
simpler setup                  more complex setup
good for small-medium load     better for high volume
already used for caching       separate service
```

For NutriTrack — Redis is correct. Low task volume, already in use, simpler infrastructure. RabbitMQ makes sense for millions of tasks/day or complex routing requirements.

---

## 142 — Celery on Windows — known issues and fixes

**Issue 1 — `unknown command 'HELLO'`:**
Celery 5.x requires Redis 6+. The `HELLO` command was added in Redis 6 for RESP3 protocol negotiation. Windows Redis port (tporadowski) is stuck at 5.x.

Fix — use Celery 5.4.0 which has better compatibility, or install Redis via WSL.

**Issue 2 — `PermissionError: Access is denied` with prefork pool:**
Celery's default `prefork` pool uses shared memory (Windows semaphores) which requires elevated permissions.

Fix — use `--pool=solo` for Windows development:
```bash
celery -A nutritrack.worker.celery_app worker --loglevel=info --pool=solo
```

`solo` runs tasks in the same process — no multiprocessing, no permission issues. Fine for development; use `prefork` in production on Linux.

---

## 143 — Celery worker subcommands

```bash
celery -A myapp worker    # start worker that executes tasks
celery -A myapp beat      # start scheduler for periodic tasks
celery -A myapp flower    # web monitoring UI
celery -A myapp inspect   # inspect running workers
celery -A myapp purge     # clear all pending tasks
```

Full worker command for NutriTrack on Windows:
```bash
celery -A nutritrack.worker.celery_app worker --loglevel=info --pool=solo
```

In production on Linux — run both worker and beat:
```bash
celery -A nutritrack.worker.celery_app worker  # executes tasks
celery -A nutritrack.worker.celery_app beat    # schedules periodic tasks
```

---

## 144 — Rendering Jinja2 templates outside Flask

Flask's `render_template()` only works inside a Flask app context. To render templates from a Celery task or standalone script, use Jinja2 directly:

```python
from jinja2 import Environment, FileSystemLoader
from pathlib import Path

def render_html(summary_data: dict) -> str:
    template_dir = Path(__file__).parent.parent / "admin" / "templates"
    env = Environment(loader=FileSystemLoader(str(template_dir)))
    template = env.get_template("admin/weekly_report_email.html")
    return template.render(**summary_data)
```

- `Environment` — Jinja2 rendering engine with configuration
- `FileSystemLoader` — loads templates from a directory on disk
- `env.get_template()` — loads a specific template file (relative to template_dir)
- `template.render(**data)` — replaces `{{ variable }}` with actual values

---

## 145 — Sending HTML emails with smtplib

```python
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

def send_email(to: str, subject: str, html_body: str) -> None:
    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = settings.mail_from
    msg["To"] = to
    msg.attach(MIMEText(html_body, "html"))

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(settings.mail_username, settings.mail_password)
        server.sendmail(settings.mail_from, to, msg.as_string())
```

For Gmail, use an **App Password** (not your regular password):
1. Enable 2FA on Google account
2. Go to https://myaccount.google.com/apppasswords
3. Generate app password for "Mail"
4. Remove spaces from the 16-character password in `.env`

`SMTP_SSL` on port 465 — encrypted connection from the start. Alternative: `SMTP` on port 587 with `starttls()`.

---

## 146 — CSV streaming with Flask

For large exports, stream CSV row by row instead of building it all in memory:

```python
from flask import Response, stream_with_context
import csv, io

@bp.route("/export/food-log/<int:user_id>")
def export_food_log(user_id: int):
    def generate():
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(["id", "food_name", "weight_g", "calories"])  # header
        yield output.getvalue()
        output.seek(0); output.truncate(0)

        with get_session() as session:
            for entry in FoodEntryRepository(session).get_by_user(user_id):
                writer.writerow([entry.id, entry.food.name, ...])
                yield output.getvalue()
                output.seek(0); output.truncate(0)

    return Response(
        stream_with_context(generate()),
        mimetype="text/csv",
        headers={"Content-Disposition": f"attachment; filename=food_log_{user_id}.csv"}
    )
```

`stream_with_context()` — keeps Flask's request context alive during streaming. Without it, accessing `session` or other context-dependent objects fails mid-stream.

User still downloads a complete file — browser assembles the chunks automatically.

---

## 147 — PDF generation with reportlab

```python
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib import colors
import io

buffer = io.BytesIO()
c = canvas.Canvas(buffer, pagesize=letter)

# coordinate system: (0,0) = bottom-left, y increases upward
# letter page = 612 × 792 points (1 point = 1/72 inch)
c.drawString(100, 750, "NutriTrack Weekly Report")  # x=100, y=750 from bottom
c.drawString(100, 720, f"User: {email}")

# draw horizontal line: (x1, y1) to (x2, y2)
c.setStrokeColor(colors.black)
c.line(100, 648, 500, 648)

# columns at fixed x positions
c.drawString(100, 630, "Calories")
c.drawString(300, 630, "703.05")      # Total column at x=300
c.drawString(450, 630, "2896.95")     # Remaining column at x=450

c.save()
buffer.seek(0)

return Response(
    buffer.getvalue(),
    mimetype="application/pdf",
    headers={"Content-Disposition": "attachment; filename=report.pdf"}
)
```

Key points:
- `\n` and `\t` don't work in `drawString` — use separate calls at different y/x positions
- Decrease y by ~20 points per line to move down the page
- Use `c.line(x1, y1, x2, y2)` for horizontal separators — `─` character renders as black blocks in default font
- `io.BytesIO()` — in-memory binary buffer, no file written to disk

---

## 148 — N+1 query problem in templates

Keeping the session open while rendering a template risks the N+1 query problem:

```python
# session open during render_template
with get_session() as session:
    users = session.query(UserModel).all()
    return render_template("users.html", users=users)

# template accesses user.food_entries for each user
# → 1 query for users + N queries for food_entries = N+1 queries total
```

Solution — convert to dicts inside the session, extracting only what the template needs:

```python
with get_session() as session:
    users = [{"id": u.id, "email": u.email} for u in session.query(UserModel).all()]
return render_template("users.html", users=users)
# template has no access to session — can't trigger extra queries
```

---

## 149 — Flask streaming response vs building all at once

```
Build all at once:
- All data loaded into memory simultaneously
- Simple code
- Risk of memory exhaustion for large datasets

Stream with generator:
- Only small chunks in memory at a time
- Slightly more complex code  
- Scales to any dataset size
- Browser assembles chunks into complete file automatically
```

Use streaming for CSV/file exports in production. Use build-all for PDFs (reportlab requires the complete document before writing).

---

## 150 — NutriTrack Phase 5 file structure

```
nutritrack/
├── admin/
│   ├── __init__.py
│   ├── app.py              ← Flask app factory
│   ├── routes.py           ← dashboard, users, exports, task triggers
│   └── templates/
│       └── admin/
│           ├── base.html
│           ├── dashboard.html
│           ├── users.html
│           ├── task_status.html
│           └── weekly_report_email.html
├── worker/
│   ├── __init__.py
│   ├── celery_app.py       ← Celery config with Redis broker
│   ├── tasks.py            ← generate_weekly_report, send_weekly_report_email
│   └── utils.py            ← send_email, render_html
└── run_admin.py            ← Flask entry point (port 5000)
```

Run three processes simultaneously:
```bash
uvicorn nutritrack.api.main:app --reload          # FastAPI on port 8000
python run_admin.py                                # Flask on port 5000
celery -A nutritrack.worker.celery_app worker      # Celery worker
    --loglevel=info --pool=solo
```

---

---

## 151 — Why automated tests? The core motivation

Manual testing through Swagger or the UI tells you "does this one specific thing I just tried still work" — it doesn't tell you "did this change silently break something three files away that I forgot even existed." By the time you'd notice something broke via manual testing, it's already potentially in front of a real user.

Automated tests solve this by encoding verification *once*, as code, then re-running that entire verification — every dataclass, every repository, every endpoint — in seconds, any time anything changes. The test suite becomes a permanent, reusable safety net that catches regressions automatically, rather than relying on manually re-clicking through Swagger every time.

**The concrete payoff observed in NutriTrack:** when the `@validate_macros` decorator was tested against all four negative-macro cases, it proved the decorator rejects negative values for *every* parameter — not just protein (the one originally tested manually). Without the parametrized tests, a bug where negative carbs was silently accepted could have gone undetected.

---

## 152 — Unit tests vs integration tests — the fundamental distinction

```
Unit test:
  → tests ONE small, isolated piece of logic
  → no external dependencies (no database, no network, no file system)
  → fast (milliseconds), simple to write, run constantly during development

Integration test:
  → tests how multiple real pieces work together
  → requires real external dependencies (a real database, real connection)
  → slower (hundreds of milliseconds), more setup required
  → catches bugs that unit tests can't (FK violations, transaction behavior, etc.)
```

**Why Phase 1 dataclasses/utils are easiest to unit test:** `MacroAggregator`, `calculate_calories`, `FoodEntry.scaled_calories()` etc. have zero external dependencies — you just construct them in memory and call methods. No database session, no connection pool, no network.

**Why repositories require integration tests:** `FoodEntryRepository.delete()` genuinely needs a real database row to exist with real ownership relationships. You cannot meaningfully test "does the user-scoped query correctly reject another user's entry" without actually hitting a real database.

The architectural separation between Phase 1 (pure dataclasses, no DB) and Phase 2+ (SQLAlchemy ORM) exists precisely to make unit testing easy — it's not accidental that the business logic runs entirely on plain Python objects. This is the payoff of that architectural decision, felt concretely for the first time in Phase 7.

---

## 153 — pytest basics — discovery, assertions, test functions

pytest automatically discovers tests using naming conventions:
- Test **files** must start with `test_` (e.g. `test_utils.py`)
- Test **functions** inside those files must start with `test_`
- `conftest.py` is a special reserved filename — pytest loads it automatically and makes everything defined there available to every test in the same directory and subdirectories, without any import statement needed

**One test function = one specific behavior/scenario.** Splitting tests into separate functions means each scenario gets checked and reported independently — if the first assertion fails, pytest still runs and reports all remaining tests:

```python
# ❌ merged — if the first assertion fails, you never know about the second
def test_calculate_calories():
    assert calculate_calories(10, 20, 5) == 125
    assert calculate_calories(10, 20, 5, fiber_g=3.0) == 113

# ✅ separated — both scenarios always reported independently
def test_calculate_calories_no_fiber():
    assert calculate_calories(10, 20, 5) == 125

def test_calculate_calories_with_fiber():
    assert calculate_calories(10, 20, 5, fiber_g=3.0) == 113
```

**`assert` in pytest:** plain Python `assert` statement — if the condition is `False`, pytest intercepts it, shows a detailed diff of what was expected vs what was received, and marks the test as FAILED. No special assertion library needed.

---

## 154 — Fixtures — reusable test setup

A fixture is a function decorated with `@pytest.fixture` that prepares reusable test data or setup, which pytest automatically supplies to any test function that lists it as a parameter:

```python
# conftest.py
@pytest.fixture
def sample_food() -> Food:
    return Food(name="chicken breast", protein_per_100g=31.0, carbs_per_100g=0.0, fat_per_100g=3.6)

# test file — no import needed, pytest wires it automatically
def test_scaled_calories(sample_food):   # ← pytest sees "sample_food" and calls the fixture
    entry = FoodEntry(food=sample_food, weight_g=150, logged_date=date.today(), meal_slot="lunch")
    assert entry.scaled_calories() == round((31.0*4 + 0.0*4 + 3.6*9) * 150/100, 2)
```

**Fixtures can depend on other fixtures** — exactly like test functions:

```python
@pytest.fixture
def sample_food_entry(sample_food: Food) -> FoodEntry:
    # pytest calls sample_food first, passes the result in as "sample_food"
    return FoodEntry(food=sample_food, weight_g=150, logged_date=date.today(), meal_slot="lunch")
```

**Fixture scope** — controls how often the fixture is created and torn down:

```
scope="function"  — default, fresh instance for EVERY test function
scope="session"   — created ONCE for the entire test run, shared by all tests
scope="module"    — created once per test file
```

`db_engine` uses `scope="session"` (creating a database engine is expensive, no per-test state). `db_session` uses the default `scope="function"` (must be fresh per test for transaction isolation).

**The `yield` pattern in fixtures — setup and teardown in one function:**

```python
@pytest.fixture
def db_session(db_engine):
    connection = db_engine.connect()
    transaction = connection.begin()
    session = Session(bind=connection)

    yield session        # ← test runs here, receives the session

    session.close()      # ← teardown: everything after yield runs after the test
    transaction.rollback()
    connection.close()
```

Everything before `yield` = setup (runs before the test). The test receives the yielded value. Everything after `yield` = teardown (runs after the test, whether it passed or failed — equivalent to `try/finally`).

---

## 155 — `pytest.mark.parametrize` — running one test with multiple inputs

When the same test logic needs to run with several different inputs:

```python
@pytest.mark.parametrize("protein_g, carbs_g, fat_g, fiber_g", [
    (-10, 20, 5, None),   # negative protein
    (10, -20, 5, None),   # negative carbs
    (10, 20, -5, None),   # negative fat
    (10, 20, 5, -2.0),    # negative fiber
])
def test_calculate_calories_negative_macro_raises(protein_g, carbs_g, fat_g, fiber_g):
    with pytest.raises(InvalidMacroError):
        calculate_calories(protein_g=protein_g, carbs_g=carbs_g, fat_g=fat_g, fiber_g=fiber_g)
```

Each tuple becomes its own separate test case with an auto-generated name showing the actual parameter values: `[-10-20-5-None]`, `[10--20-5-None]`, etc. If one case fails, the others still run independently. Prefer `parametrize` when test logic is truly identical across cases; use separate functions when each case has meaningfully different setup or assertions.

---

## 156 — `pytest.raises()` — testing that exceptions are raised

```python
def test_calculate_calories_negative_protein_raises():
    with pytest.raises(InvalidMacroError):
        calculate_calories(protein_g=-10, carbs_g=20, fat_g=5)
```

The `with pytest.raises(SomeException):` block passes if and only if the code inside raises exactly that exception type. If the code runs without raising → test FAILS (expected exception didn't happen). If it raises a different exception → test also FAILS.

Used throughout Phase 7 to test that:
- `@validate_macros` raises `InvalidMacroError` for negative macro values
- `FoodEntryRepository.delete()` raises `FoodNotFoundError` when user 2 tries to delete user 1's entry (IDOR prevention proven)

---

## 157 — Integration tests — transactional fixture for database isolation

The core problem: tests must be completely isolated (one test's data shouldn't affect another's), and they must leave no junk data behind in the database after running.

**The solution — wrap every test in a database transaction, then roll it back after the test completes:**

```python
@pytest.fixture(scope="session")
def db_engine():
    engine = create_engine(settings.database_url)
    Base.metadata.create_all(engine)
    yield engine
    engine.dispose()

@pytest.fixture
def db_session(db_engine):
    connection = db_engine.connect()
    transaction = connection.begin()    # explicit outer transaction
    Session = sessionmaker(bind=connection)
    session = Session()

    yield session                        # test runs, can flush/query — but never commits

    session.close()
    transaction.rollback()               # everything discarded — as if the test never happened
    connection.close()
```

**Why `transaction.rollback()` and not `session.rollback()`:** the session is nested *inside* the explicitly-started connection-level transaction. `session.rollback()` only rolls back SQLAlchemy's inner view — the outer `transaction` you started with `connection.begin()` is still open, and closing the connection without explicitly rolling it back could auto-commit depending on the driver. `transaction.rollback()` discards everything at the level you explicitly started it.

**Why repositories never call `session.commit()`:** repositories call only `session.flush()` (sends SQL to DB, assigns IDs, stays within the open transaction). The *caller* decides when to commit. In production, `get_db_session()` commits after a successful endpoint request. In tests, no commit ever happens — `transaction.rollback()` fires instead. This architectural decision (repositories flush only, never commit) is what makes the transactional test fixture work cleanly.

**The "insert happens but never commits" sequence:**

```
session.flush()   → row EXISTS within the transaction → visible to THIS session ✅
                  → NOT visible to other connections
session.commit()  → row PERMANENT → visible to ALL connections (never called in tests)
transaction.rollback() → row DISCARDED → visible to NO ONE ✅
```

`food.id` is a real integer after `flush()` (the database sequence assigned it), but after `rollback()`, the row is gone — the sequence value is "used up" (PostgreSQL sequences don't roll back) but the data itself doesn't exist.

---

## 158 — Session vs transaction — the distinction

**Session** — SQLAlchemy's unit-of-work workspace. Tracks which Python objects correspond to which database rows (the "identity map"), accumulates changes in memory, knows how to `flush`/`commit`/`rollback`.

**Transaction** — a database-level guarantee. A group of SQL statements that either all succeed together or all fail together (ACID atomicity). Rolling back discards all statements in the current transaction.

A SQLAlchemy session *always* operates within a transaction, whether you think about it or not. `flush()` sends SQL within the current transaction (open). `commit()` closes and commits the transaction (makes it permanent), starts a new one. `rollback()` closes and discards the transaction.

**Why `get_session()` (production) uses implicit transaction management:**

```python
@contextmanager
def get_session():
    session = SessionLocal()
    try:
        yield session
        session.commit()   # ← session owns its transaction, commits are the goal
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()
```

Session created → SQLAlchemy implicitly begins a transaction → `session.commit()` makes everything permanent. `session.rollback()` correctly rolls back everything because the session owns its own transaction from start to finish.

**Why test fixture uses explicit `connection.begin()`:**

The test fixture explicitly creates a transaction *before* the session, then binds the session to that connection. The session is a guest inside the outer transaction — `session.rollback()` only affects the inner layer. `transaction.rollback()` is needed to roll back the outer one. This provides the stronger guarantee that no data persists regardless of SQLAlchemy's internal session-transaction bookkeeping.

**Why production `get_session()` doesn't use explicit transactions:** production code *wants* commits — data persistence is the whole point. Explicit `connection.begin()` + `transaction.rollback()` would prevent data from ever being saved. The implicit session transaction is appropriate precisely because it commits normally when everything succeeds.

---

## 159 — Context managers — `@contextmanager` and `with` statement

A context manager guarantees cleanup code always runs, regardless of how the code block exits — whether it returns normally, returns early, or raises an exception.

```python
# ❌ fragile — if anything raises, close() never runs, connection leaks
session = SessionLocal()
do_something(session)   # what if this raises?
session.close()          # never reached

# ✅ guaranteed — session.close() always runs
with get_session() as session:
    do_something(session)   # raises? doesn't matter
# session.close() always fires here
```

Python's `with` statement calls two special methods:
- `__enter__` — runs on entry, returns the value bound to `as session`
- `__exit__` — runs on exit, *always*, whether the block succeeded or raised

`@contextmanager` is a convenience decorator that lets you write a context manager as a generator (with `yield`) rather than defining a class with `__enter__`/`__exit__` explicitly:

```python
@contextmanager
def get_session():
    session = SessionLocal()
    try:
        yield session          # ← __enter__ equivalent: everything before yield
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()        # ← __exit__ equivalent: everything in finally
```

Common production uses: database sessions (always close), file handles (`with open(...)`), locks (always release), temporary directories (always delete). The common thread — a resource that *must* be released, where forgetting the release step is easy but catastrophic.

---

## 160 — `raise err` vs bare `raise` — traceback preservation

```python
# ❌ raise err — resets the traceback to this line, losing original location
except Exception as err:
    session.rollback()
    raise err   # traceback points to THIS line, not where the error originally occurred

# ✅ bare raise — re-raises the ORIGINAL exception with its ORIGINAL traceback
except Exception:
    session.rollback()
    raise       # traceback shows where the error actually happened
```

Bare `raise` (no argument) re-raises the current exception object with its full original traceback intact, so you see exactly where in your application code the error first occurred. `raise err` treats it as a new raise at that line, losing that information. Always prefer bare `raise` in exception handlers that re-raise.

---

## 161 — FastAPI `TestClient` and dependency overrides

`TestClient` (from Starlette) runs the full FastAPI request/response cycle — routing, middleware, dependency injection, exception handlers, Pydantic validation — all in memory, without starting a real server:

```python
from fastapi.testclient import TestClient
from nutritrack.api.main import app

client = TestClient(app)
response = client.get("/foods/99999")
assert response.status_code == 404
```

**Dependency overrides — replacing `Depends()` functions for tests:**

```python
from nutritrack.api.dependencies import get_current_user, get_db_session

def override_get_current_user():
    return UserModel(id=test_user.id, email="fixture_user@test.com", ...)

def override_get_db_session():
    yield db_session   # use the test's rolled-back session instead

app.dependency_overrides[get_current_user] = override_get_current_user
app.dependency_overrides[get_db_session] = override_get_db_session

# after tests:
app.dependency_overrides.clear()   # MUST clear — app is a singleton, overrides persist
```

`app.dependency_overrides` is a plain Python dict on the module-level singleton `app`. FastAPI checks it per request: "is this dependency in the override dict? if yes, call the override instead." Overrides only activate when a dependency is actually *requested* by an endpoint — an endpoint that never declares `Depends(get_current_user)` (like register/login) is completely unaffected by overriding it.

**Why the `client` fixture creates a real user in the database:**

The fake `override_get_current_user` returns a `UserModel` object — but endpoints that insert `food_entries` with `user_id=test_user.id` need that user to actually exist in the database (FK constraint). A made-up `id=99999` fails with `ForeignKeyViolation` when the endpoint tries to insert. Solution: create a real user via the repository inside the fixture, then return that user from the override. The user gets rolled back with everything else at the end of the test.

**The `id=99999` vs real-user tradeoff discovered during testing:**

Using a non-existent fake ID (`id=99999`) works for tests that *read* data (returning empty results is fine) but breaks tests that *write* data (FK constraints require the user to exist). Using a real created user satisfies both requirements — exists for FK constraints, and has no attached data (just created, clean state).

---

## 162 — Mocking external services with `unittest.mock`

Mocking replaces a real function with a fake that returns a predetermined response instantly, without making any real external calls. Essential for testing code that calls the Anthropic API — real calls cost money, take seconds, require internet, and produce non-deterministic results.

**`patch()` as a context manager:**

```python
from unittest.mock import patch, AsyncMock

with patch(
    "nutritrack.api.routers.logs.parse_natural_language_meal",
    new_callable=AsyncMock,
    return_value=[{"food_name": "chicken breast", "weight_g": 150.0, ...}],
):
    response = client.post("/log/natural", json={...})
    assert response.status_code == 201
```

**Patch WHERE the function is used, not WHERE it is defined:**

`parse_natural_language_meal` is *defined* in `nutritrack.ai.client`, but *imported and used* in `nutritrack.api.routers.logs`. Patch the usage location — `"nutritrack.api.routers.logs.parse_natural_language_meal"`. If you patched the definition location instead, the router would still hold its own reference to the original function and the patch would have no effect.

**`new_callable=AsyncMock` for async functions:**

`parse_natural_language_meal` is `async`. Regular `Mock` objects aren't awaitable — calling `await mock()` raises `TypeError`. `AsyncMock` is specifically designed for async functions, automatically awaitable, returning `return_value` when awaited.

**`side_effect` vs `return_value`:**

```python
# return_value — mock returns this value when called
return_value=[{"food_name": "chicken", ...}]   # simulates successful AI response

# side_effect — mock RAISES this exception when called
side_effect=AIServiceError("service unavailable")   # simulates AI failure

# note: side_effect (lowercase 'e') — Python is case-sensitive
# side_Effect = ... ← wrong: sets an irrelevant attribute, mock not actually configured
```

**Stacked `@patch` decorators — parameter order:**

```python
@patch("module.function_b")   # outer decorator → SECOND parameter
@patch("module.function_a")   # inner decorator → FIRST parameter
def test_something(mock_a, mock_b):
    ...
```

Bottom decorator (innermost) maps to the first parameter. Top (outermost) maps to the second. This ordering is a common source of bugs — always double-check when stacking patches.

**`ExitStack` for multiple patches without nesting:**

```python
from contextlib import ExitStack

def test_something(client):
    with ExitStack() as stack:
        stack.enter_context(patch("module.function_a", new_callable=AsyncMock, return_value=...))
        stack.enter_context(patch("module.function_b", new_callable=AsyncMock, side_effect=SomeError()))
        response = client.post(...)
```

Each patch entered cleanly on its own line, no matter how many — avoids deeply nested `with patch(): with patch():` blocks.

---

## 163 — Coverage reports with `pytest-cov`

```bash
pytest --cov=nutritrack --cov-report=term-missing
```

`--cov=nutritrack` — measure coverage only for the `nutritrack/` package (not tests themselves, not third-party libraries). `--cov-report=term-missing` — show which specific line numbers are NOT covered, not just a summary percentage.

**Reading the report:**

```
Name                          Stmts  Miss  Cover  Missing
---------------------------------------------------------
nutritrack/core/parsers.py      44     4    91%   16-19
```

`Stmts` — total executable statements. `Miss` — statements never executed by any test. `Cover` — percentage executed. `Missing` — specific line numbers not covered.

**NutriTrack's 60% baseline — what it means:**

High-coverage areas (genuinely well-tested):
- `db/models.py` 100%, `db/schemas.py` 99% — every model/schema exercised through endpoint tests
- `core/parsers.py` 91%, `core/models.py` 90% — computation layer well-tested
- `api/routers/auth.py` 94% — auth flow nearly complete

Expected 0% areas (appropriate, not failures):
- `admin/` — Flask admin intentionally excluded from Phase 7 testing scope
- `worker/` — Celery tasks require a different, more complex testing setup
- `db/seed.py` — one-time data seeding script, not worth testing

**Chasing 100% coverage is often counterproductive** — it leads to testing Python's own behavior rather than your application logic. The more useful question is: *are the highest-risk, most critical parts covered?* For NutriTrack: core computation, IDOR security, auth flow, and exception handlers are all well-covered — exactly the right priorities.

---

## 164 — IDOR prevention — security property proven by integration test

IDOR (Insecure Direct Object Reference) — a vulnerability where an attacker accesses or modifies resources they don't own by guessing/incrementing an identifier in the URL. `DELETE /log/6` attempted by a user who owns entry 7 — without ownership validation, entry 6 (belonging to someone else) gets deleted.

**The fix — make ownership part of the same database query:**

```python
def delete(self, entry_id: int, user_id: int) -> None:
    entry = (
        self.session.query(FoodEntryModel)
        .filter(FoodEntryModel.id == entry_id)
        .filter(FoodEntryModel.user_id == user_id)   # both conditions, one query
        .first()
    )
    if not entry:
        raise FoodNotFoundError(str(entry_id))
    self.session.delete(entry)
```

"Entry 6 exists but belongs to user B" produces exactly the same result as "entry 6 doesn't exist at all" — both return nothing from the query, both raise `FoodNotFoundError`, both produce a 404 response. The attacker gets no signal that entry 6 exists, removing their ability to use the endpoint as a probe.

**Why this required an integration test to prove** — the security property cannot be verified with in-memory dataclasses. It requires:
- A real database row owned by user 1
- A real query that runs with user 2's ID
- A real FK relationship between `food_entries.user_id` and `users.id`
- A real assertion that `FoodNotFoundError` was raised

The `test_delete_other_users_entry_raises` test provides permanent, automated proof that this property holds at the database-query level, not just in theory.

---

## 165 — Singletons in testing — `app` and `dependency_overrides`

A singleton is an object that exists as exactly one instance for the entire lifetime of the program — every part of the code that references it gets the same object.

```python
# module-level — created once when Python first imports this file
app = FastAPI(...)   # ← this IS the singleton

# anywhere else in the codebase:
from nutritrack.api.main import app   # ← always the SAME object, not a new one
```

**The testing consequence:** modifying `app.dependency_overrides` in one place modifies it everywhere, since there's only one `app`. This is why `app.dependency_overrides.clear()` in the `client` fixture's teardown (after `yield`) is essential — without clearing overrides after each test, the fake implementations leak into subsequent tests permanently.

**The naming collision to be aware of:** `scope="session"` in pytest means "live for the entire test run" — nothing to do with SQLAlchemy sessions. `db_session` is a SQLAlchemy concept — nothing to do with pytest's scope system. Two completely different systems that happen to share the word "session."

---

## 166 — Phase 7 test suite summary

```
tests/
├── conftest.py              ← shared fixtures: sample_food, sample_food2,
│                               sample_food_entry, sample_food_entries,
│                               sample_macro_goal, multi_day_food_entries,
│                               db_engine, db_session, client, registered_user
├── test_core_models.py      ← FoodEntry.scaled_calories(), scaled_protein()
├── test_daily_totals.py     ← get_daily_totals() grouping, entry counts, empty list
├── test_parsers.py          ← MacroAggregator totals, remaining macros, top_foods, entry_count
├── test_utils.py            ← calculate_calories, fiber behavior, negative macro validation
├── test_repositories.py     ← food creation, IDOR-safe delete (two cases)
├── test_endpoints.py        ← register, login, POST /log/natural with mocked AI
└── test_exception_handlers.py ← FoodNotFoundError→404, GoalNotSetError→404, AIServiceError→503
```

32 tests total, 2.31 seconds. Breakdown by type:
- 23 unit tests (no database) — run in ~0.07s
- 6 integration tests (real database, transactional rollback) — ~1.0s
- 3 endpoint tests (TestClient, dependency overrides, AI mocked) — ~0.67s
- 3 exception handler tests (fast — mostly "DB finds nothing" results) — ~0.15s

Coverage: 60% overall. Core computation layer 90%+. Auth, routers, repositories 70-94%. Flask admin, Celery worker, seed data intentionally at 0% (out of scope for Phase 7).

---

## 167 — Small Q&As — Phase 7 testing discussions

**"Why did we use `Optional[float] = None` instead of `fiber_g: float = None` for `calculate_calories`?"**
At runtime, both are identical — Python never enforces type hints during execution, and `(fiber_g or 0.0)` handles `None` and `0.0` the same way. The distinction matters only for mypy: `fiber_g: float = None` tells mypy "this is always a float" but then gives it `None` as the default — a direct contradiction that mypy flags as `Incompatible default for argument`. `Optional[float]` (shorthand for `Union[float, None]`) correctly communicates "this can be either a float or None," satisfying both mypy's type-checking and the caller's ability to omit the argument. Design-wise, using `None` as the default is better even when it doesn't functionally matter for a specific function — it's a codebase-wide convention signal that "omitting this value is meaningfully different from providing zero," even if this one function treats them the same.

**"Is `fiber_g: float = None` different from `fiber_g: Optional[float] = None`?"**
Identical at runtime. Different for mypy — the first is a type annotation error (None isn't a float), the second is correct (Optional explicitly includes None as a valid value). mypy will flag the first with `error: Incompatible default for argument "fiber_g"` and accept the second silently.

**"Why not test with `pytest.approx()` for floating-point comparisons?"**
`MacroAggregator` was updated to `round()` its accumulated totals to 2 decimal places before storing them, making the stored values exactly representable — `==` assertions work without tolerance. `pytest.approx()` is the correct tool when comparing raw floating-point arithmetic results that haven't been rounded, where tiny imprecision (e.g. `0.30000000000000004` instead of `0.3`) would cause `==` to fail spuriously. Since `MacroAggregator` pre-rounds its properties, and `remaining_macros()` also rounds its return values, exact `==` comparisons are reliable here.

**"Why did the repository tests fail with `UniqueViolation` when running the full suite?"**
`test_register` (endpoint test) and `test_delete_own_entry_succeeds` (repository test) were both using `test@gmail.com`. The real cause turned out to be pre-existing data in the development database (a real user with that email from earlier manual testing), not a rollback failure between tests. Fix: always use obviously-fake, test-specific email domains (`@test.com`, `@example.com`, `@pytest.local`) that can never exist in your real dev database. Verified by switching to `test@example.com` — both tests passing with the same email confirmed the transactional rollback is working correctly between test functions.

**"Will the user created inside the `client` fixture persist in the database permanently?"**
No — the `client` fixture depends on `db_session` which is `scope="function"` (fresh per test). The user is created via `session.flush()` (within the open transaction), satisfies FK constraints during the test, then gets discarded by `transaction.rollback()` at the end of `db_session`'s teardown — along with everything else the test created.

**"Why did using `id=99999` for the fake user break `test_log_natural_meal` but work for other tests?"**
Tests that only *read* data (returning empty results when nothing matches `user_id=99999`) work fine with a non-existent ID. Tests that *write* data fail with `ForeignKeyViolation` — PostgreSQL enforces the FK constraint `food_entries.user_id → users.id`, so inserting a `food_entry` with `user_id=99999` fails if no `users` row with that ID exists. Solution: create a real user inside the `client` fixture and return that real user object from `override_get_current_user`, satisfying FK constraints for write operations while keeping the test state fully isolated via transaction rollback.

**"What's the difference between `scope='session'` (pytest) and `db_session` (SQLAlchemy)?"**
Completely unrelated concepts that happen to share the word "session." `scope="session"` in pytest means "this fixture lives for the entire test run, created once, shared by all tests." `db_session` is a SQLAlchemy session — a unit-of-work workspace for communicating with the database. `db_engine` uses `scope="session"` (pytest) because creating a connection pool is expensive and has no per-test state. `db_session` (SQLAlchemy) uses the default `scope="function"` (pytest) because each test needs its own fresh transaction.

**"Why patch WHERE a function is used rather than WHERE it is defined?"**
When you `from nutritrack.ai.client import parse_natural_language_meal` in `logs.py`, the name `parse_natural_language_meal` in `logs.py` gets its own reference to the function. Patching the definition location (`nutritrack.ai.client.parse_natural_language_meal`) only replaces it there — `logs.py` still holds its own imported reference to the original. Patching the usage location (`nutritrack.api.routers.logs.parse_natural_language_meal`) replaces the name in the module that actually calls it, so the router gets the mock when it calls the function.

**"What is a singleton?"**
An object that exists as exactly one instance for the entire lifetime of the program. Every import of `app` from `nutritrack.api.main` returns the same object — not a fresh copy. Relevant for testing because `app.dependency_overrides` is a dict on that one shared object — modifying it in one place affects all tests, which is why `dependency_overrides.clear()` in fixture teardown is non-negotiable.

**"What's the practical significance of 60% coverage?"**
It means 60% of your application's executable statements are exercised by at least one test. More useful than the number: the *right* things are covered — core computation (90%+), IDOR security (proven), auth flow (94%), exception handlers (proven). The 0% areas (Flask admin, Celery worker, seed script) are intentionally excluded, not forgotten. Chasing 100% often produces tests that verify Python's own behavior rather than your application's — the highest-value testing targets are the highest-risk, most complex behaviors, not total line count.

---

## Quick mental model

Think of variables as _sticky notes_ attached to objects. Reassigning moves the sticky note to a new object. Mutating changes the object itself — all sticky notes pointing to it see the change.
