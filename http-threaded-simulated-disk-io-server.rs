// rust - simulate occasional problematic (long blocking) requests for disk IO
// language version: 1.9.0
// to build: rustc http-threaded-simulated-disk-io-server.rs
// NOTE: this is my first Rust program, so much of it is probably crappy

use std::io::Read;
use std::io::Write;
use std::net::Shutdown;
use std::net::{TcpListener, TcpStream};
use std::str;
use std::thread;
use std::time::Duration;

const READ_TIMEOUT_SECS: u32 = 4;
const LISTEN_BACKLOG: u32 = 500;

const SERVER_NAME = "http-threaded-simulated-disk-io-server.rs";
const HTTP_STATUS_OK: =  "200 OK";
const HTTP_STATUS_TIMEOUT: = "408 TIMEOUT";
const HTTP_STATUS_BAD_REQUEST: = "400 BAD REQUEST";

fn current_time_millis() -> u64 {
    //TODO: time::now()
    return 0;
}

fn simulated_file_read(disk_read_time_ms: u64) {
    thread::sleep(Duration::from_millis(disk_read_time_ms));
}

fn handle_socket_request(stream: &mut TcpStream,
                         receipt_timestamp: u64) {
    // read request from client
    let mut request_buffer = [0; 1024];
    let mut rc = HTTP_STATUS_OK;
    let mut file_path = "";
    let mut tot_request_time_ms: u64 = 0;

    if stream.read(&mut request_buffer).unwrap() > 0 {
        let request_text = str::from_utf8(&request_buffer).unwrap();
        // did we get anything from client?
        if request_text.trim().len() > 0 {
            // determine how long the request has waited in queue
            let start_processing_timestamp = current_time_millis();
            let server_queue_time_ms =
                start_processing_timestamp - receipt_timestamp;
            let x = server_queue_time_ms / 1000;
            let server_queue_time_secs = x as u32;

            let mut disk_read_time_ms: u64 = 0;

            // has this request already timed out?
            if server_queue_time_secs >= READ_TIMEOUT_SECS {
                println!("timeout (queue)");
                rc = HTTP_STATUS_TIMEOUT;
            } else {
                let line_tokens: Vec<&str> = request_text.split(' ').collect();
                if line_tokens.len() > 1 {
                    let request_method = line_tokens[0];
                    let args_text = line_tokens[1];
                    let fields: Vec<&str> = args_text.split(',').collect();
                    if fields.len() == 3 {
                        let parse_rc_result = fields[0].parse();
                        match parse_rc_result {
                            Err(_) => {},
                            Ok(rc_input) => {
                                let parse_time_result = fields[1].parse();
                                match parse_time_result {
                                    Err(_) => {},
                                    Ok(req_response_time_ms) => {
                                        //rc = rc_input;
                                        disk_read_time_ms = req_response_time_ms;
                                        file_path = fields[2];
                                        simulated_file_read(disk_read_time_ms);
                                    }
                                }
                            }
                        }
                    } else {
                        // we didn't get the 3 input fields as expected
                        rc = HTTP_STATUS_BAD_REQUEST;
                    }
                } else {
                    // we didn't get the HTTP request line as expected
                    rc = HTTP_STATUS_BAD_REQUEST;
                }
            }
        } else {
            // we didn't get any input
            rc = HTTP_STATUS_BAD_REQUEST;
        }

        // total request time is sum of time spent in queue and the
        // simulated disk read time
        tot_request_time_ms =
            queue_time_ms + disk_read_time_ms;
    } else {
        // read of request failed
        rc = HTTP_STATUS_BAD_REQUEST;
        tot_request_time_ms = 0;
        file_path = "";
    }

    // create response
    let response_body = format!("{0},{1}",
        tot_request_time_ms,
        file_path);

    let response_headers = format!("",
                                   rc,
                                   SERVER_NAME,
                                   response_body.length);

    // return response to client
    stream.write_all(response_headers.as_bytes()).unwrap();
    stream.write_all(response_body.as_bytes()).unwrap();

    let _ = stream.shutdown(Shutdown::Both);
}

fn main() {
    let server_port = 7000;
    //TODO: build string using server_port
    let listener = TcpListener::bind("127.0.0.1:7000").unwrap();
    println!("server listening on port {0}", server_port);

    for stream in listener.incoming() {
        match stream {
            Err(_) => {},
            Ok(mut stream) => {
                let receipt_timestamp = current_time_millis();
                thread::spawn(move|| {
                    handle_socket_request(&mut stream, receipt_timestamp);
                });
            }
        }
    }
}

