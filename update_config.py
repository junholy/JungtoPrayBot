from telegram import Bot
import json
import os
import requests

# 1. 봇 토큰 설정
TOKEN = '7532536299:AAFzFoD584PAG3ZeANL-TAb_xB7tMLi2s6o'

# 2. 설정 파일 경로
CONFIG_FILE = 'config.json'

# 3. 기본 설정
default_config = {
    "chats": {},
    "last_processed_update_id": 0
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

if __name__ == "__main__":
    update_config_from_updates() 