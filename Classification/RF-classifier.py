# -*- coding: utf-8 -*-
"""
Created on Fri Aug  3 11:34:02 2018

@author: P. Balamurugan
"""


#The code is suitable for multi-processing
#the following code is for Random Forest Classifier with k-fold cv for 100 different seed values and reports the average rmse along with standard deviation
#This code works on only pure data (without added synthetic data).  


import numpy as np
from sklearn.preprocessing import normalize #normalize is not used in the code, but can be tried
from sklearn.utils import shuffle 
import math 
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import f1_score
from sklearn import metrics

import concurrent.futures
import time
import csv

global num_features
global crossvalidate_k 

global test_sample_index_list 

global seeds
global num_estimators_values
global splitpoints

global seed_numest_pair_arr

global seed_start
global seed_step
global final_seed
global best_est 


test_sample_index_list = []
train_pure_synthetic_index_list = []
splitpoints = []

crossvalidate_k = 5 #number of folds for cross-validation

mydata = np.genfromtxt('classification_data.csv', delimiter=',')
num_features = len(mydata[0])-1

features = mydata[:,0:num_features]
output = mydata[:,num_features:]

norm_features = features



#print(norm_features)
#print(mydata)

num_samples = len(mydata)
#print(num_samples)


seed_start = 0
seed_end = 10000 #This is based on number of seeds 
seed_step = 100



seeds = np.arange(seed_start,seed_end,seed_step) 
final_seed = (seeds[len(seeds)-1])

test_scores = np.zeros(len(seeds)) 
train_scores = np.zeros(len(seeds))

best_est = 0*np.arange(0,len(seeds),1)

num_estimators_values = np.arange(100,2100,100) 

seed_numest_pair = []

for seed in seeds:
    for num_est in num_estimators_values:
        seed_numest_pair.append([seed,num_est])

#print(seed_numest_pair)
seed_numest_pair_arr = np.array(seed_numest_pair)
#print(seed_numest_pair_arr[:,1])



estind_values = np.arange(len(num_estimators_values))

seed_indices = np.arange(len(seeds))

#print(num_estimators_values)
#print(estind_values)

#print(seeds)
#print(seed_indices)



def kfoldcv(seed,numest):
    start = time.time()
    
    np.random.seed(seed)
    
    sample_index = np.arange(num_samples)
    #print(sampleindex)

    shuffled_indices = shuffle(sample_index)
    #print(shuffled_indices)
    
    test_proportion = 0.2  #set the proportion of test samples 
    num_test = int(test_proportion * num_samples) 
    #print(num_test)

    test_sample_index = shuffled_indices[:num_test]
    
    test_sample_index_list.append(test_sample_index)
    #print(test_sample_index)
    #print(len(test_sample_index))

    #split the remaining part into ten folds 
    train_validate_index = shuffled_indices[num_test:]
    #num_train_validate_samples = len(train_validate_index)
    #print(num_train_validate_samples)
    
    
    #print ('starting kfoldcv')
    num_estimators_arg = numest

    
    
    fold_length = int(math.ceil((1.0*len(train_validate_index))/crossvalidate_k))
    splitpoints = np.arange(0,len(train_validate_index),fold_length)
    
    scores = np.zeros(crossvalidate_k) 
    for i in np.arange(len(splitpoints)):
        #print(i)
        if i<len(splitpoints)-1:
            validate_index = train_validate_index[splitpoints[i]:splitpoints[i+1]]
        else:
            validate_index = train_validate_index[splitpoints[i]:]
        train_index = [x for x in train_validate_index if x not in validate_index]
        #print(validate_index)
        #print(len(validate_index))
        #print(train_index)
        #print(len(train_index))
        #print('**************************')


        train_feat = norm_features[train_index]
        train_feat = [np.reshape(x, (num_features, )) for x in train_feat]

        train_out = output[train_index]
        train_out = np.reshape(train_out, (len(train_out),))
        #print(train_data)

        #print('train')
        #print(i,np.shape(train_feat), np.shape(train_out))

        validate_feat = norm_features[validate_index]
        validate_feat = [np.reshape(x, (num_features, )) for x in validate_feat]

        validate_out = output[validate_index]
        validate_out = np.reshape(validate_out, (len(validate_out),))
        #print(train_data)

        #print('validate')
        #print(i,np.shape(validate_feat), np.shape(validate_out))

        #print(len(validate_samples))

 
        clf = RandomForestClassifier(bootstrap=True, criterion='gini', max_depth=10000,
                                     max_features=50, max_leaf_nodes=None,
                                     min_impurity_decrease=0.0, min_impurity_split=None,
                                     min_samples_leaf=1, min_samples_split=2,
                                     min_weight_fraction_leaf=0.0, n_estimators=num_estimators_arg, n_jobs=1,
                                     oob_score=False, random_state=42, verbose=0, warm_start=False)

        clf.fit(train_feat, train_out)
        #print(clf.feature_importances_)

        #pred = clf.predict(train_feat)
        #tmp = ((x,y) for x,y in zip(pred, train_out))
        #print(list(tmp))


        pred = clf.predict(validate_feat)
        #tmp = ((x,y) for x,y in zip(pred, validate_out))
        #print(list(tmp))

        score = metrics.accuracy_score(validate_out, pred)
	#mse = sum((x-y)*(x-y) for x,y in zip(pred,validate_out))/len(validate_feat)
        #rmse = np.sqrt(mse)

        #print(i,rmse)
        #print('^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^')

        scores[i] = score

        #if i==len(splitpoints)-1:
            #print(train_feat)
            #print(train_out)
            #print(validate_out)
        #print(rmses)
    avg_score = np.average(scores)
        
    return seed,numest,time.time() - start,avg_score


def compute_testscore(seed,best_numest):
    start = time.time()
    
    np.random.seed(seed)
    
    sample_index = np.arange(num_samples)
    #print(sampleindex)

    shuffled_indices = shuffle(sample_index)
    #print(shuffled_indices)
    
    test_proportion = 0.2  #set the proportion of test samples 
    num_test = int(test_proportion * num_samples) 
    #print(num_test)

    test_sample_index = shuffled_indices[:num_test]
    
    test_sample_index_list.append(test_sample_index)
    #print(test_sample_index)
    #print(len(test_sample_index))

    #split the remaining part into ten folds 
    train_validate_index = shuffled_indices[num_test:]
    #num_train_validate_samples = len(train_validate_index)
    #print(num_train_validate_samples)
    
    #training set 
    final_train_feat = norm_features[train_validate_index]
    final_train_feat = [np.reshape(x, (num_features, )) for x in final_train_feat]

    final_train_out = output[train_validate_index]
    final_train_out = np.reshape(final_train_out, (len(final_train_out),))

    #test set 
    final_test_feat = norm_features[test_sample_index]
    final_test_feat = [np.reshape(x, (num_features, )) for x in final_test_feat]

    final_test_out = output[test_sample_index]
    final_test_out = np.reshape(final_test_out, (len(final_test_out),))


    final_best_estimator = int(best_numest)
    final_clf = RandomForestClassifier(bootstrap=True, criterion='gini', max_depth=10000,
               max_features=50, max_leaf_nodes=int(math.sqrt(len(final_train_feat[0]))),
               min_impurity_decrease=0.0, min_impurity_split=None,
               min_samples_leaf=1, min_samples_split=2,
               min_weight_fraction_leaf=0.0, n_estimators=final_best_estimator, n_jobs=1,
               oob_score=False, random_state=42, verbose=0, warm_start=False)

    final_clf.fit(final_train_feat, final_train_out)
    

    tr_pred = final_clf.predict(final_train_feat)
    final_tr_score = metrics.accuracy_score(final_train_out, tr_pred)
    #final_tr_mse = sum((x-y)*(x-y) for x,y in zip(tr_pred,final_train_out))/len(final_train_feat)
    #final_tr_rmse = np.sqrt(final_tr_mse)

    #tmp = ((x,y) for x,y in zip(pred, train_out))
    #print(list(tmp))

    #pred = final_clf.predict()
    pred = final_clf.predict(final_test_feat)
    #tmp = ((x,y) for x,y in zip(pred, final_test_out))
    #print(list(tmp))
    
    
    final_score = metrics.accuracy_score(final_test_out, pred)
    #final_mse = sum((x-y)*(x-y) for x,y in zip(pred,final_test_out))/len(final_test_feat)
    #final_rmse = np.sqrt(final_mse)

    return seed,best_numest,time.time() - start, final_score, final_tr_score



def main():
    avg_score_ret = []
    numest_ret = [] 
    
    for seed in seeds: 
        avg_score_ret.append([])
        numest_ret.append([])    
    
    start = time.time()
    with concurrent.futures.ProcessPoolExecutor() as executor:
         for seed,numest,time_ret,avg_score in executor.map(kfoldcv, seed_numest_pair_arr[:,0],seed_numest_pair_arr[:,1]):
             seed_index = int((seed-seed_start)/seed_step)
             avg_score_ret[seed_index].append(avg_score)
             numest_ret[seed_index].append(numest)
             print('seed:%f numest: %f time: %f avg_score: %f' %(seed, numest,time_ret,avg_score), flush=True)
    print('k fold cv completed ! Time taken: %f seconds' %(time.time()-start), flush=True )

    
    for seed in seeds: 
        seed_index = int((seed-seed_start)/seed_step)
        tmp = avg_score_ret[seed_index]
        #print(tmp)
        estlist = numest_ret[seed_index]
        #print(estlist)
        best_est[seed_index]= int(estlist[np.argmax(tmp)])
        
        print('seed:%d argmin numest: %d' %(seed,best_est[seed_index]), flush=True)

    #print(best_est)

    start = time.time()        
    with concurrent.futures.ProcessPoolExecutor() as executor:
         for seed,bestest,time_ret,test_score,train_score in executor.map(compute_testscore, seeds, best_est):
             print('seed:%f bestest:%f time: %f test_score: %f train score: %f' %(seed,bestest,time_ret,test_score, train_score), flush=True)
             seed_index = int((seed-seed_start)/seed_step)
             test_scores[seed_index]=test_score
             train_scores[seed_index]=train_score
    print('Test score computed ! Time taken: %f seconds' %(time.time()-start), flush=True )

    print('Test score: mean+/-std.dev of %d runs: %f +/- %f' %(len(seeds),np.average(test_scores), np.std(test_scores)) , flush=True)
    print('Train score: mean+/-std.dev of %d runs: %f +/- %f' %(len(seeds),np.average(train_scores), np.std(train_scores)) , flush=True)
    

if __name__ == '__main__':
    start = time.time()
    main()
    total_time = time.time() - start

    print('total time after completion: %f seconds' %(total_time), flush=True)



