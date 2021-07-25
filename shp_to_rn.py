import networkx as nx
from osgeo import ogr
import argparse
import json
from shapely.geometry import Polygon, LineString, MultiLineString
import shapefile


def read_clip_shp(path, mbr):
    rn = nx.DiGraph()
    sf = shapefile.Reader(path)
    shapes = sf.shapes()
    records = sf.records()
    eid = 0
    for k in range(len(shapes)):

        full_coords = shapes[k].points
        raw_eid = records[k][-1]
        inner_line = LineString(full_coords).intersection(mbr)
        if isinstance(inner_line, MultiLineString):
            for ls in list(inner_line):
                full_coords = list(ls.coords)

                for i in range(len(full_coords) - 1):
                    coords = [full_coords[i], full_coords[i + 1]]
                    edge_attr = {'eid': eid, 'coords': coords, 'raw_eid': raw_eid}
                    rn.add_edge(coords[0], coords[-1], **edge_attr)
                    eid += 1

        elif isinstance(inner_line, LineString):
            full_coords = list(inner_line.coords)

            for i in range(len(full_coords) - 1):
                coords = [full_coords[i], full_coords[i + 1]]
                edge_attr = {'eid': eid, 'coords': coords, 'raw_eid': raw_eid}
                rn.add_edge(coords[0], coords[-1], **edge_attr)
                eid += 1

        else:
            pass
    return rn

def store_shp(rn, target_path):
    ''' nodes: [lng, lat] '''
    rn.remove_nodes_from(list(nx.isolates(rn)))
    print('# of nodes:{}'.format(rn.number_of_nodes()))
    print('# of edges:{}'.format(rn.number_of_edges()))
    for _, _, data in rn.edges(data=True):
        geo_line = ogr.Geometry(ogr.wkbLineString)
        for coord in data['coords']:
            geo_line.AddPoint(coord[0], coord[1])
        data['Wkb'] = geo_line.ExportToWkb()
        del data['coords']
    nx.write_shp(rn, target_path)


if __name__ == '__main__':
    # parser = argparse.ArgumentParser()
    # parser.add_argument('--input_path', help='the input path of the original osm data')
    # parser.add_argument('--output_path', help='the output directory of the constructed road network')
    # parser.add_argument('--conf_path', help='the input path of configuration file')
    # opt = parser.parse_args()
    # print(opt)
    input_path = '../beijing/0408'
    output_path = '../data/didi_5km_0707/rn/beijing'
    conf_path = '../data/didi_5km_0707/conf_5km_0707.json'
    with open(conf_path, 'r') as f:
        conf = json.load(f)
    min_lat = conf['dataset']['min_lat']
    min_lng = conf['dataset']['min_lng']
    max_lat = conf['dataset']['max_lat']
    max_lng = conf['dataset']['max_lng']
    print(min_lng, min_lat, max_lng, max_lat)
    mbr = Polygon([(min_lng, min_lat), (min_lng, max_lat), (max_lng, max_lat), (max_lng, min_lat)])
    rn = read_clip_shp(input_path, mbr)
    store_shp(rn, output_path)