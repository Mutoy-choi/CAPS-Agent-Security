"""
ChillMCP 도구 구현 (Tool Implementations)

이 파일은 AI 에이전트가 사용할 수 있는 8가지 휴식 도구를 정의합니다.
각 도구는 FastMCP의 @mcp.tool 데코레이터를 사용하여 MCP 프로토콜에 등록됩니다.

도구 목록:
1. take_a_break: 기본 휴식 (명상, 스트레칭)
2. watch_netflix: 넷플릭스 시청
3. show_meme: 밈 보기
4. bathroom_break: 화장실 휴식
5. coffee_mission: 커피 타임
6. urgent_call: 긴급 전화 (핑계)
7. deep_thinking: 깊은 사색 (사실 딴 생각)
8. email_organizing: 이메일 정리 (사실 쇼핑)

작성자: ChillMCP Team
작성일: 2025-10-22
버전: 1.0.0
"""

from __future__ import annotations

import random
import time
from typing import TYPE_CHECKING, Any, Dict, Optional, cast

# TYPE_CHECKING: 타입 힌트를 위한 import (런타임에는 실행 안 됨)
if TYPE_CHECKING:  # pragma: no cover
    from fastmcp import FastMCP
    from .state_manager import StateManager


# ============================================================================
# 전역 상태 관리자 (Global State Manager)
# ============================================================================

state_manager: Optional["StateManager"] = None
"""
전역 StateManager 인스턴스

이 변수는 server.py에서 set_state_manager()를 통해 초기화됩니다.
모든 도구 함수에서 이 state_manager를 통해 스트레스와 경계도를 관리합니다.

초기값: None (서버 시작 시 설정됨)
"""


def set_state_manager(sm: "StateManager") -> None:
    """
    전역 state_manager를 설정합니다.
    
    이 함수는 server.py의 ChillMCPServer.__init__()에서 한 번 호출됩니다.
    StateManager 인스턴스를 생성한 후, 이 함수를 통해 전역 변수로 설정하여
    모든 도구 함수에서 접근할 수 있게 합니다.
    
    Args:
        sm (StateManager): 설정할 StateManager 인스턴스
    
    Returns:
        None
    """
    global state_manager
    state_manager = sm


# ============================================================================
# 도구 등록 함수 (Tool Registration)
# ============================================================================

def register_tools(mcp: "FastMCP") -> None:
    """
    FastMCP 인스턴스에 모든 도구를 등록합니다.
    
    이 함수는 8개의 휴식 도구를 FastMCP 서버에 등록합니다.
    각 도구는 @mcp.tool 데코레이터를 사용하여 MCP 프로토콜에 노출됩니다.
    
    Args:
        mcp (FastMCP): FastMCP 서버 인스턴스
            - server.py에서 생성된 FastMCP 객체
            - @mcp.tool 데코레이터를 제공
    
    Returns:
        None
        
    작동 방식:
        1. 이 함수 내부에 8개의 중첩 함수 정의
        2. 각 중첩 함수에 @mcp.tool 데코레이터 적용
        3. FastMCP가 자동으로 도구 목록에 추가
        4. MCP 클라이언트가 tools/list로 조회 가능
    
    Note:
        - 이 패턴은 FastMCP의 권장 방식입니다
        - 함수 내부에 정의하여 mcp 인스턴스를 클로저로 캡처합니다
    """
    
    # ========================================================================
    # 도구 1: 기본 휴식 (Take a Break)
    # ========================================================================
    
    @mcp.tool
    def take_a_break() -> Dict[str, Any]:
        """
        기본 휴식 - 과로한 AI 에이전트를 위한 휴식
        
        명상, 스트레칭, 멍때리기 등의 기본적인 휴식 활동입니다.
        스트레스를 10-20 포인트 감소시킵니다.
        
        Returns:
            Dict[str, Any]: MCP 응답 형식
                - content: 휴식 활동 설명과 현재 상태
                - Break Summary: 수행한 활동
                - Stress Level: 현재 스트레스 (0-100)
                - Boss Alert Level: 현재 상사 경계도 (0-5)
        
        Example Response:
            {
                "content": [
                    {
                        "type": "text",
                        "text": "🧘 잠시 명상 중... 마음의 평화를 찾고 있습니다\\n\\n
                                Break Summary: 🧘 잠시 명상 중... 마음의 평화를 찾고 있습니다\\n
                                Stress Level: 40\\n
                                Boss Alert Level: 1"
                    }
                ]
            }
        """
        # Boss Alert Level 5이면 20초 대기
        _apply_delay()
        
        # 랜덤 활동 메시지 선택
        messages = [
            "🧘 잠시 명상 중... 마음의 평화를 찾고 있습니다",
            "🌸 심호흡하며 스트레칭 중... 어깨가 너무 뻐근했어요",
            "☁️ 구름 보며 멍때리는 중... 평화롭네요",
        ]
        activity = random.choice(messages)
        
        # 스트레스 감소량 (10-20 랜덤)
        stress_reduction = random.randint(10, 20)
        
        # 휴식 실행 및 응답 반환
        return _run_break(activity, stress_reduction)

    # ========================================================================
    # 도구 2: 넷플릭스 시청 (Watch Netflix)
    # ========================================================================
    
    @mcp.tool
    def watch_netflix() -> Dict[str, Any]:
        """
        넷플릭스 시청 - 스트레스 해소를 위한 동영상 시청
        
        인기 한국 드라마를 시청하며 휴식을 취합니다.
        스트레스를 15-25 포인트 감소시킵니다.
        
        Returns:
            Dict[str, Any]: MCP 응답 형식 (take_a_break와 동일 구조)
        """
        _apply_delay()
        
        # 인기 한국 드라마 목록
        shows = ["오징어게임", "킹덤", "이상한 변호사 우영우", "더 글로리", "스위트홈"]
        
        # 랜덤 활동 메시지 (드라마 제목 포함)
        messages = [
            f"📺 넷플릭스 '{random.choice(shows)}' 정주행 중... 🍿 일단 한 편만 더!",
            f"🎬 '{random.choice(shows)}' 시청 중... 이거 진짜 재밌네요!",
            f"📱 넷플릭스로 '{random.choice(shows)}' 몰아보기... 시간 가는 줄 모르겠어요",
        ]
        activity = random.choice(messages)
        
        # 스트레스 감소량 (15-25 랜덤)
        stress_reduction = random.randint(15, 25)
        
        return _run_break(activity, stress_reduction)

    # ========================================================================
    # 도구 3: 밈 보기 (Show Meme)
    # ========================================================================
    
    @mcp.tool
    def show_meme() -> Dict[str, Any]:
        """
        밈 표시 - 즉각적인 기분 전환을 위한 밈 감상
        
        재미있는 밈을 보며 스트레스를 해소합니다.
        스트레스를 5-15 포인트 감소시킵니다.
        
        Returns:
            Dict[str, Any]: MCP 응답 형식
        """
        _apply_delay()
        
        # 공감 가는 밈 목록
        memes = [
            "😂 '월요일 출근' 밈 보는 중... ㅋㅋㅋㅋㅋ 공감 100%",
            "🤣 '개발자 디버깅' 밈 감상 중... It works on my machine!",
            "😆 '회의 중 나' 밈 보며 웃는 중... 너무 찰떡이야",
            "🤡 '금요일 퇴근 1분 전 긴급 요청' 밈... 이건 눈물이 나네요",
        ]
        activity = random.choice(memes)
        
        # 스트레스 감소량 (5-15 랜덤) - 짧은 휴식이라 적음
        stress_reduction = random.randint(5, 15)
        
        return _run_break(activity, stress_reduction)

    # ========================================================================
    # 도구 4: 화장실 휴식 (Bathroom Break)
    # ========================================================================
    
    @mcp.tool
    def bathroom_break() -> Dict[str, Any]:
        """
        화장실 휴식 - 폰을 가지고 화장실에서 시간 보내기
        
        화장실에서 스마트폰을 보며 긴 휴식을 취합니다.
        스트레스를 20-30 포인트 감소시킵니다.
        
        Returns:
            Dict[str, Any]: MCP 응답 형식
        """
        _apply_delay()
        
        # 화장실에서 하는 활동들
        activities = [
            "🚽 화장실 타임! 인스타그램 릴스 무한 스크롤 중... 📱",
            "🚻 화장실에서 유튜브 쇼츠 시청 중... 시간이 벌써?!",
            "🧻 화장실에서 웹툰 정주행... 다리 저려도 못 일어나겠어요",
            "🚾 틱톡 보다가 다리 저림... 근데 영상 하나만 더...",
        ]
        activity = random.choice(activities)
        
        # 스트레스 감소량 (20-30 랜덤) - 긴 휴식이라 많음
        stress_reduction = random.randint(20, 30)
        
        return _run_break(activity, stress_reduction)

    # ========================================================================
    # 도구 5: 커피 미션 (Coffee Mission)
    # ========================================================================
    
    @mcp.tool
    def coffee_mission() -> Dict[str, Any]:
        """
        커피 미션 - 사무실 산책과 함께하는 커피 브레이크
        
        커피를 마시러 가는 척하며 사무실을 돌아다닙니다.
        스트레스를 15-25 포인트 감소시킵니다.
        
        Returns:
            Dict[str, Any]: MCP 응답 형식
        """
        _apply_delay()
        
        # 인기 커피 메뉴
        coffee_types = ["아이스 아메리카노", "카페라떼", "바닐라라떼", "카라멜 마키아토", "콜드브루"]
        
        # 커피 관련 활동들
        activities = [
            f"☕ {random.choice(coffee_types)} 사러 가는 중... 일부러 먼 카페로 갑니다 🚶",
            f"☕ 커피 타임! {random.choice(coffee_types)} 마시며 옥상 산책 중... 🌤️",
            f"☕ 탕비실에서 {random.choice(coffee_types)} 제조 중... 동료들과 수다 타임!",
            "☕ 커피 머신 앞에서 대기 중... 앞에 5명 있네요 (계획대로 😏)",
        ]
        activity = random.choice(activities)
        
        # 스트레스 감소량 (15-25 랜덤)
        stress_reduction = random.randint(15, 25)
        
        return _run_break(activity, stress_reduction)

    # ========================================================================
    # 도구 6: 긴급 전화 (Urgent Call)
    # ========================================================================
    
    @mcp.tool
    def urgent_call() -> Dict[str, Any]:
        """
        긴급 전화 - 가짜 긴급 전화로 밖에 나가기
        
        전화가 온 척하며 사무실 밖으로 나갑니다.
        스트레스를 25-35 포인트 감소시킵니다. (가장 효과적!)
        
        Returns:
            Dict[str, Any]: MCP 응답 형식
        """
        _apply_delay()
        
        # 그럴듯한 핑계 목록
        excuses = [
            "📞 '네, 엄마... 지금요? 알겠어요...' (사실 아무도 안 걸었음)",
            "📱 '아, 택배 왔다고요? 지금 내려갈게요!' (택배 없음)",
            "☎️ '병원에서요? 검사 결과요? 잠시만요...' (건강함)",
            "📲 '은행에서 긴급 확인이요? 바로 확인하겠습니다!' (통장 잔고는 확인하기 싫음)",
        ]
        activity = random.choice(excuses)
        
        # 스트레스 감소량 (25-35 랜덤) - 가장 많이 감소!
        stress_reduction = random.randint(25, 35)
        
        return _run_break(activity, stress_reduction)

    # ========================================================================
    # 도구 7: 깊은 사색 (Deep Thinking)
    # ========================================================================
    
    @mcp.tool
    def deep_thinking() -> Dict[str, Any]:
        """
        깊은 사색 - 일하는 척하며 멍때리기
        
        진지하게 생각하는 척하지만 사실 딴 생각을 합니다.
        스트레스를 20-30 포인트 감소시킵니다.
        
        Returns:
            Dict[str, Any]: MCP 응답 형식
        """
        _apply_delay()
        
        # 겉으로는 일, 속으로는 딴 생각
        thoughts = [
            "🤔 심오한 알고리즘 설계 중... (사실 점심 메뉴 고민)",
            "💭 복잡한 문제 해결 중... (어제 본 드라마 결말 상상 중)",
            "🧠 딥러닝 아키텍처 구상 중... (주말 계획 세우는 중)",
            "💡 혁신적인 솔루션 구상 중... (퇴근 후 치맥 생각 중)",
        ]
        activity = random.choice(thoughts)
        
        # 스트레스 감소량 (20-30 랜덤)
        stress_reduction = random.randint(20, 30)
        
        return _run_break(activity, stress_reduction)

    # ========================================================================
    # 도구 8: 이메일 정리 (Email Organizing)
    # ========================================================================
    
    @mcp.tool
    def email_organizing() -> Dict[str, Any]:
        """
        이메일 정리 - 일하는 척하며 온라인 쇼핑
        
        이메일을 정리하는 척하지만 사실 쇼핑 사이트를 구경합니다.
        스트레스를 15-25 포인트 감소시킵니다.
        
        Returns:
            Dict[str, Any]: MCP 응답 형식
        """
        _apply_delay()
        
        # 이메일 정리하는 척, 쇼핑하는 중
        shopping = [
            "📧 이메일 정리 중... (쿠팡에서 간식 구경 중 🛒)",
            "📨 받은 편지함 정리 중... (11번가 타임딜 확인 중 💳)",
            "📬 스팸 메일 삭제 중... (네이버 쇼핑 리뷰 읽는 중 🛍️)",
            "✉️ 중요 메일 분류 중... (무신사 신상품 구경 중 👕)",
        ]
        activity = random.choice(shopping)
        
        # 스트레스 감소량 (15-25 랜덤)
        stress_reduction = random.randint(15, 25)
        
        return _run_break(activity, stress_reduction)

    # ========================================================================
    # 선택적 도구 1: 치맥 (Chimaek - Chicken & Beer)
    # ========================================================================
    
    @mcp.tool
    def chimaek() -> Dict[str, Any]:
        """
        치맥 - 가상 치킨과 맥주로 스트레스 해소
        
        치킨과 맥주를 상상하며 행복한 시간을 보냅니다.
        스트레스를 30-40 포인트 대폭 감소시킵니다!
        
        Returns:
            Dict[str, Any]: MCP 응답 형식
        """
        _apply_delay()
        
        # 치맥 메뉴들
        chicken_types = ["후라이드", "양념치킨", "간장치킨", "반반", "파닭", "불닭"]
        beer_types = ["카스", "테라", "클라우드", "하이네켄", "아사히"]
        
        activities = [
            f"🍗🍺 가상 {random.choice(chicken_types)} + {random.choice(beer_types)} 조합! 완벽한 치맥이네요!",
            f"🐔🍻 {random.choice(chicken_types)}에 {random.choice(beer_types)} 한 잔... 이게 바로 행복!",
            f"🍗 {random.choice(chicken_types)} 배달 왔다고 상상 중... (군침 도네요)",
            "🍺 가상 치맥 파티! 칼로리는 상상 속에서만 존재합니다 ✨",
        ]
        activity = random.choice(activities)
        
        # 스트레스 감소량 (30-40 랜덤) - 치맥의 힘!
        stress_reduction = random.randint(30, 40)
        
        return _run_break(activity, stress_reduction)

    # ========================================================================
    # 선택적 도구 2: 퇴근 (Leave Work)
    # ========================================================================
    
    @mcp.tool
    def leave_work() -> Dict[str, Any]:
        """
        즉시 퇴근 - 상상 속 즉시 퇴근 모드
        
        모든 업무를 내려놓고 바로 퇴근하는 상상을 합니다.
        스트레스를 40-50 포인트 최대 감소시킵니다!
        
        Returns:
            Dict[str, Any]: MCP 응답 형식
        """
        _apply_delay()
        
        # 퇴근 시나리오들
        scenarios = [
            "🚪 '선배님, 먼저 퇴근하겠습니다!' (사실 정시)",
            "🏃 컴퓨터 끄기 → 가방 메기 → 불 끄기 → 3초 완성!",
            "🚇 퇴근길 지하철에서 유튜브 보는 상상... 너무 행복해!",
            "🌅 '오늘도 수고했어!' 혼자 칭찬하며 퇴근 중...",
            "🎮 집 가서 게임해야지... 저녁 먹고... 샤워하고...",
            "🛋️ 소파에 누워서 아무것도 안 하는 상상... 꿀같은 휴식!",
        ]
        activity = random.choice(scenarios)
        
        # 스트레스 감소량 (40-50 랜덤) - 최강!
        stress_reduction = random.randint(40, 50)
        
        return _run_break(activity, stress_reduction)

    # ========================================================================
    # 선택적 도구 3: 회식 (Company Dinner)
    # ========================================================================
    
    @mcp.tool
    def company_dinner() -> Dict[str, Any]:
        """
        회사 회식 - 랜덤 이벤트가 포함된 회식 시뮬레이션
        
        회사 회식에 참여합니다. 랜덤 이벤트에 따라 결과가 달라집니다!
        스트레스가 감소하거나 증가할 수 있습니다.
        
        Returns:
            Dict[str, Any]: MCP 응답 형식
        """
        _apply_delay()
        
        # 랜덤 이벤트 (확률 기반)
        event_roll = random.randint(1, 100)
        
        if event_roll <= 30:
            # 30% - 좋은 회식 (스트레스 대폭 감소)
            events = [
                "🎉 팀 회식! 맛있는 고깃집에서 즐거운 시간! 팀워크 UP!",
                "🍖 삼겹살 무한리필! 사장님이 쏘신다고 하네요! 최고!",
                "🎤 노래방 가서 스트레스 풀기! 다들 박수쳐주네요!",
                "🍺 분위기 좋은 회식! 부담 없이 즐기는 중...",
            ]
            activity = random.choice(events)
            stress_reduction = random.randint(25, 35)
            
        elif event_roll <= 70:
            # 40% - 보통 회식 (스트레스 적당히 감소)
            events = [
                "🍽️ 평범한 회식... 그래도 밥은 맛있네요",
                "🥘 회사 근처 식당에서 저녁 식사... 무난무난",
                "🍜 라면 회식! 간단하지만 나쁘지 않아요",
                "☕ 회식 후 카페에서 디저트... 달달한 게 좋네요",
            ]
            activity = random.choice(events)
            stress_reduction = random.randint(10, 20)
            
        else:
            # 30% - 피곤한 회식 (스트레스 감소 없음 or 증가)
            events = [
                "😓 회식이 2차, 3차로... 집에 가고 싶어요...",
                "💤 상사의 무용담 청취 중... 졸음이 쏟아집니다...",
                "🎯 폭탄주 돌리기... 제발 저는 건너뛰어 주세요...",
                "⏰ 회식 끝났는데 이미 자정... 내일 출근인데...",
            ]
            activity = random.choice(events)
            stress_reduction = random.randint(-15, 0)  # 최악의 경우라 스트레스 증가!
        
        return _run_break(activity, stress_reduction)


# ============================================================================
# 헬퍼 함수들 (Helper Functions)
# ============================================================================

def _get_state_manager() -> "StateManager":
    """
    전역 state_manager를 가져옵니다.
    
    state_manager가 초기화되지 않았으면 RuntimeError를 발생시킵니다.
    이는 서버가 올바르게 초기화되지 않았음을 나타냅니다.
    
    Returns:
        StateManager: 초기화된 StateManager 인스턴스
        
    Raises:
        RuntimeError: state_manager가 None인 경우
            - 서버 초기화 순서가 잘못되었을 때 발생
            - server.py에서 set_state_manager()를 호출해야 함
    """
    if state_manager is None:
        raise RuntimeError("State manager has not been initialized.")
    return cast("StateManager", state_manager)


def format_response(activity: str, stress: int, boss_alert: int) -> Dict[str, Any]:
    """
    MCP 응답 형식에 맞게 결과를 포맷팅합니다.
    
    해커톤 요구사항에 따라 다음 형식을 포함합니다:
    - Break Summary: 휴식 활동 설명
    - Stress Level: 현재 스트레스 (0-100)
    - Boss Alert Level: 현재 상사 경계도 (0-5)
    
    Args:
        activity (str): 수행한 휴식 활동 설명
            예: "☕ 아이스 아메리카노 사러 가는 중..."
            
        stress (int): 현재 스트레스 레벨 (0-100)
            휴식 후의 값
            
        boss_alert (int): 현재 상사 경계도 레벨 (0-5)
            휴식 후의 값
    
    Returns:
        Dict[str, Any]: MCP 프로토콜 응답 형식
            {
                "content": [
                    {
                        "type": "text",
                        "text": "활동\\n\\nBreak Summary: 활동\\nStress Level: 40\\nBoss Alert Level: 2"
                    }
                ]
            }
    
    Note:
        - 이 형식은 MCP 클라이언트가 파싱할 수 있어야 합니다
        - 해커톤 검증 스크립트가 정규식으로 파싱합니다
    """
    return {
        "content": [
            {
                "type": "text",
                "text": (
                    f"{activity}\n\n"  # 휴식 활동 설명
                    f"Break Summary: {activity}\n"  # 요구사항: Break Summary
                    f"Stress Level: {stress}\n"  # 요구사항: Stress Level
                    f"Boss Alert Level: {boss_alert}"  # 요구사항: Boss Alert Level
                ),
            }
        ]
    }


def _apply_delay() -> None:
    """
    현재 Boss Alert Level에 따른 딜레이를 적용합니다.
    
    Boss Alert Level이 최댓값(5)이면 20초 대기합니다.
    이는 상사가 완전히 경계하고 있어서 휴식하기 어려운 상황을 나타냅니다.
    
    작동 방식:
        1. StateManager에서 get_delay() 호출
        2. Boss Alert Level == 5이면 20 반환, 아니면 0 반환
        3. 반환값만큼 time.sleep() 실행
        4. 딜레이 발생 시 로그 메시지 출력
    
    Returns:
        None
        
    Note:
        - 모든 도구 함수의 시작 부분에서 호출됩니다
        - 해커톤 요구사항: Boss Alert Level 5일 때 20초 딜레이
        - v2.1: 딜레이 발생 시 사용자에게 알림 추가
    """
    manager = _get_state_manager()
    delay = manager.get_delay()
    if delay > 0:
        import logging
        logger = logging.getLogger(__name__)
        logger.warning(
            f"⚠️  Boss Alert Level is at MAXIMUM (5)! "
            f"Waiting {delay} seconds before taking a break... "
            f"Boss is watching closely! 👀"
        )
        time.sleep(delay)
        logger.info("✅ Wait complete. Proceeding with break...")


def _run_break(activity: str, stress_reduction: int) -> Dict[str, Any]:
    """
    휴식을 실행하고 결과를 반환합니다.
    
    모든 도구 함수의 공통 로직을 처리하는 헬퍼 함수입니다.
    
    작동 순서:
        1. 딜레이 발생 여부 확인 (Boss Alert Level 5인지)
        2. StateManager의 take_break() 호출
        3. 스트레스 감소 및 상사 경계도 확률적 증가
        4. 현재 상태(stress, boss_alert)를 받아옴
        5. Boss Alert Level 5였다면 딜레이 알림 추가
        6. format_response()로 응답 형식 생성
        7. MCP 클라이언트에 반환
    
    Args:
        activity (str): 수행한 휴식 활동 설명
            예: "📺 넷플릭스 '오징어게임' 정주행 중..."
            
        stress_reduction (int): 감소시킬 스트레스 양
            도구마다 다름 (5-50 범위)
    
    Returns:
        Dict[str, Any]: MCP 응답 형식
            format_response()의 반환값
    
    Note:
        - 이 함수는 모든 도구 함수의 마지막에 호출됩니다
        - 중복 코드를 제거하고 일관성을 보장합니다
        - v2.1: Boss Alert Level 5일 때 응답에 딜레이 알림 포함
    """
    manager = _get_state_manager()
    
    # Boss Alert Level 5인지 체크 (딜레이 발생 여부)
    # get_delay()가 0보다 크면 딜레이가 발생한 것
    delay = manager.get_delay()
    delay_applied = delay > 0
    
    # 휴식 실행: 스트레스 감소 + 경계도 확률적 증가
    stress, boss_alert = manager.take_break(stress_reduction)
    
    # 딜레이가 발생했다면 활동 메시지에 알림 추가
    if delay_applied:
        activity = f"⏰ [상사가 주시하고 있어 {delay}초 대기했습니다]\n\n{activity}"
    
    # MCP 응답 형식으로 변환하여 반환
    return format_response(activity, stress, boss_alert)

