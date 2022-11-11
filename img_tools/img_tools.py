import requests
import json

from tokens import ACCESS_TOKEN

DISK_URL = 'https://cloud-api.yandex.net/v1/disk/resources'


def download_img(img_name):
    """
    Загрузка картинки с диска
    :param img_name: название файла
    :return:
    """
    # Получаем ссылку для скачивания
    download_url = requests.get(f"{DISK_URL}/download",
                                params={
                                    "path": f"/dataset/{img_name}",
                                },
                                headers={
                                    "Authorization": ACCESS_TOKEN
                                })

    if download_url.status_code == 200:
        download_url = json.loads(download_url.text)
        # Скачиваем файл
        img = requests.get(download_url.get('href'),
                           headers={
                               "Authorization": ACCESS_TOKEN
                           })
        if img.status_code == 200:
            return img.content


def upload_img(img_name, img_data):
    """
    Загрузка на диск
    :param img_name: название файла
    :param img_data: bytearray картинки
    """
    upload_url = requests.get(f"{DISK_URL}/upload",
                              params={
                                  "path": f"/dataset/{img_name}",
                                  "overwrite": False
                              },
                              headers={
                                  "Authorization": ACCESS_TOKEN
                              })
    if upload_url.status_code == 200:
        download_url = json.loads(upload_url.text)
        # Загружаем файл
        img = requests.put(download_url.get('href'),
                           data=img_data
                           )
        if img.status_code == 200:
            return True
