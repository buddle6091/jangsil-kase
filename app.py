from flask import Flask, render_template, request, jsonify, redirect, url_for
from pymongo import MongoClient
from datetime import datetime, timedelta
from werkzeug.utils import secure_filename
# 토큰의 만료 기한
import jwt
import hashlib

app = Flask(__name__)

# db연결부분
# client = MongoClient('localhost', 27017)
client = MongoClient('15.165.204.234', 27017, username="test", password="test")
db = client.dbsparta_plus_week_1

# JWT : JSON Web Token의 약자로 전자 서명 된 URL-safe (URL로 이용할 수있는 문자 만 구성된)의 JSON
# 아래의 키는 JWT 토큰 생성에 필요한 비밀문자열이며, 서버만 알고 있기에 내 서버에서만 토큰을 인코딩 / 디코딩이 가능
SECRET_KEY = 'SPARTA'

# 토큰 값이 있는지 확인 하고, 존재하면 index.html을 렌더링
@app.route('/')
def home():
    # 로그인에서 발급한 JWT 토큰 / 쿠키는 브라우저에 임시로 저장되는 정보, 휘발성
    token_receive = request.cookies.get('mytoken')
    try:
        # 받은 토큰을 가지고 payload 값을 받아오려고 시도 (decode : 복호화)
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
        # 정상이면 index.html 로 리다이렉팅
        return render_template('index.html')
    # 로그인 시간이 만료
    except jwt.ExpiredSignatureError:
        return redirect(url_for("login", msg="로그인 시간이 만료되었습니다."))
    # 로그인 정보가 존재하지 않음
    except jwt.exceptions.DecodeError:
        return redirect(url_for("login", msg="로그인 정보가 존재하지 않습니다."))


@app.route('/login')
def login():
    msg = request.args.get("msg")
    return render_template('login.html', msg=msg)

# 로그인 기능을 구현, 입력한 Id ('username_give'), Pw ('password_give')를 받아와 DB의 회원 정보와
# 잘 맞는지 매칭하는 함수. 그 과정에서 보안을 위해 해시값으로 넣은 비밀번호를 풀어 대조하여 로그인을 통과시키는 방식

@app.route('/sign_in', methods=['POST'])
def sign_in():
    # 로그인
    username_receive = request.form['username_give']
    password_receive = request.form['password_give']

    # input으로 받은 비밀번호를 해시값으로 변환하여 db상의 해시값과 비교
    pw_hash = hashlib.sha256(password_receive.encode('utf-8')).hexdigest()
    result = db.users.find_one({'username': username_receive, 'password': pw_hash})

    # 만약 대조한 값이 존재 하면, 토큰 값을 클라이언트에게 전달을 하는 과정
    if result is not None:
        payload = {
         'id': username_receive,
         #'exp': datetime.utcnow() + timedelta(seconds=60 * 60 * 24)  # 로그인 24시간 유지
        }
        # 위의 payload를 다시 한번 암호화하여 유저에게 전달해 줌
        token = jwt.encode(payload, SECRET_KEY, algorithm='HS256')

        # 토큰을 넘겨줌
        return jsonify({'result': 'success', 'token': token})
    # 찾지 못하면
    else:
        return jsonify({'result': 'fail', 'msg': '아이디/비밀번호가 일치하지 않습니다.'})

#
@app.route('/sign_up/save', methods=['POST'])
def sign_up():
    # 회원가입
    username_receive = request.form['username_give']
    password_receive = request.form['password_give']
    password_hash = hashlib.sha256(password_receive.encode('utf-8')).hexdigest()
    # DB에 저장
    doc = {
        "username": username_receive,
        "password": password_hash
    }
    db.users.insert_one(doc)
    return jsonify({'result': 'success'})


@app.route('/sign_up/check_dup', methods=['POST'])
def check_dup():
    # ID 중복확인
    username_receive = request.form['username_give']
    exists = bool(db.users.find_one({'username': username_receive}))
    return jsonify({'result': 'success', 'exists': exists})

# 메인
@app.route('/')
def main():
    return render_template("index.html")

# 리뷰등록 창에서 리뷰 등록한 데이터 넘겨주기
@app.route('/info', methods=["POST"])
def info_post():
    username_receive = request.form['username_give']
    star_receive = request.form['star_give']
    comment_receive = request.form['comment_give']
    file = request.files["file_give"]
    title_receive = request.form['title_give']

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
        'file': f'{filename}.{extension}',
        'title': title_receive
    }
    db.review.insert_one(doc)
    return jsonify({'msg': '등록 완료!'})

# 리뷰데이터에서 데이터 가져오기
@app.route('/info', methods=["GET"])
def info_get():
    comment_list = list(db.review.find({}, {'_id': False}))
    return jsonify({'users': comment_list})

# toilet_list 라는 키 값에 화장실 목록을 담아 클라이언트에게 반환합니다.
@app.route('/toilet', methods=["GET"])
def get_toilet():
    toilet_list = list(db.toilet.find({}, {'_id': False}))
    return jsonify({'result': 'success', 'toilet_list': toilet_list})

if __name__ == '__main__':
    app.run('0.0.0.0', port=5000, debug=True)