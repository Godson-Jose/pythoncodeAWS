import os
from flask import Flask, render_template, request
import boto3
import pymysql

app = Flask(__name__)

bucket_name = os.getenv("S3_BUCKET_NAME", "student-app-bucket-godson")

def get_db_connection():
    return pymysql.connect(
        host=os.getenv("DB_HOST", "database-1.c3miyqiu6jgi.eu-north-1.rds.amazonaws.com"),
        port=int(os.getenv("DB_PORT", 3306)),
        user=os.getenv("DB_USER", "admin"),
        password=os.getenv("DB_PASSWORD", "Godson0505"),
        database=os.getenv("DB_NAME", "studentdb"),
        autocommit=True
    )

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/register', methods=['POST'])
def register():
    name = request.form['name']
    email = request.form['email']
    course = request.form['course']

    photo = request.files['photo']

    s3 = boto3.client('s3')
    s3.upload_fileobj(
        photo,
        bucket_name,
        photo.filename
    )

    photo_url = f"https://{bucket_name}.s3.amazonaws.com/{photo.filename}"

    db = get_db_connection()
    try:
        with db.cursor() as cursor:
            sql = """
            INSERT INTO students (name, email, course, photo_url)
            VALUES (%s, %s, %s, %s)
            """
            cursor.execute(sql, (name, email, course, photo_url))
    finally:
        db.close()

    return "Student Registered Successfully"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
