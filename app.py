import json
import os
import boto3
from werkzeug.utils import secure_filename
from flask import Flask, render_template, request, redirect
from backend import backend
from communication import communication


def get_configuration(input):
    with open(input) as filestream:
        obj = json.load(filestream)
    return obj


def upload_files(uploaded_file, s3_file_name):
    s3_bucket_name = config["aws_sthree_bck"]
    s3 = boto3.client('s3',
                      aws_access_key_id=config['aws_ak'],
                      aws_secret_access_key=config['aws_sk'])
    s3.upload_file(uploaded_file, s3_bucket_name, s3_file_name)


app = Flask(__name__)
config = get_configuration(input="config.json")
db = backend(config)
session = {}
backup_path = 'storage_files'


@app.route('/')
def base_page():
    return(redirect(f'{base_url}/login'))


@app.route('/login', methods=['POST', 'GET'])
def login_page():

    if request.method == 'POST':
        print(request.form)
        if request.form['sigin'] == "Login":
            eml = request.form.get('email')
            pwd = request.form.get('password')
            cmd = f"select * from accounts  where email='{eml}' and password='{pwd}'"
            df = db.det_get(cmmd=cmd)
            print("Login method invoked")
            if len(df) != 0:
                session['session'] = {
                    'user': df['username'].values[0], "email": df['email'].values[0]}
                return redirect(f'{base_url}/share')
    return render_template('login.html')


@app.route('/register', methods=['POST', 'GET'])
def register_page():
    print("Login method invoked")
    if request.method == 'POST':
        if request.form['signup'] == "Register":
            user = request.form.get('username')
            print(user)
            email = request.form.get('new_email')
            pass_ = request.form.get('new_password')
            rep_pass = request.form.get('new_rep_password')
            exist_cmd = f"select id from accounts where email='{email}'"
            exist_account = db.det_get(cmmd=exist_cmd)
            if ((pass_ == rep_pass) and (len(exist_account) == 0)):
                insert_account = [
                    {"email": email, "username": user, "password": pass_}]
                db.put_dt(table_name="accounts",
                          json_data=insert_account)
                return redirect(f'{base_url}/login')
    return render_template('register.html')


@app.route('/share', methods=['POST', 'GET'])
def share_files(path=backup_path):
    if 'session' in session:
        user = session['session']['user']
        email = session['session']['email']
        share_s3_url = config['aws_sthree_url']
        sns = communication()
        if not os.path.isdir(path):
            os.mkdir(path)
        if request.method == 'POST':
            if request.form['share'] == "Upload":
                file = request.files['share_files']
                emails = [value for key, value in dict(request.form).items() if (
                    (value is not None) and (value != '') and ('email') in key)]
                if ((file.filename is not None) and (file.filename != '')):
                    filename = secure_filename(file.filename)
                    file.save(f'{path}/{filename}')
                    upload_files(
                        uploaded_file=f'{path}/{filename}', s3_file_name=filename)
                    file_url = share_s3_url+filename
                    file_details = [{'email': email, 'name': filename,
                                     'size': os.path.getsize(f'{path}/{filename}')}]
                    db.put_dt(
                        table_name="files_info", json_data=file_details)
                    sns.make_sub_list(sub_emails=emails, shared_by=user)
                    sns.send_email(message=file_url)
        return render_template('share.html', message=f"Welcome {user}")
    else:
        return redirect(f'{base_url}/login')


host = config['dev_ip']
base = "127.0.0.1"
port = config['port']
base_url = f"http://{base}:{port}"

if __name__ == '__main__':
    app.run(host=host, port=port, debug=False)
