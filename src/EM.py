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
    EM_weight_graph = {}
    EM_matrix =[]
    ### calculate the weight 
    for nodes in EM_graph.keys():
        EM_weight_graph[nodes] = {}
        for conn_nodes in EM_graph[nodes]:
            weight1 = round(EM_graph[nodes][conn_nodes][0]/sfc_ins.td*sfc_ins.VNFnum,4)
            weight2 = round((T_max-EM_graph[nodes][conn_nodes][1])/T_max,4)
            weight3 = round(sfc_ins.bw/EM_graph[nodes][conn_nodes][2],4)
            EM_weight_graph[nodes][conn_nodes]=[weight1,weight2,weight3]
            EM_matrix.append(EM_weight_graph[nodes][conn_nodes])
    ### using numpy to normalize matrix 
    EM_matrix=np.array(EM_matrix)
    factor = EM_matrix.mean(axis=0)
    for nodes in EM_graph.keys():
        for conn_nodes in EM_graph[nodes]:
            EM_weight_graph[nodes][conn_nodes]=round((EM_weight_graph[nodes][conn_nodes][0]/factor[0])+\
                (EM_weight_graph[nodes][conn_nodes][1]/factor[1])+\
                (EM_weight_graph[nodes][conn_nodes][2]/factor[2]),4)
    for nodes in EM_weight_graph.keys():
        EM_weight_graph[nodes][nodes] = 0
    return EM_weight_graph,EM_matrix

def cal_node_weight(sfc_instance,vnf_id,node_list):
    Node_weight_matrix = []
    for node_ins in node_list:
        Node_weight_matrix.append(node_list[node_ins].embedCost(sfc_instance,vnf_id))
    return Node_weight_matrix

def findShortestPath(src,EM_weight_graph):
    distance =np.array([1e9]*len(EM_weight_graph))
    #print("distance[src],src,EM_weight_graph[src][src]:",distance[src],src,EM_weight_graph[src][src])
    distance[src] = 0
    preNode = {i:i for i in EM_weight_graph}
    visited = {i:0 for i in EM_weight_graph}
    #print(distance)
    #print(preNode)
    #print(visited)  
    point = src
    minIndex = src

    for i in range(len(EM_weight_graph)):
        for j in EM_weight_graph[minIndex]:
            if distance[j] > EM_weight_graph[minIndex][j] + distance[minIndex] and visited[j]==0:
                distance[j] = EM_weight_graph[minIndex][j] + distance[minIndex]
                preNode[j] = minIndex
                
        minDist = 1e9
        Index = ''
        #print(distance)
        for k in range(len(distance)):
            if distance[k] < minDist and visited[k] == 0:
                minDist = distance[k]
                Index = k
        visited[Index] = 1
        
        minIndex = Index

    return distance,preNode

def embedingSFC(EM_graph,sfc_list,node_list,lambd=0):

    for sfc_ins in sfc_list:
        print("embedding sfc:",sfc_ins.id)
        for vnf in sfc_ins.vnfList:
            sfc_dst=sfc_ins.dst
            sfc_src = sfc_ins.src
            if vnf > 1:
                sfc_src=sfc_ins.nodesMap[vnf-1]
            ## calculate the weight graph
            weight_graph,EM_matrix = cal_links_weight(sfc_ins,EM_graph)
            Node_weight_matrix = cal_node_weight(sfc_instance=sfc_ins,vnf_id=vnf,node_list=node_list)
            Node_weight_matrix=np.array(Node_weight_matrix)
            ### calculate the embeding cost matrix
            distance_from_src,preNode_src = findShortestPath(sfc_src,weight_graph)
            distance_from_dst,preNode_dst = findShortestPath(sfc_dst,weight_graph)

            link_cost = (sfc_ins.VNFnum-vnf+1)/(sfc_ins.VNFnum-vnf+2)*distance_from_src + \
                1/(sfc_ins.VNFnum-vnf+2)*distance_from_dst
            
            link_cost = link_cost
            totalCost = Node_weight_matrix/Node_weight_matrix.mean() + link_cost/link_cost.mean()

            cost = min(totalCost)
            ## find the embeding node and links
            embed_node = np.argmin(totalCost)
            embed_links = []
            node_list[embed_node].embedVNF(sfc_ins,vnf_id=vnf)
            ## iteration to find the link list 
            ## Node to place VNF 
            node_index = embed_node 
            
            while node_index != sfc_src:
                embed_links.insert(0,node_index)
                node_index = preNode_src[node_index]
            embed_links.insert(0,node_index)
            sfc_ins.Mapping_Link(logic_link_id=vnf-1,phy_links=embed_links)


            embed_links = []
            if vnf == sfc_ins.VNFnum:
                while node_index != sfc_dst:
                    embed_links.append(node_index)
                    node_index = preNode_dst[node_index]
                embed_links.append(node_index)
                sfc_ins.Mapping_Link(logic_link_id=vnf,phy_links=embed_links)

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
    graph_raw = create_EM_graph(phyData=MapData,time_step=0) ## EM graph : 
    ### init node list
    node_list = init_nodes_list(graph_raw)
    ### init SFC list
    sfc_list = gen_SFC_list()
        #embedingSFC(sfc_list=sfc_list,EM_graph=EM_graph)
    src=00
    dst=44

    ## test command for cal weight of links and nodes 
    #weight_graph,EM_matrix = cal_links_weight(sfc_list[0],graph_raw)
    #Node_weight_matrix = cal_node_weight(sfc_list[0],1,node_list)

    embedingSFC(graph_raw,sfc_list,node_list)
    
            

        #print(EM_weight_graph)
    
        #print("visited:",minIndex)


    #print(visited)
