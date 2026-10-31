"""Gera os cards de status (rosa e amarelo, animados) com dados reais do GitHub."""
import json, os, urllib.request

USER = os.environ.get("GH_USER", "GabrielyManna")
TOKEN = os.environ["GH_TOKEN"]
Q = """query($l:String!){user(login:$l){followers{totalCount}
contributionsCollection{totalCommitContributions totalPullRequestContributions totalIssueContributions contributionCalendar{totalContributions}}
repositories(first:100,ownerAffiliations:OWNER){totalCount nodes{name isFork stargazerCount
languages(first:10,orderBy:{field:SIZE,direction:DESC}){edges{size node{name}}}}}}}"""
req = urllib.request.Request("https://api.github.com/graphql",
    data=json.dumps({"query": Q, "variables": {"l": USER}}).encode(),
    headers={"Authorization": f"bearer {TOKEN}", "Content-Type": "application/json"})
u = json.load(urllib.request.urlopen(req))["data"]["user"]
c = u["contributionsCollection"]; repos = u["repositories"]
stars = sum(r["stargazerCount"] for r in repos["nodes"] if not r["isFork"])
langs = {}
for r in repos["nodes"]:
    if r["name"].lower() == USER.lower():
        continue  # o repositório do perfil não conta como linguagem dela
    for e in r["languages"]["edges"]:
        langs[e["node"]["name"]] = langs.get(e["node"]["name"], 0) + e["size"]
total = sum(langs.values()) or 1
top = sorted(langs.items(), key=lambda x: -x[1])[:6]

FONT = "font-family=\"'Trebuchet MS','Segoe UI',Verdana,sans-serif\""
STYLE = """<style>.in{animation:in .8s ease-out both}@keyframes in{from{opacity:0;transform:translateX(-12px)}}
.tw{animation:tw 2.4s ease-in-out infinite;transform-box:fill-box;transform-origin:center}@keyframes tw{0%,100%{opacity:.3;transform:scale(.6)}50%{opacity:1;transform:scale(1.15)}}
.grow{transform-box:fill-box;transform-origin:left center;animation:grow 1.4s ease-out both}@keyframes grow{from{transform:scaleX(0)}}</style>"""
S4 = ('<path id="s4" d="M0,-8 C1,-2 2,-1 8,0 C2,1 1,2 0,8 C-1,2 -2,1 -8,0 C-2,-1 -1,-2 0,-8Z"/>'
      '<path id="hr" d="M0,7 C-9,1 -6,-7 0,-2 C6,-7 9,1 0,7Z"/>')
def card(h, title, body):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="400" height="{h}" viewBox="0 0 400 {h}"><defs>{S4}</defs>{STYLE}'
            f'<rect x="1.5" y="1.5" width="397" height="{h-3}" rx="14" fill="#FFF3B0" stroke="#FF8FBF" stroke-width="3"/>'
            f'<use href="#s4" x="372" y="26" class="tw" fill="#E0568F"/><use href="#s4" x="352" y="{h-22}" class="tw" fill="#FFD23F" style="animation-delay:1s"/>'
            f'<text x="24" y="38" {FONT} font-size="19" font-weight="bold" fill="#E0568F">{title}</text>{body}</svg>')

rows = [("", "Contribuições no último ano", c["contributionCalendar"]["totalContributions"]),
        ("", "Commits", c["totalCommitContributions"]),
        ("", "Pull requests", c["totalPullRequestContributions"]),
        ("", "Issues", c["totalIssueContributions"]),
        ("", "Estrelas recebidas", stars),
        ("", "Repositórios", repos["totalCount"])]
b = ""
for i, (ic, lab, v) in enumerate(rows):
    y = 72 + i * 26
    b += (f'<g class="in" style="animation-delay:{i*0.15}s"><use href="#{"hr" if i%2 else "s4"}" x="34" y="{y-5}" fill="{"#E0568F" if i%2 else "#FFD23F"}"/>'
          f'<text x="52" y="{y}" {FONT} font-size="15" fill="#9C2A5E">{lab}</text>'
          f'<text x="372" y="{y}" text-anchor="end" {FONT} font-size="15" font-weight="bold" fill="#C2185B">{v}</text></g>')
os.makedirs("dist", exist_ok=True)
open("dist/stats.svg", "w", encoding="utf-8").write(card(240, "Poderes da Princesa", b))

cols = ["#E0568F", "#FFD23F", "#FF8FBF", "#E8A800", "#C2185B", "#FFE98A"]
b = '<clipPath id="bar"><rect x="24" y="56" width="352" height="12" rx="6"/></clipPath><g clip-path="url(#bar)">'
x = 24.0
for i, (n, s) in enumerate(top):
    w = 352 * s / total
    b += f'<rect class="grow" style="animation-delay:{i*0.2}s" x="{x:.1f}" y="56" width="{w:.1f}" height="12" fill="{cols[i]}"/>'
    x += w
b += '</g>'
for i, (n, s) in enumerate(top):
    cx = 30 + (i % 2) * 180; y = 98 + (i // 2) * 30
    b += (f'<g class="in" style="animation-delay:{0.4+i*0.15}s"><circle cx="{cx}" cy="{y-5}" r="6" fill="{cols[i]}"/>'
          f'<text x="{cx+14}" y="{y}" {FONT} font-size="14" fill="#9C2A5E">{n} {100*s/total:.1f}%</text></g>')
if not top:
    b += f'<text x="24" y="100" {FONT} font-size="14" fill="#9C2A5E">Os encantos aparecem aqui em breve</text>'
open("dist/langs.svg", "w", encoding="utf-8").write(card(165, "Encantos Favoritos", b))
print("ok", rows, top)
