from telegram import Bot
import json
import os
import requests
import sys

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
    
    # 채팅 목록 초기화 (새 형식)
    if "chats" not in config or isinstance(config["chats"], dict):
        config["chats"] = []
    
    for update in updates.get("result", []):
        update_id = update["update_id"]
        max_update_id = max(max_update_id, update_id)
        
        # 이미 처리한 업데이트는 건너뛰기
        if update_id <= last_processed_id:
            continue
        
        # 메시지 확인
        if "message" in update:
            message = update["message"]
            chat = message["chat"]
            chat_id = str(chat["id"])
            chat_type = chat.get("type")
            message_thread_id = message.get("message_thread_id")
            
            # 디버깅을 위한 메시지 정보 출력
            print(f"메시지 ID: {update_id}, 내용: {message.get('text', '텍스트 없음')}")
            print(f"채팅 타입: {chat_type}, 채팅 ID: {chat_id}")
            
            # /remove_topic 명령어 처리
            if message.get('text') == '/remove_topic':
                # 채팅 목록에서 해당 채팅 제거
                removed = False
                for i, existing_chat in enumerate(config["chats"]):
                    if existing_chat.get("chat_id") == chat_id:
                        config["chats"].pop(i)
                        removed = True
                        updated = True
                        print(f"채팅 제거됨: {chat_id}")
                        # 제거 확인 메시지 보내기
                        send_removal_message(TOKEN, chat_id, message_thread_id)
                        break
                
                if not removed:
                    print(f"제거할 채팅을 찾을 수 없음: {chat_id}")
                continue
            
            # 채팅 정보 저장
            chat_entry = {
                "chat_id": chat_id,
                "type": chat_type,
                "message_thread_id": None
            }
            
            # supergroup이고 message_thread_id가 있는 경우
            if chat_type == "supergroup" and message_thread_id:
                chat_entry["message_thread_id"] = message_thread_id
                print(f"토픽 ID 감지: {message_thread_id}")
            
            # 이미 존재하는 chat_id인지 확인
            chat_exists = False
            for i, existing_chat in enumerate(config["chats"]):
                if existing_chat.get("chat_id") == chat_id:
                    # 기존 채팅 정보 업데이트
                    if message_thread_id:  # message_thread_id가 있는 경우에만 업데이트
                        config["chats"][i]["message_thread_id"] = message_thread_id
                    chat_exists = True
                    updated = True
                    break
            
            # 새 채팅 추가
            if not chat_exists and message_thread_id:
                config["chats"].append(chat_entry)
                updated = True
                print(f"새 채팅 추가: {chat_entry}")
    
    # 마지막 처리된 update_id 저장
    if max_update_id > last_processed_id:
        config["last_processed_update_id"] = max_update_id
        updated = True
    
    if updated:
        save_config(config)
        print("설정이 업데이트되었습니다.")
    else:
        print("업데이트할 설정이 없습니다.")
    
    # 현재 설정된 채팅/토픽 정보 출력
    print("현재 설정된 채팅/토픽:")
    for chat in config.get("chats", []):
        print(f"채팅 ID: {chat.get('chat_id')}, 타입: {chat.get('type')}, 토픽 ID: {chat.get('message_thread_id')}")

def update_config(bot_token, chat_id):
    # 채팅 정보 가져오기
    url = f"https://api.telegram.org/bot{bot_token}/getChat"
    params = {"chat_id": chat_id}
    
    response = requests.get(url, params=params)
    if not response.ok:
        print(f"Error getting chat info: {response.text}")
        sys.exit(1)
    
    chat_info = response.json()["result"]
    chat_type = chat_info.get("type")
    
    # config.json 파일 읽기
    try:
        with open("config.json", "r", encoding="utf-8") as f:
            config = json.load(f)
    except FileNotFoundError:
        config = {"bot_token": bot_token, "chats": [], "message": "안녕하세요! 오늘의 메시지입니다."}
    
    # 채팅 정보 업데이트
    chat_entry = {
        "chat_id": chat_id,
        "type": chat_type,
        "message_thread_id": None
    }
    
    # supergroup인 경우 message_thread_id 확인
    if chat_type == "supergroup" and "message_thread_id" in chat_info:
        chat_entry["message_thread_id"] = chat_info["message_thread_id"]
    
    # 이미 존재하는 chat_id인지 확인
    for i, chat in enumerate(config["chats"]):
        if chat["chat_id"] == chat_id:
            config["chats"][i] = chat_entry
            break
    else:
        config["chats"].append(chat_entry)
    
    # config.json 파일 업데이트
    with open("config.json", "w", encoding="utf-8") as f:
        json.dump(config, f, indent=2, ensure_ascii=False)
    
    print(f"채팅 정보가 업데이트되었습니다: {chat_entry}")
    
    # 설정 저장 후 확인 메시지 보내기
    send_confirmation_message(bot_token, chat_id)

def send_confirmation_message(bot_token, chat_id):
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    params = {
        "chat_id": chat_id,
        "text": "기도 알림 대상으로 등록되었습니다."
    }
    
    # config.json에서 현재 채팅의 message_thread_id 확인
    try:
        with open("config.json", "r", encoding="utf-8") as f:
            config = json.load(f)
            
        # 현재 채팅의 message_thread_id 찾기
        for chat in config["chats"]:
            if chat["chat_id"] == chat_id and chat["message_thread_id"]:
                params["message_thread_id"] = chat["message_thread_id"]
                break
    except Exception as e:
        print(f"설정 파일 읽기 오류: {e}")
    
    response = requests.get(url, params=params)
    if not response.ok:
        print(f"Error sending confirmation message: {response.text}")

def send_removal_message(bot_token, chat_id, message_thread_id=None):
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    params = {
        "chat_id": chat_id,
        "text": "기도 알림 대상에서 제거되었습니다."
    }
    
    if message_thread_id:
        params["message_thread_id"] = message_thread_id
    
    response = requests.get(url, params=params)
    if not response.ok:
        print(f"Error sending removal message: {response.text}")

def remove_chat(bot_token, chat_id):
    # config.json 파일 읽기
    try:
        with open("config.json", "r", encoding="utf-8") as f:
            config = json.load(f)
    except FileNotFoundError:
        print("설정 파일이 존재하지 않습니다.")
        return False
    
    # 채팅 목록에서 해당 채팅 찾기
    message_thread_id = None
    removed = False
    for i, chat in enumerate(config["chats"]):
        if chat["chat_id"] == chat_id:
            message_thread_id = chat.get("message_thread_id")
            config["chats"].pop(i)
            removed = True
            break
    
    if not removed:
        print(f"제거할 채팅을 찾을 수 없음: {chat_id}")
        return False
    
    # config.json 파일 업데이트
    with open("config.json", "w", encoding="utf-8") as f:
        json.dump(config, f, indent=2, ensure_ascii=False)
    
    print(f"채팅이 제거되었습니다: {chat_id}")
    
    # 제거 확인 메시지 보내기
    send_removal_message(bot_token, chat_id, message_thread_id)
    return True

if __name__ == "__main__":
    # 명령줄 인수가 있으면 새 함수 사용, 없으면 기존 함수 사용
    if len(sys.argv) > 1:
        if len(sys.argv) >= 3:
            bot_token = sys.argv[1]
            chat_id = sys.argv[2]
            
            # 제거 명령어 처리
            if len(sys.argv) >= 4 and sys.argv[3] == "remove":
                remove_chat(bot_token, chat_id)
            else:
                update_config(bot_token, chat_id)
        else:
            print("사용법: python update_config.py <bot_token> <chat_id> [remove]")
            sys.exit(1)
    else:
        # 기존 방식으로 업데이트
        update_config_from_updates() 