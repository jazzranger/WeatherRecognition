from flask import Flask
from img_tools import img_tools
from flask import request

app = Flask(__name__)


@app.route('/download')
def download_img(*args, **kwargs):
    if request.method == 'GET':
        img_name = request.args.get("img_name")
        return img_tools.download_img(img_name)


@app.route('/upload')
def upload_img(*args, **kwargs):
    if request.method == 'PUT':
        img_name = request.args.get("img_name")
        return img_tools.upload_img(img_name)
