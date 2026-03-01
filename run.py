#!/usr/bin/env python3
"""
AI海龟汤游戏 - 启动脚本
完全由AI生成
"""

import sys
import os

# 添加src目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def main():
    """主函数"""
    try:
        from sea_turtle_soup import SeaTurtleSoupGame
        game = SeaTurtleSoupGame()
        game.run()
    except ImportError as e:
        print(f"导入错误: {e}")
        print("请确保已安装依赖: pip install -r requirements.txt")
    except KeyboardInterrupt:
        print("\n\n游戏被中断")
    except Exception as e:
        print(f"游戏运行出错: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()