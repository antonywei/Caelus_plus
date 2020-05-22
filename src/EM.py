##EM
from EMfilter import *
from basic.sfcGen import * 
import numpy as np
from basic.Node import Node

def init_nodes_list(EM_graph):
    Node_list = {}
    for i in EM_graph.keys():
        node_ins = Node(node_id=i,connect_nodes=list(EM_graph[i].keys()))
        Node_list[i] = node_ins
    return Node_list

def cal_links_weight(sfc_ins,EM_graph):
    EM_weight_graph = EM_graph
    EM_matrix =[]
    ### calculate the weight 
    for nodes in EM_graph.keys():
        for conn_nodes in EM_graph[nodes]:
            weight1 = round(EM_graph[nodes][conn_nodes][0]/sfc_ins.td*sfc_ins.VNFnum,4)
            weight2 = round((T_max-EM_graph[nodes][conn_nodes][1])/T_max,4)
            weight3 = round(sfc_ins.bw/EM_graph[nodes][conn_nodes][2],4)
            EM_weight_graph[nodes][conn_nodes][0]=weight1
            EM_weight_graph[nodes][conn_nodes][1]=weight2
            EM_weight_graph[nodes][conn_nodes][2]=weight3
            EM_matrix.append(EM_weight_graph[nodes][conn_nodes])
    ### using numpy to normalize matrix 
    EM_matrix=np.array(EM_matrix)
    factor = EM_matrix.mean(axis=0)
    for nodes in EM_graph.keys():
        for conn_nodes in EM_graph[nodes]:
            EM_weight_graph[nodes][conn_nodes]=round((EM_weight_graph[nodes][conn_nodes][0]/factor[0])+\
                (EM_weight_graph[nodes][conn_nodes][1]/factor[1])+\
                (EM_weight_graph[nodes][conn_nodes][2]/factor[2]),4)
    for nodes in EM_graph.keys():
        EM_graph[nodes][nodes] = 0
    return EM_weight_graph,EM_matrix

def cal_node_weight(sfc_instance,vnf_id,node_list):
    Node_weight_matrix = []
    for node_ins in node_list:
        Node_weight_matrix.append(node_list[node_ins].embedCost(sfc_instance,vnf_id))
    return Node_weight_matrix

def findShortestPath(src,dst,EM_graph):
    print(EM_graph)
    distance ={i:1e9 for i in EM_graph}
    preNode = {i:src for i in EM_graph}
    visited = {i:0 for i in EM_graph}
    print(distance)
    print(preNode)
    print(visited)
    point = src
    minIndex = src
    for i in EM_graph:
        for j in EM_graph[minIndex]:
            if distance[j] > EM_graph[i][j] + distance[preNode[j]]:
                distance[j] = EM_graph[i][j] + distance[preNode[i]]
                preNode[j] = j
                print(distance,j,minIndex)
                
        minDist = 1e9
        
        for i in distance:
            if distance[i] < minDist and visited[i] == 0:
                minDist = distance[i]
                minIndex = i
            visited[minIndex] = 1
        print("********** iteration ones ******** ")

    print(distance)
    print(preNode)
    print(visited)

def embedingSFC(EM_graph,sfc_list,node_list):
    for sfc_ins in sfc_list:
        for vnf in sfc_ins:
            break
            ## input EM graph
            ## cal weight of links 
            ## cal weight of Nodes
            ## using shortest path to calculate
            ## embed vnf 
            ## update node info --  node.update
            ## update sfc info -- SFC.embedVNF
            ## update EM graph info

##em_graph {'node':{'conn_node':[td,stable,bwRe]}}


if __name__ == '__main__':
    MapData = read_csv_file()
    ## get EM graph
    EM_graph_raw = create_EM_graph(phyData=MapData,time_step=0) ## EM graph : 
    ### init node list
    node_list = init_nodes_list(EM_graph_raw)
    ### init SFC list
    sfc_list = gen_SFC_list()
    ## test command for cal weight of links and nodes 
    EM_weight_graph,EM_matrix = cal_links_weight(sfc_list[0],EM_graph_raw)
    Node_weight_matrix = cal_node_weight(sfc_list[0],1,node_list)

    #embedingSFC(sfc_list=sfc_list,EM_graph=EM_graph)
    src='00'
    dst='45'
    #print(EM_weight_graph)
    distance ={i:1e9 for i in EM_weight_graph}
    distance[src] = EM_weight_graph[src][src]
    preNode = {i:src for i in EM_weight_graph}
    visited = {i:0 for i in EM_weight_graph}
    #print(distance)
    #print(preNode)
    #print(visited)  
    point = src
    minIndex = src
    for i in range(len(EM_weight_graph)):
        for j in EM_weight_graph[minIndex]:
            if distance[j] > EM_weight_graph[minIndex][j] + distance[preNode[minIndex]] and j!= minIndex:
                distance[j] = EM_weight_graph[minIndex][j] + distance[preNode[minIndex]]
                preNode[j] = minIndex
                
        minDist = 1e9
        #print(distance)
        for k in distance:
            if distance[k] < minDist and visited[k] == 0:
                minDist = distance[k]
                Index = k
        visited[Index] = 1
        
        minIndex = Index
        #print("visited:",minIndex)

    print(distance)
    print(preNode)
    #print(visited)
