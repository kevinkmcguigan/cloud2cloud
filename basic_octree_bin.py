import random
import struct

class Node:
    def __init__(self, id, points, children):
        self.id = id
        self.children = children
        
        self.grid = [[[] for _ in range(2)] for _ in range(2)]
        for point in points:
            cell_x = int(point[0] > 0.5)
            cell_y = int(point[1] > 0.5)
            self.grid[cell_x][cell_y].append(point)

def create_node(id, points):
    if len(points) <= 1:
        return Node(id, points, [])
    
    mid = len(points) // 2
    mid_x = points[mid][0]
    mid_y = points[mid][1]
    
    children = [
        create_node(id*4 + i, [p for p in points if (p[0] < mid_x if i % 2 == 0 else p[0] >= mid_x) and (p[1] < mid_y if i < 2 else p[1] >= mid_y)])
        for i in range(4)
    ]
    
    return Node(id, [], children)

def write_node_to_file(f, index, node):
    f.write(struct.pack('I', node.id))
    index[node.id] = f.tell()
    
    f.write(struct.pack('I', len(node.children)))
    for child in node.children:
        write_node_to_file(f, index, child)
    
    for cell_x in range(2):
        for cell_y in range(2):
            points = node.grid[cell_x][cell_y]
            f.write(struct.pack('I', len(points)))
            for point in points:
                f.write(struct.pack('ff', *point))

def write_index_to_file(f, index):
    f.write(struct.pack('I', len(index)))
    for id, offset in index.items():
        f.write(struct.pack('II', id, offset))

def write_quadtree_to_file(filename, root):
    index = {}
    with open(filename, 'wb') as f:
        write_node_to_file(f, index, root)
        write_index_to_file(f, index)

# Create a list of random points
points = [(random.random(), random.random()) for _ in range(1000)]
points.sort(key=lambda p: (p[0], p[1]))

# Create the root of the quadtree
root = create_node(0, points)

# Write the quadtree to a file
write_quadtree_to_file('quadtree.bin', root)


def read_node_from_file(f):
    id = struct.unpack('I', f.read(4))[0]
    
    num_children = struct.unpack('I', f.read(4))[0]
    children = [read_node_from_file(f) for _ in range(num_children)]
    
    grid = [[[] for _ in range(2)] for _ in range(2)]
    for cell_x in range(2):
        for cell_y in range(2):
            num_points = struct.unpack('I', f.read(4))[0]
            for _ in range(num_points):
                grid[cell_x][cell_y].append(struct.unpack('ff', f.read(8)))
    
    return Node(id, grid, children)

def read_index_from_file(f):
    num_entries = struct.unpack('I', f.read(4))[0]
    
