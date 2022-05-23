import datetime
import os
import re
import sys
import struct
import time
import select
import socket
import binascii

ICMP_ECHO_REQUEST = 8
rtt_min = float('+inf')
rtt_max = float('-inf')
rtt_sum = 0
rtt_cnt = 0


def checksum(string):
    csum = 0
    countTo = (len(string) / 2) * 2

    count = 0
    while count < countTo:
        thisVal = string[count + 1] * 256 + string[count]
        csum = csum + thisVal
        csum = csum & 0xffffffff
        count = count + 2

    if countTo < len(string):
        csum = csum + ord(string[len(str) - 1])
        csum = csum & 0xffffffff

    csum = (csum >> 16) + (csum & 0xffff)
    csum = csum + (csum >> 16)
    answer = ~csum
    answer = answer & 0xffff
    answer = answer >> 8 | (answer << 8 & 0xff00)
    return answer


def receiveOnePing(mySocket, ID, timeout, destAddr):
    global rtt_min, rtt_max, rtt_sum, rtt_cnt
    timeLeft = timeout
    while 1:
        startedSelect = time.time()
        whatReady = select.select([mySocket], [], [], timeLeft)
        howLongInSelect = (time.time() - startedSelect)
        if whatReady[0] == []:  # Timeout
            return "Request timed out."

        timeReceived = time.time()
        recPacket, addr = mySocket.recvfrom(1024)

        # TODO
        # Fetching below
        # b is signed char (1 byte), H is unsigned short (2 bytes),h is short (2 bytes)
        struct_str = "bbHHh"
        # first 20 is the ip header and then the following 8 bits is icmp header
        icmpType, _, _, packet, _ = struct.unpack(struct_str, recPacket[20:28])
        # if the type is 0 then it means is a reply, and if its a 8 then its a echo request
        icmp_reply = 0
        if icmpType == icmp_reply:
            # Matching the echo reply to the request with ID and type
            if packet == ID:
                bytes = struct.calcsize("d")
                timetounpack = recPacket[28:28 + bytes]
                ts = struct.unpack("d", timetounpack)[0]

                # time in ms so we times it by 1000
                result = 1000 * (timeReceived - ts)
                # Need packet length for formatting
                packetlength = len(recPacket)

                # Gathering sum and count for the average
                rtt_sum = rtt_sum + result
                rtt_cnt += 1

                # if statements for updating the max and min values
                if result > rtt_max:
                    rtt_max = result
                if result < rtt_min:
                    rtt_min = result

                result_in_string = (
                    str(packetlength) + " bytes from " + destAddr + "; time=") + str(result) + "ms"
                return result_in_string

        # TODO END

        timeLeft = timeLeft - howLongInSelect
        if timeLeft <= 0:
            return "Request timed out."


def sendOnePing(mySocket, destAddr, ID):
    # Header is type (8), code (8), checksum (16), id (16), sequence (16)

    myChecksum = 0
    # Make a dummy header with a 0 checksum.
    # struct -- Interpret strings as packed binary data
    header = struct.pack("bbHHh", ICMP_ECHO_REQUEST, 0, myChecksum, ID, 1)
    data = struct.pack("d", time.time())    # 8 bytes
    # Calculate the checksum on the data and the dummy header.
    myChecksum = checksum(header + data)

    # Get the right checksum, and put in the header
    if sys.platform == 'darwin':
        myChecksum = socket.htons(myChecksum) & 0xffff
        # Convert 16-bit integers from host to network byte order.
    else:
        myChecksum = socket.htons(myChecksum)

    header = struct.pack("bbHHh", ICMP_ECHO_REQUEST, 0, myChecksum, ID, 1)
    packet = header + data

    # AF_INET address must be tuple, not str
    mySocket.sendto(packet, (destAddr, 1))
    # Both LISTS and TUPLES consist of a number of objects
    # which can be referenced by their position number within the object


def doOnePing(destAddr, timeout):
    icmp = socket.getprotobyname("icmp")
    # SOCK_RAW is a powerful socket type. For more details see: http://sock-raw.org/papers/sock_raw

    # TODO
    # Create Socket here
    # Created socket using SOCK_RAW
    mySocket = socket.socket(socket.AF_INET, socket.SOCK_RAW, icmp)
    # TODO END

    myID = os.getpid() & 0xFFFF  # Return the current process i
    sendOnePing(mySocket, destAddr, myID)
    delay = receiveOnePing(mySocket, myID, timeout, destAddr)

    mySocket.close()
    return delay


def ping(host, timeout=1):
    global rtt_min, rtt_max, rtt_sum, rtt_cnt
    cnt = 0
    # timeout=1 means: If one second goes by without a reply from the server,
    # the client assumes that either the client's ping or the server's pong is lost
    dest = socket.gethostbyname(host)
    print("Pinging " + dest + " using Python:")
    # Send ping requests to a server separated by approximately one second
    try:
        while True:
            cnt += 1
            print(doOnePing(dest, timeout))
            time.sleep(1)
    except KeyboardInterrupt:
        # TODO
        # Calculating the Avergae value.
        rtt_average = rtt_sum / rtt_cnt

        # printing statistics.
        print("--- " + dest + " ping statistics ---")
        print("round-trip min/avg/max " + str(rtt_min) + '/' +
              str(rtt_average) + '/' + str(rtt_max) + " ms")

        # TODO END


if __name__ == '__main__':
    # Should be sys.argv[1] but have ips for testing
    ping("199.7.83.42")
    # ping(sys.argv[1])
