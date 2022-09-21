from flask import Flask, render_template, request, jsonify, redirect, url_for
from pymongo import MongoClient
from datetime import datetime


app = Flask(__name__)

# client = MongoClient('localhost', 27017)
client = MongoClient('15.165.204.234', 27017, username="test", password="test")
db = client.dbsparta_plus_week_1


@app.route('/')
def main():
    return render_template("index.html")

@app.route("/dd")
def dd():
    return render_template("dd.html")

@app.route('/info', methods=["POST"])
def info_post():
    username_receive = request.form['username_give']
    star_receive = request.form['star_give']
    comment_receive = request.form['comment_give']
    file = request.files["file_give"]

    extension = file.filename.split('.')[-1]

    today = datetime.now()
    mytime = today.strftime('%Y-%m-%d-%H-%M-%S')

    filename = f'file-{mytime}'
    save_to = f'static/{filename}.{extension}'
    file.save(save_to)

    doc = {
        'username': username_receive,
        'star': star_receive,
        'comment': comment_receive,
        'file': f'{filename}.{extension}'
    }
    db.users.insert_one(doc)
    return jsonify({'msg': '등록 완료!'})

@app.route('/info', methods=["GET"])
def info_get():
    comment_list = list(db.users.find({}, {'_id': False}))
    return jsonify({'users': comment_list})

@app.route('/toilet', methods=["GET"])
def get_toilet():
    # 맛집 목록을 반환하는 API
    toilet_list = list(db.toilet.find({}, {'_id': False}))
    # toilet_list 라는 키 값에 맛집 목록을 담아 클라이언트에게 반환합니다.
    return jsonify({'result': 'success', 'toilet_list': toilet_list})

if __name__ == '__main__':
    app.run('0.0.0.0', port=5000, debug=True)