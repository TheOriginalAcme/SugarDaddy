import time
import random
from socket import socket
import signal
import re
import threading
from queue import Queue


class DaddyUtils(object):
    def __init__(self):
        self.channel = self._open_channel()
        self.should_record_channel = False
        self.output("off")
        self.data_queue = Queue()
        self.events_queue = Queue()
        channel_parser = threading.Thread(target=self._read_channel_and_parse)  # only because mock
        event_getter = threading.Thread(target=self._get_events)
        stuff_detector = threading.Thread(target=self._detect_stuff)
        self.threads = [channel_parser, event_getter, stuff_detector]
        for thread in self.threads:
            thread.start()
    
    def _open_channel(self):
        channel = socket()
        channel.connect(("127.0.0.1", 12345))
        return channel

    def _close_channel(self):
        self.channel.close()

    def _stop_recording_channel(self, sig, frame):
        print("Stopping recording channel")
        self.should_record_channel = False
        self.recording_file.close()
    
    def _read_channel(self):
        data = self.channel.recv(1024).decode("utf-8")
        print(data)
        return data

    def record_channel(self, output_file_path):
        print(f"Recording channel into {output_file_path}... (Press Ctrl+C to stop)")
        self.recording_file = open(output_file_path, "w")
        self.should_record_channel = True
        signal.signal(signal.SIGINT, self._stop_recording_channel)
        while self.should_record_channel:
            # we are doing this in order to block the main thread (Press Ctrl+C to stop though)
            pass

    def _read_channel_and_parse(self):
        print("Reading the channel... (run stop() to stop)")
        regex = r"EVENT> (\d)"
        self.should_read_channel = True
        while self.should_read_channel:
            data = self._read_channel()
            matches = re.findall(regex, data)
            if matches:
                for event_id in matches:
                    self.events_queue.put(event_id)
            data = re.sub(regex, "", data)  # removes all regex occurrences
            self.data_queue.put(data)
            time.sleep(0.1)

    def _get_events(self):
        print("Getting events...")
        while self.should_read_channel:
            event_id = self.events_queue.get()  # Blocks until an item is available
            if self.should_print_events:
                print(f"Event {event_id} occurred")

    def _detect_stuff(self):
        print("Detecting stuff...")
        regex = "STUFF> (\d)"
        while self.should_read_channel:
            data = self.data_queue.get()  # Blocks until an item is available
            stuff_numbers = re.findall(regex, data)
            for stuff_num in stuff_numbers:
                if self.should_print_stuff:
                    print(f"Stuff {stuff_num} occurred")
            if self.should_record_channel:
                self.recording_file.write(data) 
    
    def output(self, what_to_print="both"):
        if what_to_print == "events":
            self.should_print_events = True
        if what_to_print == "stuff":
            self.should_print_stuff = True
        if what_to_print == "both":
            self.should_print_events = True
            self.should_print_stuff = True
        if what_to_print == "off":
            self.should_print_events = False
            self.should_print_stuff = False

    def stop(self):
        print("Stopping reading channel")
        self.should_read_channel = False
        self.should_record_channel = False
        for thread in self.threads:
            thread.join()
        self._close_channel()

    def write_to_channel(self, file_path):
        with open(file_path, "rb") as input_file:
            input_data = input_file.read()
        print(f"Writing to channel data from {file_path}")
        self.channel.send(input_data)

    def _send_specific_event(self):
        while self.is_specific_event_on:
            print(".", end="")
            self.channel.send(b"SPECIFIC_EVENT")
            time.sleep(1)

    def start_specific_event(self):
        print("Starting specific event. It will continue until stop_specific_event")
        self.is_specific_event_on = True
        specific_sender = threading.Thread(target=self._send_specific_event)
        # self.channel.send(b"SPECIFIC_EVENT started") <- for real
        specific_sender.start()

    def stop_specific_event(self):
        print("Stopping specific event")
        # self.channel.send(b"SPECIFIC_EVENT stopped") <- for real
        self.is_specific_event_on = False


if __name__ == "__main__":
    daddy = DaddyUtils()
