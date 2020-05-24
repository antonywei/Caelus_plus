import numpy as np 
import pandas as pd
import matplotlib as plt
import heapq
import sys 
ORBIT_SIZE = 6
PLANE_NUM = 10
CONNECT_SATE=2 ## except the neighbor 
def read_csv_file(orbit,s):
    filename= "../csv_data/MyStar"+str(orbit)+str(s)+".csv"
    df = pd.read_csv(filename,skiprows=0)
    point = np.array([df['x'],df['y'],df['z']])
    return point.T
## using to cal distance 
distance_Matrix = dict()
for orbit1 in range(ORBIT_SIZE):
    for s1 in range(PLANE_NUM):
        distance_Matrix[str(orbit1)+str(s1)] = {}
        for orbit2 in range(ORBIT_SIZE):
            for s2 in range(PLANE_NUM):
                df1 = read_csv_file(orbit1,s1)
                df2 = read_csv_file(orbit2,s2)
                node_dis = np.sqrt(np.sum((df1-df2)**2,axis=1,keepdims=True))
                distance_Matrix[str(orbit1)+str(s1)][str(orbit2)+str(s2)] = node_dis

time_len = len(distance_Matrix['00']['00'])
distance_DIC = dict()
###  using to find the connect satellite 
for timestep in range(time_len):
    neigh_map = {}
    for orbit1 in range(ORBIT_SIZE):
        for s1 in range(PLANE_NUM):
            #### add 2 same orbit Nodes
            sameOrbitNode1 = (s1 + 9)%10
            sameOrbitNode2 = (s1 + 1)%10
            neigh_map[str(orbit1)+str(s1)]=distance_Matrix[str(orbit1)+str(sameOrbitNode1)][str(orbit1)+str(sameOrbitNode2)][timestep]
            neigh_map[str(orbit1)+str(s1)]=distance_Matrix[str(orbit1)+str(sameOrbitNode1)][str(orbit1)+str(sameOrbitNode2)][timestep]

            minK = [-sys.maxsize]*CONNECT_SATE
            minDIC = {}
            distance_M = {}
            ### iteration to calculate distance for satellite[orbit1 s1]
            for orbit2 in range(ORBIT_SIZE):
                for s2 in range(PLANE_NUM):
                    distance_M[str(orbit2)+str(s2)] = distance_Matrix[str(orbit1)+str(s1)][str(orbit2)+str(s2)][timestep]
            ## pop the same orbit satellites
            minDIC[str(orbit1)+str(sameOrbitNode1)]=distance_M.pop(str(orbit1)+str(sameOrbitNode1))
            minDIC[str(orbit1)+str(sameOrbitNode2)]=distance_M.pop(str(orbit1)+str(sameOrbitNode2))
            ## find CONNECT_SATE nearlest Nodes
            for i in range(CONNECT_SATE+1):
                index = min(distance_M,key=distance_M.get)
                minDIC[index] = distance_M.pop(index)
            neigh_map[str(orbit1)+str(s1)] = minDIC
    distance_DIC[timestep] = neigh_map

for timestep in distance_DIC:
    for s1 in distance_DIC[timestep]:
        for s2 in distance_DIC[timestep][s1]:
            distance_DIC[timestep][s2][s1] = distance_DIC[timestep][s1][s2]


frame = pd.DataFrame(distance_DIC)
frame.to_json('neigh_map_timestep.json')




