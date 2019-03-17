# -*- coding:utf-8 -*-
import numpy as np
from utils.dora import *
import lane_spline_area as lsa
import warnings
import os, json


def area_bbox(box):
    """

    :param box: list [x1, y1, x2, y2]
    :return: area of box
    """
    return (box[2] - box[0]) * (box[3] - box[1])


def cal_iou(box1, box2):
    """

    :param box1: list [x1, y1, x2, y2]
    :param box2: list [x1, y1, x2, y2]
    :return: iou
    """
    bi = [np.max((box1[0], box2[0])), np.max((box1[1], box2[1])), np.min((box1[2], box2[2])),
          np.min((box1[3], box2[3]))]
    iw = bi[2] - bi[0]
    ih = bi[3] - bi[1]
    if iw > 0 and ih > 0:
        ai = iw * ih
        return ai / (area_bbox(box1) + area_bbox(box2) - ai)

    return 0.0


def cal_box_std(object_list, normalize):
    """

    :param object_list: 一个对象的所有框
    :param normalize: 归一化
    :return: 标准差 list [std_x1, std_y1, std_x2, std_y2]
    """
    warnings.filterwarnings("ignore")
    object_array = np.array(object_list)
    std = np.std(object_array, axis=0, ddof=1)
    if not normalize:
        return std.tolist(), -1
    elif normalize:
        mean_box = np.mean(np.array(object_list), axis=0)
        height = mean_box[3] - mean_box[1]
        return [i * 50 / height for i in std.tolist()], height


def cal_point_std(object_list, normalize, mean_height):
    # todo 解决warning
    warnings.filterwarnings("ignore")
    convert_list = list()
    for i in object_list:
        point_list = list()
        keep = True
        if len(i) > 0:
            try:
                point_list.append(i[0][1])
            except:
                keep = False
            for j in i[1:]:
                try:
                    point_list.extend(j[:2])
                except:
                    keep = False
            if keep:
                convert_list.append(point_list)
    object_array = np.array(convert_list)
    std = np.std(object_array, axis=0, ddof=1)
    if not normalize:
        return std.tolist()
    elif normalize:
        try:
            return [i * 50 / mean_height for i in std.tolist()]
        except:
            return std.tolist()


def choose_object_box(convert_total_box, type_dict, thres=0.7):
    object_list = list()
    for box in convert_total_box:
        iou = cal_iou(convert_total_box[0][0], box[0])
        if iou >= thres:
            object_list.append(box)  # 选择是同一个物体的标注框
    keep_object = True
    for box in object_list:  # 如果有一个框是脑补框就不评估
        if box[0] in type_dict['guess']:
            keep_object = False
            break
    return object_list, keep_object


def box_annotation(num, convert_total_box, type_dict, normalize):
    all_object, box_std, point_std = list(), list(), list()
    miss_box_list, error_box_list = list(), list()  # 漏标、错标
    while len(convert_total_box) > 0:
        object_list, keep_object = choose_object_box(convert_total_box, type_dict)  # 选择是同一个物体的标注框
        if keep_object:  # 只处理正常框的object
            if len(object_list) > 1:
                box_ann = [i[0] for i in object_list]
                point_ann = [i[1] for i in object_list]
                b_std, mean_height = cal_box_std(box_ann, normalize)
                box_std.append(b_std)  # 计算box标准差
                p_std = cal_point_std(point_ann, normalize, mean_height)
                point_std.append(p_std if not p_std == np.nan else [])  # 计算point标准差
                miss_box_list.append(True) if len(object_list) != num else miss_box_list.append(False)  # 处理漏框
                error_box_list.append(False)
            else:
                miss_box_list.append(False)
                error_box_list.append(True)  # 处理错框
            all_object.append(object_list)
        convert_total_box = [item for item in convert_total_box if item not in object_list]
    object_num = len(box_std)  # 图片中物体数
    # print(object_num)
    return box_std, point_std, object_num, all_object, miss_box_list, error_box_list


def cal_all_std(task, test_img):
    dora = get_dora_db()
    mean_std_list = []
    for img in test_img:
        num, total, type_dict = get_annotation(dora, task, img)  # num是图片标注的次数， total为标注结果
        if len(total) > 0:
            mean_box_std, mean_point_std, object_num, all_object, miss, error = box_annotation(num, total, type_dict)
            # for object_box, miss, error in zip(all_object, miss, error):  # 预留错标漏标的处理
            #     pass
            if object_num > 0:
                if 'box' in task:
                    mean_std_list += mean_box_std[0]
                elif 'point' in task:
                    for i in mean_point_std:
                        if type(i) == list:
                            mean_std_list += i
                        else:
                            pass
    return mean_std_list


def cal_all_std_offline(task, old_cam_ann, new_cam_ann, ann_num, normalize):
    old_new = [[], []]  # 老相机结果，新相机结果
    output_dict = dict()
    for cam, cam_ann in enumerate([old_cam_ann, new_cam_ann]):
        mean_std_list = [[], []]  # box_std，point_std
        for img in cam_ann:
            img_std_list = [[], []]
            num, total, type_dict = get_annotation_offline(task, cam_ann[img], ann_num)  # 数据处理
            if len(total) > 0:
                mean_box_std, mean_point_std, object_num, all_object, miss, error = box_annotation(num, total,
                                                                                                   type_dict,
                                                                                                   normalize)  # 计算标准差
                # for object_box, miss, error in zip(all_object, miss, error):  # 预留错标漏标的处理
                #     pass
                if object_num > 0:
                    # 结果分配
                    if 'box' in task:
                        for i in mean_box_std:
                            for j in i:
                                mean_std_list[0].append(j)
                                img_std_list[0].append(j)
                        # mean_std_list += (i for i in mean_box_std)
                    elif 'point' in task:
                        for i in mean_box_std:
                            for j in i:
                                mean_std_list[0].append(j)
                                img_std_list[0].append(j)
                        for i in mean_point_std:
                            if type(i) == list:
                                for j in i:
                                    mean_std_list[1].append(j)
                                    img_std_list[1].append(j)
            keyword = 'old' if 'old' in img else 'new'
            if img.split(keyword)[0] not in output_dict:
                output_dict[img.split(keyword)[0]] = [[], [], [], []]  # old_box, old_point, new_box, new_point
            if keyword == 'old':
                output_dict[img.split(keyword)[0]][0].extend(img_std_list[0])
                output_dict[img.split(keyword)[0]][1].extend(img_std_list[1])
            if keyword == 'new':
                output_dict[img.split(keyword)[0]][2].extend(img_std_list[0])
                output_dict[img.split(keyword)[0]][3].extend(img_std_list[1])
        old_new[cam].extend(mean_std_list)
    return output_dict


def read_json(json_path):
    """读取json文件"""
    with open(json_path, 'r') as f:
        json_read = json.load(f)
    # print('finish load ' + json_path)
    return json_read


def dump_json(json_to_dump, json_dump_path):
    """写入json文件"""
    with open(json_dump_path, 'w') as f:
        json.dump(json_to_dump, f)
    print('successfully dump json ' + json_dump_path)


def convert_annotation_offline(result_dir):
    """

    :param result_dir: 标注结果保存路径
    :return: 老相机结果， 新相机结果， 图片被标注次数
    """
    total_ann = defaultdict(list)
    old_cam_ann, new_cam_ann = defaultdict(list), defaultdict(list)
    num = 0
    for id in os.listdir(result_dir):
        for camera in ['Old_Camera', 'New_Camera']:
            camera_path = os.path.join(result_dir, id, camera)
            for video in os.listdir(camera_path):
                if os.path.isdir(os.path.join(camera_path, video)):
                    for json in os.listdir(os.path.join(camera_path, video)):
                        if json.endswith('.json'):
                            ann = read_json(os.path.join(os.path.join(camera_path, video, json)))
                            old_cam_ann[json].append(ann) if 'old' in json else new_cam_ann[json].append(ann)
        num += 1
    return old_cam_ann, new_cam_ann, num


def eval(task, test_img):
    if 'line' in task:
        return lsa.cal_avg_area(task, test_img)
    else:
        return cal_all_std(task, test_img)


def eval_offline(task, old_cam_ann, new_cam_ann, ann_num, normalize):
    if 'line' in task:
        return lsa.cal_avg_area_offline(task, old_cam_ann, new_cam_ann, ann_num, normalize)
    else:
        return cal_all_std_offline(task, old_cam_ann, new_cam_ann, ann_num, normalize)
