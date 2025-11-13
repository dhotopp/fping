#!/usr/bin/env python3
#
# Script to summarize Windows ping output and beeps a frequency that increase as RTT decreases. 
# It also can play major chord notes if no loss or minor if any packets were lost
# Github link: https://github.com/dhotopp/fping.  Initial fping options based on those from 
# Fast pinger version 3.00 (c) Wouter Dhondt
#
# Script:       fping.py
# Author:       Dan Hotopp
# Date:			2025-11-13
#
# E.g python fping.py x.com --rtt_target 150 --rtt_divisor 100 -r -m 6500 -t3000 -n4 -b -c

import subprocess
import argparse, re
import time,sys
import winsound
import random
from datetime import datetime
import numpy as np

# Define the A4 note frequency
A4_FREQ = 440.0
NOTE_NAMES = ['A', 'A#', 'B', 'C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#']

# Function to calculate the frequency of a note
def calculate_frequency(note_index, octave):
    return A4_FREQ * (2 ** (note_index / 12 + (octave - 4)))

# Function to calculate the deviation in cents
def cents_deviation(actual_freq, target_freq):
    if actual_freq <= 0:
        return None
    return 1200 * np.log2(actual_freq / target_freq)

# Function to find the closest note with octave
def closest_note_frequency(frequency):
    closest_note = None
    closest_freq = None
    min_deviation = float('inf')
    octave_of_closest_note = None

    for octave in range(1, 8):  # Assuming 7 octaves
        for note_index in range(len(NOTE_NAMES)):
            note_freq = calculate_frequency(note_index, octave)
            deviation = abs(frequency - note_freq)

            if deviation < min_deviation:
                min_deviation = deviation
                closest_note = NOTE_NAMES[note_index]
                closest_freq = note_freq
                octave_of_closest_note = octave

    return closest_note, closest_freq, octave_of_closest_note

def note_to_frequency(note: str, octave: int) -> float:
    # Reference frequency for A4
    A4_FREQ = 440.0
    # Mapping for semitone offsets
    note_offsets = {
        'A': 0, 'A#': 1, 'B': 2, 'C': 3, 'C#': 4, 'D': 5, 'D#': 6,
        'E': 7, 'F': 8, 'F#': 9, 'G': 10, 'G#': 11,
    }

    # Validate input
    if note not in note_offsets:
        raise ValueError("Invalid note. Use: C, C#, D, D#, E, F, F#, G, G#, A, A#, B")
    
    # Calculate the semitone offset
    n = note_offsets[note]
    
    # Calculate frequency using the conversion equation
    frequency = A4_FREQ * (2 ** ((n + 12 * (octave - 4)) / 12))
    
    return frequency

def get_major_chord(root_freq):
    """Returns the notes of the major chord for a given root note."""
    return [
        root_freq,
	    root_freq * 2 ** (1/3),  # Major third (4 semitones above)
        root_freq * 2 ** (7/12),  # Perfect fifth (7 semitones above)
        root_freq * 2, # Octave up
        root_freq * 2 ** (7/12),  # Perfect fifth (7 semitones above)
        root_freq * 2 ** (1/3),  # Major third (4 semitones above)
        root_freq
    ]

def get_minor_chord(root_freq):
    """Returns the notes of the major chord for a given root note."""
    return [
        root_freq,
	    root_freq * 2 ** (1/4),  # Minor third (3 semitones above)
        root_freq * 2 ** (7/12),  # Perfect fifth (7 semitones above)
        root_freq * 2, # Octave up
        root_freq * 2 ** (7/12),  # Perfect fifth (7 semitones above)
	    root_freq * 2 ** (1/4),  # Minor third (3 semitones above)
        root_freq
    ]

def play_notes(freqs):
    """Plays the given notes for a specified octave."""
    for freq in freqs:
        note1, freq1, oct = closest_note_frequency(freq)        
        #print(f"{note1}{oct} {freq1:.1f}Hz", end=' - ', file=sys.stdout, flush=True)  # Show frequency being played
        print(f"{note1}{oct} ({freq1:.1f}Hz)", end=' - ', file=sys.stderr, flush=True)  # Show frequency being played
        #print('', file=sys.stderr)
        #print('', file=sys.stderr)
        #sys.stdout.flush()  # Flush the output buffer
        winsound.Beep(int(freq), 400)  # Play each note for 400 ms

# Function to play the closest note and display details
def play_note_and_compare(frequency,lost):
    closest_note, closest_freq, octave = closest_note_frequency(frequency)
    deviation = cents_deviation(frequency, closest_freq)
    print(f"Freq: {frequency:.1f}Hz Closest Note: {closest_note}{octave} ({closest_freq:.1f}Hz), {deviation:.1f}cents", file=sys.stderr)

    if lost: 
        chord = get_minor_chord(closest_freq/2) #Start at lower note freq
    else:
        chord = get_major_chord(closest_freq/2) #Start at lower note freq
    winsound.Beep(int(frequency), 250)  # Play for a bit
    winsound.Beep(int(closest_freq), 500)  # Play for a bit
    note1, freq1, oct = closest_note_frequency(closest_freq)
    if options['c'] and not lost: print(f"Playing notes with {note1}{oct-1} ({closest_freq/2:.1f}Hz) to {note1}{oct} ({closest_freq:.1f}Hz) Major Chord:", file=sys.stderr,flush=True) # Show frequency being played
    if options['c'] and lost: print(f"Playing notes with {note1}{oct-1} ({closest_freq/2:.1f}Hz) to {note1}{oct} ({closest_freq:.1f}Hz) Minor Chord:", file=sys.stderr,flush=True) # Show frequency being played
#       if options['c']: winsound.Beep(int(closest_freq), 500)  # Play closest freq again
        #time.sleep(0.01)  # Short pause between notes
#       if options['c']: play_notes(chord)
        #play_notes(chord)
        #chord = get_major_chord(closest_freq/2) #Start at lower note freq
    if options['c']: play_notes(chord)
    #chord = get_minor_chord(closest_freq/2) #Start at lower note freq
    #if options['c']: play_notes(chord)
    #print(f"\nPlayed notes in {note1}{oct-1} ({closest_freq/2:.1f}Hz) to {note1}{oct} ({closest_freq:.1f}Hz) Major  Chord.", file=sys.stderr,flush=True)  # Show frequency being played
    if options['c']: print(f"{note1}{oct} ({closest_freq:.1f}Hz).", file=sys.stderr,flush=True)  # Show frequency being played
    if options['c']: winsound.Beep(int(closest_freq), 500)  # Play closest freq again

def beep(success,latency,lost):
# Get Min and Max Frequencies
    note_with_octave = options['l']
    #print(f"Lowest Note: {note_with_octave}")
    for i in range(len(note_with_octave)):
        if note_with_octave[i].isdigit():
            note = note_with_octave[:i]
            octave = int(note_with_octave[i:])
            break
    else:
        raise ValueError("Invalid note input. Please enter a valid note and octave.")
    F_min = note_to_frequency(note,octave)
    F_max = F_min * 8 # min up 8 octaves

    if success:
        freq = F_max - (F_max - F_min) * (latency-options['rtt_target'])/options['rtt_divisor']
        #freq = F_max - (F_max - F_min) * latency/100
        if freq <= 220: freq = 220
        play_note_and_compare(freq,lost)
    else:
        winsound.Beep(220, 200)    # Beep on timeout


def summarize_ping_output(ping_output):
    # Regular expressions to extract data
    #print(f"ping_output: {ping_output}")
    #Pinging 11.1.1.1 with 32 bytes of data
    #Pinging x.com [172.66.0.227] with 42617 bytes of data:
    bytes_info_pattern =  re.compile(r'Pinging\s*(\S*\s*\[?\d+\.\d+\.\d+\.\d+\]?)\s*with (\d+) bytes of data')
    #bytes_info_pattern =  re.compile(r'Pinging\s*(\d+\.\d+\.\d+\.\d+) with (\d+) bytes of data')
    # Extracting bytes_info_pattern data
    bytes_info_match = bytes_info_pattern.search(ping_output)
    host = None
    bytes_send = None
    lost = 0
    if bytes_info_match:
        host = bytes_info_match.group(1)
        bytes_send = bytes_info_match.group(2)
        #print(f"Sending {bytes_send} bytes to {host}")	

    packet_info_pattern = re.compile(r'Packets:\s*Sent\s*=\s*(\d+),\s*Received\s*=\s*(\d+),\s*Lost\s*=\s*(\d+)\s*\((\d+)%\s*loss')

    rtt_info_pattern = re.compile(r'Minimum\s*=\s*(\d+)ms,\s*Maximum\s*=\s*(\d+)ms,\s*Average\s*=\s*(\d+)ms')
    # Extracting packet data
    packet_info_match = packet_info_pattern.search(ping_output)
    if packet_info_match:
        sent = int(packet_info_match.group(1))
        received = int(packet_info_match.group(2))
        lost = int(packet_info_match.group(3))
        loss_percentage = int(packet_info_match.group(4))
        #print(f"Pkt: S={sent}, R={received}, L={lost} ({loss_percentage}% loss)")
    else:
        return "Packet information not found"

    # Extracting RTT data
    rtt_info_match = rtt_info_pattern.search(ping_output)
    if rtt_info_match:
        min_rtt = int(rtt_info_match.group(1))
        max_rtt = int(rtt_info_match.group(2))
        ave_rtt = int(rtt_info_match.group(3))
    else:
        beep(False,None,0)
        return f"No packet results when sending {bytes_send} bytes to {host}", None

    # Create summary using abbreviations
    if rtt_info_match: summary = f"Pkts: S={sent}, R={received}, L={lost} ({loss_percentage}% loss), MinRTT={min_rtt}ms, MaxRTT={max_rtt}ms, AveRTT={ave_rtt}ms"
    if not rtt_info_match: summary = ''
    return [summary, ave_rtt, lost]

def total_bytes_from_ping(ping_output):
    # Regular expression to capture bytes from the Reply lines
    bytes_pattern = re.compile(r'Reply from (\d+\.\d+\.\d+\.\d+): bytes=(\d+)')
    
    # Initialize total bytes
    total_bytes = 0
    from_bytes = None

    # Find all matches and sum the bytes
    for match in bytes_pattern.finditer(ping_output):
        #print(f"match: {match}")
        from_bytes = match.group(1)
        total_bytes += int(match.group(2))
        
    return total_bytes, from_bytes

def ping(host, options):
    command = ["ping", host]
    
    if options['n'] is not None:
        command += ["-n", str(options['n'])]
        
    if options['w'] is not None:
        command += ["-w", str(options['w'])]
        
    if options['f']:
        command.append("-f")
        
    if options['i'] is not None:
        command += ["-i", str(options['i'])]
        
#    if options['b']: continue #Ignore this for ping command
#        command += ["-b"]

    # Handle size options
    if options['random_size']:
        data_size = random.randint(1, options['max_size'] + 1)
        command += ["-l", str(data_size)]
        packet_size = data_size
    elif options['s'] is not None:
        command += ["-l", str(options['s'])]
        packet_size = options['s']
    else:
        packet_size = 32  # Default packet size if not specified

    try:
        #print (f"CMD: {' '.join(command)}")
        reply = subprocess.run(command, capture_output=True, text=True)
        date_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        success = "Reply from" in reply.stdout
        #print(f"reply: {reply.stdout}")
        status = "Success" if success else "Timeout"
        #print(f"summarize_ping_output: {summarize_ping_output(reply.stdout)}")
        #print(f"isinst: {isinstance(summarize_ping_output(reply.stdout), list)}")
        # Summarized output
        if isinstance(summarize_ping_output(reply.stdout), list) and len(summarize_ping_output(reply.stdout)) == 3:
            summ, ave_rtt, lost = summarize_ping_output(reply.stdout)
        else:
            # If not a valid response, summ = ping output
            summ = reply.stdout
            #print(f"Error from ping output: {reply.stdout}")
        bytes, bytesfrom = total_bytes_from_ping(reply.stdout)
        #response_line = f"[{date_time}] Bytes: {total_bytes_from_ping(reply.stdout)} {summ}"
#        if success:
        if bytes: response_line = f"[{date_time}] {bytes} bytes from {bytesfrom} {summ}"
        if not bytes: response_line = f"[{date_time}] {summ}"
        print(response_line)
        sys.stdout.flush()  # Flush the output buffer
        #print(avg_rtt)

        if success:
            #if not options['b'] == '-': beep(True,ave_rtt)
            if options['b'] : beep(True,ave_rtt,lost)
            #if not options['b']: beep(True,1)
            return True
        else:
            beep(False,None,0)
            return False
    except Exception as e:
        print(f"Error: {e}")
        return False

def main():
    parser = argparse.ArgumentParser(description="Ping a host with custom options.")
    parser.add_argument('-b', default=False, action='store_true', help="Beep when reachable.  Default is when unreachable only.")
    parser.add_argument('-c', action='store_true', help="Play chord from nearest key.")
    parser.add_argument('-f', action='store_true', help="Set Don't Fragment flag in packet.")
    parser.add_argument('-i', type=int, help="TTL value.")
    parser.add_argument('-n', type=int, default=1, help="Number of echo requests to send.")
    parser.add_argument('-l', '--lowest_note', type=str.upper, default='A#3', help="Lowest beep note (default: A#3")
    parser.add_argument('--rtt_divisor', default=100, type=int, help="Divisor for latancy RTT when calculating freq")
    parser.add_argument('--rtt_target', default=0, type=int, help="Target RTT")
    parser.add_argument('-s', type=int, help="Amount of data in bytes (up to 65500).  Note, 8.8.8.8 max is 1392, x.com is ~19000 ")
    parser.add_argument('-t', type=int, default=1000, help="Time between pings in ms (default is 1000 ms).")
    parser.add_argument('-w', type=int, default=1000, help="Timeout in ms to wait for each reply.")
    parser.add_argument('-r', '--random-size', action='store_true', help="Use random size for each packet.")
    parser.add_argument('-m', '--max-size', type=int, default=1392, help="Maximum size for random packets (max possible is 65500).")
    parser.add_argument('host', help="Host to ping.")
    global options
    args = parser.parse_args()
#    print(f"l: {args.l}")   
    options = {
        't': args.t,
        'n': args.n,
        'w': args.w,
        'c': args.c,
        's': args.s,
        'f': args.f,
        'i': args.i,
        'b': args.b,
        'l': args.lowest_note,
        'random_size': args.random_size,
        'max_size': args.max_size,
        'rtt_divisor': args.rtt_divisor,
        'rtt_target': args.rtt_target,
    }
    #    'l': args.l,
    #print (f"options: {options}")
    #cli_args = {k:v for k, v in vars(args).items() if v}
    #print(f"cli_args: {cli_args}")
    try:
        while True:
            ping(args.host, options)
            time.sleep(options['t'] / 1000)  # Simulating some work with a delay
    except KeyboardInterrupt:
        #print("\nLoop interrupted. Exiting gracefully.")
        print("")

if __name__ == "__main__":
    main()
