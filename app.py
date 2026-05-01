import requests, os 
from flask import Flask, Response
from dotenv import load_dotenv

load_dotenv()
username = os.getenv("username")
apikey = os.getenv("apikey")
tags = os.getenv("tags")
rating = os.getenv("rating")
ua = f"yiffer.hu/1.0 ({username})"
url = "https://e621.net/posts.json"

params = {
        'tags': f'{tags} rating:{rating} order:random',
        'limit': 1 
}
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
    resp = requests.get(url, params=params, headers=headers, auth=auth)
    base = resp.json()['posts'][0]
    img = requests.get(base['file']['url'], headers=headers)
    imgid = base['id']
    sources = base['sources']
    tags = base['tags']['general']
    uploader = base['uploader_name']
    desc = base['description']
    return Response(img.content, mimetype=img.headers['Content-Type'], headers=buildresphdr(imgid, sources, tags, uploader, desc))

if __name__ == '__main__':
    app.run()
