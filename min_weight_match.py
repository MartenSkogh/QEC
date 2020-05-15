# This function is provided for participants of the course Quantum Qrror Correction 2020
# Author: Manuel Rispler
# Reuse outside the purposes of the course only upon request
# Dated: 11.4.2020

import networkx as nx

def mwpm(bulk_edges_weighted,boundary_edges_weighted):
    """"
    This function accepts a list of bulk edges and boundary edges and returns the minimum weight match solution
    
    INPUT format: 
    
    bulk_edges_weighted: a list of tuples of weighted edges.
    A weighted edge is a tuple (nodeA, nodeB, weightAB),
    i.e. bulk_edges_weighted = [(),(),...,()]
    Note that the graph must be a complete graph, i.e. every node that appears must have exactly one edge with every other node, all of these must appear somewhere in the list. Nodes can be labeled by integers or strings and weights must be positive (integer or float). The graph is undirected, so it does not matter which node is mentioned first in the edge tuple.

    boundary_edges_weighted: a list of tuples of the format (node, weight_to_boundary)
    Note that here we drop the label for the boundary node (this is handled internally by the algorithm, all you need to know is when a defect is matched to the boundary. All nodes that appear in bulk_edge_weighted must also have exactly one entry in boundary_edges_weighted.
    
    OUTPUT format:
    bulk_matches, boundary_matches

    bulk_matches is a list of pairs [(i,j),(k,m),...], pairs being the matchings of nodes.
    boundary_matches is a list of nodes [a,b,c,...] these are the nodes that were matched to the boundary


    EXAMPLE: Three defects, labeled by A,B,C, define the input:
    bulk_edges_weighted = [('A','B',5),('A','C',1),('B','C',3)]
    boundary_edges_weighted = [('A',1),('B',2),('C',3)]
    Output: [('A','C'),['B']], i.e. 'A' and 'C' matched and 'B' matched to boundary
    """

    # make sure we have no self-loops and all weights are positive
    for edge in bulk_edges_weighted:
        nodeA,nodeB,weight = edge
        if nodeA==nodeB:
            raise ValueError("Self-loops are not allowed, nodeA and nodeB must be different nodes!")
        if weight <=0:
            raise ValueError("Weights must be positive")

    #construct the bulk graph (turning all weights negative because networkx can only do maximum_weight_matching
    bulk_graph = nx.Graph()
    bulk_graph.add_weighted_edges_from([(nodeA,nodeB,-weight) for nodeA,nodeB,weight in bulk_edges_weighted])

    #check that graph is complete:
    # every node must have edge to every other node, i.e. check each node degree (excluded self-loops above)
    degree_list=[bulk_graph.degree[node] for node in bulk_graph.nodes]
    expected_degree_list=[bulk_graph.number_of_nodes()-1 for x in range(bulk_graph.number_of_nodes())]
    if degree_list!=expected_degree_list:
        raise ValueError("The bulk_graph is not complete, you missed some edges")

    #check that every node has an entry in the boundary_edges_weighted list
    for node,weight in boundary_edges_weighted:
        if weight<=0:
            raise ValueError('boundary weights must be positive')
        
    for node in bulk_graph.nodes:
        if node not in [entry[0] for entry in boundary_edges_weighted]:
            raise ValueError('your boundary list is missing node(s) that appear in the bulk graph')

    #construct the boundary graph as a copy of the bulk graph with zero weights
    # note that this works as long as there is at least one bulk_edge, otherwise both graphs are empty and we have to add the boundary edge by hand (which we do below)
    boundary_graph = nx.Graph()
    boundary_graph.add_weighted_edges_from([(a,b,0) for a,b,_ in bulk_edges_weighted])

    # join both graphs
    # note: nx.disjoint_union automatically replaces node labels by integer enumeration
    syndrome_graph = nx.disjoint_union(bulk_graph,boundary_graph)
        

    boundary_weight_dict = {x[0]:x[1] for x in boundary_edges_weighted}
    # add edges between bulk and boundary graphs between each bulk node and its ghost partner, the weight being the weight of matching to the boundary
    syndrome_graph.add_weighted_edges_from([(nodeindex, nodeindex+bulk_graph.number_of_nodes(),-boundary_weight_dict[nodename]) for nodeindex,nodename in enumerate(bulk_graph.nodes)])

    
    #perform the blossom algorith (maximum) weight perfect matching
    # maxcardinality=True enforces perfect matching
    matching = list(nx.max_weight_matching(syndrome_graph,maxcardinality=True))

    bulk_matches = [edge for edge in matching if edge[0]
                    < bulk_graph.number_of_nodes() and edge[1] < bulk_graph.number_of_nodes()]

    boundary_matches = [min(edge) for edge in matching if min(
        edge) < bulk_graph.number_of_nodes() and max(edge) >= bulk_graph.number_of_nodes()]

    
    #translate node names back to orignal labels provided by input
    node_name_list = {x[0]:x[1] for x in list(enumerate(bulk_graph.nodes))}
    bulk_matches = [(node_name_list[a],node_name_list[b]) for a,b in bulk_matches]
    boundary_matches = [node_name_list[i] for i in boundary_matches]

    # special case: single defect, just return the defect 
    if bulk_graph.number_of_nodes()==0:
        if len(boundary_edges_weighted)==1:
            boundary_matches=[boundary_edges_weighted[0][0]]
        elif len(boundary_edges_weighted)>1:
            raise ValueError('If your bulk list is empty, there can be at most one defect in the boundary list')
            
    return bulk_matches, boundary_matches
