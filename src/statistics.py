from typing import List, Dict

import pydotplus as pydotplus
from sklearn import tree,preprocessing
import numpy as np

from src.build import Build
from src.testie import Run, Testie, Dataset
from orderedset import OrderedSet

class Statistics:
    @staticmethod
    def run(build:Build, all_results:Dataset, testie:Testie,max_depth=3):
        print("Building dataset...")
        X,y = Statistics.buildDataset(all_results,testie)
        print("Learning dataset built with %d samples and %d features..." % (X.shape[0],X.shape[1]))
        clf = tree.DecisionTreeRegressor(max_depth=max_depth)
        clf = clf.fit(X,y)

        if max_depth is None or max_depth > 8:
            print("No tree graph when maxdepth is > 8")
        else:
            dot_data = tree.export_graphviz(clf, out_file=None, filled=True,rounded=True,special_characters=True,
                                        feature_names=testie.variables.dtype()['names'])
            graph = pydotplus.graph_from_dot_data(dot_data)
            f = build.result_path(testie,'pdf',suffix='_clf')
            graph.write_pdf(f)
            print("Decision tree visualization written to %s" % f)

        print("Feature importances :")
        for key,f in zip(testie.variables.dtype()['names'],clf.feature_importances_):
            print("  %s : %0.2f" % (key,f))


        vars_values = {}
        for run,results in all_results.items():
            for k,v in run.variables.items():
                vars_values.setdefault(k,set()).add(v)

        print("Better :")
        print("  %s" % str(X([y.argmax()])))

        print("Means and std per variables :")
        for k,vals in vars_values.items():
            print("%s :" % k)
            print("  ",end='')
            for v in vals:
                tot = 0
                std = 0
                n = 0
                for run,results in all_results.items():
                    if run.variables[k] == v:
                        tot+=np.mean(results)
                        std+=np.std(results)
                        n+=1
                print("%s : (%0.2f,%0.2f), " % (v,tot/n,std/n),end='')
            print("")

    @classmethod
    def buildDataset(cls, all_results:Dataset, testie:Testie):
        dtype = testie.variables.dtype()
        y=[]
        dataset = []
        for i,(run,results) in enumerate(all_results.items()):
            vars = list(run.variables.values())
            dataset.append(vars)
            y.append(np.mean(results))
        dtype['formats'] = dtype['formats']
        dtype['names'] = dtype['names']

        for i,f in enumerate(dtype['formats']):
            if f is str:
                dtype['formats'][i] = int
                values = OrderedSet()
                for row in dataset:
                    values.add(row[i])
                    row[i] = values.index(row[i])
        X = np.array(dataset,ndmin=2)
        return X,np.array(y,dtype=[('result',float)])
