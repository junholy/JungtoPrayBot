from telegram import Bot
from datetime import datetime, timedelta
import pytz
import asyncio
import json
import os
import requests
import sys

# 1. 봇 토큰 설정
TOKEN = '7532536299:AAFzFoD584PAG3ZeANL-TAb_xB7tMLi2s6o'

# 2. 설정 파일 경로
CONFIG_FILE = 'config.json'

# 3. 설정 로드 함수
def load_config():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, 'r') as f:
            return json.load(f)
    return {"chats": {}}

# 4. 메시지 생성 함수
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

# 5. 자동 메시지 전송 함수
async def send_daily_message():
    config = load_config()
    message = create_message()
    bot = Bot(token=TOKEN)
    
    print("\n메시지 전송 시작...")
    
    # 설정 파일에 저장된 모든 채팅/토픽에 메시지 전송
    chats = config.get("chats", [])
    if not chats:
        print("설정된 채팅방이 없습니다.")
        return
    
    for chat in chats:
        chat_id = chat.get("chat_id")
        chat_type = chat.get("type")
        message_thread_id = chat.get("message_thread_id")
        
        print(f"메시지 전송 시도: 채팅 {chat_id}, 타입 {chat_type}")
        
        try:
            # supergroup이고 message_thread_id가 있는 경우에만 thread_id 사용
            if chat_type == "supergroup" and message_thread_id:
                await bot.send_message(
                    chat_id=chat_id,
                    text=message,
                    message_thread_id=message_thread_id
                )
                print(f"메시지 전송 성공: 채팅 {chat_id}, 토픽 {message_thread_id}")
            else:
                await bot.send_message(
                    chat_id=chat_id,
                    text=message
                )
                print(f"메시지 전송 성공: 채팅 {chat_id}")
        except Exception as e:
            print(f"메시지 전송 실패: {e}")

# 6. 메인 함수
async def main():
    await send_daily_message()

def send_message():
    # config.json 파일 읽기
    try:
        with open("config.json", "r", encoding="utf-8") as f:
            config = json.load(f)
    except FileNotFoundError:
        print("config.json 파일을 찾을 수 없습니다.")
        sys.exit(1)
    
    bot_token = config.get("bot_token")
    chats = config.get("chats", [])
    message = config.get("message", "안녕하세요!")
    
    if not bot_token:
        print("봇 토큰이 설정되지 않았습니다.")
        sys.exit(1)
    
    if not chats:
        print("채팅 정보가 설정되지 않았습니다.")
        sys.exit(1)
    
    # 각 채팅에 메시지 보내기
    for chat in chats:
        chat_id = chat.get("chat_id")
        chat_type = chat.get("type")
        message_thread_id = chat.get("message_thread_id")
        
        url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
        params = {
            "chat_id": chat_id,
            "text": message
        }
        
        # supergroup이고 message_thread_id가 있는 경우 추가
        if chat_type == "supergroup" and message_thread_id:
            params["message_thread_id"] = message_thread_id
        
        response = requests.get(url, params=params)
        if response.ok:
            print(f"메시지가 성공적으로 전송되었습니다: chat_id={chat_id}")
        else:
            print(f"메시지 전송 실패: chat_id={chat_id}, 오류={response.text}")

if __name__ == "__main__":
    asyncio.run(main())
