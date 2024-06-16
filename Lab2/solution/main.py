from icmplib import ping, ICMPRequest
from icmplib.exceptions import *
from time import sleep
import argparse

HEADER_SIZE = 28

def find_min_mtu(target, min_mtu, max_mtu, interval):
    valid = True
    while min_mtu <= max_mtu:
        mtu_size = (min_mtu + max_mtu) // 2

        try:
            response = ping(target, interval=interval, count=1, payload_size=mtu_size - HEADER_SIZE)
            if response.is_alive:
                min_mtu = mtu_size + 1
            else:
                max_mtu = mtu_size - 1
        except (SocketPermissionError, NameLookupError, ICMPSocketError, SocketAddressError, Exception) as e:
            print(f"FAIL LOG -- A problem occurred: {str(e)}")
            valid = False
            break

    return max_mtu if valid else None # Здесь max_mtu меньше чем min_mtu

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Find the minimum MTU to a target host using icmplib.')
    parser.add_argument('host', help='The target host.')
    parser.add_argument('--min-mtu', type=int, default=68, help='Minimum MTU size to test. Default is 68.')
    parser.add_argument('--max-mtu', type=int, default=1500, help='Maximum MTU size to test. Default is 1500.')
    parser.add_argument('--interval', type=float, default=0.5, help='The interval in seconds between each ICMP request. Default is 0.5 second.')
    args = parser.parse_args()

    target, min_mtu, max_mtu, interval = args.host, args.min_mtu, args.max_mtu, args.interval

    try:
        health_check = ping(target)
        if not health_check.is_alive:
            print('FAIL LOG -- Cannot ping host')
            exit(1)
    except (SocketPermissionError, NameLookupError, SocketAddressError, ICMPSocketError, Exception) as e:
            print(f"FAIL LOG -- A problem occurred: {str(e)}")
            exit(1)

    try:
        mtu = find_min_mtu(target, min_mtu, max_mtu, interval)
        if mtu is not None:
            print(f'Found MTU: {mtu}')
        else:
            print("FAIL LOG -- Unable to determine the minimum MTU due to an error.")
            exit(1)
    except Exception as e:
        print(f'FAIL LOG -- An unexpected error occurred: {e}')
        exit(1)
