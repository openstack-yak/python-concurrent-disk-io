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
The client utility used for testing is 'make-http-requests.sh'. It's
just a shell script that runs Apache Bench (ab).

The Test
--------
1. Start the server implementation
2. Run 'make-http-requests.sh' on same machine

If the client requests experience timeout, then the problem scenario
has manifested itself. If none of the concurrent client requests are
able to interfere (and cause other requests to time out), then the
problem scenario is absent.

Implementations
---------------

| File                    | Language      | Problem? | Tool |
| ----                    | --------      | -------- | ---------- |
| HttpThreadsServer.cs    | C#            | N        | Mono C# compiler version 4.2.1.0 |
| HttpThreadsServer.d     | D             | N        | DMD64 D Compiler v2.069.2-devel |
| HttpThreadsServer.java  | Java (JVM)    | N        | openjdk version 1.8.0 |
| HttpThreadsServer.nim   | Nim           | N        | Nim 0.14.2 |
| HttpThreadsServer.pas   | Pascal        | N        | fpc 3.0 |
| HttpThreadsServer.scala | Scala (JVM)   | N        | Scala compiler version 2.11.8 |
| http-threads-server.py  | Python (JVM)  | N        | Jython 2.7.0 |
| http-threads-server.py  | Python        | N        | CPython 2.7.6 |
| http-threads-server.c   | C             | N        | gcc 4.8.5 |
| http-server.go          | Go            | N        | go version go1.2.1 linux/amd64 |
| http-eventlet-server.py | Python        | **Y**    | CPython 2.7 and eventlet |
| http-threads-server.rs  | Rust          | N        | Rust 1.9 |

Some guidelines for performant, reliable asynchronous programming
will be suggested.

