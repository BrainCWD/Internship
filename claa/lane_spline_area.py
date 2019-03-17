# -*- coding:utf-8 -*-
import numpy as np
from matplotlib import pyplot as plt
from utils.dora import *
import spline as sp
from utils.dora import *


def cal_avg_area(task, test_img):
    dora = get_dora_db()

    avg_area = []
    for image in test_img:
        num, lanes = get_annotation_lines(dora, task, image)
        # 该图的所有线的的平均间距
        area = get_area(lanes, step=1, thres=50, del_thres=20)
        for line in area:
            number = 0
            for num in line:
                number += num
            avg_area.append(number / len(line))

    # print(1)
    return avg_area


def cal_avg_area_offline(task, old_cam_ann, new_cam_ann, ann_num, normalize):
    old_new = [[], []]  # 老相机结果，新相机结果
    output_dict = dict()
    for cam, cam_ann in enumerate([old_cam_ann, new_cam_ann]):
        mean_std_list = [[], []]  # line_dis, ego_dis
        for img in cam_ann:
            img_dis_list = [[], []]
            num, lanes = get_annotation_lines_offline(task, cam_ann[img], ann_num)  # 数据处理
            # 该图的所有线的的平均间距
            area = get_area(lanes, step=1, thres=50, del_thres=20)
            for line in area:
                number = 0
                for num in line:
                    number += num
                mean_std_list[0].append(number / len(line))
                img_dis_list[0].append(number / len(line))
            keyword = 'old' if 'old' in img else 'new'
            if img.split(keyword)[0] not in output_dict:
                output_dict[img.split(keyword)[0]] = [[], [], [], []]  # old_line, old_ego, new_line, new_ego
            if keyword == 'old':
                output_dict[img.split(keyword)[0]][0].extend(img_dis_list[0])
            if keyword == 'new':
                output_dict[img.split(keyword)[0]][2].extend(img_dis_list[0])
        print('finish one camera')
        old_new[cam].extend(mean_std_list)
    return output_dict


def get_area(lanes, step, thres, del_thres=20, del_Y_V=False):
    # 第一步，样条函数拟合。第二步，筛选不同标注员标注的同一条线。第三步，算面积。

    # 1 样条函数拟合
    spline_lane = []
    for r in lanes:
        for l in r:
            # 按照y值从大到小排序
            if l[0]['y'] < l[-1]['y']:
                l = l[-1::-1]
            spline_lane.append(sp.spline_interp_step(l, step))

    # 2 筛选同一条线
    spline_lane_object = []
    while len(spline_lane) != 0:
        li = spline_lane[0]
        temp = [li]
        for l in spline_lane:
            if abs(l[0]['x'] - li[0]['x']) <= thres and abs(l[0]['y'] - li[0]['y']) <= thres and abs(
                    l[-1]['x'] - li[-1]['x']) <= thres and abs(l[-1]['x'] - li[-1]['x']) <= thres and l != li:
                # 判断是否是一条线
                temp.append(l)
        for l in temp:
            spline_lane.remove(l)
        if len(temp) > 1:
            spline_lane_object.append(temp)

    # 3 算面积
    return cal_area(spline_lane_object)


def cal_area(spline_lane):
    area = []
    for l in spline_lane:
        area_l = []
        for i in range(len(l) - 1):
            for j in range(i + 1, len(l)):
                area_l.append((cal_dis(l[i], l[j]) + cal_dis(l[j], l[i])) / 2)
        area.append(area_l)
    return area


def cal_dis(l1, l2):
    dis = 0
    if abs(l1[0]['y'] - l1[-1]['y']) >= abs(l1[0]['x'] - l1[-1]['x']):
        m = 0
        n = 0
        p = 0
        while m < len(l1) and l1[m]['y'] > l2[n]['y']:
            m += 1
        while n < len(l2) and l2[n]['y'] > l1[m]['y']:
            n += 1
        if l1[0]['y'] >= l2[0]['y']:
            dis += abs((l1[m]['x'] - l2[n]['x']) * (m - 1)) / 2
            p += m - 1
        else:
            dis += abs((l1[m]['x'] - l2[n]['x']) * (n - 1)) / 2
            p += n - 1

        while m < len(l1) and n < len(l2):
            dis += abs(l1[m]['x'] - l2[n]['x'])
            m += 1
            n += 1
            p += 1
        if m < len(l1):
            dis += abs((l1[m - 1]['x'] - l2[-1]['x']) * (len(l1) - m - 1)) / 2
            p += len(l1) - m - 1
        if n < len(l2):
            dis += abs((l1[-1]['x'] - l2[n - 1]['x']) * (len(l2) - n - 1)) / 2
            p += len(l2) - n - 1
        return dis / p
    else:
        m = 0
        n = 0
        p = 0
        if l1[0]['x'] < l1[-1]['x']:
            l1 = l1[-1::-1]
            l2 = l2[-1::-1]
        while m < len(l1) and l1[m]['x'] > l2[n]['x']:
            m += 1
        while n < len(l2) and l2[n]['x'] > l1[m]['x']:
            n += 1
        if l1[0]['x'] >= l2[0]['x']:
            dis += abs((l1[m]['y'] - l2[n]['y']) * (m - 1)) / 2
            p += m - 1
        else:
            dis += abs((l1[m]['y'] - l2[n]['y']) * (n - 1)) / 2
            p += n - 1

        while m < len(l1) and n < len(l2):
            dis += abs(l1[m]['y'] - l2[n]['y'])
            m += 1
            n += 1
            p += 1
        if m < len(l1):
            dis += abs((l1[m - 1]['y'] - l2[-1]['y']) * (len(l1) - m - 1)) / 2
            p += len(l1) - m - 1
        if n < len(l2):
            dis += abs((l1[-1]['y'] - l2[n - 1]['y']) * (len(l2) - n - 1)) / 2
            p += len(l2) - n - 1
        return dis / p

# def cal_avg_area(area):
