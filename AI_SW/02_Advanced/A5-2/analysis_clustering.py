"""필수 실행 1: K 선택, PCA 산점도, 원본 단위별 군집 평균을 저장한다."""
import json
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from src.analysis import CustomerAnalysis, ROOT

def run():
    analysis = CustomerAnalysis()
    result = analysis.cluster()
    (ROOT/'reports/clustering.json').write_text(json.dumps(result, ensure_ascii=False, indent=2))
    fig, axes = plt.subplots(1, 2, figsize=(12,4))
    axes[0].plot([r['k'] for r in result['candidates']], [r['inertia'] for r in result['candidates']], 'o-')
    axes[0].set(xlabel='K', ylabel='Inertia', title='Elbow (supporting criterion)')
    axes[1].plot([r['k'] for r in result['candidates']], [r['silhouette'] for r in result['candidates']], 'o-')
    axes[1].set(xlabel='K', ylabel='Silhouette', title=f"Selected K={result['chosen_k']} (sample=1500)")
    fig.tight_layout(); fig.savefig(ROOT/'reports/k_selection.png',dpi=140); plt.close(fig)
    fig, ax = plt.subplots(figsize=(8,6))
    points = analysis.pca_coordinates
    for label in range(result['chosen_k']):
        mask = analysis.labels == label
        ax.scatter(points[mask,0], points[mask,1], s=8, alpha=.35, label=f'Cluster {label}')
    evr=result['explained_variance_ratio']
    ax.set(xlabel=f'PC1 ({evr[0]:.1%})',ylabel=f'PC2 ({evr[1]:.1%})',title=f'PCA view only; KMeans uses all 6 features. Total={sum(evr):.1%}')
    ax.legend();fig.tight_layout();fig.savefig(ROOT/'reports/pca_clusters.png',dpi=140);plt.close(fig)
    print(json.dumps(result,ensure_ascii=False,indent=2))

if __name__ == '__main__': run()
