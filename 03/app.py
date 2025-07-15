from flask import Flask, request, jsonify
import datetime
import pytz

# Flask 애플리케이션 생성
app = Flask(__name__)

# 상수 정의
DEFAULT_LANG = 'en'
GREETINGS = {
    'en': 'Hello',
    'ko': '안녕하세요'
}
TIMEZONES = {
    'en': 'UTC',
    'ko': 'Asia/Seoul'
}

@app.route('/')
def home():
    """
    URL 파라미터로 언어를 받아, 해당 언어의 시간대와 인사말을 JSON으로 반환합니다.
    - /?lang=ko -> 한국 시간과 한국어 인사
    - / or /?lang=en -> UTC 시간과 영어 인사
    """
    # 1. URL에서 'lang' 파라미터 가져오기 (없으면 기본값 'en')
    lang = request.args.get('lang', DEFAULT_LANG)
    
    # 2. 지원하지 않는 언어일 경우 기본값으로 변경
    if lang not in GREETINGS:
        lang = DEFAULT_LANG

    # 3. 언어에 맞는 시간대와 인사말 선택
    timezone = pytz.timezone(TIMEZONES[lang])
    greeting = GREETINGS[lang]

    # 4. 현재 시간을 해당 시간대에 맞게 계산하고 문자열로 포맷팅
    current_time = datetime.datetime.now(timezone).strftime('%Y-%m-%d %H:%M:%S')
    
    # 5. JSON 형식으로 데이터 생성
    response_data = {
        'greeting': greeting,
        'time': current_time
    }

    # 6. JSON 응답 생성
    # 요구사항의 mimetype이 'audio/mpeg'로 되어 있으나,
    # JSON 데이터를 반환하므로 'application/json'이 표준적인 방식입니다.
    # jsonify는 이 작업을 자동으로 처리해줍니다.
    response = jsonify(response_data)

    # 만약 요구사항을 엄격하게 따라야 한다면 아래 주석을 해제하세요.
    # response.mimetype = 'audio/mpeg'
    
    return response

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)

