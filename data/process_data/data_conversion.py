## using to converse data from .e to .csv
import pandas as pd 
import numpy as np 
file_head="../raw_data/Satellite1"
for orbit in range(1,7):
    for s in range(1,11):
        if s != 10:
            tempS = str(0)+str(s)
        else:
            tempS = str(10)
        file = file_head + str(orbit)+str(tempS)+".e"
        f = open(file,'r')
        result = []
        flag = False
        for line in open(file):
            line = f.readline()
            line = line.split()
            if line != []:
                if line[0] == "EphemerisTimePosVel":
                    flag=True
                    continue
                if line[0] == "END":
                    flag=False
                    break
            if flag == True and line !=[]:
                result.append(line)
        f.close()
        res=np.array(result)
        name = ['time','x','y','z']
        wt = pd.DataFrame(columns=name,data=res[:,0:4])
        filename= "../csv_data/MyStar"+str(orbit-1)+str(s-1)+".csv"
        wt.to_csv(filename)