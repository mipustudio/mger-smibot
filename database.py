import json
import os
from typing import Dict, List, Any, Optional
from datetime import datetime

class JSONDatabase:
    def __init__(self, data_dir: str = "data"):
        self.data_dir = data_dir
        os.makedirs(data_dir, exist_ok=True)
        
        self.whitelist_file = os.path.join(data_dir, "whitelist.json")
        self.events_file = os.path.join(data_dir, "events.json")
        self.media_file = os.path.join(data_dir, "media.json")
        
        self._init_files()
        self.cache = {}  # Простое кэширование в памяти
        
    def _init_files(self):
        """Инициализация JSON файлов если их нет"""
        defaults = {
            self.whitelist_file: {"users": [], "admins": []},
            self.events_file: {"events": []},
            self.media_file: {"media": []}
        }
        
        for file, default_data in defaults.items():
            if not os.path.exists(file):
                with open(file, 'w', encoding='utf-8') as f:
                    json.dump(default_data, f, ensure_ascii=False, indent=2)
    
    # Методы для работы с whitelist (остаются как в предыдущем коде)
    def add_to_whitelist(self, username: str) -> bool:
        data = self._load_json(self.whitelist_file)
        if username not in data["users"]:
            data["users"].append(username)
            self._save_json(self.whitelist_file, data)
            self.cache.pop('whitelist', None)
            return True
        return False
    
    def is_whitelisted(self, username: str) -> bool:
        cache_key = f'whitelist_{username}'
        if cache_key in self.cache:
            return self.cache[cache_key]
        
        data = self._load_json(self.whitelist_file)
        is_whitelisted = username in data["users"] or username in data["admins"]
        self.cache[cache_key] = is_whitelisted
        return is_whitelisted
    
    # Методы для мероприятий
    def add_event(self, event_data: Dict) -> str:
        data = self._load_json(self.events_file)
        event_id = str(len(data["events"]) + 1)
        event_data["id"] = event_id
        event_data["created_at"] = datetime.now().isoformat()
        data["events"].append(event_data)
        self._save_json(self.events_file, data)
        self.cache.pop('events', None)
        return event_id
    
    def get_events(self) -> List[Dict]:
        if 'events' in self.cache:
            return self.cache['events']
        
        data = self._load_json(self.events_file)
        self.cache['events'] = data["events"]
        return data["events"]
    
    def delete_event(self, event_id: str) -> bool:
        data = self._load_json(self.events_file)
        initial_len = len(data["events"])
        data["events"] = [e for e in data["events"] if e["id"] != event_id]
        
        if len(data["events"]) < initial_len:
            self._save_json(self.events_file, data)
            self.cache.pop('events', None)
            return True
        return False
    
    # Методы для базы СМИ
    def add_media(self, media_data: Dict) -> None:
        data = self._load_json(self.media_file)
        data["media"].append(media_data)
        self._save_json(self.media_file, data)
        self.cache.pop('media', None)
    
    def search_media(self, query: str) -> List[Dict]:
        if 'media' not in self.cache:
            data = self._load_json(self.media_file)
            self.cache['media'] = data["media"]
        
        query = query.lower()
        return [
            media for media in self.cache['media']
            if query in media.get("name", "").lower() 
            or query in media.get("description", "").lower()
        ]
    
    # Вспомогательные методы
    def _load_json(self, filepath: str) -> Dict:
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return {}
    
    def _save_json(self, filepath: str, data: Dict) -> None:
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

# Создаем глобальный экземпляр базы данных
db = JSONDatabase()
