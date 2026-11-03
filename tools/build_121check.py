"""121check.html 안의 멤버 명단을 data/members.json 에서 다시 채운다. 멤버가 바뀌면: python3 tools/build_121check.py"""
import json, re
m = [{"n": x["n"], "co": x.get("co", ""), "f": x.get("f", "")} for x in json.load(open("data/members.json", encoding="utf-8"))]
blob = "/*MEMBERS*/" + json.dumps(m, ensure_ascii=False, separators=(",", ":")) + "/*END*/"
s = open("121check.html", encoding="utf-8").read()
s = re.sub(r"/\*MEMBERS\*/.*?/\*END\*/", lambda _: blob, s, flags=re.S)
open("121check.html", "w", encoding="utf-8").write(s)
print(len(m), "명 반영")
