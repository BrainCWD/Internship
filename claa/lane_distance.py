# -*- coding:utf-8 -*-
lane_1 = [(100, 100), (80, 90), (54, 70), (45, 60)]
lane_2 = [(100, 97), (80, 92), (54, 71), (45, 58)]
lane_3 = [(99, 97), (87, 92), (58, 71), (45, 57)]
lane = [lane_1, lane_2, lane_3]

distance = []
for i in range(len(lane)):
    for j in range(len(lane)):
        if i != j:
            lane1 = lane[i]
            lane2 = lane[j]


            lane1_start = lane1[0]
            lane1_end = lane1[len(lane1) - 1]

            lane2_start = lane2[0]
            lane2_end = lane2[len(lane2) - 1]

            if lane1_start[0] - lane2_start[0] <= 30 and lane1_end[0] - lane2_end[0] <= 30 and lane1_start[1] - lane2_start[
                1] <= 30 and lane1_end[1] - lane2_end[1] <= 30:
                # 判断是否是一条线
                for point in lane1:
                    dis = {}
                    for point_2 in lane2:
                        dis[(point[0] - point_2[0]) ** 2 + (point[1] - point_2[1]) ** 2] = point_2
                    # print(dis)
                    # print(min(dis))
                    cloest1 = dis[min(dis)]
                    dis.pop(min(dis))
                    cloest2 = dis[min(dis)]
                    # print(cloest1, cloest2)
                    x = point[0]
                    y = point[1]
                    A = cloest2[1] - cloest1[1]
                    B = cloest1[0] - cloest2[0]
                    C = cloest2[0] * cloest1[1] - cloest1[0] * cloest2[1]
                    d = abs((A * x + B * y + C)/((A ** 2 + B ** 2) ** 0.5))
                    distance.append(d)
print(distance)
print(len(distance))
