from flask import Flask, jsonify
import boto3
import os
import zipfile
import subprocess

app = Flask(__name__)

# S3 設置
BUCKET_NAME = 'demo-bucket-20240930'
DOWNLOAD_PATH = '/home/Demo'  # 下載並解壓的目標路徑

# 初始化 S3 客戶端
s3_client = boto3.client('s3')

def get_sorted_files():
    # 列出 S3 中所有物件
    response = s3_client.list_objects_v2(Bucket=BUCKET_NAME)
    
    if 'Contents' not in response:
        print("Bucket is empty.")
        return []

    # 根據最後修改時間排序，最近的在前
    return sorted(response['Contents'], key=lambda x: x['LastModified'], reverse=True)

def download_and_install(file_key):
    try:
        # 定義本地下載的路徑
        artifact_local_path = os.path.join(DOWNLOAD_PATH, 'artifact.zip')

        # 從 S3 下載指定的 Artifact
        s3_client.download_file(BUCKET_NAME, file_key, artifact_local_path)

        # 解壓縮文件
        with zipfile.ZipFile(artifact_local_path, 'r') as zip_ref:
            zip_ref.extractall(DOWNLOAD_PATH)

        # 執行 .NET 程式 (假設主程式為 MyApp.dll)
        result = subprocess.run(['dotnet', os.path.join(DOWNLOAD_PATH, 'MyApp.dll')], capture_output=True, text=True)

        return {
            "message": "Artifact downloaded, extracted, and application executed successfully.",
            "output": result.stdout
        }

    except Exception as e:
        return {"error": str(e)}

@app.route('/install-latest', methods=['POST'])
def install_latest():
    sorted_files = get_sorted_files()
    if not sorted_files:
        return jsonify({"error": "No files found in S3 bucket"}), 404

    latest_file = sorted_files[0]
    response = download_and_install(latest_file['Key'])
    return jsonify(response)

@app.route('/install-second-latest', methods=['POST'])
def install_second_latest():
    sorted_files = get_sorted_files()
    if len(sorted_files) < 2:
        return jsonify({"error": "Less than two files found in S3 bucket"}), 404

    second_latest_file = sorted_files[1]
    response = download_and_install(second_latest_file['Key'])
    return jsonify(response)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
