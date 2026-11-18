"""Read-only research: pull public posts of a Business/Creator Instagram account
via Meta's business_discovery and save them (plus images) for analysis.
Posts nothing.  Usage: python research.py <username> [max_posts]
"""
import json, os, sys, urllib.parse, urllib.request

TOKEN = os.environ["IG_TOKEN"].strip()
IG_ID = os.environ.get("IG_USER_ID", "").strip() or "17841449209573024"
API = "https://graph.facebook.com/v21.0"
user = sys.argv[1].lstrip("@")
limit = int(sys.argv[2]) if len(sys.argv) > 2 else 100

FIELDS = "id,caption,media_type,media_product_type,like_count,comments_count,timestamp,permalink,media_url,children{media_url,media_type}"

def get(url):
    with urllib.request.urlopen(url, timeout=60) as r:
        return json.loads(r.read())

posts, after, profile = [], None, {}
while len(posts) < limit:
    media = f"media.limit(50){{{FIELDS}}}" if not after else f"media.limit(50).after({after}){{{FIELDS}}}"
    q = f"business_discovery.username({user}){{username,name,biography,followers_count,media_count,{media}}}"
    d = get(f"{API}/{IG_ID}?" + urllib.parse.urlencode({"fields": q, "access_token": TOKEN}))["business_discovery"]
    profile = {k: d.get(k) for k in ("username", "name", "biography", "followers_count", "media_count")}
    m = d.get("media", {})
    posts += m.get("data", [])
    after = m.get("paging", {}).get("cursors", {}).get("after")
    if not after or not m.get("data"):
        break
posts = posts[:limit]

out = os.path.join("research_out", user)
os.makedirs(os.path.join(out, "img"), exist_ok=True)
for i, p in enumerate(posts):
    urls = []
    if p.get("media_type") == "CAROUSEL_ALBUM":
        urls = [c.get("media_url") for c in p.get("children", {}).get("data", []) if c.get("media_type") == "IMAGE"][:3]
    elif p.get("media_type") == "IMAGE":
        urls = [p.get("media_url")]
    p["saved_images"] = []
    for j, u in enumerate(urls):
        if not u: continue
        fn = f"{i:03d}_{j}.jpg"
        try:
            urllib.request.urlretrieve(u, os.path.join(out, "img", fn)); p["saved_images"].append(fn)
        except Exception as e:
            print("img fail", fn, e)
json.dump({"profile": profile, "posts": posts}, open(os.path.join(out, "posts.json"), "w"), indent=1)
print(json.dumps(profile))
print(f"saved {len(posts)} posts")
