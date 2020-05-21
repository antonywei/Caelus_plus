from EMfilter import *


def migrate_EM_graph(phyData,EM_graph_pre,time_step):
    EM_graph_new = create_EM_graph(phyData,time_step)
    disconn_Links = set()
    for i in EM_graph_pre:
        for j in EM_graph_pre[i]:
            if j not in EM_graph_new[i].keys():
                disconn_Links.add(i+j)
    return EM_graph_new,disconn_Links

Map = read_csv_file()
EM_graph = create_EM_graph(Map,0)
EM_graph_new,disconn_Links = migrate_EM_graph(Map,EM_graph,1)