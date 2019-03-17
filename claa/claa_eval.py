# -*- coding:utf-8 -*-
from utils.common import *
from utils.dora import *
import spline as sp
import lane_spline_area as lsa
from utils.data_plot import *
import json

if __name__ == '__main__':
    offline_annotation = True  # 离线标注数据
    normalize = False  # 拉框/标点数据归一化处理
    offline_annotation_path = '/home/huhaoyu/Downloads/3d标点离线标注/annotation'  # 标注结果存放文件夹
    # offline_annotation_path = '/home/huhaoyu/Downloads/离线标注/annotation'
    # offline_annotation_path = '/home/huhaoyu/Downloads/车道画线_FLV_V10/车道画线_FLV_V10'

    # 选择评测类型
    task_dict = {
        1: 'box',
        2: 'point',
        3: 'line'
    }
    task = task_dict[2]

    # todo 标注结果可视化
    if offline_annotation:
        old_cam_ann, new_cam_ann, ann_num = convert_annotation_offline(offline_annotation_path)  # 离线数据格式转换
        output_dict = eval_offline(task, old_cam_ann, new_cam_ann, ann_num, normalize)  # 评测
        data_plot(output_dict, task)  # 可视化
    else:
        # 预留的线上数据接口
        test_img = get_test_image(task)  # 获取数据列表
        # output_list = eval(task, test_img)  # 获取评估结果
        # output_list = eval_offline(task, old_cam_ann, new_cam_ann, ann_num)
        # data_plot(output_list)  # 可视化
