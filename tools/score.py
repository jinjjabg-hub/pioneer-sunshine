"""121 추천 점수 (index.html과 같은 계산). 사용: python3 tools/score.py 이름 [이름2]"""
import json, os, sys
D = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'data') + os.sep
M = json.load(open(D + 'members.json', encoding='utf8'))
G = json.load(open(D + 'groups.json', encoding='utf8'))
SYN = json.load(open(D + 'synergy-map.json', encoding='utf8'))
RAW2G = {r: g for g, a in G.items() for r in a}
by = {m['n']: m for m in M}

def groupsOf(m):
    out = []
    for r in m['c']:
        g = RAW2G.get(r)
        if g and g not in out: out.append(g)
    return out

GDF = {}
for m in M:
    for g in groupsOf(m): GDF[g] = GDF.get(g, 0) + 1
gPts = lambda g: 4 if GDF[g] <= 2 else 3 if GDF[g] <= 4 else 2
wants = lambda a, b: [s for s in a['s'] if b['n'] in SYN.get(s, [])]

def score(a, b):
    a, b = by[a], by[b]; iW, tW = wants(a, b), wants(b, a)
    shared = sorted([g for g in groupsOf(a) if g in groupsOf(b)], key=lambda g: -gPts(g))[:3]
    mutual = 4 if iW and tW else 0; give = (5 if iW else 0) + (5 if tW else 0)
    return dict(total=mutual + give + sum(gPts(g) for g in shared), iW=iW, tW=tW, shared=shared)

if __name__ == '__main__':
    if len(sys.argv) == 3:
        print(score(sys.argv[1], sys.argv[2]))
    else:
        a = sys.argv[1]
        for t, b in sorted(((score(a, o['n'])['total'], o['n']) for o in M if o['n'] != a), reverse=True)[:8]:
            print(t, b, score(a, b))
