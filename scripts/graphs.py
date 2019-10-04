#Python script to manage lnd nodes
from __future__ import print_function
import random

# Create a tree
# Returns adj list
def create_graph_tree(n, children = 2):
    matrix = [];

    next_child = 1
    for p_i in range(0, n):
        # Add node
        matrix.append([])

        while len(matrix[p_i]) < children:
            if next_child == n:
                break
            matrix[p_i].append(next_child)
            next_child += 1

        if next_child == n:
            continue
    return matrix

# Create a centralized graph
# Returns adj list
def create_graph_central(n):
    matrix = []

    # create central node
    matrix.append([])

    for child_i in range(1,n):

        # add every other node to central node
        matrix[0].append(child_i)

        # create child nodes
        matrix.append([])

    return matrix

# Create a ring graph
# returns adj list
def create_graph_ring(n):
    matrix = []

    for i in range(0, n):

        # find next node in loop
        next_node = (i + 1) % (n)

        # Add node
        matrix.append([next_node])

    return matrix

def create_graph_star(n):
    mat = []

    for i in range(0, n):
        mat.append([])


graph_types = {
    "tree": create_graph_tree,
    "central": create_graph_central,
    "ring": create_graph_ring
};
