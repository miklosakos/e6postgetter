import requests, os, subprocess, io, base64
from flask import Flask, Response, request, send_file
from dotenv import load_dotenv

load_dotenv()
username = os.getenv("username")
apikey = os.getenv("apikey")
tags = os.getenv("tags")
gitcommit = subprocess.check_output(["git", "rev-parse", "--short", "HEAD"]).strip().decode("utf-8")
rating = os.getenv("rating")
blacklisted = os.getenv("blacklisted_tags")
base_url = os.getenv("base_url")
base_url = base_url.split('.')
default_tags = os.getenv("default_tags")
attack_bots = os.getenv("attack_bots")
ua = f"{".".join(base_url)}/{gitcommit} ({username})"
shortcuticon = "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AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAyWYkAMduEwDIbBcPxmwXKMVqGA3FaxgAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA////////8P///+B////gA///4AP//gAB//wAAf/8AAP//AAD//wAA//8AAH//4AB//+AAf//gAH8P8AB+A/8I/gA/H/4AP//4AB//4AA//+AAP//gAA//4AAP/+AAB//gAAf//AAP//wAD//+AP////H//////////////////8="
notfoundhtml = """
<html>
<meta charset="UTF-8" />
<meta name="viewport" content="width=device-width" />
<style>
:root {
            --bg-color: #0d0d11;
            --text-color: #e0e0e0;
            --muted-color: #888899;
            --glitch-cyan: #00ffff;
            --glitch-magenta: #ff0055;
        }

        html, body {
            height: 100%;
            margin: 0;
            overflow: hidden;
            background-color: var(--bg-color);
            color: var(--text-color);
            font-family: monospace;
        }

        body {
            display: grid;
            place-content: center;
            text-align: center;
            position: relative;
        }

        .content {
            z-index: 3;
            position: relative;
        }

        .sadface {
            font-size: 5rem;
            font-weight: bold;
            margin: 0 0 1rem 0;
            display: inline-block;
        }

        .msg {
            font-size: 1.1rem;
            color: var(--muted-color);
            margin: 0;
            letter-spacing: 1px;
        }

        .highlight {
            color: var(--glitch-cyan);
        }

        body::before {
            content: "";
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: repeating-linear-gradient(
                0deg,
                rgba(0, 0, 0, 0.3),
                rgba(0, 0, 0, 0.3) 1px,
                transparent 1px,
                transparent 2px
            );
            pointer-events: none;
            z-index: 2;
        }

        body::after {
            content: "";
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: linear-gradient(90deg, rgba(0,255,255,0.03), rgba(255,0,85,0.03));
            pointer-events: none;
            z-index: 1;
            animation: glitch-anim 2s infinite steps(2, start);
        }

        @keyframes glitch-anim {
            0% {
                transform: translate(0, 0);
                clip-path: inset(10% 0 70% 0);
            }
            20% {
                transform: translate(-5px, 5px);
                clip-path: inset(40% 0 30% 0);
            }
            40% {
                transform: translate(5px, -5px);
                clip-path: inset(80% 0 5% 0);
            }
            60% {
                transform: translate(-2px, 2px);
                clip-path: inset(20% 0 50% 0);
            }
            80% {
                transform: translate(3px, -3px);
                clip-path: inset(60% 0 10% 0);
            }
            100% {
                transform: translate(0, 0);
                clip-path: inset(30% 0 40% 0);
            }
        }
</style>
</head>
<body>
<div class="content">
<p class="sadface">:(</p>
<p class="msg">Looked far and wide and the great e6 returned nothing.</p>
</div>
</body>
</html>
"""
url = "https://e621.net/posts.json"
def tagbuilder(inctag):
    print(inctag)
    params = {
        'tags': f'{tags} {inctag} {blacklisted} rating:{rating} order:random',
        'limit': 1 
    }
    return params

headers = {
        'User-Agent': ua
}
auth = (username, apikey)
def buildresphdr(srcimg, othersources, tags, uploader, desc):
    e6tags = ",".join(tags)
    if len(e6tags) > 100:
        e6tags = e6tags[:97] + "..."

    if len(desc) > 100:
        desc = desc[:97] + "..."

    resphdrs = {
        'X-Powered-By': f'{".".join(base_url)} app',
        'X-Source-Code': 'https://github.com/miklosakos/e6postgetter',
        'Access-Control-Allow-Origin': '*',
        'X-Source': 'https://e621.net',
        'E6-Post': f'https://e621.net/posts/{srcimg}',
        'E6-Other-Sources': " ".join(othersources),
        'E6-Tags': e6tags,
        'E6-Uploader': uploader,
        'E6-Desc': desc
    }
    return resphdrs

def nuke_bots(total_bytes, chunk_size = 4*1024*1024):
    bytes_sent = 0
    while bytes_sent < total_bytes:
        to_read = min(chunk_size, total_bytes - bytes_sent)
        yield os.urandom(to_read)
        bytes_sent =+ to_read

app = Flask(__name__)

@app.route('/')
def index():
    hosthdr = request.headers.get('Host', '')
    inctag = hosthdr.split('.')
    tags_str=""
    if inctag[0] == base_url[0] or inctag[0] == "www":
        inctag[0] = default_tags
        print(inctag[0])
    elif "-" in inctag[0]:
        tags_str = " ".join(["rating:safe" if tag == "sfw" or tag == "safe" else tag for tag in inctag[0].split('-')])
        print(tags_str)
        inctag[0]=tags_str
    elif inctag[0] == "sfw" or inctag[0] == "safe":
        inctag[0]="rating:safe"
    elif inctag[0] == "help":
        myurl = ".".join(base_url)
        if os.getenv("tags") == "" or os.getenv("tags") is None:
            taginfo = "The following tags are used globally: none"
        else:
            taginfo = f'The following tags are used globally: {os.getenv("tags")}'
        return Response(f"Help for {myurl}\n=====================================================================\nVisiting {myurl} or www.{myurl} will default to the '{default_tags}' tag(s) on e621.\nYou can be granular with your tags by specifying a '-' separated list as a subdomain, i.e. fox-gay-sfw.{myurl}. This will be the equivalent of fox gay rating:safe on e621.\n!! WARNING !!\nSometimes posts on e621 are mislabeled and/or misrated and thus NSFW content may still appear despite the sfw/rating:safe search tag! Always proceed with caution and the expectation you'll see NSFW content!\n!! WARNING !!\nThe implementation also allows for tags that have an '_', i.e. chastity_cage-femboy.{myurl}. This will be the equivalent of chastity_cage femboy on e621.\n{taginfo}\nThe following filter is used for ratings: {rating}\nThe following tags are blacklisted and won't appear in the roster: {blacklisted} to provide some filtering.\nSource code available at https://github.com/miklosakos/e6postgetter\n", status=200, mimetype='text/plain')

    resp = requests.get(url, params=tagbuilder(inctag[0]), headers=headers, auth=auth)
    if not resp.json().get('posts'):
        return Response(notfoundhtml, status=404, mimetype='text/html')

    base = resp.json()['posts'][0]

    if not base.get('file') or not base['file'].get('url'):
        return Response(notfoundhtml, status=404, mimetype='text/html')

    img = requests.get(base['file']['url'], headers=headers)
    imgid = base['id']
    sources = base['sources']
    tags = base['tags']['general']
    uploader = base['uploader_name']
    desc = base['description']
    raw_headers = buildresphdr(imgid, sources, tags, uploader, desc)
    clean_headers = {
        k: str(v).replace('\n', ' ').replace('\r', '').strip().encode('ascii', 'ignore').decode('ascii')
        for k, v in raw_headers.items()
    }
    return Response(img.content, mimetype=img.headers['Content-Type'], headers=clean_headers)

@app.route('/favicon.ico')
def favicon():
    scb = base64.b64decode(shortcuticon)
    scio = io.BytesIO(scb)
    return send_file(scio, mimetype='image/x-icon')

@app.route('/sitemap.xml')
def sitemap():
    return Response(notfoundhtml, status=404, mimetype='text/html')

if attack_bots:
    @app.route('/<path:subpath>')
    def attack(subpath):
       garbage_amount=1024**5
       return Response(
               nuke_bots(garbage_amount),
               mimetype='text/plain',
                headers={"Content-Length": str(garbage_amount)}
               )

if __name__ == '__main__':
    app.run()
