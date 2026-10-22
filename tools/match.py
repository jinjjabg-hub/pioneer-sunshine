"""121 데이 매칭 (정수계획법). pip install pulp==2.9.0 후 python3 tools/match.py
규칙: 3라운드, 1:1만(3인 조 금지), 같은 짝 반복 금지, 0점 짝 금지, 홀수면 라운드마다 1명 휴식.
목표: 점수 합계 + 10 × (한 사람이 받는 3라운드 합계의 최솟값) 최대화.
결과는 data/121day.json의 rounds/rest에 쓴다. excluded는 파일에 있는 값을 그대로 쓴다."""
import json, itertools, os, sys
import pulp
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from score import M, score, D
day = json.load(open(D + '121day.json', encoding='utf8'))
EXCL = set(day.get('excluded', []))
P = [m['n'] for m in M if m['n'] not in EXCL]; R = [0, 1, 2]
w = {e: score(*e)['total'] for e in itertools.combinations(P, 2)}
pairs = [e for e in w if w[e] > 0]
prob = pulp.LpProblem('m', pulp.LpMaximize)
x = {(e, r): pulp.LpVariable(f"x{i}_{r}", cat='Binary') for i, e in enumerate(pairs) for r in R}
rest = {(p, r): pulp.LpVariable(f"r{j}_{r}", cat='Binary') for j, p in enumerate(P) for r in R}
mn = pulp.LpVariable('mn', lowBound=0)
inc = {p: [e for e in pairs if p in e] for p in P}
prob += pulp.lpSum(w[e] * x[(e, r)] for e in pairs for r in R) + 10 * mn
odd = len(P) % 2
for r in R:
    for p in P: prob += pulp.lpSum(x[(e, r)] for e in inc[p]) + rest[(p, r)] == 1
    prob += pulp.lpSum(rest[(p, r)] for p in P) == odd
for p in P: prob += pulp.lpSum(rest[(p, r)] for r in R) <= 1
for e in pairs: prob += pulp.lpSum(x[(e, r)] for r in R) <= 1
for p in P: prob += pulp.lpSum(w[e] * x[(e, r)] for e in inc[p] for r in R) + 99 * pulp.lpSum(rest[(p, r)] for r in R) >= mn
prob.solve(pulp.PULP_CBC_CMD(msg=0, timeLimit=300))
print(len(P), '명', pulp.LpStatus[prob.status], '최소', mn.value())
day['rounds'] = [sorted([list(e) for (e, rr), v in x.items() if rr == r and v.value() > 0.5], key=lambda p: -w[tuple(p)]) for r in R]
day['rest'] = [next((p for p in P if rest[(p, r)].value() > 0.5), None) for r in R] if odd else []
print('합계', sum(w[tuple(p)] for rd in day['rounds'] for p in rd))
json.dump(day, open(D + '121day.json', 'w', encoding='utf8'), ensure_ascii=False, indent=1)
