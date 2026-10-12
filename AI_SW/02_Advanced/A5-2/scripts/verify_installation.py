"""새 프로세스에서 설치 경로·메타데이터·TreeSHAP·실제 Streamlit 입력을 확인한다."""
import sys
from pathlib import Path
import json
import importlib.metadata as metadata
import shap
import sklearn
import streamlit
import numpy as np
import pandas as pd
from streamlit.testing.v1 import AppTest

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from src.analysis import CustomerAnalysis

expected='/Users/oliverjoo/Dev/Anaconda/anaconda3/envs/py312/'
assert sys.executable.startswith(expected)
modules={'shap':shap,'streamlit':streamlit,'scikit-learn':sklearn,'pandas':pd}
result={'python':sys.executable,'packages':{}}
for name,module in modules.items():
    assert str(module.__file__).startswith(expected)
    versions=[d.version for d in metadata.distributions() if (d.metadata.get('Name') or '').lower().replace('_','-') == name]
    assert len(versions)==1,(name,versions)
    assert versions[0] == module.__version__
    result['packages'][name]={'version':module.__version__,'path':module.__file__,'metadata_versions':versions}
analysis=CustomerAnalysis()
sample=analysis.features.iloc[:3]
explanation=analysis.explain(sample)
error=float(np.max(np.abs(explanation.base_values+explanation.values.sum(axis=1)-analysis.probabilities(sample))))
assert error<1e-7
result['tree_shap_additivity_error']=error
app=AppTest.from_file(str(ROOT/'app.py'),default_timeout=120).run()
assert not app.exception,list(app.exception)
app.number_input[0].set_value(40)
app.number_input[4].set_value(2)
app.slider[0].set_value(.8)
app.button[0].click().run()
assert not app.exception,list(app.exception)
expected_result=analysis.probabilities(__import__('pandas').DataFrame([dict(age=40,annual_income=5000,spending_score=50,debt_ratio=.8,credit_card_count=3,overdue_count_6m=2)]))[0]
assert app.metric[0].value==f'{expected_result:.2%}'
result['streamlit_e2e']={'metric':app.metric[0].value,'expected_probability':float(expected_result),
                         'exceptions':0,'input_changed':True,'output_widgets':len(app.get('arrow_vega_lite_chart'))}
(ROOT/'reports/installation_verification.json').write_text(json.dumps(result,indent=2))
print(json.dumps(result,indent=2))
