"""Read-only hashtag scout: uses the official Instagram Graph API hashtag search
to find recent/top public posts for a few Chennai diet-food hashtags, and pulls
@mentions and phone numbers out of their captions.  Posts nothing.

Output: scout_out/scout_results.json   (uploaded as a workflow artifact only)
Instagram allows 30 unique hashtag searches per 7 days per account - keep the list short.
"""
import json, os, re, sys, urllib.error, urllib.parse, urllib.request
from collections import Counter, defaultdict

TOKEN = os.environ.get("IG_TOKEN", "").strip()
IG_ID = os.environ.get("IG_USER_ID", "").strip() or "17841449209573024"
API = "https://graph.facebook.com/v21.0"
OUT_DIR = "scout_out"
OUT = os.path.join(OUT_DIR, "scout_results.json")

HASHTAGS = [
    "chennaimealprep", "healthyfoodchennai", "ketochennai", "chennaidietfood",
    "dietfoodchennai", "mealprepchennai", "chennaihealthyfood", "chennaisaladbowl",
    "highproteinchennai", "chennaiweightloss",
]
FIELDS = "id,caption,permalink,timestamp,media_type"

MENTION_RE = re.compile(r"(?<![\w.])@([A-Za-z0-9_](?:[A-Za-z0-9_.]{0,28}[A-Za-z0-9_])?)")
PHONE_RE = re.compile(r"(?<!\d)(?:\+?91[\s\-.]?|0)?([6-9]\d{4})[\s\-.]?(\d{5})(?!\d)")


def save(obj):
    os.makedirs(OUT_DIR, exist_ok=True)
    with open(OUT, "w") as f:
        json.dump(obj, f, indent=1, ensure_ascii=False)


def scrub(text):
    return text.replace(TOKEN, "***") if TOKEN else text


def get(path, params):
    params = dict(params, access_token=TOKEN)
    url = f"{API}/{path}?" + urllib.parse.urlencode(params)
    try:
        with urllib.request.urlopen(url, timeout=60) as r:
            return json.loads(r.read()), None
    except urllib.error.HTTPError as e:
        body = scrub(e.read().decode(errors="replace"))
        try:
            err = json.loads(body).get("error", {})
            return None, {"http": e.code, "code": err.get("code"), "subcode": err.get("error_subcode"),
                          "message": err.get("message")}
        except Exception:
            return None, {"http": e.code, "message": body[:300]}
    except Exception as e:
        return None, {"message": scrub(str(e))[:300]}


def phones(text):
    out = []
    for a, b in PHONE_RE.findall(text or ""):
        n = f"+91 {a} {b}"
        if n not in out:
            out.append(n)
    return out


def mentions(text):
    out = []
    for m in MENTION_RE.findall(text or ""):
        m = m.lower().rstrip(".")
        if m not in out:
            out.append(m)
    return out


def main():
    if not TOKEN:
        save({"supported": False, "reason": "IG_TOKEN secret is missing."})
        print("IG_TOKEN secret is missing.")
        return
    if TOKEN.startswith("IG"):
        reason = ("IG_TOKEN is an Instagram-login token (starts with 'IG', graph.instagram.com). "
                  "Hashtag search (ig_hashtag_search) is only available with a Facebook-login / "
                  "system-user token on graph.facebook.com, for an Instagram professional account "
                  "linked to a Facebook Page (permissions: instagram_basic, pages_show_list, "
                  "and Instagram Public Content Access).")
        save({"supported": False, "reason": reason})
        print("Hashtag search NOT supported by this token:", reason)
        return

    results = {"supported": True, "ig_user_id": IG_ID, "hashtags": {}, "errors": []}
    handle_count, handle_tags, handle_links = Counter(), defaultdict(set), defaultdict(list)
    phone_count, phone_tags, phone_links = Counter(), defaultdict(set), defaultdict(list)

    for tag in HASHTAGS:
        d, err = get("ig_hashtag_search", {"user_id": IG_ID, "q": tag})
        if err or not d or not d.get("data"):
            err = err or {"message": "no hashtag id returned"}
            print(f"#{tag}: search error {err}")
            results["errors"].append({"hashtag": tag, "stage": "search", **err})
            continue
        hid = d["data"][0]["id"]
        entry = {"hashtag_id": hid, "media": []}
        seen = set()
        for edge in ("top_media", "recent_media"):
            m, err = get(f"{hid}/{edge}", {"user_id": IG_ID, "fields": FIELDS, "limit": 50})
            if err:
                print(f"#{tag} {edge}: error {err}")
                results["errors"].append({"hashtag": tag, "stage": edge, **err})
                continue
            for item in m.get("data", []):
                if item["id"] in seen:
                    continue
                seen.add(item["id"])
                cap = item.get("caption") or ""
                rec = {"id": item["id"], "edge": edge, "permalink": item.get("permalink"),
                       "timestamp": item.get("timestamp"), "media_type": item.get("media_type"),
                       "caption": cap[:300], "mentions": mentions(cap), "phones": phones(cap)}
                entry["media"].append(rec)
                for h in rec["mentions"]:
                    handle_count[h] += 1; handle_tags[h].add(tag)
                    if len(handle_links[h]) < 5: handle_links[h].append(rec["permalink"])
                for p in rec["phones"]:
                    phone_count[p] += 1; phone_tags[p].add(tag)
                    if len(phone_links[p]) < 5: phone_links[p].append(rec["permalink"])
        results["hashtags"][tag] = entry
        print(f"#{tag}: {len(entry['media'])} media")

    results["candidates"] = {
        "handles": [{"handle": h, "count": c, "hashtags": sorted(handle_tags[h]), "permalinks": handle_links[h]}
                    for h, c in handle_count.most_common()],
        "phones": [{"phone": p, "count": c, "hashtags": sorted(phone_tags[p]), "permalinks": phone_links[p]}
                   for p, c in phone_count.most_common()],
    }
    save(results)
    total = sum(len(e["media"]) for e in results["hashtags"].values())
    print(f"done: {total} media, {len(handle_count)} handles, {len(phone_count)} phones, "
          f"{len(results['errors'])} errors")


if __name__ == "__main__":
    main()
