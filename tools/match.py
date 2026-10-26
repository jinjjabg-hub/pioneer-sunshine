"""121 데이 매칭 (정수계획법). pip install pulp==2.9.0 후 python3 tools/match.py
규칙: 3라운드, 1:1만(3인 조 금지), 같은 짝 반복 금지, 0점 짝 금지, 홀수면 라운드마다 1명 휴식.
선택 키(121day.json): fixed = [[라운드, 이름, 이름]] 미리 정한 짝(상대는 그 라운드에 다른 짝 없음, 점수 계산 밖), newcomer = 매칭 계산에서 빼는 신입 이름, zeroPenalty = 0점 짝 허용 시 감점(없으면 금지), partial = {이름: [참여하는 라운드 번호]} (제외자도 해당 라운드에만 넣음), must = 반드시 만나야 하는 짝(0점이어도 허용), absent = {이름: [빠지는 라운드 번호(0부터)]}.
목표: 점수 합계 + 10 × (한 사람이 받는 3라운드 합계의 최솟값) 최대화.
결과는 data/121day.json의 rounds/rest에 쓴다. excluded는 파일에 있는 값을 그대로 쓴다."""
import json, itertools, os, sys
import pulp
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from score import M, score, D
day = json.load(open(D + '121day.json', encoding='utf8'))
PART = {p: set(r) for p, r in day.get('partial', {}).items()}
EXCL = (set(day.get('excluded', [])) - set(PART)) | set(day.get('newcomer', []))
FIX = [(r, a, b) for r, a, b in day.get('fixed', [])]
P = [m['n'] for m in M if m['n'] not in EXCL]; R = [0, 1, 2]
w = {e: score(*e)['total'] for e in itertools.combinations(P, 2)}
MUST = [e if e in w else (e[1], e[0]) for e in map(tuple, day.get('must', []))]
ABS = {p: set(r) for p, r in day.get('absent', {}).items()}
for p, rs in PART.items(): ABS[p] = set(R) - rs
for r, a, b in FIX:
    for n in (a, b):
        if n not in EXCL: ABS.setdefault(n, set()).add(r)
ZP = day.get('zeroPenalty')  # 있으면 0점 짝도 이 값만큼 감점하고 허용
pairs = [e for e in w if w[e] > 0 or e in MUST or ZP]
prob = pulp.LpProblem('m', pulp.LpMaximize)
x = {(e, r): pulp.LpVariable(f"x{i}_{r}", cat='Binary') for i, e in enumerate(pairs) for r in R}
rest = {(p, r): pulp.LpVariable(f"r{j}_{r}", cat='Binary') for j, p in enumerate(P) for r in R}
mn = pulp.LpVariable('mn', lowBound=0)
inc = {p: [e for e in pairs if p in e] for p in P}
prob += pulp.lpSum((w[e] if w[e] > 0 or e in MUST else -ZP) * x[(e, r)] for e in pairs for r in R) + 10 * mn
here = lambda p, r: 0 if r in ABS.get(p, ()) else 1
for r in R:
    for p in P:
        prob += pulp.lpSum(x[(e, r)] for e in inc[p]) + rest[(p, r)] == here(p, r)
        if not here(p, r): prob += rest[(p, r)] == 0
    prob += pulp.lpSum(rest[(p, r)] for p in P) == sum(here(p, r) for p in P) % 2
for p in P:
    if p not in PART: prob += pulp.lpSum(rest[(p, r)] for r in R) + len(ABS.get(p, ())) <= 1
for e in MUST: prob += pulp.lpSum(x[(e, r)] for r in R) == 1
for e in pairs: prob += pulp.lpSum(x[(e, r)] for r in R) <= 1
for p in P:
    if p in PART or sum(p in e for e in MUST) >= 3: continue  # 필수 짝이 3개면 점수를 고를 수 없어 최솟값에서 제외
    prob += pulp.lpSum(w[e] * x[(e, r)] for e in inc[p] for r in R) + 99 * (pulp.lpSum(rest[(p, r)] for r in R) + len(ABS.get(p, ()))) >= mn
prob.solve(pulp.PULP_CBC_CMD(msg=0, timeLimit=300))
print(len(P), '명', pulp.LpStatus[prob.status], '최소', mn.value())
day['rounds'] = [sorted([list(e) for (e, rr), v in x.items() if rr == r and v.value() > 0.5], key=lambda p: -w[tuple(p)]) for r in R]
for r, a, b in FIX: day['rounds'][r].append([a, b])
day['rest'] = [next((p for p in P if rest[(p, r)].value() > 0.5), None) for r in R]
print('합계', sum(w.get(tuple(p), 0) for rd in day['rounds'] for p in rd))
json.dump(day, open(D + '121day.json', 'w', encoding='utf8'), ensure_ascii=False, indent=1)
