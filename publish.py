"""FitEats Instagram scheduler.

Runs inside GitHub Actions. Every run it looks in queue/ for posts whose time
(Indian time) has arrived, publishes them to Instagram, and moves each folder to
posted/ (or failed/ with the error).

A post is a folder in queue/ containing:
  post.json    {"time": "2026-11-21 19:45", "type": "reel" | "image" | "carousel"}
  caption.txt  the caption (hashtags included)
  reel:        video.mp4 (+ optional cover.jpg)
  image:       image.jpg
  carousel:    1.jpg, 2.jpg, ... (2 to 10 images)

Usage: python publish.py          publish everything that is due
       python publish.py check    test the Instagram connection, publish nothing
"""
import json, os, shutil, sys, time, urllib.parse, urllib.request
from datetime import datetime, timedelta, timezone

IST = timezone(timedelta(hours=5, minutes=30))
TOKEN = os.environ.get("IG_TOKEN", "").strip()
REPO = os.environ.get("GITHUB_REPOSITORY", "")
BRANCH = os.environ.get("GITHUB_REF_NAME", "main")
# Instagram-login tokens start with "IG" and use graph.instagram.com with /me.
# System-user / Facebook-login tokens (usually "EAA") use graph.facebook.com with the IG account id.
IG_USER_ID = os.environ.get("IG_USER_ID", "").strip() or "17841449209573024"  # @fit_eats_25
if TOKEN.startswith("IG"):
    API, ME = "https://graph.instagram.com/v21.0", "me"
else:
    API, ME = "https://graph.facebook.com/v21.0", IG_USER_ID


def call(method, url, params=None, data=None, headers=None):
    params = dict(params or {})
    if "rupload" not in url:
        params["access_token"] = TOKEN
    if method == "GET" and params:
        url += "?" + urllib.parse.urlencode(params)
        body = data
    else:
        body = data if data is not None else urllib.parse.urlencode(params).encode()
    req = urllib.request.Request(url, data=body, method=method, headers=headers or {})
    try:
        with urllib.request.urlopen(req, timeout=300) as r:
            return json.loads(r.read() or b"{}")
    except urllib.error.HTTPError as e:
        raise RuntimeError(f"{e.code} {e.read().decode(errors='replace')[:600]}")


def raw_url(folder, name):
    # public repo raw link (Instagram downloads images from a public URL)
    return f"https://raw.githubusercontent.com/{REPO}/{BRANCH}/{folder}/{name}"


def wait_ready(cid, label):
    for _ in range(60):  # up to ~10 min
        st = call("GET", f"{API}/{cid}", {"fields": "status_code,status"})
        code = st.get("status_code")
        if code == "FINISHED":
            return
        if code in ("ERROR", "EXPIRED"):
            raise RuntimeError(f"{label} processing failed: {st}")
        time.sleep(10)
    raise RuntimeError(f"{label} still processing after 10 minutes")


def make_reel(folder, caption):
    p = {"media_type": "REELS", "video_url": raw_url(folder, "video.mp4"), "caption": caption, "share_to_feed": "true"}
    if os.path.exists(os.path.join(folder, "cover.jpg")):
        p["cover_url"] = raw_url(folder, "cover.jpg")
    cid = call("POST", f"{API}/{ME}/media", p)["id"]
    wait_ready(cid, "video")
    return cid


def make_image(folder, caption):
    cid = call("POST", f"{API}/{ME}/media", {"image_url": raw_url(folder, "image.jpg"), "caption": caption})["id"]
    wait_ready(cid, "image")
    return cid


def make_carousel(folder, caption):
    imgs = sorted([f for f in os.listdir(folder) if f.split(".")[0].isdigit() and f.lower().endswith(".jpg")],
                  key=lambda f: int(f.split(".")[0]))
    if not 2 <= len(imgs) <= 10:
        raise RuntimeError(f"carousel needs 2 to 10 images named 1.jpg, 2.jpg ... found {len(imgs)}")
    kids = []
    for im in imgs:
        kid = call("POST", f"{API}/{ME}/media", {"image_url": raw_url(folder, im), "is_carousel_item": "true"})["id"]
        wait_ready(kid, im)
        kids.append(kid)
    cid = call("POST", f"{API}/{ME}/media", {"media_type": "CAROUSEL", "children": ",".join(kids), "caption": caption})["id"]
    wait_ready(cid, "carousel")
    return cid


def publish(folder):
    meta = json.load(open(os.path.join(folder, "post.json")))
    cap_file = os.path.join(folder, "caption.txt")
    caption = open(cap_file, encoding="utf-8").read().strip() if os.path.exists(cap_file) else ""
    kind = meta.get("type", "reel").lower()
    maker = {"reel": make_reel, "image": make_image, "carousel": make_carousel}[kind]
    cid = maker(folder, caption)
    media_id = call("POST", f"{API}/{ME}/media_publish", {"creation_id": cid})["id"]
    link = call("GET", f"{API}/{media_id}", {"fields": "permalink"}).get("permalink", "")
    return media_id, link


def due_time(folder):
    meta = json.load(open(os.path.join(folder, "post.json")))
    return datetime.strptime(meta["time"].strip(), "%Y-%m-%d %H:%M").replace(tzinfo=IST)


def finish(folder, dest, info):
    name = os.path.basename(folder)
    target = os.path.join(dest, name)
    shutil.move(folder, target)
    # posted: drop the heavy media so the repo stays small; failed: keep it for a retry
    for f in (os.listdir(target) if dest == "posted" else []):
        if f.lower().endswith((".mp4", ".mov")):
            os.remove(os.path.join(target, f))
    json.dump(info, open(os.path.join(target, "result.json"), "w"), indent=2)


def main():
    if not TOKEN:
        sys.exit("IG_TOKEN secret is missing. See README step 3.")
    if len(sys.argv) > 1 and sys.argv[1] == "check":
        me = call("GET", f"{API}/{ME}", {"fields": "username" if ME != "me" else "user_id,username,account_type"})
        lim = call("GET", f"{API}/{ME}/content_publishing_limit", {"fields": "quota_usage,config"})
        print("Connected to Instagram:", me)
        print("Publishing usage (last 24h):", lim)
        return
    now = datetime.now(IST)
    for d in ("queue", "posted", "failed"):
        os.makedirs(d, exist_ok=True)
    queue = sorted(os.path.join("queue", d) for d in os.listdir("queue") if os.path.isdir(os.path.join("queue", d)))
    failed = 0
    for folder in queue:
        try:
            when = due_time(folder)
        except Exception as e:
            print(f"SKIP {folder}: bad post.json ({e})"); continue
        if when > now:
            print(f"WAIT {folder}: due {when:%d %b %H:%M} IST"); continue
        print(f"POST {folder} (due {when:%d %b %H:%M} IST)")
        try:
            mid, link = publish(folder)
            print(f"  done: {link}")
            finish(folder, "posted", {"posted_at": datetime.now(IST).isoformat(), "media_id": mid, "permalink": link})
        except Exception as e:
            failed += 1
            print(f"  FAILED: {e}")
            finish(folder, "failed", {"failed_at": datetime.now(IST).isoformat(), "error": str(e)})
    if failed:
        sys.exit(f"{failed} post(s) failed - see the failed/ folder")


if __name__ == "__main__":
    main()
