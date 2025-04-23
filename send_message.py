from telegram import Bot
from datetime import datetime, timedelta
import pytz
import asyncio

# 1. 봇 토큰과 대상 채팅 ID
TOKEN = '7532536299:AAFzFoD584PAG3ZeANL-TAb_xB7tMLi2s6o'
CHAT_ID = '-1002533690170'  # 실제 채팅 ID로 변경 필요
MESSAGE_THREAD_ID = 9  # 필요한 경우 토픽 ID 입력

# 2. 한국 시간대 설정
korea_tz = pytz.timezone('Asia/Seoul')
today = datetime.now(korea_tz)

# # 테스트용 날짜 설정 (실제 배포 시 주석 처리)
# test_mode = True
# if test_mode:
#     # 테스트용 날짜 (2025년 2월 16일로부터 10일 지난 것으로 가정)
#     today = datetime(2025, 2, 26, tzinfo=korea_tz)

# 3. 불기 연도 계산 (서기 + 544)
buddhist_year = today.year + 544

# 4. 요일 한글 변환
weekdays = ['월', '화', '수', '목', '금', '토', '일']
weekday_korean = weekdays[today.weekday()]

# 5. 결사 일자 계산
start_date = datetime(2025, 2, 16, tzinfo=korea_tz)  # 입재식 날짜
days_passed = (today - start_date).days  # +1은 시작일을 1일차로 계산

# 현재 날짜가 입재식 날짜보다 이전인 경우 D-Day로 표시
if today < start_date:
    days_to_start = (start_date - today).days
    days_message = f"입재식 D-{days_to_start}"
else:
    days_message = f"1차 천일결사 8차 백일기도 {days_passed}일 째 기도"

# 6. 메시지 템플릿
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

# 7. 비동기 함수로 메시지 전송
async def send_telegram_message():
    bot = Bot(token=TOKEN)
    await bot.send_message(
        chat_id=CHAT_ID, 
        text=message,
        message_thread_id=MESSAGE_THREAD_ID  # 토픽 ID가 있는 경우에만 사용
    )
    
# 8. 비동기 함수 실행
if __name__ == "__main__":
    asyncio.run(send_telegram_message())
