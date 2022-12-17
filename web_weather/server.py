from flask import Flask
from flask_cors import CORS, cross_origin
from img_tools import img_tools
from flask import request
import json
import torch
from torchvision import datasets, models, transforms
from PIL import Image
import io

app = Flask(__name__)
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'

WEATHERS = {
    0: 'cloudy',
    1: 'rain',
    2: 'shine',
    3: 'sunrise',
}


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


@app.route('/predict', methods=['GET', 'POST'])
@cross_origin()
def predict(*args, **kwargs):
    if request.method == 'POST':
        imageBinaryBytes = request.files['file'].read()
        imageStream = io.BytesIO(imageBinaryBytes)
        imageFile = Image.open(imageStream)
        data_transformer = transforms.Compose([
            transforms.ToTensor(),
            transforms.Resize(256),
            transforms.CenterCrop(244),
            transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
        ])
        image = data_transformer(imageFile)
        imgs = torch.stack([image])
        model = torch.load('model.pth', map_location=torch.device('cpu'))
        outputs = model(imgs)
        preds = torch.argmax(outputs, -1)
        return json.dumps({'result': f'Result: {WEATHERS.get(preds.item())}'})


app.run()
