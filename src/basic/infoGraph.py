### info graph 
### change info graph to weight graph
NodeInfo={
    {"nodeNum":1,"info":{"capResource":20,"usedResource":0,"connectEdged":[1,2]}}
}
edgeInfo={
    {"edgeNum":1,"info":{"connectNode":[1,2],"capResource":20,"usedResource":0,\
                         "delay":10,"varDelay":0.2}}
}

class infoGraph
    def __init__(self,NodeInfo=NodeInfo,edgeInfo=edgeInfo):
        self.NodeInfo=NodeInfo
        self.edgeInfo=edgeInfo
    def calWeightNode(self):
        {"nodeNum":1,"weight":2}
        pass

    def calWeighEdge(self):
        pass
    
    def find_shortest_path(self,start,end,path=[]):
        return path
