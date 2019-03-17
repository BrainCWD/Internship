# -*- coding:utf-8 -*-
from matplotlib.font_manager import *
import matplotlib.pyplot as plt
import os
import numpy as np


def accurancy_rate_graph_box(output_dict, std_thres=(0.5, 1.0, 1.5, 2, 2.5, '2.5+')):
    for video in output_dict:
        x = std_thres
        y_box_list, y_point_list = [], []
        # 设置边框，标签等信息
        ax = plt.subplot(1, 1, 1)
        ax.yaxis.grid(True)
        ax.spines['left'].set_visible(False)  # 去掉左边框
        ax.spines['right'].set_visible(False)  # 去掉右边框
        ax.set_xlabel('std_thres')
        ax.set_ylabel('percentage')
        ax.set_ylim(0, 1)
        ax.set_yticklabels(['0%', '20%', '40%', '60%', '80%', '100%'])

        # 处理box数据
        for cam in [output_dict[video][0], output_dict[video][2]]:
            y = [0, 0, 0, 0, 0, 0]
            for i in cam:
                if i == np.nan:
                    continue
                count = int(i / 0.5 if i <= 2.5 else 5)
                y[count] += 1
            y_p = [i / sum(y) for i in y]
            y_percent = []
            y_add = 0
            for i in range(len(y_p)):
                y_add += y_p[i]
                y_percent.append(y_add)
            y_box_list.append(y_percent)
        # 处理point数据
        for cam in [output_dict[video][1], output_dict[video][3]]:
            y = [0, 0, 0, 0, 0, 0]
            for i in cam:
                if i == np.nan:
                    continue
                count = int(i / 0.5 if i <= 2.5 else 5)
                y[count] += 1
            y_p = [i / sum(y) for i in y]
            y_percent = []
            y_add = 0
            for i in range(len(y_p)):
                y_add += y_p[i]
                y_percent.append(y_add)
            y_point_list.append(y_percent)
        # 设置图中显示数据点数值
        # 画box的线
        for a, b, c in zip(x, y_box_list[0], y_box_list[1]):
            plt.text(a / 0.5 - 1 if a != '2.5+' else a, b - 0.05, '%.2f%%' % (b * 100), color='r', ha='center',
                     va='bottom', fontsize=10.5)
            plt.text(a / 0.5 - 1 if a != '2.5+' else a, c + 0.05, '%.2f%%' % (c * 100), color='b', ha='center',
                     va='bottom', fontsize=10.5)
        ax.plot(list(x), list(y_box_list[0]), 'r-o', label='box_old')
        ax.plot(list(x), list(y_box_list[1]), 'b-o', label='box_new')

        # 画point的线
        for a, b, c in zip(x, y_point_list[0], y_point_list[1]):
            plt.text(a / 0.5 - 1 if a != '2.5+' else a, b - 0.05, '%.2f%%' % (b * 100), color='r', ha='center',
                     va='bottom', fontsize=10.5)
            plt.text(a / 0.5 - 1 if a != '2.5+' else a, c + 0.05, '%.2f%%' % (c * 100), color='b', ha='center',
                     va='bottom', fontsize=10.5)
        ax.plot(list(x), list(y_point_list[0]), 'r--o', label='point_old')
        ax.plot(list(x), list(y_point_list[1]), 'b--o', label='point_new')

        plt.legend(loc=4)
        ax.text(0.2, 0.02, video[:-1])
        plt.savefig('test.jpg')
        plt.show()


def accurancy_rate_graph_line(output_dict, std_thres=(0.5, 1.0, 1.5, 2, 2.5, '2.5+')):
    for video in output_dict:
        x = std_thres
        y_line_list = []
        # 设置边框，标签等信息
        ax = plt.subplot(1, 1, 1)
        ax.yaxis.grid(True)
        ax.spines['left'].set_visible(False)  # 去掉左边框
        ax.spines['right'].set_visible(False)  # 去掉右边框
        ax.set_xlabel('distance_thres')
        ax.set_ylabel('percentage')
        ax.set_ylim(0, 1)
        ax.set_yticklabels(['0%', '20%', '40%', '60%', '80%', '100%'])

        # 处理line数据
        for cam in [output_dict[video][0], output_dict[video][2]]:
            y = [0, 0, 0, 0, 0, 0]
            for i in cam:
                if i == np.nan:
                    continue
                count = int(i / 0.5 if i <= 2.5 else 5)
                y[count] += 1
            y_p = [i / sum(y) for i in y]
            y_percent = []
            y_add = 0
            for i in range(len(y_p)):
                y_add += y_p[i]
                y_percent.append(y_add)
            y_line_list.append(y_percent)

        # 设置图中显示数据点数值
        # 画line的线
        for a, b, c in zip(x, y_line_list[0], y_line_list[1]):
            plt.text(a / 0.5 - 1 if a != '2.5+' else a, b - 0.05, '%.2f%%' % (b * 100), color='r', ha='center',
                     va='bottom', fontsize=10.5)
            plt.text(a / 0.5 - 1 if a != '2.5+' else a, c + 0.05, '%.2f%%' % (c * 100), color='b', ha='center',
                     va='bottom', fontsize=10.5)
        ax.plot(list(x), list(y_line_list[0]), 'r-o', label='line_old')
        ax.plot(list(x), list(y_line_list[1]), 'b-o', label='line_new')

        plt.legend(loc=4)
        ax.text(0.2, 0.02, video[:-1])
        # plt.savefig('test.jpg')
        plt.show()


# def annotation_rate_graph():
#     x = []
#     y = []
#     for i in range(len(file_names)):
#         data = xlrd.open_workbook(os.path.join(excel_path, file_names[i]))
#         x.append(file_names[i][3:-4])
#         y.append(data.sheets()[2].cell_value(-1, 1))
#     # 设置边框，标签等信息
#     ax = plt.subplot(1, 1, 1)
#     ax.yaxis.grid(True)
#     # ax.spines['top'].set_visible(False)  # 去掉上边框
#     # ax.spines['bottom'].set_visible(False)  # 去掉下边框
#     ax.spines['left'].set_visible(False)  # 去掉左边框
#     ax.spines['right'].set_visible(False)  # 去掉右边框
#     ax.set_xlabel('时间', fontproperties=myfont)
#     ax.set_ylabel('正确率', fontproperties=myfont)
#     ax.set_ylim(0.9, 1)
#     ax.set_yticklabels(['90%', '92%', '94%', '96%', '98%', '100%'])
#     # 设置图中显示数据点数值
#     for a, b in zip(x, y):
#         plt.text(a, b + 0.005, '%.2f%%' % (b * 100), color='b', ha='center', va='bottom', fontsize=10.5)
#     plt.plot(list(reversed(x)), list(reversed(y)), 'b-o')
#     plt.savefig('感知各任务平均正确率.jpg')
#     plt.show()


def data_plot(output_dict, task):
    if not 'line' in task:
        accurancy_rate_graph_box(output_dict)
    else:
        accurancy_rate_graph_line(output_dict)
    # todo 标出度
    # annotation_rate_graph()
