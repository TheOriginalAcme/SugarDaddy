from socket import socket
import random
import time
import select


def send_gibrish(channel: socket):
    data = "abcdefghijklmnopqrstuvwxyz"
    data += "1234567890"
    data += "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    channel.send(bytes(f"DATA> {data}", "utf-8"))

def send_event(channel: socket):
    event_id = random.randint(1, 4)
    channel.send(bytes(f"EVENT> {event_id}", "utf-8"))

def send_stuff(channel: socket):
    stuff_id = random.randint(0, 9)
    channel.send(bytes(f"STUFF> {stuff_id}", "utf-8"))

def randomly_send_something(channel: socket):
    rand = random.random()
    if rand > 0.5:
        send_gibrish(channel)
    if rand < 0.2:
        send_event(channel)
    if rand > 0.8:
        send_stuff(channel)

def send_raw_audio(channel: socket):
    with open("binary_ulaw.raw", "rb") as raw_audio_file:
        raw_audio_bytes = raw_audio_file.read()
    channel.send(raw_audio_bytes)

def main():
    server = socket()
    server.bind(("", 12345))
    server.listen(5)
    inputs = [server]
    outputs = []
    while inputs:
        readable, writable, exceptional = select.select(inputs, outputs, inputs)
        for ch in readable:
            if ch is server:
                channel, addr_pair = server.accept()
                print(f"{addr_pair[0]} connected from port {addr_pair[1]}")
                inputs.append(channel)
                if channel not in outputs:
                    outputs.append(channel)
            else:
                data = ch.recv(1024)
                if data:
                    data = data.decode("utf-8")
                    print(f"Received {data}")
                else:
                    if ch in outputs:
                        outputs.remove(ch)
                    inputs.remove(ch)
                    ch.close()

        for ch in writable:
            randomly_send_something(ch)
            # for testing:
            # time.sleep(5)
            # send_raw_audio(ch)

        for ch in exceptional:
            inputs.remove(ch)
            if ch in outputs:
                outputs.remove(ch)
            ch.close()
        
        time.sleep(0.5)


if __name__ == "__main__":
    main()
