"""필수 실행 2: 실제 모델의 전체/개별/변수별 TreeSHAP 결과를 저장한다."""
import json
import hashlib
import numpy as np
import shap
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from src.analysis import CustomerAnalysis, ROOT, FEATURES

def save_plot(name):
    plt.tight_layout();plt.savefig(ROOT/'reports'/name,dpi=140,bbox_inches='tight');plt.close()

def run():
    analysis=CustomerAnalysis()
    clusters=json.loads((ROOT/'reports/clustering.json').read_text())
    indices=analysis.features.sample(1000,random_state=42).index
    sample=analysis.features.loc[indices]
    explanation=analysis.explain(sample)
    probabilities=analysis.probabilities(sample)
    error=float(np.max(np.abs(explanation.base_values+explanation.values.sum(axis=1)-probabilities)))
    assert error < 1e-7
    shap.summary_plot(explanation.values,sample,show=False)
    save_plot('shap_summary.png')
    importance=np.mean(np.abs(explanation.values),axis=0)
    order=np.argsort(importance)[::-1]
    ranking=[]
    for index in order:
        values=sample.iloc[:,index].to_numpy();q1,q3=np.quantile(values,[.25,.75])
        low=explanation.values[values<=q1,index].mean();high=explanation.values[values>=q3,index].mean()
        ranking.append({'feature':FEATURES[index],'mean_abs_shap':float(importance[index]),'low_quartile_mean_shap':float(low),'high_quartile_mean_shap':float(high)})
    dependence=list(dict.fromkeys([FEATURES[order[0]],FEATURES[order[1]],'debt_ratio']))
    for feature in dependence:
        shap.dependence_plot(feature,explanation.values,sample,interaction_index=None,show=False)
        save_plot(f'dependence_{feature}.png')
    full_probabilities=analysis.probabilities(analysis.features)
    selections={'approval':int(np.argmin(full_probabilities)),'rejection':int(np.argmax(full_probabilities))}
    selections.update({f'cluster_{r["cluster"]}':r['representative'] for r in clusters['clusters']})
    cases={}
    for name,index in selections.items():
        frame=analysis.features.iloc[[index]];local=analysis.explain(frame)
        probability=float(full_probabilities[index]);shap.plots.waterfall(local[0],show=False)
        save_plot(f'waterfall_{name}.png')
        cases[name]={'row_index':index,'probability':probability,'decision':analysis.decision(probability),
                     'actual_is_overdue':int(analysis.frame.iloc[index]['is_overdue']),
                     'features':frame.iloc[0].to_dict(),'base':float(local.base_values[0]),
                     'contributions':dict(zip(FEATURES,local.values[0].tolist()))}
    assert cases['approval']['probability'] < .5 <= cases['rejection']['probability']
    result={'explainer':'TreeExplainer','output':'P(is_overdue=1)','sample_size':1000,'seed':42,
            'max_additivity_error':error,'ranking':ranking,'dependence_features':dependence,'cases':cases,
            'threshold':.5,'model_sha256':hashlib.sha256((ROOT/'models/random_forest.joblib').read_bytes()).hexdigest()}
    (ROOT/'reports/shap.json').write_text(json.dumps(result,ensure_ascii=False,indent=2));print(json.dumps(result,ensure_ascii=False,indent=2))

if __name__ == '__main__':run()
