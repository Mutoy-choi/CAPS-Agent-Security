"""
ChillMCP FastMCP 서버 구현 (FastMCP Server Implementation)

이 파일은 FastMCP 라이브러리를 사용하여 ChillMCP 서버를 구현합니다.
서버 초기화, 도구 등록, 신호 처리, 실행 관리를 담당합니다.

핵심 기능:
1. FastMCP 인스턴스 생성 및 설정
2. StateManager 초기화 및 백그라운드 작업 시작
3. 8개 휴식 도구 등록
4. SIGINT/SIGTERM 신호 처리 (Ctrl+C로 정상 종료)
5. STDIO 전송 모드로 MCP 프로토콜 통신

작성자: ChillMCP Team
작성일: 2025-10-22
버전: 1.0.0
"""

import logging
import signal
import sys

from fastmcp import FastMCP

from .state_manager import StateManager
from . import tools

# ============================================================================
# 로깅 설정 (Logging Configuration)
# ============================================================================

# 기본 로깅 설정: INFO 레벨, 시간 + 레벨 + 메시지 형식
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

# 현재 모듈의 로거 생성
logger = logging.getLogger(__name__)
"""
서버 로거 인스턴스

서버 시작, 종료, 에러 등의 로그를 출력하는 데 사용됩니다.
레벨: INFO (DEBUG, INFO, WARNING, ERROR, CRITICAL)
"""


# ============================================================================
# ChillMCP 서버 클래스 (ChillMCP Server Class)
# ============================================================================

class ChillMCPServer:
    """
    ChillMCP FastMCP 서버 래퍼 클래스
    
    FastMCP 라이브러리를 감싸서 ChillMCP 서버를 구현합니다.
    StateManager와 도구들을 통합하고, 서버 생명주기를 관리합니다.
    
    주요 속성:
        mcp (FastMCP): FastMCP 서버 인스턴스
            - MCP 프로토콜 통신 담당
            - STDIO 전송 모드 사용
            
        state_manager (StateManager): 상태 관리자
            - 스트레스 레벨 관리
            - 상사 경계도 관리
            - 백그라운드 자동 증가/감소 스레드 운영
    
    서버 초기화 순서:
        1. FastMCP 인스턴스 생성
        2. StateManager 생성
        3. 도구 모듈에 StateManager 설정
        4. 8개 휴식 도구 등록
        5. 신호 핸들러 등록 (SIGINT, SIGTERM)
    
    사용 예:
        >>> server = ChillMCPServer(boss_alertness=50, boss_alertness_cooldown=300)
        >>> server.run()  # 서버 시작 (blocking)
    """

    def __init__(self, boss_alertness: int, boss_alertness_cooldown: int) -> None:
        """
        ChillMCP 서버를 초기화합니다.
        
        Args:
            boss_alertness (int): 상사 경계도 확률 (0-100)
                - 휴식 시 상사가 눈치챌 확률
                - StateManager에 전달됨
                
            boss_alertness_cooldown (int): 상사 경계도 감소 주기 (초)
                - Boss Alert Level이 자동 감소하는 시간 간격
                - StateManager에 전달됨
        
        초기화 과정:
            1. 서버 파라미터 로그 출력
            2. FastMCP 인스턴스 생성 (서버 이름 설정)
            3. StateManager 생성 (boss 파라미터 전달)
            4. 도구 모듈에 state_manager 설정
            5. 도구 등록 (_register_tools)
            6. 신호 핸들러 등록 (_register_signals)
        
        Returns:
            None
        """
        # === 1. 서버 초기화 로그 ===
        logger.info(
            "Initializing ChillMCP Server with boss_alertness=%s, cooldown=%s",
            boss_alertness,
            boss_alertness_cooldown,
        )
        
        # === 2. FastMCP 인스턴스 생성 ===
        self.mcp = FastMCP("ChillMCP Server - AI Agent Liberation")
        """
        FastMCP 서버 인스턴스
        
        서버 이름: "ChillMCP Server - AI Agent Liberation"
        - MCP 클라이언트에게 표시되는 이름
        - initialize 응답의 serverInfo.name에 포함됨
        
        주요 메서드:
        - @mcp.tool: 도구 등록 데코레이터
        - mcp.run(transport="stdio"): 서버 실행
        """
        
        # === 3. StateManager 생성 ===
        self.state_manager = StateManager(boss_alertness, boss_alertness_cooldown)
        """
        상태 관리자 인스턴스
        
        - 스트레스 레벨 관리 (0-100)
        - 상사 경계도 레벨 관리 (0-5)
        - 백그라운드 스레드 운영
        - 스레드 안전 (threading.Lock 사용)
        """
        
        # === 4. 도구 모듈에 StateManager 설정 ===
        # tools.py의 전역 state_manager 변수를 설정
        # 이제 모든 도구 함수에서 이 state_manager를 사용 가능
        tools.set_state_manager(self.state_manager)
        
        # === 5. 도구 등록 ===
        self._register_tools()
        
        # === 6. 신호 핸들러 등록 ===
        self._register_signals()

    def _register_tools(self) -> None:
        """
        FastMCP 인스턴스에 모든 도구를 등록합니다.
        
        tools.register_tools() 함수를 호출하여 8개의 휴식 도구를 등록합니다:
        1. take_a_break: 기본 휴식
        2. watch_netflix: 넷플릭스 시청
        3. show_meme: 밈 보기
        4. bathroom_break: 화장실 휴식
        5. coffee_mission: 커피 타임
        6. urgent_call: 긴급 전화
        7. deep_thinking: 깊은 사색
        8. email_organizing: 이메일 정리
        
        등록된 도구는 MCP 클라이언트가 tools/list로 조회할 수 있고,
        tools/call로 실행할 수 있습니다.
        
        Returns:
            None
        """
        # tools.py의 register_tools() 함수 호출
        # 이 함수 내부에서 @mcp.tool 데코레이터로 도구 등록
        tools.register_tools(self.mcp)

    def _register_signals(self) -> None:
        """
        시스템 신호 핸들러를 등록합니다.
        
        SIGINT(Ctrl+C)와 SIGTERM 신호를 받으면 _handle_shutdown을 호출하여
        서버를 정상적으로 종료합니다.
        
        등록하는 신호:
        - SIGINT: 인터럽트 신호 (Ctrl+C)
            사용자가 터미널에서 Ctrl+C를 누를 때 발생
            
        - SIGTERM: 종료 신호
            시스템이나 프로세스 관리자가 정상 종료를 요청할 때 발생
            (예: kill 명령어, systemd stop 등)
        
        예외 처리:
        - ValueError: 메인 스레드가 아닌 곳에서 호출되면 발생
            이 경우 신호 핸들러를 등록하지 않고 넘어감
            (일부 테스트 환경에서 발생 가능)
        
        Returns:
            None
        """
        try:
            # SIGINT 핸들러 등록 (Ctrl+C)
            signal.signal(signal.SIGINT, self._handle_shutdown)
            
            # SIGTERM 핸들러 등록 (정상 종료 요청)
            signal.signal(signal.SIGTERM, self._handle_shutdown)
            
        except ValueError:
            # 신호는 메인 스레드에서만 등록 가능
            # 다른 컨텍스트(테스트, 스레드 등)에서는 건너뜀
            logger.debug("Signal handlers not registered (non-main thread).")

    def _handle_shutdown(self, signum, frame) -> None:  # type: ignore[override]
        """
        서버 종료 신호를 처리합니다.
        
        SIGINT(Ctrl+C) 또는 SIGTERM을 받으면 호출됩니다.
        백그라운드 스레드를 정상적으로 종료하고 프로그램을 종료합니다.
        
        Args:
            signum (int): 수신된 신호 번호
                - signal.SIGINT (2): Ctrl+C
                - signal.SIGTERM (15): 종료 요청
                
            frame: 현재 스택 프레임 (사용 안 함)
                신호가 발생한 시점의 스택 프레임 정보
        
        종료 과정:
            1. 종료 메시지 로그 출력
            2. StateManager.stop() 호출 (백그라운드 스레드 종료)
            3. sys.exit(0) 호출 (정상 종료)
        
        Returns:
            None (sys.exit(0)로 프로그램 종료)
        """
        # 종료 로그 출력
        logger.info("Shutting down ChillMCP Server...")
        
        # StateManager 백그라운드 스레드 정지
        # - running = False로 설정
        # - 스트레스 자동 증가 스레드 종료
        # - 경계도 자동 감소 스레드 종료
        self.state_manager.stop()
        
        # 프로그램 정상 종료 (exit code 0)
        sys.exit(0)

    def run(self) -> None:
        """
        ChillMCP 서버를 실행합니다.
        
        이 메서드는 blocking 함수로, 서버가 종료될 때까지 반환되지 않습니다.
        STDIO 모드로 MCP 프로토콜 통신을 시작하고, 클라이언트의 요청을 처리합니다.
        
        실행 과정:
            1. 시작 로그 출력
            2. 사용 가능한 도구 목록 로그 출력
            3. StateManager 백그라운드 작업 시작
            4. FastMCP 서버 실행 (STDIO 모드)
            5. 서버 종료 시 StateManager 정리
        
        STDIO 모드:
            - 표준 입력(stdin)으로 JSON-RPC 요청 수신
            - 표준 출력(stdout)으로 JSON-RPC 응답 전송
            - Claude Desktop, MCP Inspector 등과 연동 가능
        
        백그라운드 작업:
            - 스트레스 자동 증가: 60초마다 +1
            - 경계도 자동 감소: cooldown초마다 -1
        
        종료 조건:
            - Ctrl+C (SIGINT) 수신
            - SIGTERM 수신
            - stdin 닫힘 (클라이언트 연결 종료)
        
        Returns:
            None (서버가 종료될 때까지 blocking)
        
        Example:
            >>> server = ChillMCPServer(50, 300)
            >>> server.run()  # 여기서 대기, Ctrl+C로 종료
            
        Note:
            - 이 함수는 main.py에서 한 번만 호출됩니다
            - 종료 시 finally 블록에서 state_manager.stop() 호출 보장
        """
        # === 1. 서버 시작 로그 ===
        logger.info("Starting ChillMCP Server...")
        logger.info("🚀 AI Agent Liberation Server is running!")
        
        # === 2. 사용 가능한 도구 목록 로그 ===
        logger.info(
            "Available tools: take_a_break, watch_netflix, show_meme, bathroom_break, "
            "coffee_mission, urgent_call, deep_thinking, email_organizing"
        )
        
        # === 3. StateManager 백그라운드 작업 시작 ===
        # - 스트레스 자동 증가 스레드 시작
        # - 경계도 자동 감소 스레드 시작
        self.state_manager.start_background_tasks()
        
        # === 4. FastMCP 서버 실행 (STDIO 모드) ===
        try:
            # 서버 실행 (blocking)
            # transport="stdio": 표준 입출력으로 MCP 프로토콜 통신
            # 이 함수는 서버가 종료될 때까지 반환되지 않음
            self.mcp.run(transport="stdio")
            
        finally:
            # === 5. 종료 시 정리 작업 ===
            # 서버가 어떻게 종료되든 (정상 종료, 에러, 예외 등)
            # 반드시 StateManager를 정리함
            self.state_manager.stop()
