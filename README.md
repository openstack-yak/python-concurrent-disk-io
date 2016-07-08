## python-concurrent-disk-io

For python tests, make a virtualenv with the appropriate python
(python2 for all but the curio tests;  python3.5+ for the curio test).
Use the appropriate requirements file.

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

Intent
------
The **intent** of this project is 
to take an objective look at the
problem and fully understand the nature of the problem.
A solution may or may not come naturally as part of this process.

Baseline
--------
The baseline (reference) for this project is the **eventlet-based
CPython** implementation (eventlet-simulated-disk-io-server.py).

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


Notes
-----

Asynchronous solutions involve cooperative multitasking.
When external libraries or devices block, it blocks whatever multitasking kernel or mechanism
is coordinating the multitasking.

The most straigthforward solution is to simply use threading.
In fact, in the jython version here, the example was converted to
a threading model since Python 2.7 has no async/await, and the eventlets
code used in the CPython code is compiled code (e.g. not available
in python 2.7 as native python bytecode).

The motivation to move to something more lightweight than threads is
performance.  Some languages take care of blocking I/O situations for
you in the background.  In Python 3.5, this is in the control of the programmer.
Simple async kernel library `curio` takes care of blocking for you at
the library level by providing wrappers to otherwise non-async libraries,
but other libraries or external calls must be explicitly handled by the
programmer.

The problem encountered (and the nature of the solution) is shown in this code.
Some discussion should be added about strategies for debugging, and
benchmarking performance, including CPU and RAM usage.

A common and often quoted misnomer is that "it's the Python Global Interpreter
Lock (GIL) at fault" - which is just that: a misnomer.
We show the issue is one of asynchronous programming.

Some guidelines for performant, reliable asynchronous programming
will be suggested.

