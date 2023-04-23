import numpy as np
import json
import struct

def read_metadata(metadata_path):
    with open(metadata_path, 'r') as f:
        metadata = json.load(f)
    return metadata

def read_hierarchy_bin(file_path, step_size):
    with open(file_path, "rb") as f:
        nodes = []
        while True:
            node_name_data = f.read(step_size)
            if not node_name_data:
                break
            node_name = node_name_data.decode('latin1').rstrip('\x00')
            point_count = int.from_bytes(f.read(4), byteorder='little')
            nodes.append((node_name, point_count))
        return nodes

def read_octree_bin(file_path, point_format, hierarchy, bbox_min, bbox_max):
    point_data = []
    point_size = sum(attr["size"] for attr in point_format)
    
    def read_point(f):
        point = {}
        for attribute in point_format:
            point_value = struct.unpack(attribute["type"], f.read(attribute["size"]))[0]
            point[attribute["name"]] = point_value
        return point

    def is_leaf_node(node_name):
        return not any(node.startswith(node_name) for node, _ in hierarchy if node != node_name)

    with open(file_path, "rb") as f:
        for node_name, point_count in hierarchy:
            if is_leaf_node(node_name):
                for _ in range(point_count):
                    point = read_point(f)
                    coords = np.array([point["position"][0], point["position"][1], point["position"][2]])
                    if np.all(bbox_min <= coords) and np.all(coords <= bbox_max):
                        point_data.append(coords)
            else:
                f.seek(point_count * point_size, 1)  # Skip points for non-leaf nodes

    return np.array(point_data)

# Example usage
metadata_path = './pointclouds/5000/metadata.json'
octree_bin_path = './pointclouds/5000/octree.bin'
hierarchy_bin_path = './pointclouds/5000/hierarchy.bin'

# Read metadata
metadata = read_metadata(metadata_path)
point_format = metadata['attributes']
hierarchy_info = metadata['hierarchy']
step_size = hierarchy_info['stepSize']

# Read hierarchy
hierarchy = read_hierarchy_bin(hierarchy_bin_path, step_size)

# Define bounding box
bbox_min = np.array([269000, 5227000, 63.15])
bbox_max = np.array([269999.99, 5227999.99, 412.09])

# Read point data within bounding box
point_data = read_octree_bin(octree_bin_path, point_format, hierarchy, bbox_min, bbox_max)

# Print point data
print(point_data)
