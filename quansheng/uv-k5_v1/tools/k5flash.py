#!/usr/bin/env python3
# Minimal UV-K5 bootloader flasher (protocol ported from qrp73/K5TOOL, V2 bootloader).
# Usage: k5flash.py <port> <raw_firmware.bin> <version16>
import serial
import struct
import sys
import time

XOR = bytes([0x16, 0x6C, 0x14, 0xE6, 0x2E, 0x91, 0x0D, 0x40,
             0x21, 0x35, 0xD5, 0x40, 0x13, 0x03, 0xE9, 0x80])

def xor_(data):
    return bytes(c ^ XOR[i % 16] for i, c in enumerate(data))

def crc16_xmodem(data):
    crc = 0
    for byte in data:
        crc ^= byte << 8
        for _ in range(8):
            crc = ((crc << 1) ^ 0x1021) & 0xFFFF if crc & 0x8000 else (crc << 1) & 0xFFFF
    return crc

def send(ser, payload):
    crc = crc16_xmodem(payload)
    body = xor_(payload + struct.pack('<H', crc))
    ser.write(b'\xAB\xCD' + struct.pack('<H', len(payload)) + body + b'\xDC\xBA')
    ser.flush()

def recv(ser, timeout=6.0):
    """Return decoded payload of next well-framed packet, or None on timeout."""
    deadline = time.time() + timeout
    while time.time() < deadline:
        b = ser.read(1)
        if b != b'\xAB':
            continue
        if ser.read(1) != b'\xCD':
            continue
        hdr = ser.read(2)
        if len(hdr) != 2:
            continue
        size = struct.unpack('<H', hdr)[0]
        if size > 2048:
            continue
        rest = ser.read(size + 4)  # payload + crc + DC BA
        if len(rest) != size + 4 or rest[-2:] != b'\xDC\xBA':
            continue
        return xor_(rest[:size + 2])[:size]
    return None

def main():
    port, fwfile, version = sys.argv[1], sys.argv[2], sys.argv[3]
    fw = open(fwfile, 'rb').read()
    chunk_count = (len(fw) + 255) // 256
    assert chunk_count * 256 <= 0xF000, "firmware too large"

    ser = serial.Serial(port, 38400, timeout=0.3)
    print(f"port open: {port}, firmware {len(fw)} bytes, {chunk_count} chunks")

    # 1. wait for bootloader beacon (0x0518)
    print("waiting for bootloader beacon...")
    while True:
        p = recv(ser, timeout=15)
        if p is None:
            print("ERROR: no beacon - is the radio in flash mode?")
            return 1
        pid = p[0] | (p[1] << 8)
        if pid == 0x0518:
            text = bytes(c for c in p[4:] if 32 <= c < 127).decode(errors='replace')
            print(f"beacon: {text}")
            break

    # 2. send version handshake (0x0530), expect beacon back
    vbuf = version.encode()[:16]
    vbuf += b'\x00' * (16 - len(vbuf))
    send(ser, b'\x30\x05\x10\x00' + vbuf)
    p = recv(ser)
    if p is None or (p[0] | (p[1] << 8)) != 0x0518:
        print(f"ERROR: unexpected version reply: {p.hex() if p else None}")
        return 1
    print(f"version '{version}' accepted")

    # 3. write chunks (0x0519 -> ack 0x051A)
    seq = 0x1D9F8D8A
    for n in range(chunk_count):
        data = fw[n * 256:(n + 1) * 256]
        dlen = len(data)
        data = data + b'\xFF' * (256 - dlen)
        payload = (b'\x19\x05\x0C\x01' + struct.pack('<I', seq) +
                   struct.pack('<HHHH', n, chunk_count, dlen, 0) + data)
        send(ser, payload)

        ack = None
        for _ in range(12):  # skip interleaved beacons
            p = recv(ser)
            if p is None:
                break
            pid = p[0] | (p[1] << 8)
            if pid == 0x0518:
                continue
            ack = p
            break
        if ack is None:
            print(f"\nERROR: no ack for chunk {n}")
            return 1
        pid = ack[0] | (ack[1] << 8)
        if pid != 0x051A or ack[10] != 0:
            print(f"\nERROR: chunk {n} failed: {ack.hex()}")
            return 1
        got_chunk = ack[8] | (ack[9] << 8)
        if got_chunk != n:
            print(f"\nERROR: chunk mismatch {got_chunk} != {n}")
            return 1
        done = (n + 1) * 100 // chunk_count
        print(f"\r  {n + 1}/{chunk_count} ({done}%)", end='', flush=True)

    print("\nFLASH OK - radio should reboot with the new firmware")
    return 0

if __name__ == '__main__':
    sys.exit(main())
