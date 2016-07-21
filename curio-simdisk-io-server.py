# python - simulate occasional problematic (long blocking) requests within curio
# python version: 3.5
# curio version: 0.4

from curio import run, spawn, run_in_thread
from curio.socket import *
import string
import time


READ_TIMEOUT_SECS = 4

STATUS_OK = 0
STATUS_QUEUE_TIMEOUT = 1
STATUS_BAD_INPUT = 2

#  Since disk I/O will not in general be async, do not use curio.sleep;
#   do not async this simulation;  rather run it in a thread;
def simulated_file_read(elapsed_time_ms):
    # do not use curio.sleep(elapsed_time_ms / 1000.0)  # seconds
    time.sleep(elapsed_time_ms / 1000.0)  # seconds


async def client_request(client, receipt_timestamp):
    s = client.as_stream()
    request_text = await s.readline()
    if request_text:
        start_processing_timestamp = time.time()
        queue_time_ms = start_processing_timestamp - receipt_timestamp
        queue_time_secs = queue_time_ms / 1000

        rc = STATUS_OK
        disk_read_time_ms = 0
        file_path = ''

        # has this request already timed out?
        if queue_time_secs >= READ_TIMEOUT_SECS:
            rc = STATUS_QUEUE_TIMEOUT
        else:
            fields = request_text.split(b',')
            if len(fields) == 3:
                rc = int(fields[0])
                disk_read_time_ms = int(fields[1])
                file_path = fields[2]
                # real disk I/O will be blocking; run in a thread:
                await run_in_thread(simulated_file_read, disk_read_time_ms)
            else:
                rc = STATUS_BAD_INPUT

        # total request time is sum of time spent in queue and the
        # simulated disk read time
        tot_request_time_ms = queue_time_ms + disk_read_time_ms

        # construct response and send back to client
        read_resp_text = b"%d,%d,%s" % \
            (rc, tot_request_time_ms, file_path)
        await s.write(read_resp_text)


async def main(server_port):
    sock = socket(AF_INET, SOCK_STREAM)
    sock.bind(('', server_port))
    sock.listen(100)
    print("server listening on port %d" % server_port)

    # TODO: move this interrupt handling into client
    try:
        while True:
            client, addr = await sock.accept()
            await spawn(client_request(client, time.time()))
    except KeyboardInterrupt:
        pass  # exit


if __name__=='__main__':
    server_port = 7000
    run(main(server_port), with_monitor=True)

