#!/usr/bin/env python3
"""
Robot Telemetry Receiver
========================
Receives UDP telemetry from ESP32-S3 and displays live data.

Usage:
    python3 telemetry_receiver.py           # console output
    python3 telemetry_receiver.py --plot    # live matplotlib plot
    python3 telemetry_receiver.py --log     # log to CSV
"""

import socket
import struct
import time
import argparse
from collections import deque
from datetime import datetime

# Must match firmware struct
TELEMETRY_FORMAT = '<IffffffBBI'  # 34 bytes
TELEMETRY_SIZE = struct.calcsize(TELEMETRY_FORMAT)

STATE_NAMES = {
    0: "BOOT", 1: "TEST", 2: "LEGS", 3: "SPINUP",
    4: "BALANCING", 5: "JUGGLING", 6: "FALL", 7: "ESTOP"
}

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--port', type=int, default=5000)
    parser.add_argument('--plot', action='store_true')
    parser.add_argument('--log', action='store_true')
    args = parser.parse_args()
    
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind(('0.0.0.0', args.port))
    sock.setblocking(False)
    
    log_file = None
    if args.log:
        path = f"telemetry_{datetime.now():%Y%m%d_%H%M%S}.csv"
        log_file = open(path, 'w')
        log_file.write("t_ms,theta_deg,theta_dot_dps,phi_rev,phi_dot_rps,torque,juggle_torque,vbat,state,flags\n")
        print(f"Logging to: {path}")
    
    print(f"Listening on UDP port {args.port}...")
    
    if args.plot:
        try:
            import matplotlib
            matplotlib.use('TkAgg')
            import matplotlib.pyplot as plt
            from matplotlib.animation import FuncAnimation
        except ImportError:
            print("matplotlib required: pip install matplotlib")
            return
        
        fig, axes = plt.subplots(3, 1, figsize=(12, 8), sharex=True)
        fig.suptitle("Robot Telemetry", fontsize=14)
        
        max_pts = 500
        t_d = deque(maxlen=max_pts)
        th_d = deque(maxlen=max_pts)
        td_d = deque(maxlen=max_pts)
        u_d = deque(maxlen=max_pts)
        
        lines = [ax.plot([], [], linewidth=1)[0] for ax in axes]
        for ax, lbl in zip(axes, ['θ [°]', 'θ̇ [°/s]', 'τ [N·m]']):
            ax.set_ylabel(lbl); ax.grid(True, alpha=0.3)
        axes[-1].set_xlabel('Time [s]')
        state_text = fig.text(0.02, 0.95, '', fontsize=11, fontweight='bold')
        t0 = time.time()
        
        def update(frame):
            while True:
                try:
                    data, _ = sock.recvfrom(1024)
                    if len(data) < TELEMETRY_SIZE: continue
                    p = struct.unpack(TELEMETRY_FORMAT, data[:TELEMETRY_SIZE])
                    t_d.append(p[0]/1000.0 - t0)
                    th_d.append(p[1]); td_d.append(p[2]); u_d.append(p[5])
                    if log_file:
                        log_file.write(f"{p[0]},{p[1]:.3f},{p[2]:.2f},{p[3]:.4f},{p[4]:.2f},{p[5]:.3f},{p[6]:.3f},{p[7]:.2f},{p[8]},{p[9]}\n")
                except BlockingIOError: break
            
            if t_d:
                t = list(t_d)
                for line, d in zip(lines, [th_d, td_d, u_d]):
                    line.set_data(t, list(d))
                for ax in axes: ax.relim(); ax.autoscale_view(scalex=True, scaley=False)
                axes[0].set_ylim([-15, 15]); axes[2].set_ylim([-20, 20])
                state_text.set_text(f"State: {STATE_NAMES.get(p[8], '?')}")
            return lines
        
        anim = FuncAnimation(fig, update, interval=20, blit=False)
        plt.tight_layout()
        plt.show()
    else:
        # Console mode
        print(f"{'Time':>8} {'θ[°]':>8} {'θ̇[°/s]':>9} {'τ[N·m]':>8} {'Vbat[V]':>8} {'State':>10}")
        print("-" * 55)
        try:
            while True:
                try:
                    data, _ = sock.recvfrom(1024)
                    if len(data) < TELEMETRY_SIZE: continue
                    p = struct.unpack(TELEMETRY_FORMAT, data[:TELEMETRY_SIZE])
                    state = STATE_NAMES.get(p[8], f"UNK({p[8]})")
                    print(f"\r{p[0]/1000:8.2f} {p[1]:8.2f} {p[2]:9.1f} {p[5]:8.2f} {p[7]:8.2f} {state:>10}", end='', flush=True)
                    if log_file:
                        log_file.write(f"{p[0]},{p[1]:.3f},{p[2]:.2f},{p[3]:.4f},{p[4]:.2f},{p[5]:.3f},{p[6]:.3f},{p[7]:.2f},{p[8]},{p[9]}\n")
                except BlockingIOError:
                    time.sleep(0.001)
        except KeyboardInterrupt:
            print("\nStopped.")
    
    sock.close()
    if log_file: log_file.close()

if __name__ == "__main__":
    main()
