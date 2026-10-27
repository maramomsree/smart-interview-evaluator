"""
question_bank.py
================
The curated interview questions, stored as plain Python data, plus a few
helper functions to search and filter them.

HOW TO ADD A QUESTION
---------------------
Copy any dictionary in QUESTIONS, give it a new unique "id", and edit the text.
Each question has:

    id            unique string, e.g. "PY-07"
    topic         must be one of TOPICS
    difficulty    must be one of DIFFICULTIES
    question      the text shown to the user
    concepts      list of expected key concepts, built with _c(...)
    model_answer  a clear reference answer
    why_effective short explanation of what makes the model answer strong

A concept is: _c(name, hint, keyword1, keyword2, ...)
    name      shown in the report ("Mutability")
    hint      advice shown when the concept is missing
    keywords  phrases that count as "the user mentioned this concept".
              Write them in lowercase; the evaluator normalizes text anyway.
              Prefer specific phrases ("hash function") over generic words
              ("function") to avoid false matches.

The evaluator never needs to change when you add questions.
"""

TOPICS = [
    "Python",
    "Object-Oriented Programming",
    "Data Structures and Algorithms",
    "SQL and Databases",
    "Operating Systems",
    "Computer Networks",
]

DIFFICULTIES = ["Beginner", "Intermediate", "Challenging"]

# A reusable way of structuring answers, shown in Learning Mode.
ANSWER_FRAMEWORKS = {
    "Python": (
        "1) Define the feature in one sentence. 2) Explain how it behaves differently from "
        "the alternative. 3) Show a tiny example. 4) Mention a trade-off or a pitfall."
    ),
    "Object-Oriented Programming": (
        "1) Define the principle in plain words. 2) Give a real-world or code analogy. "
        "3) Say what problem it solves. 4) Mention when NOT to use it."
    ),
    "Data Structures and Algorithms": (
        "1) Describe the idea. 2) State time and space complexity. 3) Walk through a small "
        "example. 4) Compare with an alternative and say when you would pick each."
    ),
    "SQL and Databases": (
        "1) Define the term. 2) Show a short example query or table. 3) Explain the effect "
        "on data correctness or performance. 4) Mention a trade-off."
    ),
    "Operating Systems": (
        "1) Define the concept. 2) Explain the problem it solves. 3) Describe how it works "
        "step by step. 4) Mention costs or failure cases."
    ),
    "Computer Networks": (
        "1) State what the protocol or concept is for. 2) Walk through how it works in order. "
        "3) Contrast it with a related concept. 4) Give a real use case."
    ),
}


def _c(name, hint, *keywords):
    """Build one expected-concept dictionary."""
    return {"name": name, "hint": hint, "keywords": list(keywords)}


QUESTIONS = [
    # ------------------------------------------------------------------ PYTHON
    {
        "id": "PY-01",
        "topic": "Python",
        "difficulty": "Beginner",
        "question": "What is the difference between a list and a tuple in Python?",
        "concepts": [
            _c("Mutability",
               "State that lists are mutable (can be changed after creation) while tuples are immutable.",
               "mutable", "immutable", "can be changed", "cannot be changed", "can be modified",
               "cannot be modified", "unchangeable", "modify", "modified"),
            _c("Performance and memory",
               "Mention that tuples are usually slightly faster and use less memory.",
               "faster", "memory", "lightweight", "performance", "speed"),
            _c("Use cases",
               "Say when you would choose each: a list for data that changes, a tuple for fixed data or dictionary keys.",
               "fixed", "constant data", "dictionary key", "hashable", "coordinates", "record",
               "use a tuple", "use a list", "collection that changes", "dynamic", "used when", "are used for"),
        ],
        "model_answer": (
            "Both are ordered sequences, but a list is mutable, so you can add, remove or modify items after "
            "creating it, while a tuple is immutable and cannot be changed once created. Because tuples are fixed, "
            "they are slightly faster and use less memory, and a tuple of hashable items can be used as a "
            "dictionary key, which a list cannot. For example, I use a list for a shopping cart that changes, and "
            "a tuple for fixed data such as the coordinates (x, y)."
        ),
        "why_effective": (
            "It names the core difference (mutability) first, explains the consequences (speed, hashing), and "
            "ends with a practical rule for choosing between them."
        ),
    },
    {
        "id": "PY-02",
        "topic": "Python",
        "difficulty": "Beginner",
        "question": "What is a dictionary in Python and why is looking up a value so fast?",
        "concepts": [
            _c("Key-value mapping",
               "Explain that a dictionary stores data as key-value pairs.",
               "key value", "key value pairs", "keys and values", "mapping", "associative"),
            _c("Hash-based lookup",
               "Explain that keys are hashed to find the storage location, giving average constant-time lookup.",
               "hash", "hash table", "hashing", "o 1", "constant time", "average constant"),
            _c("Unique hashable keys",
               "Mention that keys must be unique and hashable (so lists cannot be keys).",
               "unique", "hashable", "immutable keys", "duplicate keys", "must be immutable"),
        ],
        "model_answer": (
            "A dictionary is a mapping that stores data as key-value pairs, so you retrieve a value by its key "
            "rather than by position. Internally it is a hash table: Python hashes the key to compute where the "
            "value is stored, which makes lookup, insert and delete O(1) on average. Keys must be unique and "
            "hashable, which is why a tuple can be a key but a list cannot. For example, "
            "ages = {'Asha': 25} lets me get her age with ages['Asha'] instantly."
        ),
        "why_effective": (
            "It connects the interface (key-value pairs) to the implementation (hash table) and explains the "
            "resulting rule about keys, which shows real understanding."
        ),
    },
    {
        "id": "PY-03",
        "topic": "Python",
        "difficulty": "Intermediate",
        "question": "What is a decorator in Python and why would you use one?",
        "concepts": [
            _c("Function that wraps a function",
               "Explain that a decorator takes a function and returns a new function that wraps it.",
               "wraps", "wrapper", "takes a function", "function as an argument", "higher order",
               "returns a function", "wrap"),
            _c("Extends behavior without modifying code",
               "Say that decorators add behavior without changing the original function's code.",
               "without modifying", "without changing", "extend behavior", "extend behaviour",
               "add behavior", "add behaviour", "add functionality", "extra functionality"),
            _c("Syntax",
               "Mention the @decorator syntax placed above a function definition (syntactic sugar).",
               "syntactic sugar", "at symbol", "at sign", "above the function", "decorated", "decorator syntax"),
            _c("Common use cases",
               "Give practical uses such as logging, timing, authentication or caching.",
               "logging", "timing", "authentication", "caching", "memoization", "access control", "retry"),
        ],
        "model_answer": (
            "A decorator is a function that takes another function as an argument and returns a new function that "
            "wraps it, so you can add behavior without modifying the original code. The @decorator line above a "
            "function definition is syntactic sugar for reassigning the function to the wrapped version. "
            "For example, a timing decorator can measure how long any function takes, and decorators are also "
            "commonly used for logging, authentication and caching."
        ),
        "why_effective": (
            "It defines the mechanism precisely, explains the @ syntax, and gives concrete use cases that show "
            "why decorators matter in real code."
        ),
    },
    {
        "id": "PY-04",
        "topic": "Python",
        "difficulty": "Intermediate",
        "question": "What is a generator in Python and how is it different from returning a list?",
        "concepts": [
            _c("The yield keyword",
               "Mention that a generator function uses yield instead of return.",
               "yield", "generator function", "generator expression"),
            _c("Lazy evaluation",
               "Explain that values are produced one at a time, only when requested.",
               "lazy", "lazily", "on demand", "one at a time", "as needed", "when requested"),
            _c("Memory efficiency",
               "Explain that a generator does not store all values in memory, so it handles huge or infinite sequences.",
               "memory efficient", "large dataset", "large data", "infinite", "not store all",
               "does not store", "saves memory", "less memory"),
            _c("Iterator and state",
               "Mention that a generator is an iterator that remembers its state between calls to next().",
               "iterator", "next", "resumes", "pauses", "remembers its state", "maintains state", "state"),
        ],
        "model_answer": (
            "A generator is a function that uses the yield keyword to produce values one at a time instead of "
            "building a full list. It is lazy, so each value is computed only on demand, and the function pauses "
            "and resumes where it left off, remembering its state between calls to next(). This makes generators "
            "very memory efficient for large datasets or even infinite sequences, because they do not store all "
            "the values at once. A list is better when you need random access or must reuse the data."
        ),
        "why_effective": (
            "It explains both what a generator is and why it exists (memory), and it honestly includes the "
            "trade-off against lists."
        ),
    },
    {
        "id": "PY-05",
        "topic": "Python",
        "difficulty": "Challenging",
        "question": "What is the Global Interpreter Lock (GIL) in Python and how does it affect multithreading?",
        "concepts": [
            _c("Only one thread runs Python bytecode at a time",
               "Explain that the GIL is a lock in CPython that lets only one thread execute Python bytecode at once.",
               "one thread", "single thread", "only one thread", "mutex", "lock", "cpython"),
            _c("Impact on CPU-bound work",
               "Explain that CPU-bound threads gain no true parallelism because of the GIL.",
               "cpu bound", "cpu intensive", "no true parallelism", "not truly parallel", "parallelism"),
            _c("Workarounds",
               "Mention multiprocessing, asyncio for I/O-bound work, or C extensions that release the GIL.",
               "multiprocessing", "separate process", "processes", "asyncio", "io bound", "i o bound",
               "c extension", "releases the gil"),
            _c("Why it exists",
               "Mention that the GIL simplifies memory management (reference counting) and thread safety.",
               "reference counting", "memory management", "thread safe", "thread safety"),
        ],
        "model_answer": (
            "The GIL is a mutex in CPython that allows only one thread to execute Python bytecode at a time. It "
            "exists because CPython's memory management uses reference counting, and a single lock keeps that "
            "thread safe and simple. The consequence is that CPU bound code gets no true parallelism from "
            "threads, although threads still help with I/O bound tasks because the lock is released while "
            "waiting. To use multiple cores, you use multiprocessing with separate processes, or write the heavy "
            "parts in C extensions that release the GIL."
        ),
        "why_effective": (
            "It explains the purpose of the GIL, then separates CPU-bound from I/O-bound consequences, and "
            "finishes with practical workarounds."
        ),
    },
    {
        "id": "PY-06",
        "topic": "Python",
        "difficulty": "Challenging",
        "question": "Why is using a mutable default argument, such as a list, in a Python function dangerous?",
        "concepts": [
            _c("Default evaluated once",
               "Explain that default values are evaluated once, when the function is defined, not on each call.",
               "evaluated once", "only once", "function is defined", "definition time",
               "at definition", "created once"),
            _c("Shared between calls",
               "Explain that every call without the argument shares the same object, so changes persist.",
               "shared", "same list", "same object", "persists", "accumulates", "across calls", "between calls"),
            _c("The fix",
               "Show the fix: use None as the default and create a new list inside the function.",
               "none", "is none", "sentinel", "create a new list", "inside the function"),
        ],
        "model_answer": (
            "Default argument values are evaluated only once, when the function is defined, not every time it is "
            "called. If the default is a mutable object like a list, every call that omits the argument shares "
            "the same list, so items accumulate across calls and produce surprising bugs. The fix is to use None "
            "as the default and create a new list inside the function, for example: if items is None: items = []."
        ),
        "why_effective": (
            "It identifies the root cause (evaluated once), describes the visible symptom, and gives the "
            "standard idiomatic fix."
        ),
    },
    # -------------------------------------------------------------------- OOP
    {
        "id": "OOP-01",
        "topic": "Object-Oriented Programming",
        "difficulty": "Beginner",
        "question": "What are the four pillars of object-oriented programming?",
        "concepts": [
            _c("Encapsulation",
               "Explain that encapsulation bundles data with methods and hides internal details.",
               "encapsulation", "encapsulate", "data hiding", "bundling", "private"),
            _c("Abstraction",
               "Explain that abstraction exposes essential features and hides complexity.",
               "abstraction", "hide complexity", "hiding complexity", "essential details", "hides implementation"),
            _c("Inheritance",
               "Explain that a child class reuses and extends a parent class.",
               "inheritance", "inherit", "child class", "parent class", "subclass", "base class"),
            _c("Polymorphism",
               "Explain that the same interface can behave differently for different objects.",
               "polymorphism", "many forms", "overriding", "same interface", "different behavior",
               "different behaviour"),
        ],
        "model_answer": (
            "The four pillars are encapsulation, abstraction, inheritance and polymorphism. Encapsulation bundles "
            "data and methods together and hides internal state behind a controlled interface. Abstraction hides "
            "complexity and exposes only the essential details. Inheritance lets a child class reuse and extend a "
            "parent class. Polymorphism lets different objects respond to the same method call in their own way, "
            "for example Dog and Cat both implementing speak()."
        ),
        "why_effective": (
            "It lists all four, gives each a one-line plain-language definition, and closes with a short example."
        ),
    },
    {
        "id": "OOP-02",
        "topic": "Object-Oriented Programming",
        "difficulty": "Beginner",
        "question": "What is the difference between a class and an object?",
        "concepts": [
            _c("Class as blueprint",
               "Describe a class as a blueprint or template that defines structure and behavior.",
               "blueprint", "template", "definition of", "prototype"),
            _c("Object as instance",
               "Explain that an object is a concrete instance created from the class.",
               "instance", "instantiate", "created from", "concrete", "real entity"),
            _c("Attributes and methods",
               "Mention that a class defines attributes (state) and methods (behavior).",
               "attributes", "methods", "properties", "state and behavior", "state and behaviour", "fields"),
        ],
        "model_answer": (
            "A class is a blueprint or template that defines the attributes (state) and methods (behavior) "
            "something will have. An object is a concrete instance created from that class, with its own values "
            "for those attributes. For example, Car is a class, while my red Honda and your blue Toyota are two "
            "objects, each an instance of Car, that share the same methods but hold different data."
        ),
        "why_effective": (
            "The blueprint-versus-instance contrast is memorable, and the Car example makes it concrete."
        ),
    },
    {
        "id": "OOP-03",
        "topic": "Object-Oriented Programming",
        "difficulty": "Intermediate",
        "question": "What is the difference between method overloading and method overriding?",
        "concepts": [
            _c("Overriding",
               "Explain that overriding is when a subclass redefines a method of its parent with the same signature.",
               "override", "overriding", "overrides", "redefine", "same signature", "subclass", "child class"),
            _c("Overloading",
               "Explain that overloading is multiple methods with the same name but different parameters.",
               "overload", "overloading", "same name", "different parameters", "different signature",
               "different arguments"),
            _c("Compile-time vs runtime polymorphism",
               "Link them to polymorphism: overloading is resolved at compile time, overriding at runtime.",
               "compile time", "runtime", "run time", "static polymorphism", "dynamic dispatch",
               "runtime polymorphism"),
        ],
        "model_answer": (
            "Overriding happens when a subclass redefines a method it inherited from its parent class using the "
            "same signature, so the subclass version runs instead. Overloading means defining several methods "
            "with the same name but different parameters. Overloading is resolved at compile time (static "
            "polymorphism), while overriding is resolved at runtime through dynamic dispatch. Note that Python "
            "does not support true overloading; you use default arguments instead."
        ),
        "why_effective": (
            "It defines both terms, ties them to compile-time and runtime polymorphism, and adds a "
            "language-specific note that shows depth."
        ),
    },
    {
        "id": "OOP-04",
        "topic": "Object-Oriented Programming",
        "difficulty": "Intermediate",
        "question": "What is the difference between inheritance and composition, and which would you usually prefer?",
        "concepts": [
            _c("Is-a versus has-a",
               "Explain that inheritance models an is-a relationship and composition models a has-a relationship.",
               "is a", "has a", "is a relationship", "has a relationship", "part of"),
            _c("Coupling and flexibility",
               "Explain that inheritance creates tight coupling while composition is more flexible and loosely coupled.",
               "tight coupling", "loose coupling", "loosely coupled", "tightly coupled", "coupling",
               "flexible", "flexibility", "fragile", "swap"),
            _c("Guideline: prefer composition",
               "State the common guideline: favor composition over inheritance, using inheritance for true is-a cases.",
               "composition over inheritance", "prefer composition", "favor composition",
               "favour composition", "reuse"),
        ],
        "model_answer": (
            "Inheritance models an is-a relationship, such as a Dog is an Animal, while composition models a has-a "
            "relationship, such as a Car has an Engine. Inheritance creates tight coupling between parent and "
            "child, so changes in the base class can break subclasses and deep hierarchies become fragile. "
            "Composition keeps classes loosely coupled and flexible, because you can swap the contained part at "
            "runtime. That is why the usual guideline is to prefer composition over inheritance, and reserve "
            "inheritance for genuine is-a cases."
        ),
        "why_effective": (
            "It contrasts the two relationships, justifies a preference with coupling arguments, and states the "
            "well-known guideline."
        ),
    },
    {
        "id": "OOP-05",
        "topic": "Object-Oriented Programming",
        "difficulty": "Intermediate",
        "question": "What is the difference between an abstract class and an interface?",
        "concepts": [
            _c("Abstract class can hold implementation and state",
               "Explain that an abstract class can contain concrete methods, fields and constructors shared by subclasses.",
               "concrete methods", "partial implementation", "shared code", "implemented methods",
               "fields", "constructor", "shared state", "can have state"),
            _c("Interface is a contract",
               "Explain that an interface defines a contract of method signatures with no (or minimal) implementation.",
               "contract", "only signatures", "method signatures", "no implementation", "protocol",
               "abstract methods"),
            _c("When to use which",
               "Mention multiple interfaces can be implemented, and choose an interface for capabilities, an abstract class for a shared base.",
               "multiple interfaces", "multiple inheritance", "implement multiple", "capability",
               "common base", "can do", "shared base"),
        ],
        "model_answer": (
            "An abstract class is a partially implemented base class: it can contain concrete methods, fields and "
            "a constructor that subclasses share, along with abstract methods they must implement. An interface "
            "is a pure contract that lists method signatures with no implementation, describing what a class can "
            "do. A class can usually implement multiple interfaces but extend only one abstract class. I use an "
            "abstract class when subclasses share code and state, and an interface to describe a capability that "
            "unrelated classes can offer."
        ),
        "why_effective": (
            "It separates 'shared implementation' from 'pure contract' and ends with a clear decision rule."
        ),
    },
    {
        "id": "OOP-06",
        "topic": "Object-Oriented Programming",
        "difficulty": "Challenging",
        "question": "Explain the Single Responsibility Principle and the Open/Closed Principle.",
        "concepts": [
            _c("Single Responsibility Principle",
               "Explain that a class should have one responsibility, meaning only one reason to change.",
               "single responsibility", "one reason to change", "one responsibility", "one job", "one purpose"),
            _c("Open/Closed Principle",
               "Explain that code should be open for extension but closed for modification.",
               "open closed", "open for extension", "closed for modification", "extend without modifying",
               "without modifying existing"),
            _c("Benefits",
               "Explain the benefits: easier testing, lower risk of regressions, better maintainability.",
               "maintainable", "maintainability", "easier to test", "testable", "regression",
               "loose coupling", "readability", "less risk"),
        ],
        "model_answer": (
            "The Single Responsibility Principle says a class should have only one responsibility, meaning one "
            "reason to change. A class that both calculates invoices and sends emails should be split in two. "
            "The Open/Closed Principle says software should be open for extension but closed for modification: "
            "you add new behavior by writing new code, for example a new Shape subclass, without modifying "
            "existing tested code. Together they make code more maintainable, easier to test and less likely to "
            "cause regressions."
        ),
        "why_effective": (
            "Each principle gets a definition and a concrete example, and the answer closes with why the "
            "principles matter."
        ),
    },
    # ------------------------------------------------------------------- DSA
    {
        "id": "DSA-01",
        "topic": "Data Structures and Algorithms",
        "difficulty": "Beginner",
        "question": "What is the difference between a stack and a queue?",
        "concepts": [
            _c("Stack is LIFO",
               "Explain that a stack is Last-In-First-Out: the most recently added item is removed first.",
               "lifo", "last in first out", "last in", "top of the stack"),
            _c("Queue is FIFO",
               "Explain that a queue is First-In-First-Out: the oldest item is removed first.",
               "fifo", "first in first out", "first in", "front of the queue", "rear"),
            _c("Core operations",
               "Name the operations: push/pop/peek for stacks, enqueue/dequeue for queues.",
               "push", "pop", "enqueue", "dequeue", "peek"),
            _c("Use cases",
               "Give uses: undo and the call stack for stacks; scheduling and BFS for queues.",
               "undo", "call stack", "recursion", "bfs", "scheduling", "print queue",
               "breadth first", "backtracking", "task queue"),
        ],
        "model_answer": (
            "A stack is Last-In-First-Out (LIFO): you push items on top and pop the most recent one first, like a "
            "pile of plates. A queue is First-In-First-Out (FIFO): you enqueue at the rear and dequeue from the "
            "front, like a line at a ticket counter. Stacks are used for undo features, the function call stack "
            "and backtracking, while queues are used for task scheduling and breadth first search."
        ),
        "why_effective": (
            "Each structure gets its ordering rule, its operations and a use case, and the real-life analogies make "
            "it easy to remember."
        ),
    },
    {
        "id": "DSA-02",
        "topic": "Data Structures and Algorithms",
        "difficulty": "Beginner",
        "question": "How does binary search work, what is its time complexity, and what must be true about the data?",
        "concepts": [
            _c("Requires sorted data",
               "State the precondition: the data must be sorted.",
               "sorted", "sort", "ordered", "in order"),
            _c("Halves the search space",
               "Explain that each step compares with the middle element and discards half of the remaining items.",
               "half", "halves", "middle", "mid", "divide", "eliminate", "discard"),
            _c("O(log n) complexity",
               "State the time complexity: O(log n).",
               "o log n", "log n", "logarithmic", "logn", "log2"),
        ],
        "model_answer": (
            "Binary search works only on sorted data. It compares the target with the middle element; if they are "
            "not equal it discards the half that cannot contain the target and repeats on the remaining half. "
            "Because the search space halves every step, the time complexity is O(log n), compared with O(n) for "
            "a linear scan. For example, finding a number in 1,000,000 sorted items takes about 20 comparisons."
        ),
        "why_effective": (
            "It states the precondition, explains the mechanism, gives the complexity, and backs it up with a "
            "number that makes O(log n) feel real."
        ),
    },
    {
        "id": "DSA-03",
        "topic": "Data Structures and Algorithms",
        "difficulty": "Intermediate",
        "question": "Compare arrays and linked lists. When would you choose each?",
        "concepts": [
            _c("Array: contiguous memory and fast indexing",
               "Explain that arrays store items contiguously and allow O(1) access by index.",
               "contiguous", "random access", "index", "indexing", "o 1", "constant time access"),
            _c("Linked list: nodes and pointers",
               "Explain that a linked list is made of nodes, each holding a value and a pointer to the next node.",
               "node", "pointer", "next node", "reference to the next", "linked nodes"),
            _c("Insertion and deletion trade-off",
               "Explain that inserting or deleting in an array needs shifting (O(n)), while a linked list can do it in O(1) once the position is known.",
               "shifting", "shift", "insertion", "deletion", "insert", "delete", "o n"),
            _c("Memory and overhead",
               "Mention extra memory for pointers, fixed versus dynamic size, and cache friendliness.",
               "extra memory", "overhead", "dynamic size", "fixed size", "resize", "cache"),
        ],
        "model_answer": (
            "An array stores elements in contiguous memory, so it gives O(1) random access by index and is cache "
            "friendly, but inserting or deleting in the middle requires shifting elements, which is O(n), and a "
            "fixed-size array may need to be resized. A linked list is a chain of nodes, each holding a value and "
            "a pointer to the next node, so inserting or deleting at a known position is O(1), but reaching the "
            "nth element requires walking the list in O(n) and each node has extra memory overhead for the "
            "pointer. I choose arrays when I need fast indexing and linked lists when I insert and delete often."
        ),
        "why_effective": (
            "It compares both structures on the same dimensions (access, insert, memory) and ends with a decision "
            "rule."
        ),
    },
    {
        "id": "DSA-04",
        "topic": "Data Structures and Algorithms",
        "difficulty": "Intermediate",
        "question": "How does a hash table work, and how are collisions handled?",
        "concepts": [
            _c("Hash function maps key to an index",
               "Explain that a hash function converts a key into an index (bucket) in an underlying array.",
               "hash function", "bucket", "index", "underlying array", "maps the key"),
            _c("What a collision is",
               "Define a collision: two different keys hashing to the same index.",
               "collision", "same index", "same bucket", "two keys"),
            _c("Collision resolution",
               "Name a strategy: chaining (linked lists per bucket) or open addressing (probing).",
               "chaining", "linked list", "open addressing", "probing", "linear probing", "double hashing"),
            _c("Load factor and resizing",
               "Mention load factor and resizing/rehashing to keep average operations O(1).",
               "load factor", "resize", "rehash", "rehashing", "average o 1", "o 1"),
        ],
        "model_answer": (
            "A hash table uses a hash function to convert a key into an index in an underlying array of buckets, "
            "giving O(1) average lookup, insert and delete. A collision occurs when two different keys map to the "
            "same bucket. Chaining handles this by storing a linked list in each bucket, while open addressing "
            "probes for the next free slot, for example with linear probing. To keep operations fast, the table "
            "tracks its load factor and resizes with rehashing when it gets too full."
        ),
        "why_effective": (
            "It explains the normal path first, then the exceptional case (collisions) and how performance is "
            "maintained."
        ),
    },
    {
        "id": "DSA-05",
        "topic": "Data Structures and Algorithms",
        "difficulty": "Intermediate",
        "question": "What is the difference between breadth-first search (BFS) and depth-first search (DFS)?",
        "concepts": [
            _c("BFS explores level by level using a queue",
               "Explain that BFS visits nodes level by level using a queue.",
               "level by level", "level order", "queue", "breadth", "nearest first", "layer by layer"),
            _c("DFS goes deep using a stack or recursion",
               "Explain that DFS follows a path as deep as possible before backtracking, using a stack or recursion.",
               "stack", "recursion", "recursive", "as deep as possible", "as far as possible",
               "backtrack", "depth"),
            _c("Typical uses",
               "Say BFS finds shortest paths in unweighted graphs, while DFS suits cycle detection, topological sort and exploring all paths.",
               "shortest path", "unweighted", "cycle detection", "topological", "connected components",
               "maze", "path finding"),
            _c("Complexity",
               "State that both run in O(V+E) time on a graph.",
               "o v+e", "v+e", "vertices and edges", "linear in the size", "time complexity"),
        ],
        "model_answer": (
            "BFS explores a graph level by level, visiting all neighbors of a node before going deeper, and it "
            "uses a queue. DFS follows one path as deep as possible before backtracking, and it uses a stack or "
            "recursion. BFS finds the shortest path in an unweighted graph, while DFS is useful for cycle "
            "detection, topological sorting and exploring every path. Both have time complexity O(V+E), where V "
            "is the number of vertices and E the number of edges."
        ),
        "why_effective": (
            "It contrasts the traversal order, the supporting data structure, the best use cases and the "
            "complexity."
        ),
    },
    {
        "id": "DSA-06",
        "topic": "Data Structures and Algorithms",
        "difficulty": "Challenging",
        "question": "Compare quicksort and merge sort in terms of approach, complexity and stability.",
        "concepts": [
            _c("Divide and conquer approach",
               "Explain that both split the problem into smaller subproblems and solve them recursively.",
               "divide and conquer", "divide", "recursively", "subarrays", "sub arrays", "split"),
            _c("Quicksort pivot and partition",
               "Explain that quicksort picks a pivot and partitions elements around it, while merge sort splits in half and merges.",
               "pivot", "partition", "random pivot", "median of three", "merge step", "merging"),
            _c("Time complexity",
               "State O(n log n) average for both, with quicksort's worst case O(n squared) and merge sort always O(n log n).",
               "n log n", "nlogn", "worst case", "quadratic", "n squared", "o n2", "o n 2", "average case"),
            _c("Space and stability",
               "Mention that merge sort is stable and needs O(n) extra space, while quicksort is usually in-place and not stable.",
               "stable", "stability", "in place", "extra space", "auxiliary", "extra memory"),
        ],
        "model_answer": (
            "Both are divide and conquer algorithms that split the array and sort the parts recursively. Quicksort "
            "chooses a pivot and partitions the elements around it, while merge sort splits the array in half and "
            "then merges the sorted halves. Both average O(n log n) time, but quicksort has an O(n squared) worst "
            "case with bad pivots such as an already sorted array, which a random pivot makes unlikely, whereas "
            "merge sort is always O(n log n). Merge sort is stable but needs O(n) extra space, while quicksort "
            "sorts in place and is not stable."
        ),
        "why_effective": (
            "It compares the two across approach, worst-case behavior and space, which is exactly what "
            "interviewers want to hear."
        ),
    },
    # ------------------------------------------------------------------- SQL
    {
        "id": "SQL-01",
        "topic": "SQL and Databases",
        "difficulty": "Beginner",
        "question": "What is the difference between a primary key and a foreign key?",
        "concepts": [
            _c("Primary key uniquely identifies a row",
               "Explain that a primary key uniquely identifies each row and cannot be NULL.",
               "uniquely", "unique", "identifies", "identifier", "not null"),
            _c("Foreign key references another table",
               "Explain that a foreign key is a column that refers to the primary key of another table.",
               "references", "refers to", "links", "another table", "parent table", "relationship"),
            _c("Referential integrity",
               "Mention that foreign keys enforce referential integrity, preventing orphan records.",
               "referential integrity", "integrity", "constraint", "orphan", "consistency"),
        ],
        "model_answer": (
            "A primary key uniquely identifies each row in a table, so its values must be unique and cannot be "
            "NULL. A foreign key is a column in one table that references the primary key of another table, "
            "creating a relationship between them. Foreign keys enforce referential integrity, because the "
            "database will not allow an orphan record that points to a row that does not exist. For example, "
            "orders.customer_id is a foreign key to customers.id."
        ),
        "why_effective": (
            "It defines both keys, explains the guarantee that foreign keys give, and uses a familiar "
            "customers-and-orders example."
        ),
    },
    {
        "id": "SQL-02",
        "topic": "SQL and Databases",
        "difficulty": "Beginner",
        "question": "What is the difference between WHERE and HAVING in SQL?",
        "concepts": [
            _c("WHERE filters rows before grouping",
               "Explain that WHERE filters individual rows before any grouping happens.",
               "before grouping", "before group by", "individual rows", "filters rows", "filter rows", "each row"),
            _c("HAVING filters groups after aggregation",
               "Explain that HAVING filters groups after GROUP BY and aggregation.",
               "after grouping", "after group by", "filters groups", "filter groups", "after aggregation",
               "aggregated", "groups"),
            _c("Aggregate functions",
               "Mention that HAVING can use aggregate functions such as COUNT or SUM, but WHERE cannot.",
               "aggregate function", "aggregate functions", "count", "sum", "avg", "max", "min"),
        ],
        "model_answer": (
            "WHERE filters individual rows before any grouping happens, while HAVING filters groups after GROUP BY "
            "and aggregation. Because WHERE runs before aggregation, it cannot use aggregate functions, whereas "
            "HAVING can use them. For example, SELECT dept, COUNT(*) FROM staff WHERE active = 1 GROUP BY dept "
            "HAVING COUNT(*) > 5 first keeps only active rows, then keeps only departments with more than five "
            "people."
        ),
        "why_effective": (
            "It explains the order of execution, which is the real reason for the difference, and proves it with "
            "one query."
        ),
    },
    {
        "id": "SQL-03",
        "topic": "SQL and Databases",
        "difficulty": "Intermediate",
        "question": "What is the difference between an INNER JOIN and a LEFT JOIN?",
        "concepts": [
            _c("INNER JOIN returns only matches",
               "Explain that INNER JOIN returns only rows that have a match in both tables.",
               "only matching", "matching rows", "match in both", "both tables", "intersection"),
            _c("LEFT JOIN keeps all left rows",
               "Explain that LEFT JOIN returns every row from the left table, whether or not it has a match.",
               "all rows from the left", "left table", "all rows", "unmatched", "keeps all", "preserved"),
            _c("NULLs for missing matches",
               "Explain that unmatched right-side columns are filled with NULL.",
               "null", "nulls", "no match", "missing"),
            _c("Practical use",
               "Give a use, such as finding customers who have no orders.",
               "without orders", "no orders", "anti join", "missing records", "customers who"),
        ],
        "model_answer": (
            "An INNER JOIN returns only the rows that have a matching value in both tables. A LEFT JOIN returns "
            "all rows from the left table, and for rows with no match in the right table the right-side columns "
            "are filled with NULL. For example, joining customers to orders with a LEFT JOIN keeps customers who "
            "have no orders, and filtering for NULL on the orders side finds customers who have never ordered, "
            "which an INNER JOIN would silently drop."
        ),
        "why_effective": (
            "It describes the result of each join, explains the NULL behavior, and shows a realistic reason to "
            "pick LEFT JOIN."
        ),
    },
    {
        "id": "SQL-04",
        "topic": "SQL and Databases",
        "difficulty": "Intermediate",
        "question": "What is database normalization and why is it used?",
        "concepts": [
            _c("Reduces redundancy",
               "Explain that normalization organizes data to remove duplicated information.",
               "redundancy", "duplicate data", "duplication", "repeated data", "redundant"),
            _c("Prevents anomalies",
               "Explain that it prevents update, insertion and deletion anomalies and keeps data consistent.",
               "anomaly", "anomalies", "update anomaly", "insertion anomaly", "deletion anomaly",
               "inconsistent", "inconsistency"),
            _c("Normal forms",
               "Mention the normal forms (1NF, 2NF, 3NF).",
               "1nf", "2nf", "3nf", "first normal form", "second normal form", "third normal form",
               "normal forms", "bcnf"),
            _c("Trade-off with denormalization",
               "Mention the trade-off: more joins can slow reads, so some systems denormalize on purpose.",
               "denormalization", "denormalize", "more joins", "joins", "read performance", "trade off"),
        ],
        "model_answer": (
            "Normalization is the process of organizing tables so that each fact is stored once, which reduces "
            "redundancy. This prevents update, insertion and deletion anomalies; for example, if a customer's "
            "address is stored on every order, changing it in one place leaves inconsistent data. It is done "
            "through normal forms such as 1NF, 2NF and 3NF, which progressively remove repeating groups and "
            "dependencies. The trade-off is that queries need more joins, so read-heavy systems sometimes "
            "denormalize on purpose."
        ),
        "why_effective": (
            "It explains the purpose, gives a concrete anomaly, names the normal forms, and shows balanced "
            "judgment by mentioning denormalization."
        ),
    },
    {
        "id": "SQL-05",
        "topic": "SQL and Databases",
        "difficulty": "Intermediate",
        "question": "What are the ACID properties of a database transaction?",
        "concepts": [
            _c("Atomicity",
               "Explain atomicity: a transaction is all-or-nothing.",
               "atomicity", "atomic", "all or nothing", "rollback", "rolled back"),
            _c("Consistency",
               "Explain consistency: a transaction moves the database from one valid state to another, respecting constraints.",
               "consistency", "consistent", "valid state", "constraints"),
            _c("Isolation",
               "Explain isolation: concurrent transactions do not interfere with each other.",
               "isolation", "isolated", "concurrent", "concurrency", "interfere"),
            _c("Durability",
               "Explain durability: once committed, data survives crashes.",
               "durability", "durable", "permanent", "persist", "crash", "power failure", "committed"),
        ],
        "model_answer": (
            "ACID stands for Atomicity, Consistency, Isolation and Durability. Atomicity means a transaction is "
            "all or nothing: if any step fails, everything is rolled back. Consistency means a transaction moves "
            "the database from one valid state to another and respects all constraints. Isolation means concurrent "
            "transactions do not interfere with each other's intermediate results. Durability means that once a "
            "transaction is committed, it persists even after a crash or power failure. A bank transfer is the "
            "classic example: debit and credit must both happen or neither."
        ),
        "why_effective": (
            "All four properties are defined in one sentence each, and the bank transfer ties them together."
        ),
    },
    {
        "id": "SQL-06",
        "topic": "SQL and Databases",
        "difficulty": "Challenging",
        "question": "How do database indexes work, and what are the trade-offs of adding them?",
        "concepts": [
            _c("Speeds up reads",
               "Explain that an index lets the database find rows without scanning the whole table.",
               "full table scan", "faster lookup", "speed up", "speeds up", "faster queries",
               "query performance", "avoid scanning", "quickly find"),
            _c("Data structure (B-tree)",
               "Mention that indexes are typically B-tree structures that keep keys sorted.",
               "b tree", "b+ tree", "balanced tree", "sorted structure", "tree"),
            _c("Cost on writes and storage",
               "Explain that indexes slow down inserts, updates and deletes and use extra storage.",
               "slower writes", "slow down writes", "slow down inserts", "extra storage", "overhead",
               "must be updated", "maintain the index", "additional storage"),
            _c("When to index",
               "Say to index columns used in WHERE, JOIN and ORDER BY clauses and avoid over-indexing.",
               "where clause", "join", "frequently queried", "selective", "high cardinality",
               "over indexing", "too many indexes", "foreign key"),
        ],
        "model_answer": (
            "An index is an additional data structure, usually a B-tree, that keeps the values of a column sorted "
            "with pointers to the rows, so the database can find rows quickly instead of doing a full table scan. "
            "This speeds up queries that filter or join on that column. The cost is that every insert, update and "
            "delete must also update the index, which means slower writes, and the index takes extra storage. "
            "So I index columns that are frequently used in WHERE clauses and joins and have high cardinality, "
            "and avoid too many indexes on write-heavy tables."
        ),
        "why_effective": (
            "It explains how an index works, who benefits, who pays, and gives a rule of thumb for choosing "
            "columns."
        ),
    },
    # -------------------------------------------------------------------- OS
    {
        "id": "OS-01",
        "topic": "Operating Systems",
        "difficulty": "Beginner",
        "question": "What is the difference between a process and a thread?",
        "concepts": [
            _c("Process is an isolated program in execution",
               "Explain that a process is a running program with its own separate memory space.",
               "own memory", "separate memory", "memory space", "address space", "isolated",
               "program in execution", "independent"),
            _c("Threads share memory within a process",
               "Explain that threads live inside a process and share its memory and resources.",
               "share memory", "shares memory", "shared memory", "within a process", "same process",
               "lightweight"),
            _c("Cost and switching",
               "Mention that threads are cheaper to create and switch between than processes.",
               "context switch", "context switching", "overhead", "cheaper", "faster to create"),
            _c("Communication and risks",
               "Mention that threads need synchronization to avoid race conditions, while processes need IPC.",
               "ipc", "inter process communication", "race condition", "synchronization",
               "synchronisation", "crash"),
        ],
        "model_answer": (
            "A process is a program in execution with its own separate memory space, so processes are isolated "
            "from each other. A thread is a lightweight unit of execution inside a process, and all threads in "
            "the same process share its memory and resources. Because of this, creating a thread and switching "
            "context between threads is cheaper than for processes. The downside is that threads need "
            "synchronization to avoid a race condition on shared data, while separate processes must use IPC "
            "(inter process communication) to talk, but one crashing process does not take down the others."
        ),
        "why_effective": (
            "It contrasts isolation versus sharing and links each to its cost and risk."
        ),
    },
    {
        "id": "OS-02",
        "topic": "Operating Systems",
        "difficulty": "Beginner",
        "question": "What is a deadlock, and what conditions must hold for it to occur?",
        "concepts": [
            _c("Definition of deadlock",
               "Define deadlock: processes are blocked forever, each waiting for a resource another one holds.",
               "waiting for each other", "wait for each other", "blocked", "indefinitely", "forever",
               "stuck", "never release"),
            _c("The four Coffman conditions",
               "Name the four conditions: mutual exclusion, hold and wait, no preemption, circular wait.",
               "mutual exclusion", "hold and wait", "no preemption", "circular wait"),
            _c("Prevention and handling",
               "Mention ways to deal with it: prevention, avoidance (Banker's algorithm), detection and recovery, or lock ordering.",
               "prevention", "avoidance", "detection", "recovery", "banker", "lock ordering",
               "timeout", "break one"),
        ],
        "model_answer": (
            "A deadlock is a situation where a set of processes are blocked forever because each is waiting for a "
            "resource held by another, so none can proceed. It requires four conditions at the same time: mutual "
            "exclusion, hold and wait, no preemption, and circular wait. Breaking any one of them prevents "
            "deadlock. Systems handle it through prevention, avoidance such as the Banker's algorithm, detection "
            "and recovery, or in practice by always acquiring locks in a fixed order. A classic example is two "
            "threads each holding one lock and waiting for the other."
        ),
        "why_effective": (
            "It defines the problem, names all four conditions precisely, and shows practical ways to deal with it."
        ),
    },
    {
        "id": "OS-03",
        "topic": "Operating Systems",
        "difficulty": "Intermediate",
        "question": "What is virtual memory and how does paging work?",
        "concepts": [
            _c("Virtual memory abstraction",
               "Explain that virtual memory gives each process the illusion of a large private address space.",
               "virtual memory", "virtual address", "illusion", "larger than ram", "address space",
               "abstraction"),
            _c("Pages, frames and page table",
               "Explain that memory is split into fixed-size pages and frames, and a page table maps virtual pages to physical frames.",
               "page table", "pages", "frames", "paging", "fixed size"),
            _c("Page faults and swapping",
               "Explain that when a page is not in RAM a page fault occurs and the OS loads it from disk (swap).",
               "page fault", "swap", "swapping", "disk", "demand paging", "secondary storage"),
            _c("Benefits",
               "Mention benefits: process isolation, efficient use of RAM and less fragmentation.",
               "isolation", "protection", "fragmentation", "efficient use", "memory management"),
        ],
        "model_answer": (
            "Virtual memory gives every process the illusion of its own large, continuous address space, even if "
            "the physical RAM is smaller. With paging, the address space is split into fixed size pages and "
            "physical memory into frames of the same size, and a page table maps each virtual page to a frame. "
            "If a process touches a page that is not in RAM, a page fault occurs and the OS loads that page from "
            "disk, which is called demand paging, swapping out another page if needed. This provides isolation "
            "between processes and reduces fragmentation."
        ),
        "why_effective": (
            "It starts with the purpose, explains the mechanism step by step including the exceptional case, and "
            "closes with benefits."
        ),
    },
    {
        "id": "OS-04",
        "topic": "Operating Systems",
        "difficulty": "Intermediate",
        "question": "Explain common CPU scheduling algorithms and how to compare them.",
        "concepts": [
            _c("Scheduling goals and metrics",
               "Name the metrics used to compare them: throughput, turnaround time, waiting time, response time, fairness.",
               "throughput", "turnaround", "waiting time", "response time", "fairness", "cpu utilization"),
            _c("Named algorithms",
               "Describe at least two algorithms, such as FCFS, SJF, Round Robin or priority scheduling.",
               "fcfs", "first come first served", "sjf", "shortest job first", "round robin",
               "priority scheduling", "multilevel"),
            _c("Trade-offs and problems",
               "Mention trade-offs such as starvation, the convoy effect, time quantum choice and preemption.",
               "starvation", "convoy effect", "time quantum", "quantum", "preemptive", "non preemptive",
               "aging"),
        ],
        "model_answer": (
            "Schedulers are compared using metrics such as throughput, turnaround time, waiting time, response "
            "time and fairness. FCFS runs processes in arrival order and is simple, but short jobs can get stuck "
            "behind a long one, which is the convoy effect. Shortest Job First minimizes average waiting time but "
            "can cause starvation of long jobs, which aging can fix. Round Robin gives each process a time "
            "quantum, which is fair and gives good response time, but a quantum that is too small wastes time on "
            "context switches. Real systems combine these ideas in priority and multilevel queues."
        ),
        "why_effective": (
            "It first defines how to judge schedulers, then compares algorithms against those criteria, including "
            "their failure modes."
        ),
    },
    {
        "id": "OS-05",
        "topic": "Operating Systems",
        "difficulty": "Intermediate",
        "question": "What is the difference between a mutex and a semaphore?",
        "concepts": [
            _c("Mutex: exclusive lock with ownership",
               "Explain that a mutex is a lock for mutual exclusion, held and released by the same thread.",
               "mutex", "mutual exclusion", "ownership", "owner", "unlock", "only one thread"),
            _c("Semaphore: counter",
               "Explain that a semaphore is a counter that allows up to N threads and uses wait and signal operations.",
               "semaphore", "counter", "counting semaphore", "binary semaphore", "signal", "permits"),
            _c("Purpose: protect shared resources",
               "Explain that both are used to prevent race conditions on shared data in a critical section.",
               "critical section", "race condition", "shared resource", "shared data", "synchronization"),
        ],
        "model_answer": (
            "Both are synchronization tools used to protect shared data and prevent race conditions in a critical "
            "section. A mutex is a lock for mutual exclusion: only one thread can hold it, and the same thread "
            "that locked it must unlock it, so it has ownership. A semaphore is a counter that controls access to "
            "a limited number of resources: wait decrements it and signal increments it, so a counting semaphore "
            "can allow several threads at once, and it can also be used for signaling between threads. For "
            "example, a mutex guards one shared variable, while a semaphore limits a pool to five database "
            "connections."
        ),
        "why_effective": (
            "It separates ownership and exclusivity (mutex) from counting and signaling (semaphore), and the "
            "connection-pool example makes the difference practical."
        ),
    },
    {
        "id": "OS-06",
        "topic": "Operating Systems",
        "difficulty": "Challenging",
        "question": "What are user mode and kernel mode, and how do system calls connect them?",
        "concepts": [
            _c("Two privilege modes",
               "Explain that kernel mode has full hardware access while user mode is restricted.",
               "user mode", "kernel mode", "privileged", "privilege", "restricted", "ring"),
            _c("System calls",
               "Explain that a system call is the controlled way a user program requests a kernel service, using a trap or interrupt.",
               "system call", "syscall", "trap", "software interrupt", "request the kernel", "kernel service"),
            _c("Why the separation exists",
               "Explain that the split protects the system: a buggy or malicious program cannot directly access hardware or crash the OS.",
               "protection", "security", "stability", "crash", "direct access", "hardware", "isolate"),
        ],
        "model_answer": (
            "Modern CPUs run code in at least two privilege levels. In kernel mode the operating system has full "
            "access to hardware and memory, while in user mode applications are restricted and cannot directly "
            "touch devices. When a program needs a privileged service such as reading a file, it makes a system "
            "call, which triggers a trap that switches the CPU into kernel mode, runs the kernel code, and then "
            "returns to user mode. This separation provides protection and stability, because a buggy or "
            "malicious application cannot directly access hardware or crash the whole system."
        ),
        "why_effective": (
            "It explains the two modes, the controlled transition between them, and the reason the design exists."
        ),
    },
    # -------------------------------------------------------------- NETWORKS
    {
        "id": "NET-01",
        "topic": "Computer Networks",
        "difficulty": "Beginner",
        "question": "What is the difference between TCP and UDP?",
        "concepts": [
            _c("TCP is reliable and connection-oriented",
               "Explain that TCP sets up a connection (three-way handshake) and guarantees ordered, reliable delivery with acknowledgements and retransmission.",
               "reliable", "reliability", "connection oriented", "handshake", "acknowledgement",
               "acknowledgment", "retransmission", "retransmit", "ordered delivery", "in order"),
            _c("UDP is connectionless and fast",
               "Explain that UDP has no connection setup and no delivery guarantees, so it has lower latency and overhead.",
               "connectionless", "no handshake", "low latency", "lightweight", "no guarantee",
               "unreliable", "best effort", "faster"),
            _c("Use cases",
               "Give uses: TCP for web, email and file transfer; UDP for streaming, gaming, VoIP and DNS.",
               "http", "file transfer", "email", "streaming", "video", "gaming", "voip", "dns",
               "live", "web browsing"),
        ],
        "model_answer": (
            "TCP is connection-oriented and reliable: it establishes a connection with a three way handshake, "
            "numbers the data, uses acknowledgements and retransmission, and delivers bytes in order. UDP is "
            "connectionless, with no handshake and no delivery guarantee, so it is lighter and has lower "
            "latency. TCP is used where correctness matters, such as web pages, email and file transfer, while "
            "UDP is used where speed matters more than perfect delivery, such as video streaming, online gaming "
            "and DNS."
        ),
        "why_effective": (
            "It compares reliability, overhead and use cases and shows the trade-off between correctness and speed."
        ),
    },
    {
        "id": "NET-02",
        "topic": "Computer Networks",
        "difficulty": "Beginner",
        "question": "What happens when you type a URL into your browser and press Enter?",
        "concepts": [
            _c("DNS resolution",
               "Explain that the browser uses DNS to translate the domain name into an IP address.",
               "dns", "domain name", "ip address", "resolve", "name server"),
            _c("TCP and TLS connection",
               "Explain that the browser opens a TCP connection to the server and, for HTTPS, performs a TLS handshake.",
               "tcp", "handshake", "tls", "ssl", "https", "three way handshake"),
            _c("HTTP request and response",
               "Explain that the browser sends an HTTP request and the server returns a response with a status code and content.",
               "http request", "request", "response", "status code", "server responds"),
            _c("Rendering",
               "Explain that the browser parses the HTML, loads CSS, JavaScript and images, and renders the page.",
               "render", "rendering", "html", "css", "javascript", "dom", "parse"),
        ],
        "model_answer": (
            "First the browser uses DNS to resolve the domain name into an IP address, checking caches before "
            "asking a DNS server. It then opens a TCP connection to that IP with a handshake and, for HTTPS, "
            "performs a TLS handshake to set up encryption. The browser sends an HTTP request, and the server "
            "sends back a response with a status code and the HTML. Finally the browser parses the HTML, fetches "
            "CSS, JavaScript and images, builds the DOM and renders the page."
        ),
        "why_effective": (
            "The steps are in the correct order, and each one names the protocol responsible."
        ),
    },
    {
        "id": "NET-03",
        "topic": "Computer Networks",
        "difficulty": "Intermediate",
        "question": "Explain the OSI model and how it relates to the TCP/IP model.",
        "concepts": [
            _c("The seven OSI layers",
               "Name the seven layers: physical, data link, network, transport, session, presentation, application.",
               "physical layer", "data link", "network layer", "transport layer", "session layer",
               "presentation layer", "application layer", "seven layers", "7 layers"),
            _c("TCP/IP has four layers",
               "Explain that TCP/IP condenses these into four layers: link, internet, transport and application.",
               "four layers", "4 layers", "internet layer", "link layer", "tcp ip"),
            _c("Responsibilities and examples",
               "Give examples per layer, such as Ethernet and MAC addresses, IP and routing, TCP/UDP, HTTP.",
               "ethernet", "mac address", "routing", "ip address", "tcp", "udp", "http", "encapsulation"),
            _c("Purpose of layering",
               "Explain that layering standardizes communication, hides complexity and makes troubleshooting modular.",
               "standardize", "standardization", "interoperability", "reference model", "modular",
               "troubleshooting", "conceptual"),
        ],
        "model_answer": (
            "The OSI model is a seven layer reference model: physical, data link, network, transport, session, "
            "presentation and application layers. Each layer has a defined job, for example the data link layer "
            "uses MAC addresses over Ethernet, the network layer uses IP addresses and routing, the transport "
            "layer provides TCP or UDP, and the application layer carries protocols like HTTP. The TCP/IP model "
            "that the internet actually uses has four layers: link, internet, transport and application, "
            "combining several OSI layers. Layering standardizes communication, hides complexity and makes "
            "troubleshooting modular, because you can reason about one layer at a time."
        ),
        "why_effective": (
            "It lists the layers, maps them to real protocols, relates the model to TCP/IP, and explains why "
            "layering exists."
        ),
    },
    {
        "id": "NET-04",
        "topic": "Computer Networks",
        "difficulty": "Intermediate",
        "question": "What is the difference between HTTP and HTTPS, and how does TLS secure a connection?",
        "concepts": [
            _c("Encryption in transit",
               "Explain that HTTPS encrypts traffic, so attackers cannot read or modify it, unlike plain-text HTTP.",
               "encrypt", "encrypted", "encryption", "plain text", "plaintext", "eavesdrop",
               "eavesdropping", "confidentiality", "port 443"),
            _c("TLS handshake and keys",
               "Explain that the TLS handshake uses certificates and public-key cryptography to agree on a symmetric session key.",
               "tls", "ssl", "handshake", "certificate", "public key", "private key", "symmetric",
               "session key"),
            _c("Authentication and integrity",
               "Explain that certificates prove the server's identity and TLS detects tampering, preventing man-in-the-middle attacks.",
               "authenticate", "authentication", "identity", "integrity", "tampering",
               "man in the middle", "certificate authority", "trusted"),
        ],
        "model_answer": (
            "HTTP sends data in plain text, so anyone on the path can read or modify it. HTTPS is HTTP running "
            "over TLS, which encrypts the traffic, usually on port 443. During the TLS handshake the server "
            "presents a certificate, and the client and server use public key cryptography to agree on a "
            "symmetric session key that encrypts the rest of the session. The certificate, signed by a trusted "
            "certificate authority, proves the server's identity, and TLS also provides integrity so tampering "
            "is detected, which protects against man in the middle attacks."
        ),
        "why_effective": (
            "It explains the problem with HTTP, then the TLS mechanism step by step, and finishes with the three "
            "guarantees: confidentiality, authentication and integrity."
        ),
    },
    {
        "id": "NET-05",
        "topic": "Computer Networks",
        "difficulty": "Intermediate",
        "question": "What is DNS and how does a DNS lookup work?",
        "concepts": [
            _c("Maps domain names to IP addresses",
               "Explain that DNS translates human-readable domain names into IP addresses, like a phone book.",
               "domain name", "ip address", "translate", "translates", "maps", "phone book"),
            _c("Resolution hierarchy",
               "Explain that a recursive resolver queries root servers, then TLD servers, then the authoritative name server.",
               "recursive", "resolver", "root server", "tld", "authoritative", "name server",
               "hierarchy", "iterative"),
            _c("Caching",
               "Mention that answers are cached at several levels for the duration of the TTL.",
               "cache", "cached", "caching", "ttl", "time to live"),
            _c("Record types",
               "Mention common record types such as A, AAAA, CNAME and MX.",
               "a record", "aaaa", "cname", "mx", "ns record", "records"),
        ],
        "model_answer": (
            "DNS is the internet's phone book: it translates human-readable domain names into IP addresses. When "
            "you look up a name, your device asks a recursive resolver, which checks its cache first. If it does "
            "not have the answer, it asks a root server, which points to the TLD server (for .com), which points "
            "to the authoritative name server that returns the real record. Answers are cached for the duration "
            "of the TTL to make future lookups faster. Common records include A for IPv4, AAAA for IPv6, CNAME "
            "for aliases and MX for mail."
        ),
        "why_effective": (
            "It explains the purpose, walks through the hierarchy in order, and includes caching and record types "
            "that many candidates forget."
        ),
    },
    {
        "id": "NET-06",
        "topic": "Computer Networks",
        "difficulty": "Challenging",
        "question": "What is the difference between TCP flow control and congestion control?",
        "concepts": [
            _c("Flow control protects the receiver",
               "Explain that flow control stops a fast sender from overwhelming the receiver, using the receive window.",
               "receiver", "receive window", "window size", "sliding window", "rwnd", "overwhelm",
               "buffer"),
            _c("Congestion control protects the network",
               "Explain that congestion control limits sending rate to avoid overloading routers, using the congestion window, slow start and AIMD.",
               "congestion", "congestion window", "cwnd", "router", "routers", "packet loss",
               "slow start", "congestion avoidance", "aimd"),
            _c("Why both are needed",
               "Explain that they solve different problems and the sender uses the smaller of the two windows.",
               "different problems", "different problem", "smaller of", "minimum of", "both",
               "network and the receiver", "end to end"),
        ],
        "model_answer": (
            "Flow control and congestion control both limit how fast a TCP sender transmits, but they protect "
            "different things. Flow control protects the receiver: the receiver advertises a receive window "
            "(rwnd) telling the sender how much buffer space it has, so a fast sender does not overwhelm a slow "
            "receiver. Congestion control protects the network: the sender maintains a congestion window (cwnd) "
            "and grows it with slow start and congestion avoidance, then reduces it when packet loss signals "
            "that routers are overloaded. They solve different problems, so the sender uses the smaller of the "
            "two windows."
        ),
        "why_effective": (
            "It states up front what each mechanism protects, names the exact variables, and closes with how "
            "they work together."
        ),
    },
]


# ---------------------------------------------------------------------------
# Helper functions
# ---------------------------------------------------------------------------

def get_all_questions():
    """Return every question (a list of dictionaries)."""
    return list(QUESTIONS)


def get_question_by_id(question_id):
    """Return the question with this id, or None if it does not exist."""
    for question in QUESTIONS:
        if question["id"] == question_id:
            return question
    return None


def filter_questions(topic=None, difficulty=None, keyword=None):
    """
    Return questions matching ALL given filters.

    topic / difficulty : exact match; None or "All" means "do not filter".
    keyword            : case-insensitive text that must appear in the question
                         text, the topic, or any expected concept name.
                         (We deliberately do NOT search the model answer so that
                         searching cannot reveal answers.)
    """
    results = []
    keyword = (keyword or "").strip().lower()
    for question in QUESTIONS:
        if topic and topic != "All" and question["topic"] != topic:
            continue
        if difficulty and difficulty != "All" and question["difficulty"] != difficulty:
            continue
        if keyword:
            searchable = " ".join(
                [question["question"], question["topic"]] + [c["name"] for c in question["concepts"]]
            ).lower()
            if keyword not in searchable:
                continue
        results.append(question)
    return results


def validate_question_bank(questions=None):
    """
    Check that every question is well-formed.
    Returns a list of problem descriptions (an empty list means everything is fine).
    """
    questions = QUESTIONS if questions is None else questions
    problems = []
    seen_ids = set()
    required = ("id", "topic", "difficulty", "question", "concepts", "model_answer", "why_effective")
    for q in questions:
        qid = q.get("id", "<missing id>")
        for field_name in required:
            if not q.get(field_name):
                problems.append(f"{qid}: missing '{field_name}'")
        if qid in seen_ids:
            problems.append(f"{qid}: duplicate id")
        seen_ids.add(qid)
        if q.get("topic") not in TOPICS:
            problems.append(f"{qid}: unknown topic {q.get('topic')!r}")
        if q.get("difficulty") not in DIFFICULTIES:
            problems.append(f"{qid}: unknown difficulty {q.get('difficulty')!r}")
        for concept in q.get("concepts", []):
            if not concept.get("name") or not concept.get("keywords") or not concept.get("hint"):
                problems.append(f"{qid}: concept {concept.get('name')!r} needs name, hint and keywords")
    return problems
