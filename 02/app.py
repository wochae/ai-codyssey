from flask import Flask

# Flask 애플리케이션 생성
app = Flask(__name__)

# '/' 경로에 대한 요청을 처리하는 함수 정의
@app.route('/')
def hello_world():
    return "Hello, DevOps!"

# 이 스크립트가 직접 실행될 때만 웹 서버를 구동
if __name__ == '__main__':
    # 외부에서 접근 가능하도록 host='0.0.0.0'으로 설정
    # 포트는 8080으로 지정
    app.run(host='0.0.0.0', port=8080)