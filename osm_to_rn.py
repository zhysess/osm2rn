import networkx as nx
import osmium as o
from osgeo import ogr
import argparse
import json
from shapely.geometry import Polygon, LineString, MultiLineString
from coords_transform import wgs84_to_gcj02


class OSM2RNHandler(o.SimpleHandler):

    def __init__(self, rn, mbr):
        super(OSM2RNHandler, self).__init__()
        self.candi_highway_types = {'motorway', 'trunk', 'primary', 'secondary', 'tertiary', 'unclassified',
                                    'residential', 'motorway_link', 'trunk_link', 'primary_link', 'secondary_link',
                                    'tertiary_link', 'living_street', 'service', 'road'}
        self.rn = rn
        self.eid = 0
        self.mbr = mbr

    def way(self, w):
        if 'highway' in w.tags and w.tags['highway'] in self.candi_highway_types:
            raw_eid = w.id
            full_coords = []
            for n in w.nodes:
                full_coords.append((wgs84_to_gcj02(n.lon, n.lat)))
                # full_coords.append((n.lon, n.lat))
            inner_line = LineString(full_coords).intersection(self.mbr)
            print(type(inner_line))
            if isinstance(inner_line, MultiLineString):
                for ls in list(inner_line):
                    full_coords = list(ls.coords)
                    if 'oneway' in w.tags:
                        if w.tags['oneway'] != 'yes':
                            full_coords.reverse()
                        for i in range(len(full_coords) - 1):
                            coords = [full_coords[i], full_coords[i + 1]]
                            edge_attr = {'eid': self.eid, 'coords': coords, 'raw_eid': raw_eid,
                                         'highway': w.tags['highway']}
                            rn.add_edge(coords[0], coords[-1], **edge_attr)
                            self.eid += 1
                    else:
                        for i in range(len(full_coords) - 1):
                            coords = [full_coords[i], full_coords[i + 1]]
                            # add edges for both directions
                            edge_attr = {'eid': self.eid, 'coords': coords, 'raw_eid': raw_eid,
                                         'highway': w.tags['highway']}
                            rn.add_edge(coords[0], coords[-1], **edge_attr)
                            self.eid += 1

                        reversed_full_coords = full_coords.copy()
                        reversed_full_coords.reverse()
                        for i in range(len(reversed_full_coords) - 1):
                            reversed_coords = [reversed_full_coords[i], reversed_full_coords[i + 1]]
                            edge_attr = {'eid': self.eid, 'coords': reversed_coords, 'raw_eid': raw_eid,
                                         'highway': w.tags['highway']}
                            rn.add_edge(reversed_coords[0], reversed_coords[-1], **edge_attr)
                            self.eid += 1
            elif isinstance(inner_line, LineString):
                full_coords = list(inner_line.coords)
                if 'oneway' in w.tags:
                    if w.tags['oneway'] != 'yes':
                        full_coords.reverse()
                    for i in range(len(full_coords) - 1):
                        coords = [full_coords[i], full_coords[i + 1]]
                        edge_attr = {'eid': self.eid, 'coords': coords, 'raw_eid': raw_eid,
                                     'highway': w.tags['highway']}
                        rn.add_edge(coords[0], coords[-1], **edge_attr)
                        self.eid += 1
                else:
                    for i in range(len(full_coords) - 1):
                        coords = [full_coords[i], full_coords[i + 1]]
                        # add edges for both directions
                        edge_attr = {'eid': self.eid, 'coords': coords, 'raw_eid': raw_eid,
                                     'highway': w.tags['highway']}
                        rn.add_edge(coords[0], coords[-1], **edge_attr)
                        self.eid += 1

                    reversed_full_coords = full_coords.copy()
                    reversed_full_coords.reverse()
                    for i in range(len(reversed_full_coords) - 1):
                        reversed_coords = [reversed_full_coords[i], reversed_full_coords[i + 1]]
                        edge_attr = {'eid': self.eid, 'coords': reversed_coords, 'raw_eid': raw_eid,
                                     'highway': w.tags['highway']}
                        rn.add_edge(reversed_coords[0], reversed_coords[-1], **edge_attr)
                        self.eid += 1
            else:
                pass


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
    input_path = '../data/didi_5km_0707/rn/interest_region.osm.pbf'
    output_path = '../data/didi_5km_0707/rn/osm'
    conf_path = '../data/didi_5km_0707/conf_5km_0707.json'
    with open(conf_path, 'r') as f:
        conf = json.load(f)
    min_lat = conf['dataset']['min_lat']
    min_lng = conf['dataset']['min_lng']
    max_lat = conf['dataset']['max_lat']
    max_lng = conf['dataset']['max_lng']
    print(min_lng, min_lat, max_lng, max_lat)
    mbr = Polygon([(min_lng, min_lat), (min_lng, max_lat), (max_lng, max_lat), (max_lng, min_lat)])
    print(mbr)
    rn = nx.DiGraph()
    handler = OSM2RNHandler(rn, mbr)
    handler.apply_file(input_path, locations=True)
    store_shp(rn, output_path)
