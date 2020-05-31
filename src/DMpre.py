from EM import *
from basic.globalvar import *
class DM(object):
    def __init__(self,phyData,Refactory,Tdfactory,Migfactory,Linkfactory,migration_gate):
        self.reroute_links={} ## {time step:{sfc_id:{logic_link_id:[new links]},{}}
        self.reroute_links_count=[0 for i in range(8)]
        self.replacement_vnf_count=[0 for i in range(8)]
        self.migration_SFC={} ## {time step:{sfc_id:{vnf_id},{}}
        self.phyData=phyData
        self.EM_graph={}
        self.time_step=0
        self.node_list_status=[]
        self.sfc_list_status=[]
        self.disconnect_Links={}
        self.disconn_logic_links={} ## {time step:{sfc_id:[logic_link_id],{}}
        self.Refactory = Refactory
        self.Tdfactory = Tdfactory
        self.Migfactory = Migfactory
        self.Linkfactory = Linkfactory
        self.migration_gate = migration_gate
        Refactor = 0.6
        self.sfc_need_mig={}
    # def resetCount(self):
    #     self.reroute_links_count=0
    #     self.replacement_vnf_count=0

    def EM_init(self,sfc_list):
        em=EM(self.phyData,sfc_list)
        self.EM_graph[0],self.node_list_status,self.sfc_list_status=em.EM_embeding(Tdfactory=self.Tdfactory,Refactory=self.Refactory,Migfactory=self.Migfactory)
        self.time_step=1

    def EM_GLL(self,sfc_list):
        self.EM_graph[0],self.node_list_status,self.sfc_list_status=EM_embeding_GLL(phyData=phyData,\
            sfc_list=sfc_list,Tdfactory=self.Tdfactory,Refactory=self.Refactory,Migfactory=self.Migfactory)
        self.time_step=1

    def EM_SNH(self,sfc_list):
        self.EM_graph[0],self.node_list_status,self.sfc_list_status=EM_embeding_SNH(phyData=phyData,\
            sfc_list=sfc_list,Tdfactory=self.Tdfactory,Refactory=self.Refactory,Migfactory=self.Migfactory)
        self.time_step=1

    def migrate_EM_graph(self):
        self.EM_graph[self.time_step] = create_EM_graph(self.phyData,self.time_step,self.EM_graph[self.time_step-1])
        disconn_Links = set()
        for i in self.EM_graph[self.time_step]:
            for j in self.EM_graph[self.time_step-1][i]:
                if j not in self.EM_graph[self.time_step][i].keys():
                    disconn_Links.add((i,j))
        self.disconnect_Links[self.time_step]=disconn_Links

    def check_sfc(self):
        self.disconn_logic_links[self.time_step] = {}  ## sfc_id:[logic links,logic links,logic links]
        for sfc_ins in self.sfc_list_status:
            logic_link_disconn = set()
            for logic_link in sfc_ins.linkMap:
                for phy_link in sfc_ins.linkMap[logic_link]:
                    if phy_link in self.disconnect_Links[self.time_step]:
                        logic_link_disconn.add(logic_link)
            logic_link_disconn = list(logic_link_disconn)
            if logic_link_disconn != []:
                self.disconn_logic_links[self.time_step][sfc_ins.id]=logic_link_disconn

    def release_SFC_links(self,sfc_id):
        for logic_link in self.disconn_logic_links[self.time_step][sfc_id]:
            old_links = self.sfc_list_status[sfc_id].linkMap[logic_link]
            for link in old_links:
                if link not in self.disconnect_Links[self.time_step]:
                    self.EM_graph[self.time_step][link[0]][link[1]][2] = \
                        self.EM_graph[self.time_step][link[0]][link[1]][2] + \
                        self.sfc_list_status[sfc_id].bw
            self.sfc_list_status[sfc_id].linkMap[logic_link]={}
    
    def release_SFC_ins(self,sfc_id):
        sfc_node_map = copy.deepcopy(self.sfc_list_status[sfc_id].nodesMap)
        sfc_link_map = copy.deepcopy(self.sfc_list_status[sfc_id].linkMap)
        released_node = set()

        for node in sfc_node_map:
            #print("node: ",node," sfc_id: ",sfc_id)
            if sfc_node_map[node] not in released_node and sfc_node_map[node]!=None:
                self.node_list_status[sfc_node_map[node]].release_embedding_sfc(self.sfc_list_status[sfc_id])
                released_node.add(sfc_node_map[node])
        self.sfc_list_status[sfc_id].release_embedding_result()

        ### release links
        for logic_link in sfc_link_map:
            for phy_link in sfc_link_map[logic_link]:  
                if phy_link not in self.disconnect_Links[self.time_step]:
                    self.EM_graph[self.time_step][phy_link[0]][phy_link[1]][2] = \
                        self.EM_graph[self.time_step][phy_link[0]][phy_link[1]][2] + \
                        self.sfc_list_status[sfc_id].bw
        return sfc_node_map,sfc_link_map

    def modify_sfc(self):
        ### jugdement sfc need to migration or rerouting
        #sfc_reroute={}
        #
        # self.reroute_links[self.time_step] = {}
        # for sfc_id in self.disconn_logic_links[self.time_step].keys():
        #     if len(self.disconn_logic_links[self.time_step][sfc_id]) < round((self.sfc_list_status[sfc_id].VNFnum)*self.migration_gate):
        #         ### release old links only in EM_graph not in SFC_LIST
        #         self.release_SFC_links(sfc_id=sfc_id)
        #         result = self.reroute_sfc(sfc_id)
        #         if result == 0:
        #             print("cannot reroute tyr")
        #             sfc_node_map,sfc_link_map=self.release_SFC_ins(sfc_id)
        #             self.replacement_sfc(sfc_id,sfc_node_map,sfc_link_map)
        #         else:
        #             self.reroute_links[self.time_step][sfc_id] = result
        #     ### reroute sfc
        #     else:
        #         print("SFC need migration")
        #         sfc_node_map,sfc_link_map=self.release_SFC_ins(sfc_id)
        #         self.replacement_sfc(sfc_id,sfc_node_map,sfc_link_map)

                #self.sfc_list_status[sfc],modify_info=migration_sfc(self.sfc_list_status[sfc],EM_graph_new,sfc_mig[sfc])
                #sfc_reroute[sfc]=len(disconn_logic_links[sfc])
            ### migration sfc

        sfc_reroute={}
        self.reroute_links[self.time_step] = {}
        for sfc_id in self.disconn_logic_links[self.time_step].keys():
            self.release_SFC_links(sfc_id=sfc_id)
            result = self.reroute_sfc(sfc_id)
            if result != False:
                self.reroute_links[self.time_step][sfc_id] = result
            # if len(self.disconn_logic_links[self.time_step][sfc_id]) < round((self.sfc_list_status[sfc_id].VNFnum)*self.migration_gate):
            #     ### release old links only in EM_graph not in SFC_LIST
            #     self.release_SFC_links(sfc_id=sfc_id)
            #     result = self.reroute_sfc(sfc_id)
            #     if result == 0:
            #         print("cannot reroute tyr")
            #         sfc_node_map,sfc_link_map=self.release_SFC_ins(sfc_id)
            #         self.replacement_sfc(sfc_id,sfc_node_map,sfc_link_map)
            #     else:
            #         self.reroute_links[self.time_step][sfc_id] = result
            ### reroute sfc
            else:
                print("SFC need migration")
                sfc_node_map,sfc_link_map=self.release_SFC_ins(sfc_id)
                self.replacement_sfc(sfc_id,sfc_node_map,sfc_link_map)



        self.time_step=self.time_step+1
        

        ### release disconnect links
    ### the number of logic links reroute 
    ### the number of sfc instance replacement
    def reroute_sfc(self,sfc_id):
        #### sfc need to reroute  type sfc object
        #### new graph info type  graph dict 
        #### reroute links type list [logic links need to reroute]
        sfc_ins=self.sfc_list_status[sfc_id]
        reroute_links=self.disconn_logic_links[self.time_step][sfc_id]


        logic_link_reroute={}

        for logic_link in reroute_links:
            ### reroute vnf of  id = logic_link to id=logic_link+1
            if logic_link > 0 and logic_link < sfc_ins.VNFnum:
                vnf_src = sfc_ins.nodesMap[logic_link]
                vnf_dst = sfc_ins.nodesMap[logic_link+1]
            elif logic_link == 0:    
                vnf_src = sfc_ins.src
                vnf_dst = sfc_ins.nodesMap[1]
            elif logic_link == sfc_ins.VNFnum:
                vnf_src = sfc_ins.nodesMap[logic_link]
                vnf_dst = sfc_ins.dst
            else:
                print("logic link id error")
                return
            ## calculate the weight graph
            weight_graph = cal_links_weight(sfc_ins,self.EM_graph[self.time_step],\
                Tdfactory=self.Tdfactory,Refactory=self.Refactory,Migfactory=self.Migfactory)
            ### calculate the embeding cost matrix
            distance_from_src,preNode_src = findShortestPath(vnf_src,weight_graph)
            if min(distance_from_src) > 1e6:
                print("cannot reroute try to migration")
                return False
            ### debug 

            link_cost = distance_from_src[vnf_dst]
            embed_links = []

            ## iteration to find the link list 
            ## Node to place VNF 
            node_index = vnf_dst
            while node_index != vnf_src:
                embed_links.insert(0,(preNode_src[node_index],node_index))
                node_index = preNode_src[node_index]
            logic_link_reroute[logic_link] = embed_links
            sfc_ins.Mapping_Link(logic_link_id=logic_link,phy_links=embed_links)
            update_link_status(sfc_ins,embed_links,self.EM_graph[self.time_step])
            self.reroute_links_count[self.sfc_list_status[sfc_id].VNFnum]+=1
        return logic_link_reroute
    #def release_links(self,EM_graph,reroute_links):

    def replacement_sfc(self,sfc_id,sfc_node_map_pre,sfc_link_map_pre):
        #### sfc need to reroute  type sfc object
        #### new graph info type  graph dict 
        #### reroute links type list [logic links need to reroute]
        sfc_ins=self.sfc_list_status[sfc_id]
        #print("embedding sfc:",sfc_ins.id)
        for vnf in sfc_ins.vnfList:
            sfc_dst=sfc_ins.dst
            
            if vnf == 1:
                sfc_src = sfc_ins.src
            else:
                sfc_src=sfc_ins.nodesMap[vnf-1]
            ## calculate the weight graph
            weight_graph = cal_links_weight(sfc_ins,self.EM_graph[self.time_step],\
                Tdfactory=self.Tdfactory,Refactory=self.Refactory,Migfactory=self.Migfactory)
            Node_weight_matrix = cal_node_weight(sfc_instance=sfc_ins,vnf_id=vnf,\
                node_list=self.node_list_status,Refactory=self.Refactory)
            Node_weight_matrix=np.array(Node_weight_matrix)



            for link in sfc_link_map_pre[vnf-1]:
                if link[1] in weight_graph[link[0]].keys():
                    weight_graph[link[0]][link[1]]*=Refactor

            if vnf == sfc_ins.VNFnum:
                for link in sfc_link_map_pre[vnf]:
                    if link[1] in weight_graph[link[0]].keys():
                        weight_graph[link[0]][link[1]]*=Refactor

            Node_weight_matrix[sfc_node_map_pre[vnf]]*=Refactor
            ### calculate the embeding cost matrix
            distance_from_src,preNode_src = findShortestPath(sfc_src,weight_graph)
            distance_from_dst,preNode_dst = findShortestPath(sfc_dst,weight_graph)

            link_cost = (sfc_ins.VNFnum-vnf+1)/(sfc_ins.VNFnum-vnf+2)*distance_from_src + \
                1/(sfc_ins.VNFnum-vnf+2)*distance_from_dst
            
            link_cost = link_cost
            totalCost = self.Refactory*Node_weight_matrix/Node_weight_matrix.clip(0,100).mean() + self.Migfactory*link_cost/link_cost.clip(0,100).mean()

            cost = min(totalCost)
            ## find the embeding node and links
            embed_node = np.argmin(totalCost)
            
            
            embed_res = self.node_list_status[embed_node].embedVNF(sfc_ins,vnf_id=vnf)
            if embed_res==0:
                print("embed sfc ",sfc_ins.id,"failed.")
                break
            ## iteration to find the link list 
            ## Node to place VNF 
            node_index = embed_node
            if node_index != sfc_node_map_pre[vnf]:
                self.replacement_vnf_count[self.sfc_list_status[sfc_id].VNFnum]+=1
            embed_links = []
            if node_index == sfc_src:
                embed_links.insert(0,(preNode_src[node_index],node_index))
                sfc_ins.Mapping_Link(logic_link_id=vnf-1,phy_links=embed_links)
            else:
                while node_index != sfc_src:
                    embed_links.insert(0,(preNode_src[node_index],node_index))
                    node_index = preNode_src[node_index]
                
                sfc_ins.Mapping_Link(logic_link_id=vnf-1,phy_links=embed_links)
                update_link_status(sfc_ins,embed_links,self.EM_graph[self.time_step])
            
            if embed_links != sfc_link_map_pre[vnf-1]:
                self.reroute_links_count[self.sfc_list_status[sfc_id].VNFnum]+=1
            

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
                    update_link_status(sfc_ins,embed_dst_links,self.EM_graph[self.time_step])
                if embed_dst_links != sfc_link_map_pre[vnf]:
                    self.reroute_links_count[self.sfc_list_status[sfc_id].VNFnum]+=1


             ## input EM graph
            ## cal weight of links 
            ## cal weight of Nodes
            ## using shortest path to calculate
            ## embed vnf 
            ## update node info --  node.update
            ## update sfc info -- SFC.embedVNF
            ## update EM graph inf
        
    #def release_links(self,EM_graph,reroute_links):
    def count_delay(self):
        for sfc in self.sfc_list_status:
            self.sfc_list_status[sfc].delayCount(self.EM_graph[self.time_step-1])



    def draw_cdf(self,figureName):

        ## count cpu
        nodeCPURe = []
        for node in self.node_list_status:
            nodeCPURe.append(self.node_list_status[node].cpuRe)
        nodeCPURe = np.array(nodeCPURe)
        CPUconsum=1-nodeCPURe
        #draw_CDF(CPUconsum,graph_name="BLCPU.jpg")
        ## count Resource
        linkBwRe = []
        for node1 in self.EM_graph[self.time_step-1]:
            for node2 in self.EM_graph[self.time_step-1][node1]:
                linkBwRe.append(self.EM_graph[self.time_step-1][node1][node2][2])
        linkBwRe = np.array(linkBwRe)
        linkConsum=linkBwRe

        Delay = []
        for sfc_ins in self.sfc_list_status:
            sfc_ins.delayCount(self.EM_graph[self.time_step-1])
            Delay.append(sfc_ins.delay/(sfc_ins.VNFnum+1))
        Delay=np.array(Delay)
        draw_CDF(data=CPUconsum,graph_name="fig/"+figureName+"CPU"+".jpg")
        #draw_CDF(data=linkConsum,graph_name="fig/"+figureName+"BW"+".jpg")
        draw_CDF(data=Delay,graph_name="fig/"+figureName+"Delay"+".jpg")
        #draw_CDF(data=linkConsum,graph_name="BLBW.jpg")
        return CPUconsum,linkConsum,Delay



def draw_CDF(data,graph_name):
    n_bins = 50
    x = data
    #x = x/30
    x_max = np.max(x)
    x_min = np.min(x)
    print(x_max)

    width = 5
    high = width*0.618
    fig_size = [width, high]

    fig, ax = plt.subplots(figsize=fig_size)

    ax.set_xlim(0, x_max)
    ax.set_ylim(0, 1)

    # plot the cumulative histogram
    n, bins, patches = ax.hist(x, n_bins, density=1, histtype='step',
                               cumulative=True, color='black', linewidth=1.4)


    # tidy up the figure
    ax.grid(True)
    ticks_font_x = {'family' : 'Arial',  
                  'color'  : 'black',  
                  'weight' : 'medium',  
                  'size'   : 15.5} 
    #ax.set_xticks([0.0, 0.10, 0.20, 0.30, 0.40, 0.50, 0.60 ,0.70, 0.80, 0.90, 1]) 
    #ax.set_xticklabels(("0", "0.1", "0.2", "0.3", "0.4", "0.5", "0.6", "0.7","0.8","0.9","1"), fontdict=ticks_font_x)

    ticks_font_y = {'family' : 'Arial',  
                  'color'  : 'black',  
                  'weight' : 'medium',  
                  'size'   : 15.5}  
    #ax.set_yticks([0, 0.2, 0.4, 0.6, 0.8, 1.0])
    #ax.set_yticklabels(("0", "0.2", "0.4", "0.6", "0.8", "1.0"), fontdict=ticks_font_y)

    label_font_x = {'family' : 'Arial',  
                  'color'  : 'black',  
                  'weight' : 'medium',  
                  'size'   : 16.5}
    label_font_y = {'family' : 'Arial',  
                  'color'  : 'black',  
                  'weight' : 'medium',  
                  'size'   : 16.5} 
    
    plt.savefig(graph_name)
    plt.close()
    #plt.show()
def count_cpu_overflow(CPUconsum):
    count = 0
    for i in range(len(CPUconsum)):
        if CPUconsum[i] > 0.85:
            count+=1
    return count 

if __name__ == '__main__':
    phyData = read_csv_file()
    sfc_list = gen_SFC_list()
    sfc_list2 = copy.deepcopy(sfc_list)
    sfc_list3=copy.deepcopy(sfc_list)
    sfc_list4=copy.deepcopy(sfc_list)

    sfc_len_count=[0 for i in range(8)]
    for sfc in sfc_list:
        sfc_len_count[sfc.VNFnum]+=1

    ## get previous topo info
    caelus = DM(phyData=phyData,Refactory=1,Tdfactory=1,Migfactory=1.5,Linkfactory=1,migration_gate=0.7) 
    caelus.EM_init(sfc_list)
    caelusCPUconsum,caeluslinkConsum,caelusDelay=caelus.draw_cdf(figureName="caelus-EM")
    caelusCPUover = count_cpu_overflow(caelusCPUconsum)
    for i in range(90):
        caelus.migrate_EM_graph()
        caelus.check_sfc()
        caelus.modify_sfc()
    caelus.draw_cdf(figureName="caelus-DM")
    caelusLinkRe =  np.array(caelus.reroute_links_count[2:7]) / np.array(sfc_len_count[2:7])

    # ## get previous topo info
    # MMT = DM(phyData=phyData,Refactory=0.1,Tdfactory=1,Migfactory=10,Linkfactory=1,migration_gate=0.7) 
    # MMT.EM(sfc_list2)
    # MMTCPUconsum,MMTlinkConsum,MMTDelay=MMT.draw_cdf(figureName="MMT-EM")
    # MMTCPUover = count_cpu_overflow(MMTCPUconsum)
    # for i in range(90):
    #     MMT.migrate_EM_graph()
    #     MMT.check_sfc()
    #     MMT.modify_sfc()
    # MMT.draw_cdf(figureName="RO-DM")
    # MMTLinkRe =  np.array(MMT.reroute_links_count[2:7]) / np.array(sfc_len_count[2:7])

    # SOH = DM(phyData=phyData,Refactory=5,Tdfactory=5,Migfactory=1,Linkfactory=1,migration_gate=2) 
    # SOH.EM_GLL(sfc_list3)
    # SOHCPUconsum,GLLlinkConsum,GLLDelay=SOH.draw_cdf(figureName="SOH-EM")
    # SOHCPUover = count_cpu_overflow(SOHCPUconsum)
    # for i in range(90):
    #     SOH.migrate_EM_graph()
    #     SOH.check_sfc()
    #     SOH.modify_sfc()
    # SOH.draw_cdf(figureName="SOH-DM")
    # SOHLinkRe =  np.array(SOH.reroute_links_count[2:7]) / np.array(sfc_len_count[2:7])

    # SNH = DM(phyData=phyData,Refactory=1,Tdfactory=1,Migfactory=1,Linkfactory=1,migration_gate=2) 
    # SNH.EM_SNH(sfc_list4)
    # SNHCPUconsum,SNHlinkConsum,SNHDelay=SNH.draw_cdf(figureName="SNH-EM")
    # SNHCPUover = count_cpu_overflow(SNHCPUconsum)
    # for i in range(90):
    #     SNH.migrate_EM_graph()
    #     SNH.check_sfc()
    #     SNH.modify_sfc()
    # SNH.draw_cdf(figureName="SNH-DM")
    # SNHLinkRe =  np.array(SNH.reroute_links_count[2:7]) / np.array(sfc_len_count[2:7])

    #graph_raw,node_list_pre,sfc_list = EM_embeding(phyData=phyData)
    ## generate new topo
    #EM_graph_new,disconn_Links=dm.migrate_EM_graph(phyData,graph_raw,time_step=1)
    ## find the SFCs need to migration
    #sfc_mig = dm.check_sfc(sfc_list,disconn_Links)
    ## decide the migration method  
    #sfc_ins,logic_link_reroute,weight_graph = reroute_sfc(sfc_ins,EM_graph_new,reroute_links)

    ## for sfc in SFC_list 
    ## 1. rerouting  --- return cannot use rerouting 

    ## 2. replacement --- return cannot replacement

    ## 