import os
import re
from datetime import datetime, timezone
from github import Github

USERNAME = os.environ["GH_USERNAME"]
g = Github(os.environ["GH_TOKEN"])
user = g.get_user(USERNAME)

repos = [
    r for r in user.get_repos()
    if not r.fork
    and r.name.lower() != USERNAME.lower()
    and not r.private
    and r.description
]

def score(r):
    days_since_push = (datetime.now(timezone.utc) - r.pushed_at).days
    recency = 15 if days_since_push < 90 else (8 if days_since_push < 180 else 0)
    return r.stargazers_count * 3 + r.watchers_count * 2 + recency

repos.sort(key=score, reverse=True)
top = repos[:4]

lines = ["## Selected Projects\n"]
lines.append("<!-- AUTO-UPDATED EVERY 3 MONTHS BY GITHUB ACTIONS — DO NOT EDIT THIS BLOCK MANUALLY -->\n")

for r in top:
    lang = r.language or "Python"
    desc = r.description.strip()
    stars = f" · ⭐ {r.stargazers_count}" if r.stargazers_count > 0 else ""
    topics = list(r.get_topics())[:3]
    topic_tags = " ".join([f"`{t}`" for t in topics])
    lines.append(f"### [{r.name}]({r.html_url})")
    lines.append(f"{desc}{stars}")
    lines.append(f"`{lang}` {topic_tags}\n")

lines.append("<!-- END AUTO-UPDATE BLOCK -->")
new_block = "\n".join(lines)

with open("README.md", "r") as f:
    content = f.read()

pattern = r"## Selected Projects\n[\s\S]*?<!-- END AUTO-UPDATE BLOCK -->"
if re.search(pattern, content):
    updated = re.sub(pattern, new_block.strip(), content)
else:
    updated = content.rstrip() + "\n\n" + new_block.strip()

with open("README.md", "w") as f:
    f.write(updated)

print(f"✅ Featured projects updated: {[r.name for r in top]}")
