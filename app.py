import requests, os 
from flask import Flask, Response, request
from dotenv import load_dotenv

load_dotenv()
username = os.getenv("username")
apikey = os.getenv("apikey")
tags = os.getenv("tags")

rating = os.getenv("rating")
blacklisted = os.getenv("blacklisted_tags")
base_url = os.getenv("base_url")
base_url = base_url.split('.')

attack_bots = os.getenv("attack_bots")

ua = f"yiffer.hu/1.0 ({username})"
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
        'X-Powered-By': 'yiffer.hu app',
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
        inctag[0] = "gay"
        print(inctag[0])
    elif "-" in inctag[0]:
        tags_str = " ".join(["rating:safe" if tag == "sfw" else tag for tag in inctag[0].split('-')])
        print(tags_str)
        inctag[0]=tags_str
    elif inctag[0] == "sfw":
        inctag[0]="rating:safe"
    elif inctag[0] == "help":
        myurl = ".".join(base_url)
        if os.getenv("tags") == "" or os.getenv("tags") is None:
            taginfo = "The following tags are used globally: none"
        else:
            taginfo = f'The following tags are used globally: {os.getenv("tags")}'
        return Response(f"Help for {myurl}\n=====================================================================\nVisiting {myurl} or www.{myurl} will default to the 'gay' tag on e621.\nYou can be granular with your tags by specifying a '-' separated list as a subdomain, i.e. fox-gay-sfw.{myurl}. This will be the equivalent of fox gay rating:safe on e621.\n!! WARNING !!\nSometimes posts on e621 are mislabeled and/or misrated and thus NSFW content may still appear despite the sfw/rating:safe search tag! Always proceed with caution and the expectation you'll see NSFW content!\n!! WARNING !!\nThe implementation also allows for tags that have an '_', i.e. chastity_cage-femboy.{myurl}. This will be the equivalent of chastity_cage femboy on e621.\n{taginfo}\nThe following tags are blacklisted and won't appear in the roster: {blacklisted} to provide some filtering.\nSource code available at https://github.com/miklosakos/e6postgetter\n", status=200, mimetype='text/plain')

    resp = requests.get(url, params=tagbuilder(inctag[0]), headers=headers, auth=auth)
    if not resp.json().get('posts'):
        resp = requests.get(url, params=tagbuilder("gay"), headers=headers, auth=auth)

    base = resp.json()['posts'][0]

    if not base.get('file') or not base['file'].get('url'):
        return Response("No image URL found.", status=404, mimetype='text/plain')

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
    return Response(status=404)

if attack_bots:
    @app.route('/<path:subpath>')
    def attack(subpath):
       garbage_amount=1024**5
       return Response(
               nuke_bots(garbage_amount),
               mimetype='image/png',
                headers={"Content-Length": str(garbage_amount)}
               )

if __name__ == '__main__':
    app.run()
