"""선택: 상속 파이프라인과 데이터 크기별 Train/Validation 학습곡선."""
from pathlib import Path
import json
import numpy as np
import pandas as pd
from sklearn.model_selection import learning_curve, StratifiedKFold
from workflow import FinanceWorkflow, FEATURES, classification_metrics
from bonus import BonusWorkflow
from experiment import ROOT, save_figure
import matplotlib.pyplot as plt

def run_bonus():
    """기본과 같은 Train/Test, learning_curve도 오직 Train 내부 5-fold."""
    frame=pd.read_csv(ROOT/"finance_data.csv")
    train,test=FinanceWorkflow().split(frame)
    model=BonusWorkflow().classifier().fit(train[FEATURES],train.is_overdue)
    scores=model.predict_proba(test[FEATURES])[:,1]
    result=dict(derived_features=["income_per_card","debt_overdue"],
                classifier=classification_metrics(test.is_overdue,(scores>=.5).astype(int),scores),
                parent="FinanceWorkflow",test_reused_only_for_final_reporting=True)
    folds=StratifiedKFold(n_splits=5,shuffle=True,random_state=42)
    sizes,training,validation=learning_curve(model,train[FEATURES],train.is_overdue,cv=folds,
                                             train_sizes=[.1,.25,.5,.75,1],scoring="f1",n_jobs=1,
                                             shuffle=True,random_state=42)
    result["learning_curve"]=dict(scope="only original Train; internal Validation",sizes=sizes.tolist(),
                                  train_mean=training.mean(axis=1).tolist(),validation_mean=validation.mean(axis=1).tolist(),
                                  train_std=training.std(axis=1).tolist(),validation_std=validation.std(axis=1).tolist(),
                                  train_folds=training.tolist(),validation_folds=validation.tolist())
    figure,axis=plt.subplots(figsize=(8,5))
    for values,name,color in [(training,"Train","#14213d"),(validation,"Validation","#a67c20")]:
        mean,std=values.mean(axis=1),values.std(axis=1)
        axis.plot(sizes,mean,"o-",label=name,color=color)
        axis.fill_between(sizes,mean-std,mean+std,alpha=.12,color=color)
    axis.set(xlabel="Rows in each internal Train fold",ylabel="Overdue positive F1",title="Bonus: 5-fold Train-only learning curve")
    axis.legend();save_figure(figure,"learning_curve.png")
    (ROOT/"reports/bonus.json").write_text(json.dumps(result,ensure_ascii=False,indent=2))
    print(json.dumps(result,ensure_ascii=False,indent=2))
    return result

if __name__ == "__main__":
    run_bonus()
