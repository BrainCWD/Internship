# Copyright (c) 2016 Momenta, Inc.
# An Implemention of natural cubic spline
# Similar to http://algorithmist.net/docs/spline.pdf
# We spline according to the chord instead of x

import numpy as np

def spline_interp_step(lane, step=1):
    # in case of string value
    float_lane = [{'x': float(p['x']), 'y': float(p['y'])} for p in lane]
    if len(float_lane) < 2:
        print("Less than two points in lane")
        return float_lane

    spline_param = get_spline_param(float_lane)
    spline_lane = []
    for param in spline_param:
        t = 0
        while t<param['h']:
            spline_lane.append(sample_pt(param, t))
            t += step
    # to ensure the lane finish at the last point
    spline_lane.append(float_lane[-1])
    return spline_lane

def get_spline_param(lane):
    all_params = []
    n = len(lane)
    if n < 2:
        return all_params
    if n == 2:
        # straight lane becomes linear function
        h0 = ((lane[0]['x'] - lane[-1]['x'])**2 + (lane[0]['y'] - lane[-1]['y'])**2)**0.5
        a_x = lane[0]['x']
        a_y = lane[0]['y']
        b_x = (lane[1]['x'] - a_x)/h0
        b_y = (lane[1]['y'] - a_y)/h0
        curr_param = {"a_x":a_x, "b_x":b_x, "c_x":0, "d_x":0, "a_y":a_y, "b_y":b_y, "c_y":0, "d_y":0, "h":h0}
        all_params.append(curr_param)
        return all_params
    ###########################################################
    # Step1: construct Equation [6]
    # h_{i-1}*z_{i-1} + u_i*z_i + h_i*z_{i+1} = v_i
    # H0[i] = h_{i}, H1[i] = h[i+1]

    h = []
    for i in range(n - 1):
        h.append(((lane[i+1]['x'] - lane[i]['x'])**2 + (lane[i+1]['y'] - lane[i]['y'])**2)**0.5)

    H0 = []
    U = []
    H1 = []
    Vx = []
    Vy = []
    for i in range(n - 2):
        H0.append(h[i])
        U.append(2*(h[i] + h[i+1]))
        H1.append(h[i+1])
        bx0 = (lane[i+1]['x'] - lane[i]['x']) / h[i]
        bx1 = (lane[i+2]['x'] - lane[i+1]['x']) / h[i+1]
        Vx.append(6*(bx1-bx0))
        by0 = (lane[i + 1]['y'] - lane[i]['y']) / h[i]
        by1 = (lane[i + 2]['y'] - lane[i + 1]['y']) / h[i + 1]
        Vy.append(6 * (by1 - by0))

    ###########################################################
    # Step2: solve Equation [7] by row ops
    H1[0] /= U[0]
    Vx[0] /= U[0]
    Vy[0] /= U[0]

    for i in range(1, n-2):
        elimin_base = U[i] - H0[i]*H1[i-1]
        H1[i] /= elimin_base
        Vx[i] = (Vx[i] - H0[i]*Vx[i-1]) / elimin_base
        Vy[i] = (Vy[i] - H0[i]*Vy[i-1]) / elimin_base

    ###########################################################
    # Step3: solve z
    Zx = np.zeros(n)
    Zy = np.zeros(n)
    Zx[-2] = Vx[n-3]
    Zy[-2] = Vy[n-3]
    for i in range(n - 4, -1, -1):
        Zx[i+1] = Vx[i] - H1[i] * Zx[i+2]
        Zy[i+1] = Vy[i] - H1[i] * Zy[i+2]

    # natural
    Zx[0] = 0
    Zx[-1] = 0
    Zy[0] = 0
    Zy[-1] = 0

    ############################################################
    # Step4: final set equations
    # d should be divided by h (https://zh.wikipedia.org/wiki/%E6%A0%B7%E6%9D%A1%E6%8F%92%E5%80%BC), if not, the C0 constraint cannot match
    for i in range(n-1):
        curr_param = {}
        curr_param['a_x'] = lane[i]['x']
        curr_param['b_x'] = (lane[i+1]['x'] - lane[i]['x']) / h[i] -  h[i]*Zx[i+1]/6 - h[i]*Zx[i]/3
        curr_param['c_x'] = Zx[i] / 2
        curr_param['d_x'] = (Zx[i+1] - Zx[i])/(6*h[i])
        curr_param['a_y'] = lane[i]['y']
        curr_param['b_y'] = (lane[i+1]['y'] - lane[i]['y']) / h[i] -  h[i]*Zy[i+1]/6 - h[i]*Zy[i]/3
        curr_param['c_y'] = Zy[i] / 2
        curr_param['d_y'] = (Zy[i+1] - Zy[i])/(6*h[i])
        curr_param['h'] = h[i]
        all_params.append(curr_param)

    return all_params

def sample_pt(param, t):
    return {"x":get_x_val(param, t), "y":get_y_val(param, t)}

def get_x_val(param, t):
    return param['a_x'] + param['b_x']*t + param['c_x']*t*t + param['d_x']*t*t*t

def get_y_val(param, t):
    return param['a_y'] + param['b_y']*t + param['c_y']*t*t + param['d_y']*t*t*t
