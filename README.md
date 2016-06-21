## python-concurrent-disk-io

Start up an eventlet-based server that simulates disk io:

    python simulated-disk-io-server.py
   
Then, fire up several terminals and in each one run:

    ./make_requests.sh
    
(that's a candidate for rewriting in Python-3/curio)
 
The server will print out `timeout (service)` when the eventlet problem is encountered.
