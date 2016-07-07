## python-concurrent-disk-io

Quickstart
----------
Start up an eventlet-based server that simulates disk io:

    python simulated-disk-io-server.py

Then, fire up several requests:

    $ for i in {1..10}; do
        ./make_requests.py&
      done

(that's a candidate for rewriting in Python-3/curio)

The server will print out `timeout (service)` when the eventlet problem is encountered.


Project Focus (problem definition)
----------------------------------
The focus of this project is to explore server functionality that
receives a request from a TCP socket and then simulates a blocking
IO disk read and then returns a reply to the client. Ideally, the
server should support multiple concurrent requests and service
the requests in parallel.

Motivation/Background
---------------------
The motivation for this project comes from OpenStack Swift where
the 'object server' (written in Python and making use of 'eventlet')
could occasionally hang due to dying disk drives that cause excessive
read times (measured in seconds as opposed to milliseconds).

Long Blocking IO
----------------
The fundamental problem is that when hard disk drives are starting
to go bad IO requests to the drive can block for an extended period
of time (tens of seconds). The problem is not present when all disk
drives are functioning normally.

Testing Long Blocking IO
------------------------
Since the long blocking IO scenario here occurs when a disk drive
is going bad, it's very difficult (if not impossible) to reliably
reproduce. The concensus from some of the OpenStack Swift experts
on this topic is to use a 'sleep' call to mimic the blocking call.
This is what each of the implementations presented here does to
simulate the long blocking call.

"Just Use Async IO"
-------------------
"Just use async IO" is probably the most common suggested solution
to the problem at hand. Unfortunately, it doesn't solve the problem.
The problem is that file I/O operations are blocking.
The favored standard Python implementation uses green threads,
while other languages (explicitly or implicitly) affect non-blocking
file I/O (either through threads, or otherwise).
The commonly held nothion that this is due to Python's
Global Interpreter Lock (GIL) is a misnomer - any blocking
operation on cooperatively scheduled asynchronous coroutines will
block, regardless of the language.
Green threads implement effectively what Python 3.5+ async/await
accomplishes, and it is up the the programmer to choose the appropriate
cooperative asynchronous models at the right points.
The correct programming paradigm is to always put I/O in asynchronous
coroutines, and thus avoid blocking.
Unfortunately, physical devices, like disk drives, do not cooperate
well in this model (unpredictably slow - even more so when intermittent
failures appear), and thus doing operations on physical devices
appropriately should be done in a separate thread, so as to ensure
a consistent cooperative multitasking environment.
This becomes clearly obvious when looking at the jython implementation,
where greenlets (which are compiled code - not python native) are
not available, and the other option is a full on threading model.
While the point of threading there masks the specific point of failure,
it is a good hint.
Following a disciplined paradigm for cooperative multiprocessing,
and thus using async, leads to a solution for the blocked, problematic IO requests.


The Problem is Not Python
-------------------------
It would be easy to pin the problem on Python (the language) and
conclude that the language is fundamentally flawed. Such a conclusion
would be incorrect. The test performed using **Jython** (Python
implemented on the Java Virtual Machine) did not experience the same
problems encountered by CPython. Therefore, it's not a defect in the
language definition. The problems experienced with CPython appear to
be based on the **implementation** *of the solution code*.

Intent
------
The **intent** of this project is 
to take an objective look at the
problem and fully understand the nature of the problem.
A solution may or may not come naturally as part of this process.

Baseline
--------
The baseline (reference) for this project is the **eventlet-based
CPython** implementation (simulated-disk-io-server.py).

Alternatives Explored
---------------------
The goal of this project is to demonstrate the problem in a concise
and understandable manner and to explore various alternatives (whether
they be eventlet alternatives in Python or even different programming
languages).

Note on Implementations
-----------------------
None of the implementations presented here are idiomatic for their
respective languages. This was done intentionally to keep the code
clear and somewhat similar (across languages).

Client
------
The client utility used for testing is 'make_requests.py'.

The Test
--------
1. Start the server implementation
2. Run multiple request processes (at least 4 or 5)
3. run 'python make_requests.py&', ensuring the shell sessions are running concurrently

If the client requests experience timeout, then the problem scenario
has manifested itself. If none of the concurrent client requests are
able to interfere (and cause other requests to time out), then the
problem scenario is absent.

Implementations
---------------

| File                               | Language      | Problem? | Tool |
| ----                               | --------      | -------- | ---------- |
| SimulatedDiskIOServer.cs           | C#            | N        | Mono C# compiler version 4.2.1.0 |
| SimulatedDiskIOServer.d            | D             | N        | DMD64 D Compiler v2.069.2-devel |
| SimulatedDiskIOServer.java         | Java (JVM)    | N        | openjdk version 1.8.0 |
| SimulatedDiskIOServer.nim          | Nim           | N        | Nim 0.14.2 |
| SimulatedDiskIOServer.scala        | Scala (JVM)   | N        | Scala compiler version 2.11.8 |
| jython-simulated-disk-io-server.py | Python (JVM)  | N        | Jython 2.7.0 |
| simulated-disk-io-server.c         | C             | N        | gcc 4.8.5 |
| simulated-disk-io-server.go        | Go            | N        | go version go1.2.1 linux/amd64 |
| curio-simdisk-io-server.py         | Python 3.5    | N        | CPython 3.5 and curio |
| simulated-disk-io-server.py        | Python 2.7    | **Y**    | CPython 2.7 and eventlet |
| threaded-simulated-disk-io-server.py        | Python 2.7    | N    | CPython 2.7 and eventlet; corrected to use threaded disk I/O |
| simulated-disk-io-server.rs        | Rust          | N        | Rust 1.9 |

