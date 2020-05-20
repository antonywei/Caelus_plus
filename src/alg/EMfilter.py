## transfer neigh map to info map at t
from SSFChead import *

def read_csv_file(filename=filename):
    with open(filename) as load_f:
        mapData = json.load(load_f)
    return mapData
def compare_links(mapData,time_step):
    pass

def create_EM_graph(phyData,time_step):
    ## transfer phy graphs to EM graphs
    EM_graph = phyData[str(time_step)]
    T = len(phyData)
    for nodes in EM_graph.keys():
        for conn_nodes in EM_graph[nodes]:
            EM_graph[nodes][conn_nodes].append(0)
            for i in range(T):
                timeIndex = str((i + time_step)%T)
                if conn_nodes in phyData[timeIndex][nodes].keys():
                    EM_graph[nodes][conn_nodes][1] +=1
                else:
                    continue
    EM_graph = cal_EM_graph_delay(EM_graph)
    return EM_graph


def cal_EM_graph_delay(EM_graph):
    for i in EM_graph:
        for j in EM_graph[i]:
            EM_graph[i][j][0] = round(EM_graph[i][j][0]/(3*10**5))
    return EM_graph



def find_least_cost_path(src,dst):
    pass


#Map = read_csv_file()
#EM_graph = create_EM_graph(Map,0)
