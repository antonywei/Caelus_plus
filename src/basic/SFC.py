class SFC:
    sfcCount = 0
    def __init__(self, sfc_id, src, dst, vnf_list, bw, td):
        ## a SFC consists of K VNFs and K+1 logic links
        ## VNF ID : 1...K Link ID 0...K
        ## logic_link_id k is used to connect k'th (k+1)'th VNF 
        #link 0 connect src to VNF1, link k connect VNF k and dist
        self.id = sfc_id
        self.src = src
        self.dst = dst
        self.vnfList = vnf_list ### vnfList = {"VNF_id":[type,cpu_consum]} eg. {1:(1,10),2:(2,20)}
        self.bw = bw
        self.td = td
        self.VNFnum = len(self.vnfList) 
        SFC.sfcCount += 1
        self.nodesMap = {i:None for i in range(1,(self.VNFnum)+1)}
        self.linkMap = {i:[] for i in range((self.VNFnum)+1)}

        self.linkMap[0].append(src)
        self.linkMap[self.VNFnum].append(dst)

    def displaySFC(self):
        print("******* the info of SFC request "+str(self.id)+" is ************")
        Dict = [{"id":self.id},{"src":self.src},{"dst":self.dst},\
               {"vnfList":self.vnfList},{"bw":self.bw},{"td":self.td}, \
               {"Nodes_Map":self.nodesMap},{"linkMap":self.linkMap}]
        print(Dict)
    def Mapping_VNF(self,vnf_id,nodes):
        self.nodesMap[vnf_id] = nodes
    def Mapping_Link(self,logic_link_id,phy_links):
        ## connect_logic_nodes 2-tuple (in,out)
        ## logic_link_id k is used to connect k'th (k+1)'th VNF 
        ## link 0 connect src to VNF1, link k connect VNF k and dist
        ## phy_links a list of physical links
        self.linkMap[logic_link_id] = phy_links
    def Find_Links(self,phy_link_id):
        result = []
        for key in self.linkMap:
            if phy_link_id in linkMap[key]:
                result.append(key)
        return result



#a = SFC(SFC_id=1, src=2, dst=3, vnfList={1:(1,10),2:(2,20)}, bw=2, td=10)