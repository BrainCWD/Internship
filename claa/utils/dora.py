# -*- coding:utf-8 -*-
import pymongo
from collections import defaultdict


def convert_coordinate(xywh_list):
    x1, y1 = xywh_list[0], xywh_list[1]
    x2, y2 = xywh_list[0] + xywh_list[2] + 1, xywh_list[1] + xywh_list[3] + 1
    return [x1, y1, x2, y2]


def get_dora_db():
    """连接 dora 服务器"""
    dora_setting = {'host': 'mumbai.momenta.works:8025',
                    'database': 'dora',
                    'username': 'research',
                    'password': 'vrl1r0oLbsKht262eybX',
                    'options': 'ssl=false'}
    try:
        conn = pymongo.MongoClient(
            "mongodb://{username}:{password}@{host}/{database}?{options}".format(**dora_setting))
        db = conn.dora
        return db
    except Exception as ex:
        print("Error:", ex)
        exit("Failed to connect, exit.")


def get_test_image(task):
    dora = get_dora_db()
    cursor = dora[task].find({'result.1': {'$exists': True}})
    test_img = list()
    for i in cursor:
        if len(test_img) < 20:
            test_img.append(i['md5'])
    return test_img


def normalized(ann, normalize):
    if not normalize:
        return ann
    elif normalize:
        ratio = 100 / (ann[0][3] - ann[0][1])
        normalize_box = []
        for i in ann[0]:
            normalize_box.append(i * ratio)
        normalize_point = []
        for point in ann[1]:
            normalize_point_single = []
            for i in point[:2]:
                normalize_point_single.append(i * ratio)
            normalize_point_single.append(point[2])
            normalize_point.append(normalize_point_single)
        return [normalize_box, normalize_point]


def get_annotation(dora, task, img, type_list=('box', 'guess'), normalize=False):  # 预留guess属性接口
    # 接收路径/md5作为输入
    if len(img) == 32 and img.isalnum():
        cursor = dora[task].find({'md5': img})
    else:
        try:
            cursor = dora[task].find({'origin_path': img})
        except:
            print('输入图片信息有误，请检查路径/md5')
            # todo 鲁棒性
            return None
    for rec in cursor:
        # todo 适配拉框和标点任务
        ann_num = len(rec['result'])  # 总标注次数
        ann_total, type_dict = list(), defaultdict(list)
        if 'box' in task:
            for i in rec['result']:  # 目前先按一张图有多个标注结果处理
                if i['raw']['Skip'] or i['raw']['Hardscene']:  # skip/hardscnen图片不做处理
                    print(img + ' 标注为skip/hardscene, 无效图片跳过')
                    continue
                else:
                    if 'Rects' in i['raw']:
                        for box in i['raw']['Rects']:
                            if box['properties']['car2d_box_mulit_type'][-1] in type_list:
                                box_xywh = [box['x'], box['y'], box['w'], box['h']]
                                box_xyxy = convert_coordinate(box_xywh)
                                # 将dict改成list格式
                                if 'points' in box:
                                    p = []
                                    for item in box['points']:
                                        p.append([item['x'], item['y'], item['v']])
                                    ann = [box_xyxy, p]
                                else:
                                    ann = [box_xyxy, []]
                                # ann_total.append([box_xyxy, box['points'] if 'points' in box else list()])
                                # ann_total = normalized(ann_total, rec['size']['height'], normalize)
                                ann_total.append(normalized(ann, normalize))
                                type_dict[box['properties']['car2d_box_mulit_type'][-1]].append(ann_total[-1][0])
            return ann_num, ann_total, type_dict
        elif 'point' in task:
            for i in rec['result']:  # 目前先按一张图有多个标注结果处理
                if 'Rects' in i['raw']:
                    for box in i['raw']['Rects']:
                        if box['properties']['car2d_box_mulit_type'][-1] in type_list:
                            box_xywh = [box['x'], box['y'], box['w'], box['h']]
                            box_xyxy = convert_coordinate(box_xywh)
                            # 将dict改成list格式
                            if 'points' in box:
                                p = []
                                for item in box['points']:
                                    p.append([item['x'], item['y'], item['v']])
                                ann = [box_xyxy, p]
                            else:
                                ann = [box_xyxy, []]
                            # ann_total.append([box_xyxy, box['points'] if 'points' in box else list()])
                            # ann_total = normalized(ann_total, rec['size']['height'], normalize)
                            ann_total.append(normalized(ann, normalize))
                            type_dict[box['properties']['car2d_box_mulit_type'][-1]].append(ann_total[-1][0])
            return ann_num, ann_total, type_dict


def get_annotation_offline(task, img, ann_num, type_list=('box'), normalize=False):  # 预留guess属性接口
    ann_total, type_dict = list(), defaultdict(list)
    if 'box' in task:
        for i in img:
            if i['Skip'] or i['Hardscene']:  # skip/hardscnen图片不做处理
                print(' 标注为skip/hardscene, 无效图片跳过')
                continue
            else:
                if 'Rects' in i:
                    for box in i['Rects']:
                        if box['properties']['car2d_box_mulit_type'][-1] in type_list:
                            box_xywh = [box['x'], box['y'], box['w'], box['h']]
                            box_xyxy = convert_coordinate(box_xywh)
                            # 将dict改成list格式
                            if 'points' in box:
                                p = []
                                for item in box['points']:
                                    p.append([item['x'], item['y'], item['v']])
                                ann = [box_xyxy, p]
                            else:
                                ann = [box_xyxy, []]
                            ann_total.append(normalized(ann, normalize))
                            type_dict[box['properties']['car2d_box_mulit_type'][-1]].append(ann_total[-1][0])
        return ann_num, ann_total, type_dict
    elif 'point' in task:
        for i in img:  # 目前先按一张图有多个标注结果处理
            if 'Rects' in i:
                for box in i['Rects']:
                    if box['properties']['car2d_box_mulit_type'][-1] in type_list:
                        box_xywh = [box['x'], box['y'], box['w'], box['h']]
                        box_xyxy = convert_coordinate(box_xywh)
                        # 将dict改成list格式
                        if 'points' in box:
                            p = []
                            for item in box['points']:
                                p.append([item['x'], item['y'], item['v']])
                            ann = [box_xyxy, p]
                        else:
                            ann = [box_xyxy, []]
                        # ann_total.append([box_xyxy, box['points'] if 'points' in box else list()])
                        # ann_total = normalized(ann_total, rec['size']['height'], normalize)
                        ann_total.append(normalized(ann, normalize))
                        type_dict[box['properties']['car2d_box_mulit_type'][-1]].append(ann_total[-1][0])  # 获取框的属性
        return ann_num, ann_total, type_dict


def get_annotation_lines(dora, task, img, type_list=('normal_lane', 'guess')):  # 预留guess属性接口
    # 接收路径/md5作为输入
    if len(img) == 32 and img.isalnum():
        cursor = dora[task].find({'md5': img})
    else:
        try:
            cursor = dora[task].find({'origin_path': img})
        except:
            print('输入图片信息有误，请检查路径/md5')
            # todo 鲁棒性
            return None
    for image in cursor:
        # todo 确认标注的方式：一张图多个结果/多张图一张图一个结果
        ann_num = len(image['result'])  # 总标注次数
        ann_total = list()
        for i in image['result']:  # 目前先按一张图有多个标注结果处理
            if i['raw']['Skip'] or i['raw']['Hardscene']:  # skip/hardscnen图片不做处理
                # todo 确认SH场景的处理方式
                pass
            else:
                li = []
                for line in i['raw']['Lines']:
                    if line['properties']['lane_type'][0] in type_list:  # 只处理正常框（预留guess属性接口）
                        li.append(line['cpoints'])
            ann_total.append(li)
        return ann_num, ann_total


def get_annotation_lines_offline(task, img, ann_num, type_list=('normal_lane')):  # 预留guess属性接口
    ann_total = list()
    for i in img:
        # todo 确认标注的方式：一张图多个结果/多张图一张图一个结果
        if i['Skip'] or i['Hardscene']:  # skip/hardscnen图片不做处理
            # todo 确认SH场景的处理方式
            print(' 标注为skip/hardscene, 无效图片跳过')
            continue
        else:
            if 'Lines' in i:
                li = []
                for line in i['Lines']:
                    if line['properties']['lane_type'][0] in type_list:  # 只处理正常框（预留guess属性接口）
                        li.append(line['cpoints'])
                ann_total.append(li)
    return ann_num, ann_total
