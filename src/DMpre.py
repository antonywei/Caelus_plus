from EM import *
from basic.globalvar import *
class DM(object):
    def __init__(self,phyData):
        self.reroute_links={} ## {time step:{sfc_id:{logic_link_id:[new links]},{}}

        self.reroute_links_count=0

        self.migration_SFC={} ## {time step:{sfc_id:{vnf_id},{}}
        self.phyData=phyData
        self.EM_graph={}
        self.time_step=0
        self.node_list_status={}
        self.sfc_list_status={}
        self.disconnect_Links={}
        self.disconn_logic_links={} ## {time step:{sfc_id:[logic_link_id],{}}
    def EM(self,sfc_list):
        self.EM_graph[0],self.node_list_status,self.sfc_list_status=EM_embeding(phyData=phyData,sfc_list=sfc_list)
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


    def modify_sfc(self):
        ### jugdement sfc need to migration or rerouting
        #sfc_reroute={}
        #sfc_migration=
        self.reroute_links[self.time_step] = {}
        for sfc_id in self.disconn_logic_links[self.time_step].keys():
            if len(self.disconn_logic_links[self.time_step][sfc_id]) < round((self.sfc_list_status[sfc_id].VNFnum)*migration_gate):
                ### release old links only in EM_graph not in SFC_LIST
                self.release_SFC_links(sfc_id=sfc_id)
                self.reroute_links[self.time_step][sfc_id] = self.reroute_sfc(sfc_id)
            ### reroute sfc
            else:
                print("SFC need migration")
                #self.sfc_list_status[sfc],modify_info=migration_sfc(self.sfc_list_status[sfc],EM_graph_new,sfc_mig[sfc])
                #sfc_reroute[sfc]=len(disconn_logic_links[sfc])
            ### migration sfc
            self.reroute_links_count+=1

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
            weight_graph = cal_links_weight(sfc_ins,self.EM_graph[self.time_step])
            ### calculate the embeding cost matrix
            distance_from_src,preNode_src = findShortestPath(vnf_src,weight_graph)
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
        return logic_link_reroute
    #def release_links(self,EM_graph,reroute_links):




if __name__ == '__main__':
    phyData = read_csv_file()
    sfc_list = gen_SFC_list()
    ## get previous topo info
    dm = DM(phyData) 
    dm.EM(sfc_list)
    for i in range(90):
        dm.migrate_EM_graph()
        dm.check_sfc()
        dm.modify_sfc()


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