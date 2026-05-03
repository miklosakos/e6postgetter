# e6postgetter
This is a Python3 Flask app to fetch and return random posts from e621/e926 similar to yiff.gay

## How to use?
- create a user and apikey on e621
- create python3 virtual environment with `python3 -m venv /path/to/venv`
- install required python dependencies with `pip3 install -r requirements.txt`
- optionally install and customize the provided systemd service (`systemd/e6postgetter.service`) to `/lib/systemd/system/e6postgetter.service` 
- fill out your credentials and other info in `env.sample` and save it as `.env`
- create a \*.domain.tld CNAME record to domain.tld (this is how users can specify one specific tag on top of the ones you specified in your `.env`)

### Nginx configuration
```
server {
        listen 80;
        listen [::]:80;
        listen 443 ssl;
        listen [::]:443 ssl;
        ssl_protocols TLSv1.2 TLSv1.3;
        ssl_certificate /path/to/cert.pem;
        ssl_certificate_key /path/to/cert.key;
        server_name $base_url *.$base_url; #specify the same domain for $base_url as the one you set in your .env

        location / {
                proxy_pass http://127.0.0.1:5000;
                proxy_set_header Host   $host;
                proxy_set_header X-Real-IP $remote_addr;
                #add_header Content-Type text/plain;
                #return 200 "OK";
                #return 403;
        }
}
```

## Navigation
You can navigate the served webpage by visiting `$base_url` or `tag.$base_url` or `tag1-tag2-tag3-tag4_withaspace.$base_url`.


