import requests, os, subprocess
from flask import Flask, Response, request
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
@app.route('/sitemap.xml')
def favicon():
    return Response(status=404)

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
