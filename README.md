# Cropification

Cropification is a web-based Agriculture Facilitation System, that provides object detection using YOLOv3 and trained on custom dataset(Crop RGB).

It's implemented using django framework and python libraries. 

## Dependencies
- Django
- Python
- OpenCV
- PostgreSQL

You also need to download the yolo6000.weights file and place it in the "weights" directory.

You can download the weights from the following link (this action may require permission):
```
https://drive.google.com/open?id=1-0jFXFO8xIqhgio6XgPjmmGDqIQVlfmx
```

## Usage
Firstly, you need to create a database using postgresql, then change `DATABASES` values with your credentials in `setting.py` file.
Then to activate enviormental variable in `.env` file you need to make a virtualenviorment with `pipenv` and to activate it, run following command in your cmd:
```
pipenv shell
```
To install all dependencies:
```
pip install -r requirements.txt
```
To run server:
```
pip manage.py collectstatic
pip manage.py makemigrations
pip manage.py migrate
pip manage.py runserver
```
Server will start running on localhost(127.0.0.1/8000).

Inorder to use the provided services, you need to signup.

## Example
The website also shows the detection output with bounding boxes around the detected objects. There will be no box if the input doesn't contain any object.

### Input (Object Detection)
![]()

## TO-DO
- Make website live and deploy it on Google App Engine


## Contribute
If you want to contribute and/or find any bug, feel free to do a pull request!
