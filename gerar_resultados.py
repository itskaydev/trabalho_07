"""Le os CSVs exportados do Jupiter (jupiter_execucoes/), monta resultados_jupiter.csv,
compara com a solucao analitica (resultados_analitico.csv), gera tabela.tex e os 4 graficos."""
import glob, csv
import pandas as pd, numpy as np
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt

# (exp, lambda, c, K, pasta da execucao)
PLANO = [("E1",5,2,20,2),("E1",10,2,20,3),("E1",15,2,20,1),("E1",20,2,20,4),("E1",30,2,20,5),
         ("E2",15,1,20,6),("E2",15,2,20,1),("E2",15,4,20,7),
         ("E3",15,2,5,8),("E3",15,2,10,9),("E3",15,2,40,10),
         ("E4",10,1,10,11),("E4",20,2,20,4),("E4",40,4,40,12),
         ("Extra",30,4,20,13)]
rows = []
for exp, lam, c, K, ex in PLANO:
    f = glob.glob(f"jupiter_execucoes/execucao{ex}/*.csv")[0]
    d = pd.read_csv(f, sep=";", encoding="utf-8-sig").set_index("Metric")
    r = dict(exp=exp, lam=lam, c=c, K=K, execucao=ex, repeticoes=int(d.loc["TP","Samples"]))
    for m in ["TP","MRT","MQT","MPT","U","DP"]:
        r[m] = d.loc[m,"Value"]; r[m+"_ic_inf"] = d.loc[m,"CI Lower"]; r[m+"_ic_sup"] = d.loc[m,"CI Upper"]
    r["TP_ESPERADA"] = d.loc["TP_ESPERADA","Value"]
    rows.append(r)
J = pd.DataFrame(rows); J.to_csv("resultados_jupiter.csv", index=False, float_format="%.6f")

# comparacao com a solucao analitica
A = pd.read_csv("resultados_analitico.csv")
comp = []
for _, r in J.iterrows():
    a = A[(A.lam==r.lam)&(A.c==r.c)&(A.K==r.K)]
    if a.empty:   # cenario extra: calcular
        import spn_web; a = pd.DataFrame([spn_web.solve(mu=10.0, lam=r.lam, c=r.c, K=r.K)])
    a = a.iloc[0]
    o = dict(exp=r.exp, lam=r.lam, c=r.c, K=r.K)
    for m in ["TP","MRT","MQT","U","DP"]:
        o[m+"_jupiter"] = r[m]; o[m+"_analitico"] = a[m]
        o[m+"_dentro_IC"] = bool(r[m+"_ic_inf"] <= a[m] <= r[m+"_ic_sup"])
        o[m+"_erro_rel_%"] = abs(r[m]-a[m])/a[m]*100 if a[m] > 1e-3 else np.nan
        o[m+"_dif_abs"] = r[m]-a[m]
    comp.append(o)
C = pd.DataFrame(comp); C.to_csv("comparacao_jupiter_analitico.csv", index=False, float_format="%.6f")
print("erro relativo maximo (%):", {m: round(np.nanmax(C[m+'_erro_rel_%']),2) for m in ["TP","MRT","MQT","U"]})
print("dif abs maxima DP (p.p.):", round(C["DP_dif_abs"].abs().max(),3))
print("dentro do IC:", {m:int(C[m+'_dentro_IC'].sum()) for m in ["TP","MRT","MQT","U","DP"]}, "de", len(C))

# tabela para o artigo
with open("tabela.tex","w") as f:
    for _, r in J.iterrows():
        lin = f"{r.exp} & {r.lam:g} & {r.c:g} & {r.K:g} & {r.TP:.2f} & {r.MRT:.1f} & {r.MQT:.1f} & {r.U:.1f} & {r.DP:.2f} \\\\"
        f.write(lin.replace(".", "{,}") + "\n")
    f.write("\\bottomrule\n")

# graficos
plt.rcParams.update({"font.size":7,"axes.labelsize":7.5,"legend.fontsize":6.5,"xtick.labelsize":7,"ytick.labelsize":7})
CA, CB = "tab:blue", "tab:red"
def dual(d, x, xlabel, m1, l1, m2, l2, fn, xticks=None, loc="upper left", ylim1=None):
    fig, ax = plt.subplots(figsize=(3.4,2.3))
    h1 = ax.plot(x, d[m1], "o-", color=CA, label=l1, ms=4, lw=1.3)
    ax.set_xlabel(xlabel); ax.set_ylabel(l1, color=CA); ax.grid(alpha=.3)
    a2 = ax.twinx()
    h2 = a2.plot(x, d[m2], "s--", color=CB, label=l2, ms=4, lw=1.3); a2.set_ylabel(l2, color=CB)
    if xticks is not None: ax.set_xticks(xticks)
    hs = h1+h2; ax.legend(hs, [h.get_label() for h in hs], loc=loc, framealpha=.9)
    fig.tight_layout(); fig.savefig(fn, dpi=300); plt.close(fig)
d1 = J[J.exp=="E1"]
dual(d1, d1.lam, r"Taxa de chegada $\lambda$ (req/s)", "TP", "TP (req/s)", "MRT", "MRT (ms)", "fig_e1.png", xticks=[5,10,15,20,25,30], loc="upper left")
d2 = J[J.exp=="E2"]
dual(d2, d2.c, r"Número de servidores $c$", "MRT", "MRT (ms)", "U", "U (%)", "fig_e2.png", xticks=[1,2,3,4], loc="center right")
d3 = J[(J.exp=="E3")|((J.exp=="E1")&(J.lam==15))].sort_values("K")
dual(d3, d3.K, r"Capacidade do sistema $K$ (req)", "DP", "DP (%)", "MRT", "MRT (ms)", "fig_e3.png", xticks=[5,10,20,30,40], loc="center right")
d4 = J[J.exp=="E4"]; lab = [f"({int(l)},{int(c)},{int(k)})" for l,c,k in zip(d4.lam,d4.c,d4.K)]
fig, ax = plt.subplots(figsize=(3.4,2.3))
b = ax.bar(lab, d4.TP, color="tab:blue", width=.55, label="TP (req/s)"); ax.set_ylabel("TP (req/s)", color=CA); ax.set_xlabel(r"Cenário ($\lambda$ req/s, $c$, $K$)"); ax.set_ylim(0,48)
a2 = ax.twinx(); l2 = a2.plot(lab, d4.DP, "s--", color=CB, label="DP (%)", ms=4, lw=1.3); a2.set_ylabel("DP (%)", color=CB); a2.set_ylim(0,12)
ax.legend([b]+l2, ["TP (req/s)","DP (%)"], loc="upper left", framealpha=.9)
for i,v in enumerate(d4.TP): ax.text(i, v+.8, f"{v:.1f}", ha="center", fontsize=6.5)
fig.tight_layout(); fig.savefig("fig_e4.png", dpi=300); plt.close(fig)
print(J[["exp","lam","c","K","repeticoes","TP","MRT","U","DP"]].round(3).to_string())

# tabela de validacao (Jupiter x analitico) e tabela de configuracoes candidatas
def ptv(x, nd): return f"{x:.{nd}f}".replace(".", "{,}")
sel = [(15,2,20,"Ref."),(30,2,20,"E1"),(15,1,20,"E2"),(15,4,20,"E2"),(15,2,5,"E3"),(40,4,40,"E4")]
with open("tabela_validacao.tex","w") as f:
    for lam,c,K,tag in sel:
        r = C[(C.lam==lam)&(C.c==c)&(C.K==K)].iloc[0]
        f.write(f"{tag} & ({lam},{c},{K}) & {ptv(r.TP_jupiter,2)} & {ptv(r.TP_analitico,2)} & {ptv(r.MRT_jupiter,1)} & {ptv(r.MRT_analitico,1)} & {ptv(r.DP_jupiter,2)} & {ptv(r.DP_analitico,2)} \\\\\n")
    f.write("\\bottomrule\n")
cfg = [("A",15,2,10),("B",15,2,20),("C",15,4,20),("D",30,4,20)]
with open("tabela_config.tex","w") as f:
    for nome,lam,c,K in cfg:
        r = J[(J.lam==lam)&(J.c==c)&(J.K==K)].iloc[0]
        f.write(f"{nome} & {lam} & {c} & {K} & {ptv(r.TP,2)} & {ptv(r.MRT,1)} & {ptv(r.U,1)} & {ptv(r.DP,2)} \\\\\n")
    f.write("\\bottomrule\n")

# figura complementar (3 paineis, largura total): metricas nao mostradas nas figuras E1-E3
fig, axs = plt.subplots(1, 3, figsize=(7.1, 2.1))
def pair(ax, x, y1, l1, y2, l2, xl, xt=None):
    ax.plot(x, y1, "o-", color=CA, ms=3.5, lw=1.2, label=l1); ax.set_ylabel(l1, color=CA); ax.set_xlabel(xl); ax.grid(alpha=.3)
    b = ax.twinx(); b.plot(x, y2, "s--", color=CB, ms=3.5, lw=1.2, label=l2); b.set_ylabel(l2, color=CB)
    if xt is not None: ax.set_xticks(xt)
    h = ax.get_lines()+b.get_lines(); ax.legend(h, [q.get_label() for q in h], loc="best", framealpha=.9)
pair(axs[0], d1.lam, d1.U, "U (%)", d1.DP, "DP (%)", r"(a) E1: taxa de chegada $\lambda$ (req/s)", [5,10,15,20,25,30])
pair(axs[1], d2.c, d2.TP, "TP (req/s)", d2.DP, "DP (%)", r"(b) E2: número de servidores $c$", [1,2,3,4])
pair(axs[2], d3.K, d3.TP, "TP (req/s)", d3.U, "U (%)", r"(c) E3: capacidade $K$ (req)", [5,10,20,30,40])
fig.tight_layout(); fig.savefig("fig_comp.png", dpi=300); plt.close(fig)

# figura de validacao: Jupiter x analitico
fig, axs = plt.subplots(1, 2, figsize=(3.4, 1.9))
mk = {"E1":"o","E2":"s","E3":"^","E4":"D","Extra":"*"}
for e, g in C.groupby("exp"):
    axs[0].plot(g.MRT_analitico, g.MRT_jupiter, mk[e], ms=4, label=e, mfc="none")
    axs[1].plot(g.DP_analitico, g.DP_jupiter, mk[e], ms=4, mfc="none")
for ax, lim, xl, yl in [(axs[0], (80, 2200), "MRT analítico (ms)", "MRT Jupiter (ms)"), (axs[1], (-1, 36), "DP analítico (%)", "DP Jupiter (%)")]:
    ax.plot(lim, lim, "k:", lw=.8); ax.set_xlim(lim); ax.set_ylim(lim); ax.set_xlabel(xl); ax.set_ylabel(yl); ax.grid(alpha=.3)
axs[0].set_xscale("log"); axs[0].set_yscale("log"); axs[0].legend(loc="upper left", framealpha=.9, ncol=1, fontsize=5.5)
fig.tight_layout(); fig.savefig("fig_val.png", dpi=300); plt.close(fig)

# tabela completa com IC (half-width) e repeticoes
def pm(r, m, nd):
    hw = (r[m+"_ic_sup"] - r[m+"_ic_inf"])/2
    return f"{ptv(r[m],nd)}$\\pm${ptv(hw,nd)}"
with open("tabela_ic.tex","w") as f:
    for _, r in J.iterrows():
        f.write(f"{r.exp} & ({r.lam:g},{r.c:g},{r.K:g}) & {r.repeticoes} & {pm(r,'TP',2)} & {pm(r,'MRT',1)} & {pm(r,'MQT',1)} & {pm(r,'U',2)} & {pm(r,'DP',2)} \\\\\n")
    f.write("\\bottomrule\n")
