# python - simulate occasional problematic (long blocking) requests within eventlet
# language version: 2.7

from curio import run, spawn
from curio.socket import *
import string
import time


READ_TIMEOUT_SECS = 4

STATUS_OK = 0
STATUS_QUEUE_TIMEOUT = 1
STATUS_BAD_INPUT = 2


def simulated_file_read(elapsed_time_ms):
    time.sleep(elapsed_time_ms / 1000.0)  # seconds


async def client_request(client, addr, receipt_timestamp):
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
            print("timeout (queue)")
            rc = STATUS_QUEUE_TIMEOUT
        else:
            fields = request_text.split(b',')
            if len(fields) == 3:
                rc = int(fields[0])
                disk_read_time_ms = int(fields[1])
                file_path = fields[2]
                simulated_file_read(disk_read_time_ms)
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
            receipt_timestamp = time.time()
            await spawn(client_request(client, addr, receipt_timestamp))
    except KeyboardInterrupt:
        pass  # exit


if __name__=='__main__':
    server_port = 7000
    run(main(server_port))

