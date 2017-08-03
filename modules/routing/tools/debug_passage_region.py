################################################################################
#
# Copyright (c) 2017 Baidu.com, Inc. All Rights Reserved
#
################################################################################
"""
This module provides routing result and passage region parse and plot functions.

Authors: fuxiaoxin(fuxiaoxin@baidu.com)
"""

import sys
import itertools
import matplotlib.pyplot as plt
import debug_topo
import gen.topo_graph_pb2 as topo_graph_pb2
import gen.router_pb2 as router_pb2

color_iter = itertools.cycle(['navy', 'c', 'cornflowerblue', 'gold',
                              'darkorange'])
g_central_curve_dict = {}
g_center_point_dict = {}


def get_center_of_passage_region(region):
    """Get center of passage region center curve"""
    center_points = []
    for seg in region.segment:
        center_points.append(g_center_point_dict[seg.id])
    return center_points[len(center_points) // 2]


def read_routing_result(file_name):
    """Read routing result"""
    fin = open(file_name)
    result = router_pb2.RoutingResponse()
    result.ParseFromString(fin.read())
    return result


def plot_region(region, color):
    "Plot passage region"
    for seg in region.segment:
        center_pt = debug_topo.plot_central_curve_with_s_range(g_central_curve_dict[seg.id],
                                                               seg.start_s,
                                                               seg.end_s,
                                                               color=color)
        g_center_point_dict[seg.id] = center_pt
        print 'Plot lane id: %s, start s: %f, end s: %f' % (seg.id, seg.start_s, seg.end_s)


def plot_lane_change(lane_change, passage_regions):
    """Plot lane change infomation"""
    st_idx = lane_change.start_passage_region_index
    ed_idx = lane_change.end_passage_region_index
    from_pt = get_center_of_passage_region(passage_regions[st_idx])
    to_pt = get_center_of_passage_region(passage_regions[ed_idx])
    plt.gca().annotate("",
                       xy=(to_pt[0], to_pt[1]),
                       xytext=(from_pt[0], from_pt[1]),
                       arrowprops=dict(arrowstyle="->",
                                       connectionstyle="arc3"))


def plot_road(road):
    """Plot road"""
    for region in road.passage_region:
        plot_region(region, 'green')
    for lane_change in road.lane_change_info:
        plot_lane_change(lane_change, road.passage_region)


def plot_junction(junction):
    """Plot junction"""
    plot_region(junction.passage_region, 'red')


def plot_result(routing_result, central_curve_dict):
    """Plot routing result"""
    plt.close()
    plt.figure()
    for way in routing_result.route:
        if way.HasField("road_info"):
            plot_road(way.road_info)
        else:
            plot_junction(way.junction_info)

    plt.gca().set_aspect(1)
    plt.title('Passage region')
    plt.xlabel('x')
    plt.ylabel('y')
    plt.legend()

    plt.draw()


def print_help():
    """Print help information.

    Print help information of usage.

    Args:

    """
    print 'usage:'
    print '     python debug_topo.py file_path, then',
    print_help_command()


def print_help_command():
    """Print command help information.

    Print help information of command.

    Args:

    """
    print 'type in command: [q] [r]'
    print '         q               exit'
    print '         p               plot passage region'


if __name__ == '__main__':
    if len(sys.argv) != 3:
        print_help()
        sys.exit(0)
    print 'Please wait for loading data...'

    file_name = sys.argv[1]
    fin = open(file_name)
    graph = topo_graph_pb2.Graph()
    graph.ParseFromString(fin.read())
    for nd in graph.node:
        g_central_curve_dict[nd.lane_id] = nd.central_curve

    plt.ion()
    while 1:
        print_help_command()
        print 'cmd>',
        instruction = raw_input()
        argv = instruction.strip(' ').split(' ')
        if len(argv) == 1:
            if argv[0] == 'q':
                sys.exit(0)
            elif argv[0] == 'p':
                result = read_routing_result(sys.argv[2])
                plot_result(result, g_central_curve_dict)
            else:
                print '[ERROR] wrong command'
            continue

        else:
            print '[ERROR] wrong arguments'
            continue
