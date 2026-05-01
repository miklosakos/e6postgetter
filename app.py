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

app = Flask(__name__)

@app.route('/')
def index():
    resp = requests.get(url, params=params, headers=headers, auth=auth)
    print(resp.json()['posts'][0]['file']['url'])
    img = requests.get(resp.json()['posts'][0]['file']['url'], headers=headers)
    return Response(img.content, mimetype=img.headers['Content-Type'])

if __name__ == '__main__':
    app.run()
