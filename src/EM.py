##EM
from EMfilter import *
from basic.sfcGen import * 
import numpy as np
from basic.Node import Node
import matplotlib.pyplot as plt 
import copy
import random
import sys
class EM(object):
    """docstring for  """
    def __init__(self,phyData,sfc_list):
        self.phyData=phyData,
        self.EM_graph = create_EM_graph(phyData=phyData,time_step=0)
        self.sfc_list=sfc_list,
        self.Tdfactory=0,
        self.Refactory=0,
        self.Migfactory=0,
        self.node_list=self.init_nodes_list()
    def init_nodes_list(self):
        Node_list = {}
        for i in self.EM_graph.keys():
            node_ins = Node(node_id=i,connect_nodes=list(self.EM_graph[i].keys()))
            Node_list[i] = node_ins
        return Node_list
    def EM_embeding(self,Tdfactory,Refactory,Migfactory):
        ## get EM graph
        ### init node list
        ### init SFC list
        self.Tdfactory=Tdfactory,
        self.Refactory=Refactory,
        self.Migfactory=Migfactory
        self.embedingSFC(Tdfactory,Refactory,Migfactory)
        return self.EM_graph,self.node_list,self.sfc_list

    def embedingSFC(self,Tdfactory,Refactory,Migfactory):
        for sfc_ins in self.sfc_list:
            #print("embedding sfc:",sfc_ins.id)
            for vnf in sfc_ins.vnfList:
                sfc_dst=sfc_ins.dst
                
                if vnf == 1:
                    sfc_src = sfc_ins.src
                else:
                    sfc_src=sfc_ins.nodesMap[vnf-1]
                ## calculate the weight graph
                weight_graph = cal_links_weight(sfc_ins,self.EM_graph,Tdfactory=Tdfactory,Refactory=Refactory,Migfactory=Migfactory)
                Node_weight_matrix = cal_node_weight(sfc_instance=sfc_ins,vnf_id=vnf,node_list=self.node_list,Refactory=Refactory)
                Node_weight_matrix=np.array(Node_weight_matrix)
                ### calculate the embeding cost matrix
                # if sfc_ins.id == 290:
                #     print("*************** EM WEIGHT GRAPH **********************")
                #     print(weight_graph)
                #     distance_from_src,preNode_src = findShortestPath(sfc_src,weight_graph)
                #     distance_from_dst,preNode_dst = findShortestPath(sfc_dst,weight_graph)
                #     print("distance from src",distance_from_src)
                #     print("distance from dst",distance_from_dst)
                distance_from_src,preNode_src = findShortestPath(sfc_src,weight_graph)
                distance_from_dst,preNode_dst = findShortestPath(sfc_dst,weight_graph)


                link_cost = (sfc_ins.VNFnum-vnf+1)/(sfc_ins.VNFnum-vnf+2)*distance_from_src + \
                    1/(sfc_ins.VNFnum-vnf+2)*distance_from_dst
                
                link_cost = link_cost
                totalCost = Refactory*Node_weight_matrix/Node_weight_matrix.clip(0,100).mean() + Migfactory*link_cost/link_cost.clip(0,100).mean()

                cost = min(totalCost)
                ## find the embeding node and links
                embed_node = np.argmin(totalCost)
                

                #if distance_from_src[embed_node]>1000 or distance_from_dst[embed_node]>1000:
                #print("distance from src",distance_from_src[embed_node])
                #print("distance from dst",distance_from_dst[embed_node])


                embed_res = self.node_list[embed_node].embedVNF(sfc_ins,vnf_id=vnf)
                if embed_res==0:
                    print("embed sfc ",sfc_ins.id,"failed.")
                    break

                ## iteration to find the link list 
                ## Node to place VNF 
                node_index = embed_node

                embed_links = []
                if node_index == sfc_src:
                    embed_links.insert(0,(preNode_src[node_index],node_index))
                    sfc_ins.Mapping_Link(logic_link_id=vnf-1,phy_links=embed_links)
                else:
                    while node_index != sfc_src:
                        embed_links.insert(0,(preNode_src[node_index],node_index))
                        node_index = preNode_src[node_index]
                    
                    sfc_ins.Mapping_Link(logic_link_id=vnf-1,phy_links=embed_links)
                    update_link_status(sfc_ins,embed_links,self.EM_graph)
                
                if vnf == sfc_ins.VNFnum:
                    node_index = embed_node
                    embed_dst_links = []
                    if sfc_dst == node_index:
                        embed_dst_links=[(node_index,sfc_dst)]
                        sfc_ins.Mapping_Link(logic_link_id=vnf,phy_links=embed_dst_links)
                    else:
                        while node_index != sfc_dst:
                            embed_dst_links.append((node_index,preNode_dst[node_index]))
                            node_index = preNode_dst[node_index]
                        sfc_ins.Mapping_Link(logic_link_id=vnf,phy_links=embed_dst_links)
                        update_link_status(sfc_ins,embed_dst_links,EM_graph)

                ## input EM graph
                ## cal weight of links 
                ## cal weight of Nodes
                ## using shortest path to calculate
                ## embed vnf 
                ## update node info --  node.update
                ## update sfc info -- SFC.embedVNF
                ## update EM graph inf




    def init_nodes_list(self):
        Node_list = {}
        for i in self.EM_graph.keys():
            node_ins = Node(node_id=i,connect_nodes=list(self.EM_graph[i].keys()))
            Node_list[i] = node_ins
        return Node_list

    def cal_links_weight(self,sfc_ins,Tdfactory,Refactory,Migfactory):
        EM_weight_graph = {}
        EM_matrix =[]
        ### calculate the weight 
        for nodes in self.EM_graph.keys():
            EM_weight_graph[nodes] = {}
            for conn_nodes in self.EM_graph[nodes]:
                ## delay
                weight1 = round(self.EM_graph[nodes][conn_nodes][0]/sfc_ins.td*sfc_ins.VNFnum,4)
                ## stable
                weight2 = round((T_max-self.EM_graph[nodes][conn_nodes][1])/T_max,4)
                ## bw
                weight3 = 0
                if self.EM_graph[nodes][conn_nodes][2]<sfc_ins.bw:
                    weight3 = sys.maxsize
                else:
                    weight3 = round(sfc_ins.bw/self.EM_graph[nodes][conn_nodes][2],4)

                EM_weight_graph[nodes][conn_nodes]=[weight1,weight2,weight3]
                EM_matrix.append(EM_weight_graph[nodes][conn_nodes])
        ### using numpy to normalize matrix 
        EM_matrix=np.array(EM_matrix)
        factor = np.mean(EM_matrix.clip(0,100),axis=0)
        for nodes in self.EM_graph.keys():
            for conn_nodes in self.EM_graph[nodes]:
                ##[0:delay,1:stable,2:bw]
                EM_weight_graph[nodes][conn_nodes]=round(Tdfactory*(EM_weight_graph[nodes][conn_nodes][0]/factor[0])+\
                    Migfactory*(EM_weight_graph[nodes][conn_nodes][1]/factor[1])+\
                    Refactory*(EM_weight_graph[nodes][conn_nodes][2]/factor[2]),4)
        for nodes in EM_weight_graph.keys():
            EM_weight_graph[nodes][nodes] = 0

        for nodes in self.EM_graph.keys():
            for conn_nodes in self.EM_graph[nodes]:
                if self.EM_graph[nodes][conn_nodes][2]<sfc_ins.bw:
                    EM_weight_graph[nodes][conn_nodes] = 1e8
                    EM_weight_graph[conn_nodes][nodes] = 1e8
                    #print("BW overflow")
        return EM_weight_graph

    def cal_node_weight(self,sfc_instance,vnf_id,node_list,Refactory):
        Node_weight_matrix = []
        for node_ins in node_list:
            Node_weight_matrix.append(Refactory*node_list[node_ins].embedCost(sfc_instance,vnf_id))
        return Node_weight_matrix

    def findShortestPath(self,src,EM_weight_graph,N=60):
        distance =[sys.maxsize]*N
        distance[src] = 0
        preNode = {i:i for i in range(N)}
        visited = [0 for i in range(N)]
        visited[src] = 1
        point = src
        minIndex = src

        for i in range(N):
            if minIndex in EM_weight_graph.keys():
                for j in EM_weight_graph[minIndex]:
                    if distance[j] > EM_weight_graph[minIndex][j] + distance[minIndex] and visited[j]==0:
                        distance[j] = EM_weight_graph[minIndex][j] + distance[minIndex]
                        preNode[j] = minIndex
            minDist = sys.maxsize
            Index = -1
            for k in range(len(distance)):
                if distance[k] < minDist and visited[k] == 0:
                    minDist = distance[k]
                    Index = k
            if Index != -1:
                #print("index",Index)
                visited[Index] = 1
            minIndex = Index
            distance = np.array(distance)
        return distance,preNode

    def update_link_status(sfc_ins,embed_links):
        for i in range(len(embed_links)):
            if embed_links[i][0] != embed_links[i][1]:
                self.EM_graph[embed_links[i][0]][embed_links[i][1]][2] = self.EM_graph[embed_links[i][0]][embed_links[i][1]][2]-sfc_ins.bw
                self.EM_graph[embed_links[i][1]][embed_links[i][0]][2] = self.EM_graph[embed_links[i][1]][embed_links[i][0]][2]-sfc_ins.bw
                if self.EM_graph[embed_links[i][1]][embed_links[i][0]][2] < 0:
                    print("can not deploy links here")


   #def embedingSFC(self,sfc_list,node_list,Tdfactory,Refactory,Migfactory):
   #      for sfc_ins in sfc_list:
   #          #print("embedding sfc:",sfc_ins.id)
   #          for vnf in sfc_ins.vnfList:
   #              sfc_dst=sfc_ins.dst
                
   #              if vnf == 1:
   #                  sfc_src = sfc_ins.src
   #              else:
   #                  sfc_src=sfc_ins.nodesMap[vnf-1]
   #              ## calculate the weight graph
   #              weight_graph = cal_links_weight(sfc_ins,self.EM_graph,Tdfactory=Tdfactory,Refactory=Refactory,Migfactory=Migfactory)
   #              Node_weight_matrix = cal_node_weight(sfc_instance=sfc_ins,vnf_id=vnf,node_list=node_list,Refactory=Refactory)
   #              Node_weight_matrix=np.array(Node_weight_matrix)
   #              ### calculate the embeding cost matrix
   #              # if sfc_ins.id == 290:
   #              #     print("*************** EM WEIGHT GRAPH **********************")
   #              #     print(weight_graph)
   #              #     distance_from_src,preNode_src = findShortestPath(sfc_src,weight_graph)
   #              #     distance_from_dst,preNode_dst = findShortestPath(sfc_dst,weight_graph)
   #              #     print("distance from src",distance_from_src)
   #              #     print("distance from dst",distance_from_dst)
   #              distance_from_src,preNode_src = findShortestPath(sfc_src,weight_graph)
   #              distance_from_dst,preNode_dst = findShortestPath(sfc_dst,weight_graph)


   #              link_cost = (sfc_ins.VNFnum-vnf+1)/(sfc_ins.VNFnum-vnf+2)*distance_from_src + \
   #                  1/(sfc_ins.VNFnum-vnf+2)*distance_from_dst
                
   #              link_cost = link_cost
   #              totalCost = Refactory*Node_weight_matrix/Node_weight_matrix.clip(0,100).mean() + Migfactory*link_cost/link_cost.clip(0,100).mean()

   #              cost = min(totalCost)
   #              ## find the embeding node and links
   #              embed_node = np.argmin(totalCost)
                

   #              #if distance_from_src[embed_node]>1000 or distance_from_dst[embed_node]>1000:
   #              #print("distance from src",distance_from_src[embed_node])
   #              #print("distance from dst",distance_from_dst[embed_node])


   #              embed_res = node_list[embed_node].embedVNF(sfc_ins,vnf_id=vnf)
   #              if embed_res==0:
   #                  print("embed sfc ",sfc_ins.id,"failed.")
   #                  break

   #              ## iteration to find the link list 
   #              ## Node to place VNF 
   #              node_index = embed_node

   #              embed_links = []
   #              if node_index == sfc_src:
   #                  embed_links.insert(0,(preNode_src[node_index],node_index))
   #                  sfc_ins.Mapping_Link(logic_link_id=vnf-1,phy_links=embed_links)
   #              else:
   #                  while node_index != sfc_src:
   #                      embed_links.insert(0,(preNode_src[node_index],node_index))
   #                      node_index = preNode_src[node_index]
                    
   #                  sfc_ins.Mapping_Link(logic_link_id=vnf-1,phy_links=embed_links)
   #                  update_link_status(sfc_ins,embed_links,self.EM_graph)
                
   #              if vnf == sfc_ins.VNFnum:
   #                  node_index = embed_node
   #                  embed_dst_links = []
   #                  if sfc_dst == node_index:
   #                      embed_dst_links=[(node_index,sfc_dst)]
   #                      sfc_ins.Mapping_Link(logic_link_id=vnf,phy_links=embed_dst_links)
   #                  else:
   #                      while node_index != sfc_dst:
   #                          embed_dst_links.append((node_index,preNode_dst[node_index]))
   #                          node_index = preNode_dst[node_index]
   #                      sfc_ins.Mapping_Link(logic_link_id=vnf,phy_links=embed_dst_links)
   #                      update_link_status(sfc_ins,embed_dst_links,EM_graph)

   #              ## input EM graph
   #              ## cal weight of links 
   #              ## cal weight of Nodes
   #              ## using shortest path to calculate
   #              ## embed vnf 
   #              ## update node info --  node.update
   #              ## update sfc info -- SFC.embedVNF
   #              ## update EM graph inf

    # def embedingSFC_GLL(EM_graph,sfc_list,node_list,Tdfactory,Refactory,Migfactory):
    #     for sfc_ins in sfc_list:
    #         #print("embedding sfc:",sfc_ins.id)
    #         for vnf in sfc_ins.vnfList:
    #             sfc_dst=sfc_ins.dst
                
    #             if vnf == 1:
    #                 sfc_src = sfc_ins.src
    #             else:
    #                 sfc_src=sfc_ins.nodesMap[vnf-1]
    #             ## calculate the weight graph
    #             weight_graph = cal_links_weight(sfc_ins,EM_graph,Tdfactory=Tdfactory,Refactory=Refactory,Migfactory=Migfactory)
    #             Node_weight_matrix = cal_node_weight(sfc_instance=sfc_ins,vnf_id=vnf,node_list=node_list,Refactory=Refactory)
    #             Node_weight_matrix=np.array(Node_weight_matrix)
    #             ### calculate the embeding cost matrix
    #             distance_from_src,preNode_src = findShortestPath(sfc_src,weight_graph)
    #             distance_from_dst,preNode_dst = findShortestPath(sfc_dst,weight_graph)
                
    #             #link_cost = link_cost
    #             totalCost = Node_weight_matrix/Node_weight_matrix.clip(0,100).mean()

    #             # cost = min(totalCost)
    #             # ## find the embeding node and links
    #             # embed_node = np.argmin(totalCost)
    #             node1 = (sfc_src+1)%60
    #             node2 = (sfc_src-1)%60
    #             candidate = [sfc_src,node1,node2]
    #             cannot_deploy = []
    #             for candi in candidate:
    #                 if node_list[candi].cpuRe*node_list[candi].cpuCap < sfc_ins.vnfList[vnf][1]:
    #                     cannot_deploy.append(candi)

    #             for i in range(len(cannot_deploy)):
    #                 candidate.remove(cannot_deploy[i])

    #             if candidate==[]:
    #                 embed_node = np.argmin(totalCost)
    #             else:
    #                 embed_node = random.choice(candidate)
                
    #             embed_res = node_list[embed_node].embedVNF(sfc_ins,vnf_id=vnf)
    #             if embed_res==0:
    #                 print("embed sfc ",sfc_ins.id,"failed.")
    #                 break
    #             ## iteration to find the link list 
    #             ## Node to place VNF 
    #             node_index = embed_node

    #             embed_links = []
    #             if node_index == sfc_src:
    #                 embed_links.insert(0,(preNode_src[node_index],node_index))
    #                 sfc_ins.Mapping_Link(logic_link_id=vnf-1,phy_links=embed_links)
    #             else:
    #                 while node_index != sfc_src:
    #                     embed_links.insert(0,(preNode_src[node_index],node_index))
    #                     node_index = preNode_src[node_index]
                    
    #                 sfc_ins.Mapping_Link(logic_link_id=vnf-1,phy_links=embed_links)
    #                 update_link_status(sfc_ins,embed_links,EM_graph)
                
    #             if vnf == sfc_ins.VNFnum:
    #                 node_index = embed_node
    #                 embed_dst_links = []
    #                 if sfc_dst == node_index:
    #                     embed_dst_links=[(node_index,sfc_dst)]
    #                     sfc_ins.Mapping_Link(logic_link_id=vnf,phy_links=embed_dst_links)
    #                 else:
    #                     while node_index != sfc_dst:
    #                         embed_dst_links.append((node_index,preNode_dst[node_index]))
    #                         node_index = preNode_dst[node_index]
    #                     sfc_ins.Mapping_Link(logic_link_id=vnf,phy_links=embed_dst_links)
    #                     update_link_status(sfc_ins,embed_dst_links,EM_graph)


    # def embedingSFC_SNH(EM_graph,sfc_list,node_list,Tdfactory,Refactory,Migfactory):
    #     for sfc_ins in sfc_list:
    #         #print("embedding sfc:",sfc_ins.id)
    #         for vnf in sfc_ins.vnfList:
    #             sfc_dst=sfc_ins.dst
                
    #             if vnf == 1:
    #                 sfc_src = sfc_ins.src
    #             else:
    #                 sfc_src=sfc_ins.nodesMap[vnf-1]
    #             ## calculate the weight graph
    #             weight_graph = cal_links_weight(sfc_ins,EM_graph,Tdfactory=Tdfactory,Refactory=Refactory,Migfactory=Migfactory)
    #             Node_weight_matrix = cal_node_weight(sfc_instance=sfc_ins,vnf_id=vnf,node_list=node_list,Refactory=Refactory)
    #             Node_weight_matrix=np.array(Node_weight_matrix)
    #             ### calculate the embeding cost matrix
    #             distance_from_src,preNode_src = findShortestPath(sfc_src,weight_graph)
    #             distance_from_dst,preNode_dst = findShortestPath(sfc_dst,weight_graph)
                
    #             #link_cost = link_cost
    #             distance_from_src,preNode_src = findShortestPath(sfc_src,weight_graph)
    #             distance_from_dst,preNode_dst = findShortestPath(sfc_dst,weight_graph)

    #             #link_cost = (sfc_ins.VNFnum-vnf+1)/(sfc_ins.VNFnum-vnf+2)*distance_from_src + \
    #             #    1/(sfc_ins.VNFnum-vnf+2)*distance_from_dst
                
    #             #link_cost = link_cost
    #             #totalCost = link_cost/link_cost.clip(0,100).mean()

                
    #             #cost = min(totalCost)
                
    #             ## find the embeding node and links
    #             embed_node = 0
    #             totalCost = Node_weight_matrix

    #             if node_list[sfc_src].cpuRe*node_list[sfc_src].cpuCap > sfc_ins.vnfList[vnf][1]:
    #                 embed_node = sfc_src
    #             else:
    #                 embed_node = np.argmin(totalCost)

    #             embed_res = node_list[embed_node].embedVNF(sfc_ins,vnf_id=vnf)
    #             if embed_res==0:
    #                 print("embed sfc ",sfc_ins.id,"failed.")
    #                 break
    #             ## iteration to find the link list 
    #             ## Node to place VNF 
    #             node_index = embed_node

    #             embed_links = []
    #             if node_index == sfc_src:
    #                 embed_links.insert(0,(preNode_src[node_index],node_index))
    #                 sfc_ins.Mapping_Link(logic_link_id=vnf-1,phy_links=embed_links)
    #             else:
    #                 while node_index != sfc_src:
    #                     embed_links.insert(0,(preNode_src[node_index],node_index))
    #                     node_index = preNode_src[node_index]
                    
    #                 sfc_ins.Mapping_Link(logic_link_id=vnf-1,phy_links=embed_links)
    #                 update_link_status(sfc_ins,embed_links,EM_graph)
                
    #             if vnf == sfc_ins.VNFnum:
    #                 node_index = embed_node
    #                 embed_dst_links = []
    #                 if sfc_dst == node_index:
    #                     embed_dst_links=[(node_index,sfc_dst)]
    #                     sfc_ins.Mapping_Link(logic_link_id=vnf,phy_links=embed_dst_links)
    #                 else:
    #                     while node_index != sfc_dst:
    #                         embed_dst_links.append((node_index,preNode_dst[node_index]))
    #                         node_index = preNode_dst[node_index]
    #                     sfc_ins.Mapping_Link(logic_link_id=vnf,phy_links=embed_dst_links)
    #                     update_link_status(sfc_ins,embed_dst_links,EM_graph)


    # def EM_embeding(self,phyData,sfc_list,Tdfactory,Refactory,Migfactory):
    #     ## get EM graph
    #     graph_raw = create_EM_graph(phyData=phyData,time_step=0) ## EM graph : 
    #     ### init node list
    #     node_list = init_nodes_list(graph_raw)
    #     ### init SFC list
    #     sfc_list = sfc_list
    #         #embedingSFC(sfc_list=sfc_list,EM_graph=EM_graph)

    #     ## test command for cal weight of links and nodes 
    #     #weight_graph,EM_matrix = cal_links_weight(sfc_list[0],graph_raw)
    #     #Node_weight_matrix = cal_node_weight(sfc_list[0],1,node_list)
        
    #     embedingSFC(graph_raw,sfc_list,node_list,Tdfactory,Refactory,Migfactory)
    #     # nodeCPURe = []
    #     # for node in node_list:
    #     #     nodeCPURe.append(node_list[node].cpuRe)
    #     # nodeCPURe = np.array(nodeCPURe)
    #     # CPUconsum=1-nodeCPURe
    #     # #draw_CDF(CPUconsum,graph_name="BLCPU.jpg")

    #     # linkBwRe = []
    #     # for node1 in graph_raw:
    #     #     for node2 in graph_raw[node1]:
    #     #         linkBwRe.append(graph_raw[node1][node2][2])
    #     # linkBwRe = np.array(linkBwRe)
    #     # linkConsum=1-linkBwRe/100
    #     #draw_CDF(data=linkConsum,graph_name="BLBW.jpg")
    #     return graph_raw,node_list,sfc_list

    def EM_embeding_GLL(self,phyData,sfc_list,Tdfactory,Refactory,Migfactory):
        graph_raw = create_EM_graph(phyData=phyData,time_step=0) ## EM graph : 
        ### init node list
        node_list = init_nodes_list(graph_raw)
        ### init SFC list
        sfc_list = sfc_list
            #embedingSFC(sfc_list=sfc_list,EM_graph=EM_graph)

        ## test command for cal weight of links and nodes 
        #weight_graph,EM_matrix = cal_links_weight(sfc_list[0],graph_raw)
        #Node_weight_matrix = cal_node_weight(sfc_list[0],1,node_list)
        
        embedingSFC_GLL(graph_raw,sfc_list,node_list,Tdfactory,Refactory,Migfactory)
        # nodeCPURe = []
        # for node in node_list:
        #     nodeCPURe.append(node_list[node].cpuRe)
        # nodeCPURe = np.array(nodeCPURe)
        # CPUconsum=1-nodeCPURe
        #draw_CDF(CPUconsum,graph_name="BLCPU.jpg")

        # linkBwRe = []
        # for node1 in graph_raw:
        #     for node2 in graph_raw[node1]:
        #         linkBwRe.append(graph_raw[node1][node2][2])
        # linkBwRe = np.array(linkBwRe)
        # linkConsum=1-linkBwRe/100
        #draw_CDF(data=linkConsum,graph_name="BLBW.jpg")
        return graph_raw,node_list,sfc_list

    def EM_embeding_SNH(self,phyData,sfc_list,Tdfactory,Refactory,Migfactory):
        ## get EM graph
        graph_raw = create_EM_graph(phyData=phyData,time_step=0) ## EM graph : 
        ### init node list
        node_list = init_nodes_list(graph_raw)
        ### init SFC list
        sfc_list = sfc_list
            #embedingSFC(sfc_list=sfc_list,EM_graph=EM_graph)

        ## test command for cal weight of links and nodes 
        #weight_graph,EM_matrix = cal_links_weight(sfc_list[0],graph_raw)
        #Node_weight_matrix = cal_node_weight(sfc_list[0],1,node_list)
        
        embedingSFC_SNH(graph_raw,sfc_list,node_list,Tdfactory,Refactory,Migfactory)
        # nodeCPURe = []
        # for node in node_list:
        #     nodeCPURe.append(node_list[node].cpuRe)
        # nodeCPURe = np.array(nodeCPURe)
        # CPUconsum=1-nodeCPURe
        #draw_CDF(CPUconsum,graph_name="BLCPU.jpg")

        # linkBwRe = []
        # for node1 in graph_raw:
        #     for node2 in graph_raw[node1]:
        #         linkBwRe.append(graph_raw[node1][node2][2])
        # linkBwRe = np.array(linkBwRe)
        # linkConsum=1-linkBwRe/100
        #draw_CDF(data=linkConsum,graph_name="BLBW.jpg")
        return graph_raw,node_list,sfc_list
# if __name__ == '__main__':
#     EM_embeding()
    



    
            

        #print(EM_weight_graph)
    
        #print("visited:",minIndex)


    #print(visited)
