"""
ChillMCP FastMCP 서버 진입점 (Entry Point)

이 파일은 ChillMCP 서버의 메인 실행 파일입니다.
명령줄 인자를 파싱하고, 서버 인스턴스를 생성하여 실행합니다.

사용법:
    python main.py
    python main.py --boss_alertness 80 --boss_alertness_cooldown 60

작성자: ChillMCP Team
작성일: 2025-10-22
버전: 1.0.0
"""

import argparse
import sys

from src.constants import DEFAULT_BOSS_ALERTNESS, DEFAULT_BOSS_COOLDOWN
from src.server import ChillMCPServer


def main() -> None:
    """
    메인 함수: CLI 인자를 파싱하고 ChillMCP 서버를 실행합니다.
    
    명령줄 인자:
        --boss_alertness (int): 상사의 경계도 확률 (0-100)
            - 0: 상사가 전혀 눈치채지 못함 (휴식 시 Boss Alert Level 절대 증가 안함)
            - 50: 50% 확률로 상사가 눈치챔 (기본값)
            - 100: 상사가 항상 눈치챔 (휴식 시 Boss Alert Level 항상 증가)
            
        --boss_alertness_cooldown (int): 상사 경계도 감소 주기 (초 단위)
            - Boss Alert Level이 1씩 감소하는 시간 간격
            - 기본값: 300초 (5분)
            - 예: 60으로 설정하면 1분마다 Boss Alert Level 1씩 감소
    
    반환값:
        None
        
    예외 처리:
        - boss_alertness가 0-100 범위를 벗어나면 에러 메시지 출력 후 종료
        - boss_alertness_cooldown이 0 이하면 에러 메시지 출력 후 종료
    """
    # ArgumentParser 생성 - 명령줄 인자 처리를 위한 파서 객체
    parser = argparse.ArgumentParser(
        description="ChillMCP - AI Agent Liberation Server (AI 에이전트 해방 서버)"
    )
    
    # --boss_alertness 인자 추가
    # 상사가 휴식을 눈치챌 확률을 결정하는 핵심 파라미터
    parser.add_argument(
        "--boss_alertness",
        type=int,  # 정수형으로 파싱
        default=DEFAULT_BOSS_ALERTNESS,  # 기본값: 50 (constants.py에서 가져옴)
        help="상사 경계도 확률 (0-100). 높을수록 휴식 시 들킬 확률이 높아집니다.",
    )
    
    # --boss_alertness_cooldown 인자 추가
    # Boss Alert Level이 자동으로 감소하는 시간 간격
    parser.add_argument(
        "--boss_alertness_cooldown",
        type=int,  # 정수형으로 파싱
        default=DEFAULT_BOSS_COOLDOWN,  # 기본값: 300초 (constants.py에서 가져옴)
        help="상사 경계도 감소 주기 (초). 이 시간마다 Boss Alert Level이 1씩 감소합니다.",
    )
    
    # 명령줄 인자 파싱 실행
    args = parser.parse_args()

    # === 입력 값 검증 (Validation) ===
    
    # boss_alertness는 반드시 0에서 100 사이의 값이어야 함 (확률이므로)
    if not 0 <= args.boss_alertness <= 100:
        print("❌ Error: boss_alertness는 0과 100 사이의 값이어야 합니다.")
        print(f"   입력된 값: {args.boss_alertness}")
        sys.exit(1)  # 비정상 종료 (exit code 1)

    # boss_alertness_cooldown은 반드시 양수여야 함 (시간 간격이므로)
    if args.boss_alertness_cooldown <= 0:
        print("❌ Error: boss_alertness_cooldown은 양수여야 합니다.")
        print(f"   입력된 값: {args.boss_alertness_cooldown}")
        sys.exit(1)  # 비정상 종료 (exit code 1)

    # === ChillMCP 서버 생성 및 실행 ===
    
    # ChillMCPServer 인스턴스 생성
    # - 검증된 boss_alertness와 boss_alertness_cooldown 값을 전달
    # - 서버 내부에서 StateManager를 초기화하고 FastMCP를 설정함
    server = ChillMCPServer(args.boss_alertness, args.boss_alertness_cooldown)
    
    # 서버 실행 (STDIO 모드로 MCP 프로토콜 통신 시작)
    # 이 함수는 blocking 함수로, 서버가 종료될 때까지 여기서 대기함
    # Ctrl+C (SIGINT) 또는 SIGTERM 신호를 받으면 정상 종료됨
    server.run()


# Python 스크립트가 직접 실행될 때만 main() 호출
# 다른 모듈에서 import될 때는 실행되지 않음
if __name__ == "__main__":
    main()
