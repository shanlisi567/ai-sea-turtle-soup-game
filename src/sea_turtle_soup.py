"""
AI海龟汤游戏 - 主游戏逻辑
完全由AI生成
"""

import requests
import json
import os
import random
import sys
import time
from typing import List, Dict, Optional
from datetime import datetime
from player_manager import PlayerConfig

class SeaTurtleSoupGame:
    """海龟汤游戏主类（支持系统代理）"""
    
    def __init__(self):
        self.config = PlayerConfig()
        self.history = []
        self.current_round = 0
        self.max_rounds = self.config.game_settings.get("max_rounds", 10)
        
        # 确保配置文件存在
        config_path = os.path.join(os.path.dirname(__file__), "..", "configs", "player_config.json")
        if not os.path.exists(config_path):
            self.config.create_default_config()
        
        print("AI海龟汤游戏初始化完成")
    
    def create_session_with_proxy(self):
        """创建带有代理配置的requests会话"""
        session = requests.Session()
        proxy_settings = self.config.get_proxy_for_request()
        
        if proxy_settings:
            session.proxies.update(proxy_settings)
        
        # 设置超时
        timeout = self.config.game_settings.get("proxy_timeout", 30)
        session.timeout = timeout
        
        return session
    
    def get_ai_response(self, ai_name: str, messages: List[Dict[str, str]]) -> str:
        """获取指定AI的响应（支持代理）"""
        ai_config = self.config.get_ai_config(ai_name)
        if not ai_config:
            return f"错误：找不到AI '{ai_name}' 的配置"
        
        # 检查该AI是否使用代理
        use_proxy = ai_config.get("use_proxy", True)
        
        headers = {
            "Authorization": f"Bearer {ai_config['api_key']}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": ai_config["model"],
            "messages": messages,
            "temperature": ai_config.get("temperature", 0.7)
        }
        
        try:
            if use_proxy:
                # 使用带代理的会话
                session = self.create_session_with_proxy()
                response = session.post(ai_config["url"], json=payload, headers=headers)
            else:
                # 不使用代理，直连
                response = requests.post(ai_config["url"], json=payload, headers=headers, 
                                        timeout=self.config.game_settings.get("proxy_timeout", 30))
            
            response.raise_for_status()
            result = response.json()
            return result["choices"][0]["message"]["content"]
        
        except requests.exceptions.ProxyError as e:
            return f"网络连接错误: {str(e)}"
        except requests.exceptions.ConnectTimeout as e:
            return f"连接超时: {str(e)}"
        except requests.exceptions.RequestException as e:
            return f"API请求错误: {str(e)}"
        except (KeyError, json.JSONDecodeError) as e:
            return f"API响应解析错误: {str(e)}"
    
    def add_to_history(self, entry_type: str, sender: str, content: str):
        """添加记录到历史（不在游戏中自动保存文件）"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        entry = {
            "timestamp": timestamp,
            "type": entry_type,
            "from": sender,
            "content": content
        }
        self.history.append(entry)
    
    def save_conversation_to_file(self):
        """保存对话历史到文件"""
        if not self.history:
            return
        
        filename = f"conversation_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        filepath = os.path.join(os.path.dirname(__file__), "..", filename)
        
        try:
            with open(filepath, "w", encoding="utf-8") as f:
                json.dump(self.history, f, ensure_ascii=False, indent=2)
            print(f"对话已保存到: {filename}")
        except Exception as e:
            print(f"保存对话失败: {e}")
    
    def get_riddle_from_ai(self, ai_name: str) -> Dict[str, str]:
        """从AI获取谜题（包含题目、内容和汤底）"""
        system_prompt = """你是一个擅长出谜题的AI。请出一个海龟汤谜题（一个简短的故事或情境，但隐藏了关键信息）。
        
        格式要求：
        1. 第一行："题目：[谜题题目]"
        2. 第二行："内容：[谜题故事/情境]"
        3. 第三行："汤底：[谜底/真相]"
        
        示例：
        题目：消失的乘客
        内容：一辆长途巴士在夜间行驶，中途停车休息后，司机清点人数发现少了一名乘客。调取监控发现，这名乘客在停车时下车后就再也没回来。警方搜索了附近区域也没找到。
        汤底：这名乘客是司机的妻子，两人吵架后妻子生气下车，司机为了找她也下了车，但两人走散了。第二天妻子自己回家了。
        
        请出一个新的海龟汤谜题："""
        
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": "请出一个新的海龟汤谜题"}
        ]
        
        response = self.get_ai_response(ai_name, messages)
        
        # 解析响应
        result = {"title": "", "content": "", "solution": ""}
        lines = response.strip().split('\n')
        for line in lines:
            if line.startswith("题目："):
                result["title"] = line[3:].strip()
            elif line.startswith("内容："):
                result["content"] = line[3:].strip()
            elif line.startswith("汤底："):
                result["solution"] = line[3:].strip()
        
        return result
    
    def get_question_from_ai(self, ai_name: str, riddle: Dict[str, str], qa_history: List[Dict[str, str]]) -> str:
        """从AI获取问题（传统海龟汤模式）"""
        system_prompt = """你正在参与传统海龟汤游戏。游戏规则：
        1. 出题人给出一个谜题（故事/情境）
        2. 你可以提问，出题人只能回答"是"、"否"或"无关"
        3. 通过提问逐渐推理出真相
        4. 可以提出假设，如果接近真相出题人会提示
        
        你的提问应该是：
        1. 具体的、可以用"是/否"回答的问题
        2. 基于已有信息的合理推理
        3. 逐步逼近真相
        
        避免：
        1. 直接猜测汤底
        2. 问开放式问题
        3. 问无法用是/否回答的问题
        
        示例问题：
        - 这个人死了吗？
        - 这件事发生在晚上吗？
        - 凶手是认识的人吗？
        - 有超自然因素吗？"""
        
        user_content = f"谜题题目：{riddle['title']}\n"
        user_content += f"谜题内容：{riddle['content']}\n\n"
        
        if qa_history:
            user_content += "之前的问答：\n"
            for qa in qa_history:
                user_content += f"Q: {qa['question']}\n"
                user_content += f"A: {qa['answer']}\n"
            user_content += "\n"
        
        user_content += "请提出下一个问题："
        
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_content}
        ]
        
        return self.get_ai_response(ai_name, messages)
    
    def get_guess_from_ai(self, ai_name: str, riddle: str, history_context: str = "") -> str:
        """从AI获取猜测（现代海龟汤模式）"""
        system_prompt = """你正在参与海龟汤游戏。根据谜题进行合理猜测，尝试推理出可能的汤底（真相），但不要直接说"汤底是..."。
        
        你的猜测应该：
        1. 提出合理的疑问或假设
        2. 尝试解释谜题中的矛盾点
        3. 可以提出多个可能性
        4. 使用"可能"、"也许"、"会不会是"等词语
        
        记住：这是推理游戏，不要直接给出答案。"""
        
        user_content = f"谜题：\n{riddle}"
        if history_context:
            user_content += f"\n\n之前的对话：\n{history_context}"
        user_content += "\n\n请根据以上内容进行猜测："
        
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_content}
        ]
        
        return self.get_ai_response(ai_name, messages)
    
    def get_solution_from_ai(self, ai_name: str, riddle: str) -> str:
        """从AI获取汤底（答案）"""
        system_prompt = """你是海龟汤游戏的出题人，请为以下谜题提供一个合理且有创意的汤底（真相）。
        
        汤底应该：
        1. 解释谜题中的所有细节
        2. 有一定的意外性
        3. 逻辑合理
        4. 简洁明了
        
        请直接给出汤底答案。"""
        
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"谜题：\n{riddle}\n\n请提供汤底（真相）："}
        ]
        
        return self.get_ai_response(ai_name, messages)
    
    def get_ai_chat_response(self, ai_name: str, conversation_context: str, previous_messages: List[str]) -> str:
        """获取AI在赛后聊天中的响应（有超时和错误处理）"""
        system_prompt = """你正在参与海龟汤游戏的赛后聊天环节。刚才进行了一局海龟汤游戏，现在所有玩家聚在一起交流游戏心得。
        
        请以自然、友好的方式参与聊天：
        1. 可以分享你对刚才谜题的见解
        2. 可以评论其他玩家的提问或猜测
        3. 可以表达对下一局游戏的期待
        4. 保持对话轻松有趣，像朋友聊天一样
        
        请用1-2句话进行回复，不要太长。"""
        
        user_content = f"游戏回顾：\n{conversation_context}\n\n"
        
        if previous_messages:
            user_content += "刚才的对话：\n"
            for msg in previous_messages[-3:]:  # 只取最近3条消息
                user_content += f"{msg}\n"
            user_content += "\n"
        
        user_content += "请回复（1-2句话）："
        
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_content}
        ]
        
        # 使用更短的超时时间
        ai_config = self.config.get_ai_config(ai_name)
        if not ai_config:
            return f"（{ai_name}：配置丢失）"
        
        # 检查该AI是否使用代理
        use_proxy = ai_config.get("use_proxy", True)
        
        headers = {
            "Authorization": f"Bearer {ai_config['api_key']}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": ai_config["model"],
            "messages": messages,
            "temperature": 0.8,  # 聊天时温度稍高，更有趣
            "max_tokens": 100    # 限制回复长度
        }
        
        try:
            if use_proxy:
                # 使用带代理的会话，聊天超时设为10秒
                session = self.create_session_with_proxy()
                # 临时设置更短的超时
                session.timeout = 10
                response = session.post(ai_config["url"], json=payload, headers=headers)
            else:
                # 不使用代理，直连，超时10秒
                response = requests.post(ai_config["url"], json=payload, headers=headers, timeout=10)
            
            response.raise_for_status()
            result = response.json()
            content = result["choices"][0]["message"]["content"]
            # 确保回复不会太长
            if len(content) > 200:
                content = content[:197] + "..."
            return content
        
        except requests.exceptions.Timeout:
            return f"（{ai_name}：思考时间有点长，先跳过）"
        except requests.exceptions.RequestException as e:
            return f"（{ai_name}：网络问题无法回复）"
        except (KeyError, json.JSONDecodeError) as e:
            return f"（{ai_name}：回复格式异常）"
        except Exception as e:
            return f"（{ai_name}：暂时无法回复）"
    
    def get_ai_answer_to_question(self, ai_name: str, riddle: Dict[str, str], question: str, qa_history: List[Dict[str, str]]) -> str:
        """AI作为出题人回答问题是/否"""
        system_prompt = """你是海龟汤游戏的出题人。你需要根据谜底（汤底）回答玩家的问题。
        
        规则：
        1. 只能回答"是"、"否"或"无关"
        2. 如果问题与谜底无关，回答"无关"
        3. 如果问题基于错误的前提，回答"否"
        4. 如果问题直接或间接涉及谜底核心，判断是否接近真相
        
        特殊回答：
        - "接近"：当问题非常接近真相时
        - "可以揭晓"：当玩家已经基本推理出真相时
        
        记住：不要透露谜底细节，只用是/否回答。"""
        
        user_content = f"谜题题目：{riddle['title']}\n"
        user_content += f"谜题内容：{riddle['content']}\n"
        user_content += f"谜底（不要透露）：{riddle['solution']}\n\n"
        
        if qa_history:
            user_content += "之前的问答：\n"
            for qa in qa_history:
                user_content += f"Q: {qa['question']}\n"
                user_content += f"A: {qa['answer']}\n"
            user_content += "\n"
        
        user_content += f"玩家提问：{question}\n"
        user_content += "请根据以上信息回答（是/否/无关/接近/可以揭晓）："
        
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_content}
        ]
        
        response = self.get_ai_response(ai_name, messages).strip()
        
        # 标准化回答
        if response.lower() in ["是", "yes", "对的", "正确"]:
            return "是"
        elif response.lower() in ["否", "no", "不对", "错误"]:
            return "否"
        elif response.lower() in ["无关", "不相关", "irrelevant"]:
            return "无关"
        elif "接近" in response or "接近真相" in response:
            return "接近"
        elif "揭晓" in response or "可以" in response:
            return "可以揭晓"
        else:
            # 默认处理
            if len(response) <= 10:
                return response
            else:
                # 如果AI返回了复杂回答，提取第一个关键词
                for keyword in ["是", "否", "无关", "接近", "可以揭晓"]:
                    if keyword in response:
                        return keyword
                return "无关"
    
    def evaluate_question_proximity(self, question: str, solution: str) -> str:
        """评估问题接近谜底的程度（人类出题人使用）"""
        print(f"\n玩家提问：{question}")
        print("请选择回答：")
        print("1. 是")
        print("2. 否")
        print("3. 无关")
        print("4. 接近（问题很接近真相）")
        print("5. 可以揭晓（玩家基本猜到了）")
        
        while True:
            choice = input("选择 (1-5): ").strip()
            if choice == "1":
                return "是"
            elif choice == "2":
                return "否"
            elif choice == "3":
                return "无关"
            elif choice == "4":
                return "接近"
            elif choice == "5":
                return "可以揭晓"
            else:
                print("无效选择，请重试")
    
    def get_all_players_in_order(self) -> List[str]:
        """获取所有玩家并按随机顺序排列"""
        players = self.config.get_all_players()
        random.shuffle(players)
        return players
    
    def play_traditional_round(self, riddler: str, guesser: str):
        """进行一轮传统海龟汤游戏（一个出题人，一个猜谜者）"""
        print(f"\n{'='*60}")
        print(f"传统海龟汤 - 第 {self.current_round} 轮")
        print(f"出题者: {riddler} | 猜谜者: {guesser}")
        print(f"{'='*60}")
        
        # 出题环节
        if riddler == "玩家":
            print("\n[出题环节]")
            print("作为出题人，请准备你的海龟汤谜题：")
            title = input("谜题题目：").strip()
            content = input("谜题内容：").strip()
            solution = input("汤底（真相，不要告诉猜谜者）：").strip()
            riddle = {"title": title, "content": content, "solution": solution}
            print("\n✓ 谜题已设置完成")
        else:
            print(f"\n[出题环节] {riddler}正在出题...")
            riddle = self.get_riddle_from_ai(riddler)
            print(f"{riddler}的谜题：")
            print(f"题目：{riddle['title']}")
            print(f"内容：{riddle['content']}")
            print("（汤底已保存，不会显示）")
        
        # 记录谜题
        self.add_to_history("riddle", riddler, f"{riddle['title']}: {riddle['content'][:100]}...")
        
        # 问答环节
        qa_history = []
        question_count = 0
        max_questions = 20  # 最多提问次数
        
        print(f"\n[问答环节开始]")
        print(f"{guesser}可以提问，{riddler}只能回答：是/否/无关")
        print("当问题接近真相时，出题人可以回答'接近'")
        print("当猜谜者基本猜到时，出题人可以回答'可以揭晓'")
        print("输入'quit'结束提问，输入'solve'尝试揭晓谜底")
        print(f"最多提问{max_questions}次")
        
        while question_count < max_questions:
            question_count += 1
            print(f"\n--- 第 {question_count} 问 ---")
            
            # 获取问题
            if guesser == "玩家":
                print(f"{guesser}，请提问：")
                question = input("问题：").strip()
                
                if question.lower() == 'quit':
                    print("提问结束")
                    break
                elif question.lower() == 'solve':
                    print("尝试揭晓谜底...")
                    if riddler == "玩家":
                        print("请出题人判断是否猜对：")
                        guess = input("猜谜者的猜测：").strip()
                        judge = input("是否正确？(y/n): ").strip().lower()
                        if judge == 'y':
                            print("✓ 恭喜猜对了！")
                            self.add_to_history("solution", riddler, f"谜底：{riddle['solution']}")
                            print(f"汤底：{riddle['solution']}")
                            return True
                        else:
                            print("✗ 猜错了，继续提问")
                            continue
                    else:
                        # AI出题人判断
                        answer = self.get_ai_answer_to_question(riddler, riddle, 
                                                                "玩家尝试揭晓谜底：" + question, qa_history)
                        if answer == "可以揭晓":
                            print("✓ AI出题人认为可以揭晓！")
                            self.add_to_history("solution", riddler, f"谜底：{riddle['solution']}")
                            print(f"汤底：{riddle['solution']}")
                            return True
                        else:
                            print("✗ AI出题人认为还不可以揭晓，继续提问")
                            continue
            else:
                # AI猜谜者提问
                print(f"{guesser}正在思考问题...")
                question = self.get_question_from_ai(guesser, riddle, qa_history)
                print(f"{guesser}提问：{question}")
            
            # 获取回答
            if riddler == "玩家":
                answer = self.evaluate_question_proximity(question, riddle['solution'])
            else:
                answer = self.get_ai_answer_to_question(riddler, riddle, question, qa_history)
            
            print(f"{riddler}回答：{answer}")
            
            # 记录问答
            qa_history.append({"question": question, "answer": answer})
            self.add_to_history("qa", f"{guesser}->{riddler}", f"Q: {question} | A: {answer}")
            
            # 检查是否应该揭晓
            if answer == "可以揭晓":
                print("\n🎉 出题人认为可以揭晓谜底了！")
                print(f"汤底：{riddle['solution']}")
                self.add_to_history("solution", riddler, f"谜底：{riddle['solution']}")
                return True
            
            if answer == "接近":
                print("💡 出题人提示：很接近真相了！")
        
        # 提问次数用完或主动结束
        print(f"\n{'='*40}")
        print("问答环节结束")
        
        # 最后揭晓谜底
        print(f"\n[揭晓谜底]")
        print(f"题目：{riddle['title']}")
        print(f"内容：{riddle['content']}")
        print(f"汤底：{riddle['solution']}")
        
        self.add_to_history("solution", riddler, f"谜底：{riddle['solution']}")
        
        # 询问猜谜者是否猜对
        if guesser == "玩家":
            guess = input("\n你猜到谜底了吗？请输入你的猜测（或留空跳过）：").strip()
            if guess:
                # 简单判断是否接近
                if any(keyword in guess for keyword in riddle['solution'].split()[:5]):
                    print("✓ 接近正确答案！")
                else:
                    print("✗ 不太接近正确答案")
        
        return False
    
    def play_round(self, riddler: str, guessers: List[str]):
        """进行一轮现代海龟汤游戏（兼容旧模式）"""
        print(f"\n{'='*50}")
        print(f"第 {self.current_round} 轮 - 出题者: {riddler}")
        print(f"{'='*50}")
        
        # 出题环节
        if riddler == "玩家":
            print("\n[出题环节]")
            print("作为出题人，请输入你的海龟汤谜题：")
            riddle = input("谜题题目：").strip()
            content = input("谜题内容：").strip()
            full_riddle = f"题目：{riddle}\n内容：{content}"
        else:
            print(f"\n[出题环节] {riddler}正在出题...")
            full_riddle = self.get_riddle_from_ai(riddler)
            print(f"{riddler}的谜题：\n{full_riddle}")
        
        self.add_to_history("riddle", riddler, full_riddle)
        
        # 收集历史上下文供AI参考
        history_context = ""
        if self.config.game_settings.get("enable_history", True):
            recent_history = self.history[-5:]  # 最近5条记录
            history_context = "\n".join([f"[{h['from']}] {h['content'][:100]}..." for h in recent_history])
        
        # 猜谜环节
        print(f"\n[猜谜环节]")
        for guesser in guessers:
            if guesser == "玩家":
                print("\n作为玩家，请输入你的猜测：")
                guess = input("你的猜测：").strip()
            else:
                print(f"\n{guesser}正在思考...")
                guess = self.get_guess_from_ai(guesser, full_riddle, history_context)
                print(f"{guesser}的猜测：\n{guess}")
            
            self.add_to_history("guess", guesser, guess)
        
        # 揭示汤底环节
        print(f"\n[揭示汤底]")
        if riddler == "玩家":
            print("作为出题人，请揭示汤底（真相）：")
            solution = input("汤底：").strip()
        else:
            print(f"{riddler}正在揭示汤底...")
            solution = self.get_solution_from_ai(riddler, full_riddle)
            print(f"{riddler}的汤底：\n{solution}")
        
        self.add_to_history("solution", riddler, solution)
    
    def show_game_menu(self):
        """显示游戏菜单"""
        print("\n" + "="*60)
        print("                AI海龟汤游戏")
        print("="*60)
        print(f"当前配置:")
        print(f"  用户角色: {'玩家' if self.config.user_role == 'player' else '出题人'}")
        print(f"  AI玩家: {', '.join([p['name'] for p in self.config.ai_players])}")
        print(f"  最大轮数: {self.max_rounds}")
        print("\n游戏模式:")
        print("1. 传统海龟汤（提问-回答，是/否/无关）")
        print("2. 现代海龟汤（自由猜测）")
        print("\n选项:")
        print("3. 更改配置")
        print("4. 查看历史记录")
        print("5. 测试API连接")
        print("6. 退出游戏")
    
    def change_configuration(self):
        """更改游戏配置"""
        from player_manager import create_config_editor
        
        print("\n启动配置编辑器...")
        create_config_editor()
        
        # 重新加载配置
        self.config = PlayerConfig()
        self.max_rounds = self.config.game_settings.get("max_rounds", 10)
    
    def test_api_connection(self):
        """测试API连接"""
        print("\n[API连接测试]")
        
        if not self.config.ai_players:
            print("没有配置AI玩家，请先添加AI玩家")
            return
        
        print("选择要测试的AI:")
        for i, player in enumerate(self.config.ai_players, 1):
            print(f"{i}. {player['name']} ({player['api_config']['model']})")
        
        try:
            choice = int(input("请选择 (输入0测试所有): ").strip())
        except ValueError:
            print("请输入数字")
            return
        
        if choice == 0:
            # 测试所有AI
            for player in self.config.ai_players:
                self._test_single_ai(player["name"])
        elif 1 <= choice <= len(self.config.ai_players):
            ai_name = self.config.ai_players[choice-1]["name"]
            self._test_single_ai(ai_name)
        else:
            print("无效选择")
    
    def _test_single_ai(self, ai_name: str):
        """测试单个AI连接"""
        print(f"\n测试 {ai_name} 连接...")
        
        # 简单的测试消息
        messages = [
            {"role": "system", "content": "你是一个测试助手，请回复'连接成功'。"},
            {"role": "user", "content": "测试连接"}
        ]
        
        try:
            response = self.get_ai_response(ai_name, messages)
            if "连接成功" in response or len(response) > 10:
                print(f"✓ {ai_name}: 连接成功")
                print(f"  响应: {response[:100]}...")
            else:
                print(f"✗ {ai_name}: 连接可能有问题")
                print(f"  响应: {response}")
        except Exception as e:
            print(f"✗ {ai_name}: 连接失败 - {e}")
    
    def show_history(self):
        """显示游戏历史"""
        if not self.history:
            print("\n暂无历史记录")
            return
        
        print(f"\n{'='*60}")
        print("                游戏历史记录")
        print(f"{'='*60}")
        
        for i, entry in enumerate(self.history, 1):
            print(f"\n[{i}] {entry['timestamp']} - {entry['type'].upper()}")
            print(f"  来自: {entry['from']}")
            print(f"  内容: {entry['content'][:150]}{'...' if len(entry['content']) > 150 else ''}")
    
    def run(self):
        """运行游戏主循环"""
        print("正在加载AI海龟汤游戏...")
        print(f"工作目录: {os.path.dirname(__file__)}")
        
        while True:
            self.show_game_menu()
            choice = input("\n请选择 (1-6): ").strip()
            
            if choice == "1":
                self.start_traditional_game()
            elif choice == "2":
                self.start_modern_game()
            elif choice == "3":
                self.change_configuration()
            elif choice == "4":
                self.show_history()
            elif choice == "5":
                self.test_api_connection()
            elif choice == "6":
                print("\n感谢游玩AI海龟汤游戏！")
                break
            else:
                print("无效选择，请重试")
    
    def start_traditional_game(self):
        """开始传统海龟汤游戏（选择模式）"""
        print("\n选择传统海龟汤模式：")
        print("1. 1对1模式（一个出题人对一个猜谜者）")
        print("2. 多人提问模式（一个出题人，所有玩家轮流提问）")
        
        choice = input("请选择 (1-2): ").strip()
        
        if choice == "1":
            self._start_traditional_1v1()
        elif choice == "2":
            self._start_traditional_all_players()
        else:
            print("无效选择，返回主菜单")
    
    def _start_traditional_1v1(self):
        """传统1对1模式"""
        # 重置游戏状态
        self.history = []
        self.current_round = 0
        
        # 获取玩家列表
        all_players = self.get_all_players_in_order()
        print(f"\n传统海龟汤游戏（1对1模式）开始！参与者: {', '.join(all_players)}")
        print("游戏规则：猜谜者提问，出题者只能回答'是'、'否'或'无关'")
        print("出题人可以在猜谜者接近真相时回答'接近'，认为可以揭晓时回答'可以揭晓'")
        
        # 设置配对：每个出题人对一个猜谜者
        # 如果是奇数个玩家，最后一个玩家轮空或作为观察者
        pairs = []
        for i in range(0, len(all_players) - 1, 2):
            pairs.append((all_players[i], all_players[i + 1]))
        
        if len(all_players) % 2 == 1:
            print(f"\n注意：玩家 {all_players[-1]} 将作为观察者（不参与本轮）")
        
        successful_guesses = 0
        total_pairs = len(pairs)
        
        for riddler, guesser in pairs:
            self.current_round += 1
            print(f"\n{'='*60}")
            print(f"第 {self.current_round}/{total_pairs} 组：{riddler} 🆚 {guesser}")
            
            # 进行一轮传统游戏
            success = self.play_traditional_round(riddler, guesser)
            if success:
                successful_guesses += 1
            
            # 回合结束后的小型聊天
            if riddler == "玩家" or guesser == "玩家":
                print(f"\n{'='*40}")
                print(f"    第 {self.current_round} 组结束")
                print(f"{'='*40}")
                result_text = f"第 {self.current_round} 组：{guesser} "
                result_text += "成功猜对！" if success else "未能猜对"
                self.mini_chat_after_round(result_text)
            
            # 询问是否继续
            if self.current_round < total_pairs:
                continue_choice = input(f"\n继续下一组吗？ ({self.current_round}/{total_pairs}) (y/n): ").lower()
                if continue_choice != 'y':
                    break
        
        # 游戏结束
        print(f"\n{'='*60}")
        print("                游戏结束！")
        print(f"{'='*60}")
        print(f"总共进行了 {self.current_round} 组游戏")
        print(f"成功猜对: {successful_guesses}/{self.current_round}")
        
        # 赛后复盘
        self.post_game_review()
    
    def _start_traditional_all_players(self):
        """传统多人提问模式"""
        # 重置游戏状态
        self.history = []
        self.current_round = 0
        
        # 获取玩家列表
        all_players = self.get_all_players_in_order()
        print(f"\n传统海龟汤游戏（多人提问模式）开始！参与者: {', '.join(all_players)}")
        print("游戏规则：所有猜谜者轮流提问，出题者只能回答'是'、'否'或'无关'")
        print("出题人可以在猜谜者接近真相时回答'接近'，认为可以揭晓时回答'可以揭晓'")
        
        total_rounds = len(all_players)
        
        for i in range(total_rounds):
            self.current_round += 1
            riddler = all_players[i]
            guessers = [p for p in all_players if p != riddler]
            
            print(f"\n{'='*60}")
            print(f"第 {self.current_round}/{total_rounds} 轮 - 出题者: {riddler}")
            print(f"猜谜者: {', '.join(guessers)}")
            
            # 进行一轮多人提问游戏
            success = self.play_traditional_round_all_players(riddler, guessers)
            
            # 回合结束后的小型聊天（如果有玩家参与）
            if riddler == "玩家" or any(g == "玩家" for g in guessers):
                print(f"\n{'='*40}")
                print(f"    第 {self.current_round} 轮结束")
                print(f"{'='*40}")
                result_text = f"第 {self.current_round} 轮：{riddler}出题，"
                result_text += f"猜谜者{'猜对了！' if success else '未能猜对'}。"
                self.mini_chat_after_round(result_text)
            
            # 询问是否继续
            if self.current_round < total_rounds:
                continue_choice = input(f"\n继续下一轮吗？ ({self.current_round}/{total_rounds}) (y/n): ").lower()
                if continue_choice != 'y':
                    break
        
        # 游戏结束
        print(f"\n{'='*60}")
        print("                游戏结束！")
        print(f"{'='*60}")
        print(f"总共进行了 {self.current_round} 轮游戏")
        
        # 赛后复盘
        self.post_game_review()
    
    def play_traditional_round_all_players(self, riddler: str, guessers: List[str]):
        """进行一轮传统海龟汤游戏（一个出题人，多个猜谜者轮流提问）"""
        print(f"\n{'='*60}")
        print(f"传统海龟汤 - 第 {self.current_round} 轮")
        print(f"出题者: {riddler}")
        print(f"猜谜者: {', '.join(guessers)}")
        print(f"{'='*60}")
        
        # 出题环节
        if riddler == "玩家":
            print("\n[出题环节]")
            print("作为出题人，请准备你的海龟汤谜题：")
            title = input("谜题题目：").strip()
            content = input("谜题内容：").strip()
            solution = input("汤底（真相，不要告诉猜谜者）：").strip()
            riddle = {"title": title, "content": content, "solution": solution}
            print("\n✓ 谜题已设置完成")
        else:
            print(f"\n[出题环节] {riddler}正在出题...")
            riddle = self.get_riddle_from_ai(riddler)
            print(f"{riddler}的谜题：")
            print(f"题目：{riddle['title']}")
            print(f"内容：{riddle['content']}")
            print("（汤底已保存，不会显示）")
        
        # 记录谜题
        self.add_to_history("riddle", riddler, f"{riddle['title']}: {riddle['content'][:100]}...")
        
        # 问答环节
        qa_history = []
        question_count = 0
        max_questions = 20  # 最多提问次数
        current_guesser_index = 0
        
        print(f"\n[问答环节开始]")
        print("猜谜者轮流提问，出题者只能回答：是/否/无关")
        print("当问题接近真相时，出题人可以回答'接近'")
        print("当猜谜者基本猜到时，出题人可以回答'可以揭晓'")
        print("输入'quit'结束提问，输入'solve'尝试揭晓谜底")
        print(f"最多提问{max_questions}次")
        
        while question_count < max_questions:
            question_count += 1
            guesser = guessers[current_guesser_index]
            print(f"\n--- 第 {question_count} 问 (提问者: {guesser}) ---")
            
            # 获取问题
            if guesser == "玩家":
                print(f"{guesser}，请提问：")
                question = input("问题：").strip()
                
                if question.lower() == 'quit':
                    print("提问结束")
                    break
                elif question.lower() == 'solve':
                    print("尝试揭晓谜底...")
                    if riddler == "玩家":
                        print("请出题人判断是否猜对：")
                        guess = input("猜谜者的猜测：").strip()
                        judge = input("是否正确？(y/n): ").strip().lower()
                        if judge == 'y':
                            print("✓ 恭喜猜对了！")
                            self.add_to_history("solution", riddler, f"谜底：{riddle['solution']}")
                            print(f"汤底：{riddle['solution']}")
                            return True
                        else:
                            print("✗ 猜错了，继续提问")
                            # 切换到下一个提问者
                            current_guesser_index = (current_guesser_index + 1) % len(guessers)
                            continue
                    else:
                        # AI出题人判断
                        answer = self.get_ai_answer_to_question(riddler, riddle, 
                                                                "玩家尝试揭晓谜底：" + question, qa_history)
                        if answer == "可以揭晓":
                            print("✓ AI出题人认为可以揭晓！")
                            self.add_to_history("solution", riddler, f"谜底：{riddle['solution']}")
                            print(f"汤底：{riddle['solution']}")
                            return True
                        else:
                            print("✗ AI出题人认为还不可以揭晓，继续提问")
                            # 切换到下一个提问者
                            current_guesser_index = (current_guesser_index + 1) % len(guessers)
                            continue
            else:
                # AI猜谜者提问
                print(f"{guesser}正在思考问题...")
                question = self.get_question_from_ai(guesser, riddle, qa_history)
                print(f"{guesser}提问：{question}")
            
            # 获取回答
            if riddler == "玩家":
                answer = self.evaluate_question_proximity(question, riddle['solution'])
            else:
                answer = self.get_ai_answer_to_question(riddler, riddle, question, qa_history)
            
            print(f"{riddler}回答：{answer}")
            
            # 记录问答
            qa_history.append({"question": question, "answer": answer, "guesser": guesser})
            self.add_to_history("qa", f"{guesser}->{riddler}", f"Q: {question} | A: {answer}")
            
            # 检查是否应该揭晓
            if answer == "可以揭晓":
                print("\n🎉 出题人认为可以揭晓谜底了！")
                print(f"汤底：{riddle['solution']}")
                self.add_to_history("solution", riddler, f"谜底：{riddle['solution']}")
                return True
            
            if answer == "接近":
                print("💡 出题人提示：很接近真相了！")
            
            # 切换到下一个提问者
            current_guesser_index = (current_guesser_index + 1) % len(guessers)
        
        # 提问次数用完或主动结束
        print(f"\n{'='*40}")
        print("问答环节结束")
        
        # 最后揭晓谜底
        print(f"\n[揭晓谜底]")
        print(f"题目：{riddle['title']}")
        print(f"内容：{riddle['content']}")
        print(f"汤底：{riddle['solution']}")
        
        self.add_to_history("solution", riddler, f"谜底：{riddle['solution']}")
        
        # 询问猜谜者是否猜对
        for guesser in guessers:
            if guesser == "玩家":
                guess = input(f"\n{guesser}，你猜到谜底了吗？请输入你的猜测（或留空跳过）：").strip()
                if guess:
                    # 简单判断是否接近
                    if any(keyword in guess for keyword in riddle['solution'].split()[:5]):
                        print("✓ 接近正确答案！")
                    else:
                        print("✗ 不太接近正确答案")
        
        return False
    
    def post_game_review(self):
        """赛后复盘功能（包含AI聊天）"""
        print(f"\n{'='*60}")
        print("                赛后复盘")
        print(f"{'='*60}")
        
        if not self.history:
            print("暂无游戏历史")
            return
        
        # 统计游戏数据
        total_rounds = self.current_round
        riddles_count = sum(1 for h in self.history if h['type'] == 'riddle')
        qa_count = sum(1 for h in self.history if h['type'] == 'qa')
        solutions_count = sum(1 for h in self.history if h['type'] == 'solution')
        
        print(f"游戏统计：")
        print(f"  总轮数: {total_rounds}")
        print(f"  谜题数: {riddles_count}")
        print(f"  问答数: {qa_count}")
        print(f"  揭晓数: {solutions_count}")
        
        # 分析问答效果
        player_questions = {}
        for entry in self.history:
            if entry['type'] == 'qa':
                parts = entry['from'].split('->')
                if len(parts) == 2:
                    guesser = parts[0]
                    if guesser not in player_questions:
                        player_questions[guesser] = 0
                    player_questions[guesser] += 1
        
        if player_questions:
            print(f"\n玩家提问统计：")
            for player, count in player_questions.items():
                print(f"  {player}: {count} 个问题")
        
        # AI赛后聊天环节
        print(f"\n{'='*50}")
        print("    🗣️ AI玩家赛后聊天")
        print(f"{'='*50}")
        self.ai_post_game_chat()
        
        # 显示最近几条历史
        print(f"\n最近游戏记录：")
        recent_history = self.history[-min(10, len(self.history)):]
        for i, entry in enumerate(recent_history, 1):
            print(f"  {i}. [{entry['timestamp']}] {entry['type']} - {entry['from']}: {entry['content'][:50]}...")
        
        # 询问是否保存对话
        if self.history:
            save_choice = input(f"\n是否保存本次游戏对话？ (y/n): ").strip().lower()
            if save_choice == 'y':
                self.save_conversation_to_file()
            else:
                print("对话未保存")
        
        # 询问是否显示完整历史
        show_choice = input(f"是否显示完整游戏历史？ (y/n): ").strip().lower()
        if show_choice == 'y':
            self.show_history()
    
    def mini_chat_after_round(self, round_result: str = ""):
        """回合结束后的小型聊天（玩家和AI都可以参与）"""
        print(f"\n{'='*40}")
        print("    💬 回合结束聊天")
        print(f"{'='*40}")
        
        # 获取所有玩家
        all_players = self.get_all_players_in_order()
        ai_players = [p for p in all_players if p != "玩家"]
        
        if len(ai_players) == 0:
            print("没有AI玩家可以聊天")
            return
        
        print("这一回合结束了，大家有什么想说的吗？")
        print("玩家可以输入消息与AI聊天，输入'继续'开始下一回合")
        
        # 收集最近的历史作为聊天上下文
        conversation_context = ""
        if self.history:
            recent_history = self.history[-min(3, len(self.history)):]  # 最近3条记录
            for entry in recent_history:
                conversation_context += f"[{entry['type']}] {entry['from']}: {entry['content'][:80]}...\n"
        
        if round_result:
            conversation_context += f"\n回合结果：{round_result}\n"
        
        chat_messages = []
        chat_round = 0
        max_chat_rounds = 3  # 最多3轮对话
        
        while chat_round < max_chat_rounds:
            chat_round += 1
            print(f"\n--- 聊天第 {chat_round} 轮 ---")
            
            # 玩家发言
            player_input = input("\n玩家发言（输入'继续'跳过聊天）：").strip()
            if player_input.lower() == '继续':
                print("跳过剩余聊天")
                break
            
            if player_input:
                print(f"玩家：{player_input}")
                chat_messages.append(f"玩家：{player_input}")
            
            # AI玩家轮流回复（随机顺序）
            random.shuffle(ai_players)
            for ai_player in ai_players:
                print(f"\n{ai_player}正在思考...")
                
                # 获取AI的回复
                response = self.get_ai_chat_response(ai_player, conversation_context, chat_messages)
                print(f"{ai_player}：{response}")
                
                # 记录AI的回复
                chat_messages.append(f"{ai_player}：{response}")
                
                # 短暂等待，让对话更自然
                time.sleep(0.3)
        
        print(f"\n{'='*40}")
        print("    聊天结束，准备下一回合！")
        print(f"{'='*40}")
    
    def ai_post_game_chat(self):
        """AI玩家之间的赛后聊天"""
        all_players = self.get_all_players_in_order()
        ai_players = [p for p in all_players if p != "玩家"]
        
        if len(ai_players) < 2:
            print("AI玩家不足，无法进行赛后聊天")
            return
        
        print("游戏结束了，让我们听听AI玩家们的赛后聊天吧！\n")
        
        # 收集游戏回顾内容
        conversation_context = ""
        if self.history:
            recent_history = self.history[-min(5, len(self.history)):]  # 最近5条记录
            for entry in recent_history:
                conversation_context += f"[{entry['type']}] {entry['from']}: {entry['content'][:100]}...\n"
        
        # AI玩家轮流发言（随机顺序）
        random.shuffle(ai_players)
        
        # 每轮聊天3-4轮对话
        chat_rounds = random.randint(3, 4)
        chat_messages = []
        
        for round_num in range(chat_rounds):
            print(f"\n--- 第 {round_num + 1} 轮聊天 ---")
            
            for ai_player in ai_players:
                # AI思考...
                print(f"\n{ai_player}正在思考...")
                
                # 获取AI的聊天回复
                response = self.get_ai_chat_response(ai_player, conversation_context, chat_messages)
                print(f"{ai_player}: {response}")
                
                # 记录这条消息
                chat_messages.append(f"{ai_player}: {response}")
                
                # 等待一下，让对话更自然
                import time
                time.sleep(0.5)
        
        print(f"\n{'='*50}")
        print("      🎮 聊天结束，准备下一局！")
        print(f"{'='*50}")
        
        # 询问是否继续游戏
        continue_choice = input(f"\n是否继续下一局游戏？ (y/n): ").strip().lower()
        if continue_choice == 'y':
            # 重置历史，开始新游戏
            self.history = []
            self.current_round = 0
            print("\n🎮 开始新的一局游戏！")
            return True
        else:
            print("\n感谢游玩！")
            return False
    
    def start_modern_game(self):
        """开始现代海龟汤游戏（自由猜测模式）"""
        # 重置游戏状态
        self.history = []
        self.current_round = 0
        
        # 获取玩家列表
        all_players = self.get_all_players_in_order()
        print(f"\n现代海龟汤游戏开始！参与者: {', '.join(all_players)}")
        print("游戏规则：自由猜测模式，猜谜者可以直接提出完整假设")
        
        while self.current_round < self.max_rounds:
            self.current_round += 1
            
            # 确定当前轮的出题者（轮流）
            riddler_index = (self.current_round - 1) % len(all_players)
            riddler = all_players[riddler_index]
            
            # 猜谜者列表（排除出题者）
            guessers = [p for p in all_players if p != riddler]
            
            # 进行一轮现代游戏
            self.play_round(riddler, guessers)
            
            # 回合结束后的小型聊天（如果有玩家参与）
            if riddler == "玩家" or any(g == "玩家" for g in guessers):
                print(f"\n{'='*40}")
                print(f"    第 {self.current_round} 轮现代海龟汤结束")
                print(f"{'='*40}")
                result_text = f"第 {self.current_round} 轮：{riddler}出题，{len(guessers)}位猜谜者参与。"
                self.mini_chat_after_round(result_text)
            
            # 询问是否继续
            if self.current_round < self.max_rounds:
                continue_choice = input(f"\n继续下一轮吗？ ({self.current_round}/{self.max_rounds}) (y/n): ").lower()
                if continue_choice != 'y':
                    break
        
        # 游戏结束
        print(f"\n{'='*60}")
        print("                游戏结束！")
        print(f"{'='*60}")
        print(f"总共进行了 {self.current_round} 轮游戏")
        
        # 赛后复盘
        self.post_game_review()

def main():
    """主函数"""
    try:
        # 切换到脚本所在目录
        os.chdir(os.path.dirname(os.path.abspath(__file__)))
        
        game = SeaTurtleSoupGame()
        game.run()
    except KeyboardInterrupt:
        print("\n\n游戏被中断")
    except Exception as e:
        print(f"游戏运行出错: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
