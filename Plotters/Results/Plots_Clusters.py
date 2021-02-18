# -*- coding: utf-8 -*-
"""
Created on Fri Feb 4 2020


@Author: PouyaRZ

____________________________________________________
Plots to produce:
1. LCC of equipment for each scenario for all the individuals
2, SCC of equipment for each scenario for all the individuals

3. SCC vs LCC scatter plot.

4. SCC vs chiller type
5. SCC vs CHP type,
6. LCC vs chiller type
7. SCC vs CHP type

8. Traces of building types across all the runs
____________________________________________________

"""

import pandas as pd
import numpy as np
from matplotlib import pyplot as plt
from matplotlib import cm
from sklearn.cluster import KMeans as kmc
from sklearn import preprocessing as prpr
from sklearn.metrics import silhouette_score
from sklearn.cluster import DBSCAN, AgglomerativeClustering as agc, SpectralClustering as SC
from collections import Counter


def DF_Filter(filename):
    
    file = np.loadtxt(filename, dtype='float')
    
    inputDF = pd.DataFrame(file)
    
    error_tol = 1.15
    
#    print('GFA stats:')
#    print(inputDF.iloc[:,38].describe())
    print('+++++ processing %s +++++\n'%(filename))
    
    print('Count duplicates:')
    condition1 = inputDF.duplicated()==True
    print(inputDF[condition1][38].count())
    
    
    print('Count under the min GFA:') # Count non-trivial neighborhoods
    condition2 = inputDF[38] <= 1/error_tol#<=647497/10
    print(inputDF[condition2][38].count())
    
    
    print('Count over the max GFA:')
    condition3 = inputDF[38]>=647497*5*error_tol
    print(inputDF[condition3][38].count())
    
    
    print('Count over the max Site GFA:')
    condition4 = inputDF[38]/inputDF[36]>=647497*error_tol
    print(inputDF[condition4][38].count())
    
    
    print('Count valid answers:')
    print(len(inputDF) - inputDF[condition1 | condition2 | condition3 | condition4][38].count())
    
#    print('------------------')
    # Filtering the inadmissible results
    Filtered = ~(condition1 | condition2 | condition3 | condition4)
    inputDF = inputDF[Filtered]
    inputDF.reset_index(inplace=True, drop=True)
    
#    print('Annual energy demand stats (MWh):')
    inputDF[26] /= inputDF[38] # Normalizing LCC ($/m2)
    inputDF[27] /= inputDF[38] # Normalizing SCC ($/m2)
    inputDF[39] /= inputDF[38] # Normalizing CO2 (Tonnes/m2)
    inputDF[40] /= (10**3*inputDF[38]) # Normalizing total energy demand (MWh/m2)
    inputDF[41] /= inputDF[38] # Normalizing total wwater treatment demand (L/m2)
    for i in range(29,36): # Converting percent areas to integer %
        inputDF[i] = inputDF[i] * 100
#    print(inputDF[40].describe())
    
    return inputDF
    


### MAIN FUNCTION
print('loading data')
filenames = ['../RQ1_W_CWWTP_ModConsts_Feb17/SDO_LHS_TestRuns288_Constraint_SF_Test.txt',
                 '../RQ1_WO_CWWTP_ModConsts_Feb17/SDO_LHS_TestRuns288_Constraint_SF_Test.txt']
DFNames = ['CCHP|CWWTP','CCHP+WWT']
DFs = {}
for i in range(2):
    DFs[DFNames[i]] = DF_Filter(filenames[i])




plt.style.use('ggplot')
colors_rb = {DFNames[0]:'r', DFNames[1]:'b'}




######################## PLOTS ##########################
    


### Clustering the data points
# Plotting clustered building mixes, LCC, SCC, and annual energy and water uses
filteredCentroids = {}
filteredCentroidSize = {}
filteredCentroidSize_Nrm = {}
for DFName in DFNames:
    # Load the data
    #                             Bldg type ratios        LCC,SCC      Annual E, Annual WW
    DF = DFs[DFName].iloc[:, list(range(29,36))+list(range(26,28))+list(range(40,42))]
    
    
    # Plot the correlation matrix
    columns = ['Res','Off','Com','Ind','Hos','Med','Edu', 'LCC', 'SCC', 'Anl_E','Anl_WW']
    
    f = plt.figure(figsize=(10, 10))
    plt.matshow(DF.corr(), fignum=f.number, cmap = cm.get_cmap('seismic'),
                vmin=-1, vmax=1)
    plt.xticks(range(DF.shape[1]), columns, fontsize=14, rotation=45)
    plt.yticks(range(DF.shape[1]), columns, fontsize=14)
    cb = plt.colorbar()
    cb.ax.tick_params(labelsize=14)
    if DFName == 'CCHP|CWWTP':
        plt.savefig('correlation_matrix_disint.png', dpi=400, bbox_inches='tight')
    else:
        plt.savefig('correlation_matrix_int.png', dpi=400, bbox_inches='tight')
    
    
    
    # standardize data
    scaler = prpr.StandardScaler().fit(DF)
    # scaler.mean_
    # scaler.scale_
    DF_Scaled = scaler.transform(DF)
    # Forward transformation: e.g. (DF[29]-scaler.mean_[0])/scaler.scale_[0]
    
    # Clustering
    # silhouetteScore = {}
    # for n_clusters in range(8,41,2): 
    if DFName == 'CCHP|CWWTP':
        n_clusters = 26 # number of clusters:  26; Average silhouette score:  0.35865626368214515; score:  -105063.93616381194; Per individual score:  -1.1271745109302858
    else:
        n_clusters = 40 # number of clusters:  40; Average silhouette score:  0.30580379489266385; score:  -107026.40563157809; Per individual score:  -1.2211492587236787
    model = kmc(n_clusters=n_clusters, random_state=42, n_jobs=7)
    model.fit(DF_Scaled)
    centroids = model.cluster_centers_
    # print('Average silhouette score: ', silhouette_score(X=DF_Scaled, labels=model.labels_, random_state=42))
    score = model.score(DF_Scaled)
    print('score: ', score)
    print('Per individual score: ', score/len(DF_Scaled))
        
    descaled_centroids = (centroids*scaler.scale_ + scaler.mean_)
    
    
    counteredLabels = Counter(model.labels_)
    counteredLabels = dict(sorted(list(counteredLabels.items()), key=lambda item: item[1], reverse=True))
    print('Count of cluster instances: ', counteredLabels)
    cutoff_cluster_size = 500
    filteredCentroidList = [centroid for centroid in counteredLabels.keys() if counteredLabels[centroid] >= cutoff_cluster_size]
    filteredCentroidSize[DFName] = [counteredLabels[centroid] for centroid in counteredLabels.keys() if counteredLabels[centroid] >= cutoff_cluster_size]
    filteredCentroidSize_Nrm[DFName] = filteredCentroidSize[DFName] / np.max(filteredCentroidSize[DFName])
    print('number of centroids considered: ', len(filteredCentroidList))
    filteredCentroids[DFName] = descaled_centroids[filteredCentroidList,:]
    
    # Cacluate average silhouette score
    filter_for_DF = np.array([(label in filteredCentroidList) for label in model.labels_])
    print('Average filtered silhouette score: ', silhouette_score(X=DF_Scaled[filter_for_DF], labels=model.labels_[filter_for_DF], random_state=42))
    # print('Average silhouette score: ', silhouette_score(X=DF_Scaled, labels=model.labels_, random_state=42))

# Normalize LCC, SCC, Annual E, and Annual WW using the maximum values of both scenarios
ScaleFactor_LCC_SCC_Annual = np.concatenate((filteredCentroids[DFNames[0]], filteredCentroids[DFNames[1]]), axis=0)[:,7:].max(axis=0)/100
for DFName in DFNames:
    # Building trace plots
    filteredCentroids[DFName][:,7:] /= ScaleFactor_LCC_SCC_Annual
    fig = plt.figure(figsize=(10,5))
    ax = fig.add_subplot(111)
    Num_Individuals = len(filteredCentroids[DFName])
    cm = plt.get_cmap('rainbow')
    ax.set_prop_cycle(color=[cm(1.*i/Num_Individuals) for i in range(Num_Individuals)])
    for i in range(Num_Individuals):
        ax.plot(['Res','Off','Com','Ind','Hos','Med','Edu', 'LCC', 'SCC', 'Anl_E','Anl_WW'],
                filteredCentroids[DFName][i].transpose(), alpha=0.5,
                linewidth=(4*filteredCentroidSize_Nrm[DFName][i]+0.2), label='Cluster %d (Size: %d)'%(i, filteredCentroidSize[DFName][i]))
    # ax.set_xlabel('Building-Use')
    # ax.set_ylabel('Percent of Total GFA (%)')
    plt.ylim(-1, 101)
    if n_clusters < 20:
        plt.legend(bbox_to_anchor=(1.01, 1), loc=2, ncol=1, borderaxespad=0.)
    else:
        plt.legend(bbox_to_anchor=(1.01, 1), loc=2, ncol=2, borderaxespad=0.)
    if DFName == 'CCHP|CWWTP':
        fig.savefig('Cluster_Plot_Disinteg_%sCluster.png'%n_clusters, dpi=400, bbox_inches='tight')
    else:
        fig.savefig('Cluster_Plot_Integ_%sCluster.png'%n_clusters, dpi=400, bbox_inches='tight')
