"""분석 실행 또는 6변수 JSON 고객의 신용점수/연체확률 출력."""
import argparse
import json
import pandas as pd
from data_gen import generate_data
from workflow import FinanceWorkflow, FEATURES

def main():
    parser=argparse.ArgumentParser(description="PDF synthetic finance learning mission")
    parser.add_argument("--customer",help="JSON with exactly the six input features")
    args=parser.parse_args()
    if args.customer is None:
        from experiment import run_experiment
        run_experiment()
        return
    values=json.loads(args.customer)
    if set(values)!=set(FEATURES):
        parser.error("customer must contain exactly: "+", ".join(FEATURES))
    frame=generate_data()
    work=FinanceWorkflow();train,_=work.split(frame)
    customer=pd.DataFrame([values])[FEATURES]
    ridge=work.regression("ridge",1).fit(train[FEATURES],train.credit_score)
    logistic=work.classifier().fit(train[FEATURES],train.is_overdue)
    print(json.dumps(dict(credit_score=float(work.predict_credit(ridge,customer)[0]),
                          overdue_probability=float(logistic.predict_proba(customer)[0,1]),
                          model="Ridge alpha=1 + balanced Logistic, Train only"),ensure_ascii=False,indent=2))

if __name__=="__main__":
    main()
