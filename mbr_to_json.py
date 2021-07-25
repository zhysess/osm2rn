from shapely.geometry import Polygon, LineString, MultiLineString
# import json
# # conf_path='../data/baidu_big_traj/conf_big_baidu.json'
# # with open(conf_path, 'r') as f:
# #     conf = json.load(f)
# # min_lat = conf['dataset']['min_lat']
# # min_lng = conf['dataset']['min_lng']
# # max_lat = conf['dataset']['max_lat']
# # max_lng = conf['dataset']['max_lng']
# # mbr = Polygon([(min_lng,min_lat),(min_lng,max_lat),(max_lng,max_lat),(max_lng,min_lat)])
# # print(mbr)
#
#
# #square_with_hole = Polygon([(4, 4), (50, 4), (50, 61), (4, 61)],[[(5, 10), (8, 40), (14, 30.02)], [(13, 6), (15, 8), (19, 9)]])
# square_with_hole = Polygon([(4, 4), (50, 4), (50, 61), (4, 61)])
# #line = LineString([(2, 22), (50, 50)])
# line = LineString([(2, 2), (3, 3)])
# it_l = line.intersection(square_with_hole)
# print(it_l)

# with open('/Users/didi/Desktop/nohup.out', 'r') as f:
#     ls = f.readlines()
#     print(ls[0].find('[Loss: '))
#     print(ls[1].find('[Loss: '))
#     print(ls[1][:28])
#     for i in range(10):
#         print(ls[i])
import json


class MBR:

    def __init__(self, min_lon, min_lat, max_lon, max_lat):
        self.min_lon = min_lon
        self.min_lat = min_lat
        self.max_lon = max_lon
        self.max_lat = max_lat

    def mbr_to_polygon(self, path):
        res = {
            "type": "FeatureCollection",
            "features": []
        }

        coor_list = [[self.min_lon, self.min_lat],
                     [self.max_lon, self.min_lat],
                     [self.max_lon, self.max_lat],
                     [self.min_lon, self.max_lat],
                     [self.min_lon, self.min_lat]]

        t = {
            "type": "Feature",
            "geometry": {
                "type": "Polygon",
                "coordinates": [coor_list]
            },
            "properties": {
            }
        }

        res["features"].append(t)
        with open(path, "w") as f:
            f.write(json.dumps(res))


if __name__ == '__main__':
    mbr = MBR(116.29770, 39.86550, 116.35400, 39.91100)
    path = 'mbr2.json'
    mbr.mbr_to_polygon(path)
