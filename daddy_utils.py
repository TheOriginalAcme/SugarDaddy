import time
import random
from socket import socket
import signal
import re
import threading


class DaddyUtils(object):
    def __init__(self):
        self.is_specific_event_on = False
        self.channel = self._open_channel()
        channel_parser = threading.Thread(target=self._read_channel_and_parse)
        channel_parser.start()
        self.threads = [channel_parser]
        self.should_record_channel = False
    
    def stop(self):
        print("Stopping reading channel")
        self.should_read_channel = False
        self.should_record_channel = False
        for thread in self.threads:
            thread.join()
        self._close_channel()

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

    # def _get_events(self):
    #     print("Getting events... (Press Ctrl+C to stop)")
    #     regex = "EVENT> (\d)"
    #     while self.should_read_channel:
    #         data = self._read_channel() <- in real life it would be self._read_events()
    #         # TODO: 2 threads reading the same socket like this means data will be missed
    #         matches = re.findall(regex, data)
    #         if matches:
    #             for event_id in matches:
    #                 print(f"Event {event_id} occurred")
    #         time.sleep(0.1)

    # def _detect_stuff(self):
    #     print("Detecting stuff... (Press Ctrl+C to stop)")
    #     regex = "STUFF> (\d)"
    #     self.should_read_channel = True
    #     while self.should_read_channel:
    #         data = self._read_channel()
    #         # TODO: 2 threads reading the same socket like this means data will be missed
    #         matches = re.findall(regex, data)
    #         if matches:
    #             for stuff_num in matches:
    #                 print(f"Stuff {stuff_num} occurred")
    #         time.sleep(0.1)
    
    def _read_channel_and_parse(self):
        print("Getting events & detecting stuff... (Press Ctrl+C to stop)")
        regex = r"STUFF> (?P<stuff>\d)|EVENT> (?P<event>\d)"
        self.should_read_channel = True
        while self.should_read_channel:
            data = self._read_channel()
            matches = re.findall(regex, data)
            if matches:
                for match in matches:
                    if match[0]:  # TODO: and should_print_stuff
                        print(f"Stuff {match[0]} occurred")
                    if match[1]:  # TODO: and should_print_events
                        print(f"Event {match[1]} occurred")
            if self.should_record_channel:
                self.recording_file.write(data) 
            time.sleep(0.1)

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
