#Python script to manage lnd nodes
from __future__ import print_function

# Create a Circular tree
# Returns adj list
def create_graph_tree(n):
    mat = [];
    n_list = [];

    for x in range(0, n):
        # populate n_list
        n_list.append(x)

        # populate mat
        mat.append([])

    random.shuffle(n_list)
    
    p_i = 0
    while True:
        l_i = (p_i * 2) + 1
        r_i = (p_i * 2) + 2 

        p = n_list[p_i]

        if l_i < len(n_list):
            l = n_list[l_i]
            mat[p].append(l)

        if r_i < len(n_list):
            r = n_list[r_i]
            mat[p].append(r)

        if r_i >= len(n_list) and l_i >= len(n_list):
            break

        p_i += 1

    for i in range(0, n):
        # look for empty row
        if len(mat[i]) != 0: # CHANGE MAT TO LIST
            continue

        # create new peer
        for j in range(0, n):
            rand = int(random.random() * n)

            # if rand node is not self and already connected
            if rand != i and i not in mat[rand]:
                mat[i].append(rand)
                break
    
    return mat

# Create a centralized graph
# Returns adj list
def create_graph_central(n):
    mat = []

    # central node
    mat.append([])
    for i in range(1,n):
        mat[0].append(i)

        # child nodes
        mat.append([])

    return mat

# Create a ring graph
# returns adj list
def create_graph_ring(n):
    mat = []

    for i in range(0, n):
        next_node = (i + 1) % (n)
        mat.append([next_node])

    return mat

graph_types = {
    "tree": create_graph_tree,
    "central": create_graph_central,
    "ring": create_graph_ring
};
