from flask import Flask, render_template, request, jsonify, redirect, url_for
from pymongo import MongoClient


app = Flask(__name__)

# client = MongoClient('localhost', 27017)
client = MongoClient('15.165.204.234', 27017, username="test", password="test")
db = client.dbsparta_plus_week_1


@app.route('/')
def main():
    return render_template("index.html")

@app.route('/review')
def review():
    return render_template("review.html")

@app.route('/toilet', methods=["GET"])
def get_toilet():
    # 맛집 목록을 반환하는 API
    toilet_list = list(db.toilet.find({}, {'_id': False}))
    # toilet_list 라는 키 값에 맛집 목록을 담아 클라이언트에게 반환합니다.
    return jsonify({'result': 'success', 'toilet_list': toilet_list})

if __name__ == '__main__':
    app.run('0.0.0.0', port=5000, debug=True)