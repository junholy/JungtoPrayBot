from telegram import Bot
from datetime import datetime, timedelta
import pytz
import asyncio
import json
import os

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
    if "chats" not in config or not config["chats"]:
        print("설정된 채팅방이 없습니다.")
        return
    
    for chat_id, chat_config in config.get("chats", {}).items():
        if "topic_id" in chat_config:
            topic_id = chat_config["topic_id"]
            print(f"메시지 전송 시도: 채팅 {chat_id}, 토픽 {topic_id}")
            
            try:
                await bot.send_message(
                    chat_id=chat_id,
                    text=message,
                    message_thread_id=topic_id
                )
                print(f"메시지 전송 성공: 채팅 {chat_id}, 토픽 {topic_id}")
            except Exception as e:
                print(f"메시지 전송 실패: {e}")

# 6. 메인 함수
async def main():
    await send_daily_message()

if __name__ == "__main__":
    asyncio.run(main())
