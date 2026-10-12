"""선택 실행: 같은 표준화 입력에서 Ward와 K-Means를 비교한다."""
import json
from src.bonus import HierarchicalAnalysis
from src.analysis import ROOT

if __name__ == '__main__':
    k=json.loads((ROOT/'reports/clustering.json').read_text())['chosen_k']
    analysis=HierarchicalAnalysis();analysis.cluster([k])
    result=analysis.compare(k)
    (ROOT/'reports/bonus_comparison.json').write_text(json.dumps(result,ensure_ascii=False,indent=2))
    print(result)
