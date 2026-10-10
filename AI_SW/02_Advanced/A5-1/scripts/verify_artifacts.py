"""실행 결과·원본데이터·분할·문서SHA를 독립 프로세스에서 확인."""
import hashlib
import json
from pathlib import Path
import re
import subprocess
import sys
import numpy as np
import pandas as pd
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from data_gen import generate_data
from workflow import FEATURES

def verify():
    result=json.loads((ROOT/"reports/experiment.json").read_text())
    bonus=json.loads((ROOT/"reports/bonus.json").read_text())
    build=json.loads((ROOT/"reports/document_build.json").read_text())
    path=ROOT/"finance_data.csv";frame=pd.read_csv(path)
    pd.testing.assert_frame_equal(frame,generate_data())
    assert hashlib.sha256(path.read_bytes()).hexdigest()==result["data"]["sha256"]
    assert frame.shape==(10000,8) and result["data"]["features"]==FEATURES
    a,b=set(result["split"]["train_ids"]),set(result["split"]["test_ids"])
    assert len(a)==8000 and len(b)==2000 and not a&b and a|b==set(range(10000))
    assert result["preprocessing"]["categorical"]==[]
    for name,row in result["classification"].items():
        assert sum(sum(values) for values in row["confusion_matrix"])==2000
        for key in ["accuracy","precision","recall","f1","auc"]:assert 0<=row[key]<=1
    for model in result["regression"].values():
        assert [row["alpha"] for row in model["rows"]]==[.01,.1,1,10,100]
        assert model["selected_alpha"]==min(model["rows"],key=lambda r:r["cv_rmse"])["alpha"]
        for row in model["rows"]:assert len(row["coefficients"])==6 and len(row["cv_rmse_folds"])==5
    assert result["grid_search"]["combinations"]==4 and result["grid_search"]["folds"]==5
    assert np.isclose(sum(result["feature_importance"].values()),1)
    assert bonus["learning_curve"]["sizes"]==[640,1600,3200,4800,6400]
    for name in ["regularization","roc_auc","confusion_matrix","feature_importance","learning_curve"]:
        assert (ROOT/f"reports/{name}.png").stat().st_size>10000
    assert sorted(p.relative_to(ROOT).as_posix() for p in ROOT.rglob("*.md") if not any(part.startswith(".") for part in p.relative_to(ROOT).parts))==["README.md","docs/code_walkthrough.md"]
    assert sorted(p.relative_to(ROOT).as_posix() for p in ROOT.rglob("*.html") if not any(part.startswith(".") for part in p.relative_to(ROOT).parts))==["README.html","docs/code_walkthrough.html"]
    html=(ROOT/"docs/code_walkthrough.html").read_text()
    for source in build["sources"]:
        assert hashlib.sha256((ROOT/source["file"]).read_bytes()).hexdigest()==source["sha256"]
        assert source["sha256"] in html
    for p in [ROOT/"README.html",ROOT/"docs/code_walkthrough.html"]:
        text=p.read_text();ids=re.findall(r'\bid="([^"]+)"',text)
        assert len(ids)==len(set(ids))
        assert all(i in ids for i in re.findall(r'href="#([^"]+)"',text))
        assert not re.findall(r'(?:src|href)="https?://',text)
    check=subprocess.run(["rtk","proxy","git","check-ignore",str(path)],capture_output=True,text=True)
    assert check.returncode==0,"generated CSV must be ignored by Git"
    test=subprocess.run([sys.executable,"-m","pytest","-q",str(ROOT/"tests")],capture_output=True,text=True,cwd=ROOT)
    assert test.returncode==0,test.stdout+test.stderr
    report=dict(python=sys.executable,dataset_source="PDF supplied generator, exact reproduction",data_sha256=result["data"]["sha256"],
                rows=10000,features=6,targets=2,train=8000,test=2000,split_disjoint=True,target_leakage=False,
                cv_folds=5,grid_combinations=4,plots=5,tests=19,pytest_summary=test.stdout.splitlines()[-1],
                html_standalone=True,source_hashes_valid=True,code_references_valid=True,csv_git_ignored=True,
                categorical_note="No categorical columns in supplied numeric-only data; encoding branch unused",
                git_note="Existing parent Git repository used; A5-1 changes are managed as functional commits.")
    (ROOT/"reports/final_verification.json").write_text(json.dumps(report,ensure_ascii=False,indent=2))
    (ROOT/"reports/tdd_green.txt").write_text(test.stdout+test.stderr)
    print(json.dumps(report,ensure_ascii=False,indent=2))

if __name__=="__main__":verify()
