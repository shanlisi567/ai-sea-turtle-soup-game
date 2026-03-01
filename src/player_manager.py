"""
AI海龟汤游戏 - 玩家配置文件（支持系统代理）
完全由AI生成
"""

import json
import os
import sys
from typing import Dict, List, Optional
import urllib.request
from urllib.request import getproxies

class PlayerConfig:
    """玩家配置类（支持系统代理）"""
    
    def __init__(self):
        self.ai_players = []
        self.user_role = "player"  # player: 玩家, riddler: 出题人
        self.game_settings = {}
        self.proxy_settings = self.get_system_proxies()
        self.load_config()
    
    def get_system_proxies(self) -> Dict[str, str]:
        """获取系统代理设置"""
        try:
            # 使用urllib获取系统代理
            proxies = getproxies()
            if proxies:
                return proxies
            else:
                return {}
        except Exception as e:
            print(f"检测系统代理时出错: {e}")
            return {}
    
    def load_config(self):
        """从配置文件加载设置"""
        try:
            config_path = os.path.join(os.path.dirname(__file__), "..", "configs", "player_config.json")
            with open(config_path, "r", encoding="utf-8") as f:
                config = json.load(f)
                self.ai_players = config.get("ai_players", [])
                self.user_role = config.get("user_role", "player")
                self.game_settings = config.get("game_settings", {})
                # 如果配置文件中有代理设置，使用配置文件的设置
                if "proxy_settings" in config:
                    self.proxy_settings = config.get("proxy_settings", {})
        except FileNotFoundError:
            # 如果配置文件不存在，使用默认配置
            self.create_default_config()
        except Exception as e:
            print(f"加载配置文件出错: {e}")
            self.create_default_config()
    
    def create_default_config(self):
        """创建默认配置文件"""
        self.ai_players = [
            {
                "name": "DeepSeek",
                "type": "ai",
                "api_config": {
                    "api_key": "your_deepseek_api_key_here",
                    "model": "deepseek-chat",
                    "url": "https://api.deepseek.com/v1/chat/completions",
                    "temperature": 0.7,
                    "use_proxy": True  # 默认使用代理
                }
            },
            {
                "name": "ChatGPT",
                "type": "ai", 
                "api_config": {
                    "api_key": "your_chatgpt_api_key_here",
                    "model": "gpt-3.5-turbo",
                    "url": "https://api.openai.com/v1/chat/completions",
                    "temperature": 0.7,
                    "use_proxy": True
                }
            },
            {
                "name": "Kimi",
                "type": "ai",
                "api_config": {
                    "api_key": "your_kimi_api_key_here",
                    "model": "moonshot-v1-8k",
                    "url": "https://api.moonshot.cn/v1/chat/completions",
                    "temperature": 0.7,
                    "use_proxy": True
                }
            }
        ]
        self.user_role = "player"
        self.game_settings = {
            "max_rounds": 10,
            "enable_history": True,
            "save_conversations": True,
            "auto_detect_proxy": True,
            "proxy_timeout": 30
        }
        self.save_config()
    
    def save_config(self):
        """保存配置到文件"""
        config = {
            "ai_players": self.ai_players,
            "user_role": self.user_role,
            "game_settings": self.game_settings,
            "proxy_settings": self.proxy_settings
        }
        config_dir = os.path.join(os.path.dirname(__file__), "..", "configs")
        os.makedirs(config_dir, exist_ok=True)
        config_path = os.path.join(config_dir, "player_config.json")
        with open(config_path, "w", encoding="utf-8") as f:
            json.dump(config, f, ensure_ascii=False, indent=2)
    
    def add_ai_player(self, name: str, api_config: Dict):
        """添加新的AI玩家"""
        api_config.setdefault("use_proxy", True)  # 默认使用代理
        ai_player = {
            "name": name,
            "type": "ai",
            "api_config": api_config
        }
        self.ai_players.append(ai_player)
        self.save_config()
    
    def remove_ai_player(self, name: str):
        """移除AI玩家"""
        self.ai_players = [p for p in self.ai_players if p["name"] != name]
        self.save_config()
    
    def set_user_role(self, role: str):
        """设置用户角色"""
        if role in ["player", "riddler"]:
            self.user_role = role
            self.save_config()
        else:
            raise ValueError("角色必须是 'player' 或 'riddler'")
    
    def set_proxy_settings(self, proxy_settings: Dict[str, str]):
        """设置代理配置"""
        self.proxy_settings = proxy_settings
        self.save_config()
    
    def get_all_players(self) -> List[str]:
        """获取所有玩家名称列表"""
        players = ["玩家"]  # 人类玩家
        players.extend([p["name"] for p in self.ai_players])
        return players
    
    def get_ai_config(self, ai_name: str) -> Optional[Dict]:
        """获取指定AI的配置"""
        for player in self.ai_players:
            if player["name"] == ai_name:
                return player["api_config"]
        return None
    
    def get_proxy_for_request(self) -> Optional[Dict[str, str]]:
        """获取用于请求的代理设置"""
        if not self.proxy_settings or not self.game_settings.get("auto_detect_proxy", True):
            return None
        
        # 过滤出有效的代理
        valid_proxies = {}
        for protocol, proxy in self.proxy_settings.items():
            if proxy and proxy.strip():
                valid_proxies[protocol] = proxy
        
        return valid_proxies if valid_proxies else None

def create_config_editor():
    """创建配置文件编辑器（交互式）"""
    config = PlayerConfig()
    
    print("=== AI海龟汤游戏配置编辑器 ===")
    print(f"当前用户角色: {config.user_role}")
    print(f"当前AI玩家: {', '.join([p['name'] for p in config.ai_players])}")
    print(f"代理设置: {'已启用' if config.proxy_settings else '未启用'}")
    
    while True:
        print("\n选项:")
        print("1. 更改用户角色")
        print("2. 添加AI玩家")
        print("3. 移除AI玩家")
        print("4. 配置代理设置")
        print("5. 查看当前配置")
        print("6. 保存并退出")
        print("7. 退出不保存")
        
        choice = input("请选择 (1-7): ").strip()
        
        if choice == "1":
            print("\n用户角色:")
            print("1. player - 作为玩家参与游戏")
            print("2. riddler - 作为出题人")
            role_choice = input("选择角色 (1-2): ").strip()
            if role_choice == "1":
                config.set_user_role("player")
                print("✓ 已设置为玩家")
            elif role_choice == "2":
                config.set_user_role("riddler")
                print("✓ 已设置为出题人")
            else:
                print("无效选择")
        
        elif choice == "2":
            print("\n添加新的AI玩家:")
            name = input("AI名称: ").strip()
            api_key = input("API Key: ").strip()
            model = input("模型名称: ").strip()
            url = input("API URL: ").strip()
            use_proxy_input = input("是否使用代理？(y/n, 默认y): ").strip().lower()
            use_proxy = use_proxy_input != 'n'
            
            api_config = {
                "api_key": api_key,
                "model": model,
                "url": url,
                "temperature": 0.7,
                "use_proxy": use_proxy
            }
            config.add_ai_player(name, api_config)
            print(f"✓ 已添加AI玩家: {name}")
        
        elif choice == "3":
            print("\n移除AI玩家:")
            ai_names = [p["name"] for p in config.ai_players]
            for i, name in enumerate(ai_names, 1):
                print(f"{i}. {name}")
            
            if ai_names:
                try:
                    idx = int(input("选择要移除的玩家编号: ").strip()) - 1
                    if 0 <= idx < len(ai_names):
                        config.remove_ai_player(ai_names[idx])
                        print(f"✓ 已移除: {ai_names[idx]}")
                    else:
                        print("无效编号")
                except ValueError:
                    print("请输入数字")
            else:
                print("没有AI玩家可移除")
        
        elif choice == "4":
            print("\n配置代理设置:")
            print("当前系统代理:", config.proxy_settings)
            print("\n选项:")
            print("1. 使用系统代理")
            print("2. 手动配置代理")
            print("3. 禁用代理")
            
            proxy_choice = input("请选择 (1-3): ").strip()
            
            if proxy_choice == "1":
                # 重新检测系统代理
                config.proxy_settings = config.get_system_proxies()
                config.save_config()
                print("✓ 已使用系统代理设置")
            
            elif proxy_choice == "2":
                print("\n手动配置代理:")
                print("格式: http://用户名:密码@代理服务器:端口 或 http://代理服务器:端口")
                http_proxy = input("HTTP代理 (留空跳过): ").strip()
                https_proxy = input("HTTPS代理 (留空跳过): ").strip()
                
                proxy_settings = {}
                if http_proxy:
                    proxy_settings["http"] = http_proxy
                if https_proxy:
                    proxy_settings["https"] = https_proxy
                
                config.set_proxy_settings(proxy_settings)
                print("✓ 代理设置已保存")
            
            elif proxy_choice == "3":
                config.set_proxy_settings({})
                print("✓ 已禁用代理")
            
            else:
                print("无效选择")
        
        elif choice == "5":
            print("\n当前配置:")
            print(f"用户角色: {config.user_role}")
            print(f"代理设置: {config.proxy_settings}")
            print("AI玩家:")
            for player in config.ai_players:
                print(f"  - {player['name']}")
                print(f"    模型: {player['api_config']['model']}")
                print(f"    URL: {player['api_config']['url']}")
                print(f"    使用代理: {player['api_config'].get('use_proxy', True)}")
        
        elif choice == "6":
            config.save_config()
            print("✓ 配置已保存")
            break
        
        elif choice == "7":
            print("退出配置编辑器")
            break
        
        else:
            print("无效选择，请重试")

if __name__ == "__main__":
    # 如果直接运行，启动配置编辑器
    create_config_editor()