## transfer neigh map to info map at t
from SSFChead import *
from basic.SFC import SFC
import matplotlib as plt
from basic.globalvar import *
def read_csv_file(filename=filename):
    with open(filename) as load_f:
        mapData = json.load(load_f)
    return mapData
def compare_links(mapData,time_step):
    pass

def create_EM_graph(phyData,time_step,EM_graph_pre={}):
    ## transfer phy graphs to EM graphs
    EM_graph = {}
    T = len(phyData)
    if EM_graph_pre == {}:
        for nodes in phyData[str(time_step)].keys():
            EM_graph[int(nodes)]={}
            for conn_nodes in phyData[str(time_step)][nodes].keys():
                EM_graph[int(nodes)][int(conn_nodes)]=[round(phyData[str(time_step)][nodes][conn_nodes][0]/(3*10**5)),0,maxBW]
                for i in range(T):
                    timeIndex = str((i + time_step)%T)
                    if conn_nodes in phyData[timeIndex][nodes].keys():
                        EM_graph[int(nodes)][int(conn_nodes)][1] +=1
                    else:
                        continue
    else:
        for nodes in phyData[str(time_step)].keys():
            EM_graph[int(nodes)]={}
            for conn_nodes in phyData[str(time_step)][nodes].keys():
                if int(conn_nodes) not in EM_graph_pre[int(nodes)]:
                    EM_graph[int(nodes)][int(conn_nodes)]=[round(phyData[str(time_step)][nodes][conn_nodes][0]/(3*10**5)),0,maxBW]
                    for i in range(T):
                        timeIndex = str((i + time_step)%T)
                        if conn_nodes in phyData[timeIndex][nodes].keys():
                            EM_graph[int(nodes)][int(conn_nodes)][1] +=1
                        else:
                            continue
                else:
                    EM_graph[int(nodes)][int(conn_nodes)]=EM_graph_pre[int(nodes)][int(conn_nodes)]
    return EM_graph



# def cal_EM_graph_delay(EM_graph):
#     for i in EM_graph:
#         for j in EM_graph[i]:
#             EM_graph[i][j][0] = round(EM_graph[i][j][0]/(3*10**5))
#     return EM_graph

    ### init EM graph  with delay the connection info {node_id:{node_id_conn:[td,conn]}}

    ### init node_list according to EM graph

    ### add resource info {node_id:{node_id_conn:[td,conn,bw]}}

    ### return EM graph with Nodes and Links


#a = SFC(sfc_id=1, src=2, dst=3, vnf_list={1:(1,10),2:(2,20)}, bw=2, td=10)
#Map = read_csv_file()
#EM_graph = create_EM_graph(Map,0)
