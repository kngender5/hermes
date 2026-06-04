#!/usr/bin/env python3
"""
Self-Balancing Robot — Dynamic Simulation Template
====================================================
Nonlinear inverted pendulum on a wheel + LQR controller.
Adapt parameters for your specific robot.

Usage:
    python3 simulation_template.py                    # basic balance test
    python3 simulation_template.py --disturb          # with push disturbance
    python3 simulation_template.py --animate          # generate animation
    python3 simulation_template.py --sweep             # LQR parameter sweep
    python3 simulation_template.py --export           # export gains as JSON
"""

import numpy as np
from scipy.integrate import solve_ivp
from scipy import linalg
import argparse
import json
import os

# ─────────────────────────────────────────────
# PHYSICAL PARAMETERS — EDIT FOR YOUR ROBOT
# ─────────────────────────────────────────────
PARAMS = {
    # Body
    "M_b": 8.0,          # body mass [kg]
    "l": 0.25,           # CG height above axle [m]
    "I_b": 0.5,          # body moment of inertia about CG [kg·m²]
    
    # Wheel
    "M_w": 2.0,          # wheel mass [kg]
    "r": 0.203,          # wheel radius [m]
    "I_w": 0.04,         # wheel moment of inertia [kg·m²]
    
    # Motor
    "tau_max": 15.0,     # max motor torque [N·m]
    "g": 9.81,
    "b_w": 0.05,         # wheel viscous friction
    "b_b": 0.02,         # body pivot damping
    
    # Disturbance
    "disturbance_enable": False,
    "disturbance_time": 2.0,
    "disturbance_torque": 3.0,
    
    # Sensor noise
    "imu_noise_std": 0.001,
    "gyro_noise_std": 0.005,
    "encoder_noise_std": 0.001,
    
    # Control
    "control_rate": 200,
    "dt": 0.005,
}


def mass_matrix(p):
    M_b, M_w, l, r, I_b, I_w = p["M_b"], p["M_w"], p["l"], p["r"], p["I_b"], p["I_w"]
    return np.array([
        [M_b * l**2 + I_b,       M_b * l * r],
        [M_b * l * r,            M_b * r**2 + M_w * r**2 + I_w]
    ])


def dynamics_nonlinear(t, x, p, tau_ctrl, tau_dist):
    theta, theta_dot, phi, phi_dot = x
    M_b, l, r, g, b_w, b_b = p["M_b"], p["l"], p["r"], p["g"], p["b_w"], p["b_b"]
    M = mass_matrix(p)
    C = np.array([M_b * g * l * np.sin(theta) - b_b * theta_dot, -b_w * phi_dot])
    tau_total = np.array([tau_ctrl + tau_dist, -tau_ctrl])
    acc = np.linalg.solve(M, tau_total + C)
    return [theta_dot, acc[0], phi_dot, acc[1]]


def disturbance_torque(t, p):
    if not p["disturbance_enable"]:
        return 0.0
    t_d = p["disturbance_time"]
    if abs(t - t_d) < 0.025:
        return p["disturbance_torque"] / 0.05
    return 0.0


def linearize(p):
    M_b, M_w, l, r, I_b, I_w, g = (
        p["M_b"], p["M_w"], p["l"], p["r"], p["I_b"], p["I_w"], p["g"]
    )
    M = mass_matrix(p)
    M_inv = np.linalg.inv(M)
    A = np.zeros((4, 4))
    A[0, 1] = 1.0
    A[2, 3] = 1.0
    A[1, 0] = M_inv[0, 0] * M_b * g * l
    A[1, 1] = -M_inv[0, 0] * p["b_b"]
    A[3, 0] = M_inv[1, 0] * M_b * g * l
    A[3, 1] = -M_inv[1, 0] * p["b_b"]
    B = np.zeros((4, 1))
    B[1, 0] = M_inv[0, 0] - M_inv[0, 1]
    B[3, 0] = M_inv[1, 0] - M_inv[1, 1]
    return A, B


def design_lqr(p, Q=None, R=None):
    A, B = linearize(p)
    if Q is None:
        Q = np.diag([1000.0, 100.0, 10.0, 10.0])
    if R is None:
        R = np.array([[0.1]])
    P = linalg.solve_continuous_are(A, B, Q, R)
    K = np.linalg.solve(R, B.T @ P)
    return K


def check_controllability(A, B):
    """Build controllability matrix manually (scipy.linalg.ctrb was removed)."""
    n = A.shape[0]
    C = B
    for k in range(1, n):
        C = np.hstack([C, np.linalg.matrix_power(A, k) @ B])
    return np.linalg.matrix_rank(C)


def simulate(p, duration=10.0, x0=None, noisy=True):
    if x0 is None:
        x0 = np.deg2rad([5.0, 0.0, 0.0, 0.0])
    dt = p["dt"]
    N = int(duration / dt)
    t = np.zeros(N)
    x = np.zeros((N, 4))
    u = np.zeros(N)
    tau_dist_arr = np.zeros(N)
    
    K = design_lqr(p)
    theta_hat = 0.0
    gyro_bias = 0.0
    alpha = 0.98
    prev_enc = 0.0
    first_enc = True
    
    x[0] = x0
    
    for i in range(N - 1):
        t[i+1] = t[i] + dt
        theta, theta_dot, phi, phi_dot = x[i]
        
        # Sensor noise
        if noisy:
            theta_m = theta + np.random.normal(0, p["imu_noise_std"])
            gyro_m = theta_dot + np.random.normal(0, p["gyro_noise_std"])
            enc_m = phi + np.random.normal(0, p["encoder_noise_std"])
        else:
            theta_m = theta
            gyro_m = theta_dot
            enc_m = phi
        
        # Complementary filter
        accel_theta = np.arctan2(np.sin(theta_m), 1.0)
        theta_hat = alpha * (theta_hat + (gyro_m - gyro_bias) * dt) + (1 - alpha) * accel_theta
        if abs(theta_hat) < 0.1:
            gyro_bias += 0.001 * (accel_theta - theta_hat)
        
        # Wheel velocity
        if first_enc:
            enc_vel = 0.0
            prev_enc = enc_m
            first_enc = False
        else:
            delta = enc_m - prev_enc
            if delta > np.pi: delta -= 2 * np.pi
            if delta < -np.pi: delta += 2 * np.pi
            enc_vel = delta / dt
            prev_enc = enc_m
        
        x_est = np.array([theta_hat, gyro_m - gyro_bias, enc_m, enc_vel])
        
        # Control
        tau_d = disturbance_torque(t[i], p)
        tau_ctrl = np.clip(-(K @ x_est)[0], -p["tau_max"], p["tau_max"])
        
        u[i] = tau_ctrl
        tau_dist_arr[i] = tau_d
        
        # Integrate
        sol = solve_ivp(
            lambda tv, xv: dynamics_nonlinear(tv, xv, p, tau_ctrl, tau_d),
            [t[i], t[i+1]], x[i], method='RK45', max_step=dt/2
        )
        x[i+1] = sol.y[:, -1]
        
        if abs(x[i+1, 0]) > np.deg2rad(30):
            t = t[:i+2]; x = x[:i+2]; u = u[:i+2]; tau_dist_arr = tau_dist_arr[:i+2]
            break
    
    return t, x, u, tau_dist_arr


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--disturb', action='store_true')
    parser.add_argument('--duration', type=float, default=10.0)
    parser.add_argument('--tilt', type=float, default=5.0)
    parser.add_argument('--export', action='store_true')
    args = parser.parse_args()
    
    p = PARAMS.copy()
    p["disturbance_enable"] = args.disturb
    
    A, B = linearize(p)
    rank = check_controllability(A, B)
    eigs = np.linalg.eigvals(A)
    print(f"Unstable poles: {eigs[np.real(eigs) > 0]}")
    print(f"Controllability rank: {rank}/4 {'OK' if rank == 4 else 'FAIL'}")
    
    K = design_lqr(p)
    print(f"LQR gains: {K}")
    
    x0 = np.deg2rad([args.tilt, 0.0, 0.0, 0.0])
    t, x, u, tau_d = simulate(p, duration=args.duration, x0=x0)
    
    theta_deg = np.rad2deg(x[:, 0])
    print(f"Final tilt: {theta_deg[-1]:.3f} deg")
    print(f"Max |tilt|: {np.max(np.abs(theta_deg)):.3f} deg")
    print(f"Max |torque|: {np.max(np.abs(u)):.2f} Nm")
    
    if args.export:
        config = {
            "lqr_gain": K.tolist(),
            "params": {k: v for k, v in p.items() if isinstance(v, (int, float, bool))},
            "A_matrix": A.tolist(),
            "B_matrix": B.tolist(),
        }
        os.makedirs("output", exist_ok=True)
        with open("output/controller_config.json", "w") as f:
            json.dump(config, f, indent=2)
        print("Exported: output/controller_config.json")


if __name__ == "__main__":
    main()
