"""VALIDACAO ANALITICA (nao e a fonte dos resultados do artigo; esses vem do Jupiter).
SPN Servidor Web (M/M/c/K). Resolve a CTMC subjacente da SPN em regime estacionario.
Marcacao: N = #Fila + #Proc. Estados 0..K. Taxa de chegada lambda (bloqueada em N=K, guarda),
taxa de servico = min(N,c)*mu (semantica infinite-server em T_Serv com #Proc<=c)."""
import numpy as np, csv
def solve(lam, mu, c, K):
    Q = np.zeros((K+1, K+1))
    for n in range(K+1):
        if n < K: Q[n, n+1] = lam
        if n > 0: Q[n, n-1] = min(n, c)*mu
        Q[n, n] = -Q[n].sum()
    A = np.vstack([Q.T, np.ones(K+1)]); b = np.zeros(K+2); b[-1] = 1
    p = np.linalg.lstsq(A, b, rcond=None)[0]
    n = np.arange(K+1)
    DP = p[K]; TP = lam*(1-DP)
    EN = (n*p).sum(); EP = (np.minimum(n, c)*p).sum(); EQ = (np.maximum(n-c, 0)*p).sum()
    return dict(lam=lam, c=c, K=K, TP=TP, MRT=EN/TP*1000, MQT=EQ/TP*1000,
                U=EP/c*100, DP=DP*100, MPT=EP/TP*1000)
mu = 10.0; ref = dict(lam=15, c=2, K=20)
E = {"E1": [dict(ref, lam=l) for l in (5, 10, 15, 20, 30)],
     "E2": [dict(ref, c=c) for c in (1, 2, 4)],
     "E3": [dict(ref, K=k) for k in (5, 10, 40)],
     "E4": [dict(lam=10, c=1, K=10), dict(lam=20, c=2, K=20), dict(lam=40, c=4, K=40)]}
rows = []
for e, cfgs in E.items():
    for cf in cfgs:
        r = solve(mu=mu, **cf); r["exp"] = e; rows.append(r)
with open("resultados_analitico.csv", "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=["exp","lam","c","K","TP","MRT","MQT","U","DP","MPT"]); w.writeheader(); w.writerows(rows)
for r in rows: print({k:(round(v,2) if isinstance(v,float) else v) for k,v in r.items()})
