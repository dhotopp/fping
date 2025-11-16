usage: fping.py [-h] [-b] [-c] [-f] [-i I] [-n N] [-l c] [--rtt_divisor RTT_DIVISOR] [--rtt_target RTT_TARGET] [-s S]
                [-t T] [-w W] [-r] [-m MAX_SIZE]
                host

Ping a host frequently. Beep with a higher pitch for speedy replys.

positional arguments:
  host                  Host to ping.

options:
  -h, --help            show this help message and exit
  -b                    Beep when reachable. Default is when unreachable only.
  -c                    Play chord from nearest key.
  -f                    Set Don't Fragment flag in packet.
  -i I                  TTL value.
  -n N                  Number of echo requests to send.
  -l LOW_Root_NOTE, --LOW_Root_NOTE LOW_Root_NOTE
                        Lowest beep note (default: A#3
  --rtt_divisor RTT_DIVISOR
                        Divisor for latancy RTT when calculating freq
  --rtt_target RTT_TARGET
                        Target RTT
  -s S                  Amount of data in bytes (up to 65500). Note, 8.8.8.8 max is 1392, x.com is ~19000
  -t T                  Time between pings in ms (default is 1000 ms).
  -w W                  Timeout in ms to wait for each reply.
  -r, --random-size     Use random size for each packet.
  -m MAX_SIZE, --max-size MAX_SIZE
                        Maximum size for random packets (max possible is 65500).
