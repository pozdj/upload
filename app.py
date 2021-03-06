import os, boto3, json
from uuid import uuid4
from flask import Flask, render_template, jsonify, request, send_from_directory
app = Flask(__name__)

sqs = boto3.resource('sqs')
queue = sqs.get_queue_by_name(QueueName='last-album')
bucket_address = 'https://s3.eu-central-1.amazonaws.com/167985-last'

@app.route("/")
def index():
  return render_template('upload_form.html', uploadButtonName="send")

@app.route("/upload", methods=['POST'])
def upload():
  files = request.files
  album = {
    'photos': []
  }
  for f in files.getlist('file'):
    print f
    destination_name = generate_filename(f)
    album['photos'].append('%s/%s' % (bucket_address, destination_name))
    upload_s3(f, destination_name)
  return jsonify(album)

@app.route("/request_album_creation", methods=['POST'])
def request_album_creation():
  combinedField = request.form['combinedField']
  print('received string: '+combinedField)
  receivedFields = combinedField.split("##%%$$")
  print('email: '+receivedFields[0]) 
  print('title: '+receivedFields[1])   

  
  photosCount = len(request.form)
  urls = []
  for index in range(0, photosCount-1):
    key = 'photos_%s' % index
    urls.append(request.form[key])

  album = {
    'sent_to': receivedFields[0],
	'albumTitle': receivedFields[1],
    'photos': urls
  }
  dataAsString = json.dumps(album)
  response = queue.send_message(MessageBody=dataAsString)
  return render_template('upload_success.html')

def upload_s3(source_file, destination_filename):
  bucket_name = '167985-last'
  s3 = boto3.resource('s3')
  bucket = s3.Bucket(bucket_name)
  bucket.put_object(Key=destination_filename, Body=source_file, ACL='public-read')

def generate_filename(source_file):
  destination_filename = "photos/%s/%s" % (uuid4().hex, source_file.filename)
  return destination_filename

if __name__ == "__main__":
    app.run(host='0.0.0.0', debug=True)
