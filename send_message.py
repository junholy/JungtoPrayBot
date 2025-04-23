from telegram import Bot
from datetime import datetime, timedelta
import pytz
import asyncio
import json
import os
import requests

# 1. 봇 토큰 설정
TOKEN = '7532536299:AAFzFoD584PAG3ZeANL-TAb_xB7tMLi2s6o'

# 2. 설정 파일 경로
CONFIG_FILE = 'config.json'

# 3. 기본 설정
default_config = {
    "chats": {
        # 예시: "-1002357866572": {"topic_id": 6}
    }
}

# 4. 설정 로드 함수
def load_config():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, 'r') as f:
            return json.load(f)
    # 설정 파일이 없으면 기본 설정 저장 후 반환
    save_config(default_config)
    return default_config

# 5. 설정 저장 함수
def save_config(config):
    with open(CONFIG_FILE, 'w') as f:
        json.dump(config, f, indent=4)

# 6. 텔레그램 API에서 업데이트 가져오기
def get_updates():
    url = f"https://api.telegram.org/bot{TOKEN}/getUpdates"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    return None

# 7. /set_topic 명령어 확인 및 설정 업데이트
def update_config_from_updates():
    updates = get_updates()
    if not updates or not updates.get("ok"):
        print("업데이트를 가져올 수 없습니다.")
        return
    
    config = load_config()
    
    # 마지막으로 처리한 update_id 가져오기
    last_processed_id = config.get("last_processed_update_id", 0)
    updated = False
    max_update_id = last_processed_id
    
    print("텔레그램 업데이트 처리 시작...")
    
    for update in updates.get("result", []):
        update_id = update["update_id"]
        max_update_id = max(max_update_id, update_id)
        
        # 이미 처리한 업데이트는 건너뛰기
        if update_id <= last_processed_id:
            continue
        
        # 메시지 확인
        if "message" in update:
            message = update["message"]
            
            # 디버깅을 위한 메시지 정보 출력
            print(f"메시지 ID: {update_id}, 내용: {message.get('text', '텍스트 없음')}")
            
            # /set_topic 명령어 확인 (정확히 일치하는지 확인)
            if "text" in message and message["text"].strip() == "/set_topic":
                chat_id = str(message["chat"]["id"])
                message_thread_id = message.get("message_thread_id")
                
                print(f"'/set_topic' 명령어 감지: 채팅 {chat_id}, 토픽 {message_thread_id}")
                
                if message_thread_id:
                    # 설정 업데이트
                    if "chats" not in config:
                        config["chats"] = {}
                    
                    if chat_id not in config["chats"]:
                        config["chats"][chat_id] = {}
                    
                    config["chats"][chat_id]["topic_id"] = message_thread_id
                    print(f"새로운 토픽 설정 완료: 채팅 {chat_id}, 토픽 {message_thread_id}")
                    updated = True
    
    # 마지막 처리된 update_id 저장
    if max_update_id > last_processed_id:
        config["last_processed_update_id"] = max_update_id + 1
        updated = True
    
    if updated:
        save_config(config)
        print("설정이 업데이트되었습니다.")
    else:
        print("업데이트할 설정이 없습니다.")
    
    # 현재 설정된 채팅/토픽 정보 출력
    print("현재 설정된 채팅/토픽:")
    for chat_id, chat_config in config.get("chats", {}).items():
        if "topic_id" in chat_config:
            print(f"채팅 ID: {chat_id}, 토픽 ID: {chat_config['topic_id']}")

# 8. 메시지 생성 함수
def create_message():
    # 한국 시간대 설정
    korea_tz = pytz.timezone('Asia/Seoul')
    today = datetime.now(korea_tz)
    
    # 불기 연도 계산 (서기 + 544)
    buddhist_year = today.year + 544
    
    # 요일 한글 변환
    weekdays = ['월', '화', '수', '목', '금', '토', '일']
    weekday_korean = weekdays[today.weekday()]
    
    # 결사 일자 계산
    start_date = datetime(2025, 2, 16, tzinfo=korea_tz)  # 입재식 날짜
    days_passed = (today - start_date).days
    
    # 현재 날짜가 입재식 날짜보다 이전인 경우 D-Day로 표시
    if today < start_date:
        days_to_start = (start_date - today).days
        days_message = f"입재식 D-{days_to_start}"
    else:
        days_message = f"1차 천일결사 8차 백일기도 {days_passed}일 째 기도"
    
    # 메시지 템플릿
    message = f"""[불기 {buddhist_year}년 {today.month}월 {today.day}일 {weekday_korean}요일] 
정토행자 제2차 만일결사 중
{days_message}

🙏 명심문: "우리는 모자이크 붓다입니다."

[개인약속]

<전법>
백일법문, 불교대학, 행복학교 1명이상 인연맺기 및 
 특별정진 참여 계획 세우고 실행하기

[모둠약속]
<모둠별로 의논 후 모둠활동 3회 이상 진행> 
전법(백일법문, 불교대학, 행복학교), 백일법문 오프 프로그램 참여 중 선택하여 진행

🔻천일결사 기도 https://pray.jungto.org"""
    
    return message

# 9. 자동 메시지 전송 함수
async def send_daily_message():
    # 먼저 설정 업데이트
    update_config_from_updates()
    
    config = load_config()
    message = create_message()
    bot = Bot(token=TOKEN)
    
    # 설정 파일에 저장된 모든 채팅/토픽에 메시지 전송
    for chat_id, chat_config in config.get("chats", {}).items():
        if "topic_id" in chat_config:
            try:
                await bot.send_message(
                    chat_id=chat_id,
                    text=message,
                    message_thread_id=chat_config["topic_id"]
                )
                print(f"메시지 전송 성공: 채팅 {chat_id}, 토픽 {chat_config['topic_id']}")
            except Exception as e:
                print(f"메시지 전송 실패: {e}")

# 10. 메인 함수
async def main():
    await send_daily_message()

if __name__ == "__main__":
    asyncio.run(main())
