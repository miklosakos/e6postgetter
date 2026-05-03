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
    resphdrs = {
        'X-Powered-By': 'yiffer.hu app',
        'X-Source-Code': 'https://github.com/miklosakos/e6postgetter',
        'Access-Control-Allow-Origin': '*',
        'X-Source': 'https://e621.net',
        'E6-Post': f'https://e621.net/posts/{srcimg}',
        'E6-Other-Sources': " ".join(othersources),
        'E6-Tags': ",".join(tags),
        'E6-Uploader': uploader,
        'E6-Desc': desc
    }
    return resphdrs

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
        return Response(f"Help for {myurl}\n=====================================================================\nVisiting {myurl} or www.{myurl} will default to the 'gay' tag on e621.\nYou can be granular with your tags by specifying a '-' separated list as a subdomain, i.e. fox-gay-safe.{myurl}. This will be the equivalent of fox gay rating:safe on e621.\nThe implementation also allows for tags that have an '_', i.e. chastity_cage-femboy.{myurl}. This will be the equivalent of chastity_cage femboy on e621.\nThe following tags are blacklisted and won't appear in the roster: {blacklisted} to provide some filtering.\nSource code available at https://github.com/miklosakos/e6postgetter\n", status=200, mimetype='text/plain')

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

if __name__ == '__main__':
    app.run()
