"""PDF의 모든 기본 실험을 고정 Train/Test에서 실행하고 수치/그림을 저장."""
from pathlib import Path
import hashlib
import json
import os
os.environ.setdefault("MPLCONFIGDIR", str(Path(__file__).parent/".cache/matplotlib"))
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from sklearn.model_selection import KFold, cross_val_score
from sklearn.metrics import roc_curve
from data_gen import generate_data
from baseline import RuleBaseline
from workflow import FinanceWorkflow, FEATURES, ALPHAS, classification_metrics, regression_metrics

ROOT = Path(__file__).resolve().parent
COLORS = ["#14213d", "#a67c20", "#475569", "#5e7a9b", "#7c8f6f", "#9c6b50"]

def save_figure(figure, name):
    """실측 그래프를 reports/에 저장하고 Figure 메모리를 해제한다."""
    figure.tight_layout()
    figure.savefig(ROOT/"reports"/name, dpi=150, facecolor="#f3f5f7")
    plt.close(figure)

def run_experiment():
    """5-fold는 Train 안에서만; 정답 타겟 둘 다 feature에서 제거한다."""
    (ROOT/"reports").mkdir(exist_ok=True)
    path = ROOT/"finance_data.csv"
    if not path.exists():
        generate_data(path)
    frame = pd.read_csv(path)
    # 수정된 외부 CSV가 조용히 학습되지 않도록 제공 생성기의 원본과 비교한다.
    pd.testing.assert_frame_equal(frame, generate_data())
    workflow = FinanceWorkflow()
    train, test = workflow.split(frame)
    xtrain, xtest = train[FEATURES], test[FEATURES]
    ytrain, ytest = train.is_overdue, test.is_overdue
    result = dict(data=dict(shape=list(frame.shape),sha256=hashlib.sha256(path.read_bytes()).hexdigest(),
                            positive_rate=float(frame.is_overdue.mean()),features=FEATURES,
                            source="PDF exact synthetic generator",external_data=False),
                  split=dict(random_state=42,train_size=len(train),test_size=len(test),
                             train_ids=train.index.tolist(),test_ids=test.index.tolist(),
                             train_positive=int(ytrain.sum()),test_positive=int(ytest.sum())),
                  preprocessing=dict(numeric=FEATURES,categorical=[],imputer="median",scaler="StandardScaler",
                                     fit_scope="Train only; inside each CV fold",target_columns_excluded=True),
                  regression={},classification={})
    folds = KFold(n_splits=5,shuffle=True,random_state=42)
    figure, axes = plt.subplots(1,2,figsize=(14,5))
    for axis, method in zip(axes,["ridge","lasso"]):
        rows = []
        for alpha in ALPHAS:
            model = workflow.regression(method,alpha)
            cv = -cross_val_score(model,xtrain,train.credit_score,cv=folds,
                                  scoring="neg_root_mean_squared_error",n_jobs=1)
            model.fit(xtrain,train.credit_score)
            predictions = workflow.predict_credit(model,xtest)
            rows.append(dict(alpha=alpha,cv_rmse=float(cv.mean()),cv_rmse_folds=cv.tolist(),
                             coefficients=model.named_steps["model"].coef_.tolist(),
                             intercept=float(model.named_steps["model"].intercept_),
                             **regression_metrics(test.credit_score,predictions)))
        best = min(rows,key=lambda row:row["cv_rmse"])
        result["regression"][method]=dict(selected_alpha=best["alpha"],selection="minimum Train CV RMSE",
                                         rows=rows,selected_test={key:best[key] for key in ["rmse","mae","r2"]})
        for index, feature in enumerate(FEATURES):
            axis.plot(ALPHAS,[row["coefficients"][index] for row in rows],marker="o",label=feature,color=COLORS[index])
        axis.set_xscale("log");axis.set_xlabel("alpha (log scale)");axis.set_ylabel("standardized feature coefficient")
        axis.set_title(f"{method.title()}: selected alpha={best['alpha']} by Train CV")
        axis.axhline(0,color="#b8c2cf",linewidth=.8);axis.legend(fontsize=8);axis.grid(alpha=.15)
    save_figure(figure,"regularization.png")
    rule = RuleBaseline().predict(xtest)
    result["classification"]["Rule baseline"]=classification_metrics(ytest,rule,rule)
    result["classification"]["Rule baseline"]["score_type"]="binary flag, not calibrated probability"
    logistic = workflow.classifier().fit(xtrain,ytrain)
    search = workflow.ensemble_search().fit(xtrain,ytrain)
    result["grid_search"]=dict(best_params=search.best_params_,best_cv_f1=float(search.best_score_),
                              combinations=len(search.cv_results_["params"]),folds=5,selection_scope="Train only",
                              candidates=[dict(params=params,mean_f1=float(score),std_f1=float(std)) for params,score,std in
                                          zip(search.cv_results_["params"],search.cv_results_["mean_test_score"],search.cv_results_["std_test_score"])])
    scores = {"Rule baseline":rule}
    for name, model in [("Balanced Logistic",logistic),("Tuned Random Forest",search.best_estimator_)]:
        probability = model.predict_proba(xtest)[:,1]
        prediction = (probability>=0.5).astype(int)
        result["classification"][name]=classification_metrics(ytest,prediction,probability)
        result["classification"][name]["threshold"]=0.5
        scores[name]=probability
    weights = logistic.named_steps["model"].class_weight
    result["class_balance"] = dict(method=weights,formula="n_train / (2 * n_class)",
                                   weights={str(c):len(train)/(2*int((ytrain==c).sum())) for c in [0,1]},
                                   smote_used=False)
    figure, axis = plt.subplots(figsize=(7,5))
    for (name,score),color in zip(scores.items(),COLORS):
        fpr,tpr,thresholds=roc_curve(ytest,score)
        axis.plot(fpr,tpr,label=f"{name}: AUC={result['classification'][name]['auc']:.4f}",color=color)
        result["classification"][name]["roc"]=dict(fpr=fpr.tolist(),tpr=tpr.tolist())
    axis.plot([0,1],[0,1],"--",color="#b8c2cf",label="chance")
    axis.set(xlabel="False Positive Rate",ylabel="True Positive Rate",title="Same 2,000-customer Test ROC")
    axis.legend();save_figure(figure,"roc_auc.png")
    figure,axes=plt.subplots(1,3,figsize=(14,4))
    for axis,(name,row) in zip(axes,result["classification"].items()):
        matrix=np.array(row["confusion_matrix"])
        axis.imshow(matrix,cmap="Blues")
        for i in range(2):
            for j in range(2):
                axis.text(j,i,str(matrix[i,j]),ha="center",va="center",color="white" if matrix[i,j]>matrix.max()*.6 else "#14213d",fontsize=16)
        axis.set(xticks=[0,1],yticks=[0,1],xlabel="Predicted (0 normal / 1 overdue)",ylabel="Actual",title=name)
    save_figure(figure,"confusion_matrix.png")
    importance=search.best_estimator_.named_steps["model"].feature_importances_
    result["feature_importance"]={name:float(score) for name,score in zip(FEATURES,importance)}
    order=np.argsort(importance)
    figure,axis=plt.subplots(figsize=(8,5))
    axis.barh(np.array(FEATURES)[order],importance[order],color="#475569")
    axis.set(xlabel="Mean impurity decrease (not causal effect)",title="Tuned Random Forest feature importance")
    save_figure(figure,"feature_importance.png")
    example=test[FEATURES].iloc[[0]]
    selected=result["regression"]["ridge"]["selected_alpha"]
    ridge=workflow.regression("ridge",selected).fit(xtrain,train.credit_score)
    result["example"]=dict(customer_id=int(example.index[0]),input=example.iloc[0].to_dict(),
                           predicted_credit=float(workflow.predict_credit(ridge,example)[0]),
                           overdue_probability=float(logistic.predict_proba(example)[0,1]),
                           actual_credit=float(test.credit_score.iloc[0]),actual_overdue=int(test.is_overdue.iloc[0]))
    result["notes"]=["Given targets use all-data 15% quantile during synthetic generation, exactly as PDF. This is not fitted preprocessing.",
                     "All six given features are numeric. The empty categorical encoding branch is unused; no artificial category was added.",
                     "Test alpha table is diagnostic only. Alpha/model selection uses Train CV, not this Test table.",
                     "CV regression scoring uses raw model output; Test/service outputs are clipped to [0,1000].",
                     "Synthetic target noise and the random 20% normal-label override prevent perfect predictability."]
    (ROOT/"reports/experiment.json").write_text(json.dumps(result,ensure_ascii=False,indent=2))
    print(json.dumps({key:result[key] for key in ["data","grid_search","example"]},ensure_ascii=False,indent=2))
    return result

if __name__ == "__main__":
    run_experiment()
