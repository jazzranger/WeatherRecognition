from flask import Flask
from flask_cors import CORS, cross_origin
from img_tools import img_tools
from flask import request
import json
from torch import load, max, sum, device, tensor, cat
from torchvision import datasets, models, transforms
from PIL import Image
import io

app = Flask(__name__)
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'


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

        model = load('model.pth', map_location=device('cpu'))

        transform = transforms.Compose([
            transforms.Resize(256),
            transforms.CenterCrop(244),
            transforms.ToTensor(),
            transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
            ])

        image = transform(imageFile)

        predict = model(image)
        print(predict)
    return json.dumps({'result': predict})

app.run()
