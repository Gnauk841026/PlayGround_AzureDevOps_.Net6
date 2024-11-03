from flask import Flask, jsonify
import boto3
import os
import subprocess
import glob

app = Flask(__name__)

# S3 Settings
BUCKET_NAME = 'demo-bucket-20240930'
DOWNLOAD_PATH = '/home/Demo/App'  # Path where files are downloaded and unzipped

AWS_ACCESS_KEY_ID = os.getenv('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = os.getenv('AWS_SECRET_ACCESS_KEY')

# Initialize S3 client
s3_client = boto3.client(
    's3',
    aws_access_key_id=AWS_ACCESS_KEY_ID,
    aws_secret_access_key=AWS_SECRET_ACCESS_KEY
)

def stop_app():
    """
    Stops the currently running .NET application.
    """
    try:
        # Stop the current running application (assumes using pkill to kill the dotnet process)
        subprocess.run(['pkill', '-f', 'dotnet MyWebApp.dll'], check=True)
        print("Stopped the running application.")
    except subprocess.CalledProcessError:
        print("No running application found or failed to stop.")

def start_app():
    """
    Starts the .NET application.
    """
    try:
        # Start the application in the background
        subprocess.Popen(['dotnet', 'MyWebApp.dll'], cwd=DOWNLOAD_PATH)
        print("Started the application.")
    except Exception as e:
        print(f"Failed to start the application: {e}")

def get_latest_objects():
    """
    Gets the latest and second latest objects from the S3 bucket.
    """
    response = s3_client.list_objects_v2(Bucket=BUCKET_NAME)
    objects = sorted(response.get('Contents', []), key=lambda x: x['LastModified'], reverse=True)
    if len(objects) < 2:
        raise Exception("Not enough files in the bucket for rollback.")
    return objects[0], objects[1]

def download_and_extract(object_key):
    """
    Downloads the specified object from S3 and extracts it.
    """
    local_zip_path = os.path.join(DOWNLOAD_PATH, 'latest_app.zip')
    s3_client.download_file(BUCKET_NAME, object_key, local_zip_path)
    print(f"Downloaded {object_key} to {local_zip_path}")

    # Unzip the downloaded file
    subprocess.run(['unzip', '-o', local_zip_path, '-d', DOWNLOAD_PATH], check=True)
    print(f"Extracted {local_zip_path} to {DOWNLOAD_PATH}")

@app.route('/latest', methods=['POST'])
def latest():
    """
    Deploy the latest version of the application.
    """
    try:
        latest_obj, _ = get_latest_objects()
        stop_app()
        download_and_extract(latest_obj['Key'])
        start_app()
        return jsonify({'message': 'Deployed latest version successfully.'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/rollback', methods=['POST'])
def rollback():
    """
    Rollback to the second latest version of the application.
    """
    try:
        _, rollback_obj = get_latest_objects()
        stop_app()
        download_and_extract(rollback_obj['Key'])
        start_app()
        return jsonify({'message': 'Rolled back to previous version successfully.'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
