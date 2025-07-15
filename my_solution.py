from flask import Flask

# Flask 앱(웹 서버)을 생성.
app = Flask(__name__)

# "Hello" 라는 문자열을 반환.
def hello():
    return "Hello"

# '/' 주소로 접속하면 hello 함수를 실행하라고 알려줍니다.
# 즉, 홈페이지에 접속하면 "Hello"가 보이게 됩니다.
app.add_url_rule("/", "hello", hello)


# 이 파이썬 파일을 직접 실행했을 때 웹 서버를 구동합니다.
if __name__ == "__main__":
    # debug=True 모드는 코드를 수정할 때마다 서버를 자동으로 재시작해줘서 개발 시 편리합니다.
    app.run(debug=True)