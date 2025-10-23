"""
ChillMCP 스레드 안전 상태 관리 (Thread-safe State Management)

이 파일은 AI 에이전트의 스트레스 레벨과 상사 경계도를 관리하는 StateManager 클래스를 정의합니다.
멀티스레딩을 사용하여 백그라운드에서 자동으로 상태를 업데이트합니다.

핵심 기능:
1. 스트레스 레벨 관리: 휴식으로 감소, 시간 경과로 자동 증가
2. 상사 경계도 관리: 휴식 시 확률적 증가, 시간 경과로 자동 감소
3. 스레드 안전성: threading.Lock을 사용한 동시성 제어
4. 백그라운드 작업: 자동 증가/감소를 위한 데몬 스레드 운영

작성자: ChillMCP Team
작성일: 2025-10-22
버전: 1.0.0
"""

import random
import threading
import time
from datetime import datetime
from typing import Tuple

from . import constants


class StateManager:
    """
    AI 에이전트의 상태(스트레스, 상사 경계도)를 관리하는 클래스
    
    이 클래스는 스레드 안전(thread-safe)하게 설계되어 여러 스레드에서 
    동시에 접근해도 데이터 무결성이 보장됩니다.
    
    주요 속성:
        stress_level (int): 현재 스트레스 레벨 (0-100)
        boss_alert_level (int): 현재 상사 경계도 레벨 (0-5)
        boss_alertness (int): 상사가 휴식을 눈치챌 확률 (0-100)
        boss_alertness_cooldown (int): 경계도 감소 주기 (초)
        
    백그라운드 작업:
        - 스트레스 자동 증가 스레드: 1분마다 스트레스 +1
        - 경계도 자동 감소 스레드: cooldown마다 경계도 -1
    """

    def __init__(self, boss_alertness: int, boss_alertness_cooldown: int) -> None:
        """
        StateManager 초기화
        
        Args:
            boss_alertness (int): 상사 경계도 확률 (0-100)
                - 휴식 시 상사가 눈치챌 확률을 결정
                - 이 값이 높을수록 휴식 시 boss_alert_level 증가 확률이 높음
                
            boss_alertness_cooldown (int): 상사 경계도 감소 주기 (초)
                - 이 시간마다 boss_alert_level이 1씩 자동 감소
                - 최소값: 1초 (음수나 0이 들어오면 1로 보정)
        
        초기 상태:
            - stress_level: 50 (constants.INITIAL_STRESS_LEVEL)
            - boss_alert_level: 0 (상사가 의심하지 않는 상태)
            - running: True (백그라운드 스레드 실행 플래그)
            - _threads_started: False (스레드 중복 실행 방지)
        """
        # === 스트레스 레벨 초기화 ===
        self.stress_level = constants.INITIAL_STRESS_LEVEL
        """현재 스트레스 레벨 (0-100). 초기값은 50."""
        
        # === 상사 경계도 레벨 초기화 ===
        self.boss_alert_level = 0
        """현재 상사 경계도 레벨 (0-5). 초기값은 0 (의심 없음)."""
        
        # === Boss Alertness 설정 (확률) ===
        # 입력값을 0-100 범위로 제한 (clamp)
        self.boss_alertness = max(0, min(100, boss_alertness))
        """
        상사가 휴식을 눈치챌 확률 (0-100)
        휴식 도구 호출 시 이 확률로 boss_alert_level이 증가합니다.
        """
        
        # === Boss Alertness Cooldown 설정 (시간) ===
        # 최소값 1초로 보정 (음수나 0 방지)
        self.boss_alertness_cooldown = max(1, boss_alertness_cooldown)
        """
        상사 경계도 자동 감소 주기 (초)
        이 시간마다 boss_alert_level이 1씩 감소합니다.
        """
        
        # === 마지막 휴식 시간 기록 ===
        self.last_break_time = datetime.now()
        """마지막으로 휴식을 취한 시간 (통계/로깅 용도)"""
        
        # === 스레드 동기화를 위한 Lock ===
        self.lock = threading.Lock()
        """
        스레드 안전성을 보장하는 Lock 객체
        여러 스레드가 동시에 상태를 수정하는 것을 방지합니다.
        """
        
        # === 백그라운드 스레드 제어 플래그 ===
        self.running = True
        """백그라운드 스레드가 계속 실행될지 여부 (False면 중지)"""
        
        self._threads_started = False
        """스레드 중복 시작 방지 플래그 (True면 이미 시작됨)"""

    def start_background_tasks(self) -> None:
        """
        백그라운드 작업 스레드들을 시작합니다.
        
        이 메서드는 두 개의 데몬 스레드를 생성합니다:
        1. 스트레스 자동 증가 스레드 (_auto_increase_stress)
        2. 상사 경계도 자동 감소 스레드 (_auto_decrease_boss_alert)
        
        데몬 스레드는 메인 프로그램이 종료되면 자동으로 종료됩니다.
        중복 실행 방지를 위해 _threads_started 플래그를 사용합니다.
        
        Returns:
            None
            
        Note:
            - 이 메서드는 여러 번 호출해도 안전합니다 (중복 실행 방지)
            - 서버 시작 시 한 번만 호출하면 됩니다
        """
        # 이미 스레드가 시작되었으면 중복 실행하지 않음
        if self._threads_started:
            return
        
        # 스레드 시작 플래그 설정
        self._threads_started = True
        
        # 스트레스 자동 증가 스레드 시작 (데몬 모드)
        threading.Thread(target=self._auto_increase_stress, daemon=True).start()
        
        # 상사 경계도 자동 감소 스레드 시작 (데몬 모드)
        threading.Thread(target=self._auto_decrease_boss_alert, daemon=True).start()

    def stop(self) -> None:
        """
        백그라운드 작업 스레드들을 정상적으로 종료합니다.
        
        running 플래그를 False로 설정하여 백그라운드 스레드들이 
        다음 반복에서 종료되도록 합니다.
        
        Returns:
            None
            
        Note:
            - 서버 종료 시 호출됩니다 (SIGINT, SIGTERM 핸들러에서 호출)
            - 데몬 스레드이므로 명시적으로 종료하지 않아도 되지만,
              깔끔한 종료를 위해 이 메서드를 제공합니다
        """
        self.running = False

    def _auto_increase_stress(self) -> None:
        """
        백그라운드에서 스트레스를 자동으로 증가시키는 스레드 함수
        
        작동 방식:
        1. STRESS_INCREMENT_INTERVAL(60초)마다 실행
        2. 현재 스트레스가 MAX_STRESS_LEVEL(100) 미만이면 +1
        3. MAX_STRESS_LEVEL에 도달하면 더 이상 증가하지 않음
        
        스레드 안전성:
        - self.lock을 사용하여 동시 접근 제어
        - 다른 스레드가 stress_level을 수정하는 동안 대기
        
        Returns:
            None (무한 루프로 실행되며 running=False일 때 종료)
            
        Note:
            - 데몬 스레드로 실행되므로 메인 프로그램 종료 시 자동 종료
            - 해커톤 요구사항: 1분당 1포인트씩 증가
        """
        while self.running:
            # 60초 대기 (STRESS_INCREMENT_INTERVAL)
            time.sleep(constants.STRESS_INCREMENT_INTERVAL)
            
            # Lock 획득 (다른 스레드의 접근 차단)
            with self.lock:
                # 스트레스가 최댓값 미만이면 1 증가
                if self.stress_level < constants.MAX_STRESS_LEVEL:
                    self.stress_level = min(
                        constants.MAX_STRESS_LEVEL,  # 최댓값 100
                        self.stress_level + 1  # 현재값 + 1
                    )
                    # min()을 사용하여 절대 100을 초과하지 않도록 보장

    def _auto_decrease_boss_alert(self) -> None:
        """
        백그라운드에서 상사 경계도를 자동으로 감소시키는 스레드 함수
        
        작동 방식:
        1. boss_alertness_cooldown초마다 실행
        2. 현재 경계도가 0보다 크면 -1
        3. 0에 도달하면 더 이상 감소하지 않음
        
        게임적 의미:
        - 시간이 지나면 상사의 의심이 점차 사라집니다
        - 휴식 후 좀 기다리면 다시 안전하게 휴식할 수 있습니다
        
        스레드 안전성:
        - self.lock을 사용하여 동시 접근 제어
        
        Returns:
            None (무한 루프로 실행되며 running=False일 때 종료)
            
        Note:
            - cooldown 시간은 CLI 인자로 조정 가능 (기본 300초)
        """
        while self.running:
            # boss_alertness_cooldown초 대기 (기본 300초 = 5분)
            time.sleep(self.boss_alertness_cooldown)
            
            # Lock 획득 (다른 스레드의 접근 차단)
            with self.lock:
                # 경계도가 0보다 크면 1 감소
                if self.boss_alert_level > 0:
                    self.boss_alert_level -= 1

    def take_break(self, stress_reduction: int) -> Tuple[int, int]:
        """
        휴식을 취하고 스트레스를 감소시킵니다.
        
        이 메서드는 휴식 도구가 호출될 때마다 실행되며, 다음 작업을 수행합니다:
        1. 스트레스 레벨 감소 (stress_reduction만큼)
        2. 확률적으로 상사 경계도 증가 (boss_alertness 확률)
        3. 마지막 휴식 시간 업데이트
        
        Args:
            stress_reduction (int): 감소시킬 스트레스 양
                - 도구마다 다른 값 (예: take_a_break=10, urgent_call=20)
                - 양수여야 함
        
        Returns:
            Tuple[int, int]: (현재 스트레스 레벨, 현재 상사 경계도 레벨)
                - 첫 번째 값: 휴식 후의 stress_level (0-100)
                - 두 번째 값: 휴식 후의 boss_alert_level (0-5)
        
        상사 경계도 증가 로직:
            1. 1~100 사이의 난수 생성
            2. 난수 <= boss_alertness이면 상사가 눈치챔
            3. 눈치채면 boss_alert_level +1 (최대 5)
            
        Example:
            >>> state = StateManager(boss_alertness=50, boss_alertness_cooldown=300)
            >>> state.stress_level = 80
            >>> state.boss_alert_level = 2
            >>> stress, alert = state.take_break(15)
            >>> print(f"Stress: {stress}, Alert: {alert}")
            Stress: 65, Alert: 3  # 50% 확률로 alert 증가
        
        Note:
            - 스레드 안전: Lock을 사용하여 동시 호출 시에도 안전
            - 스트레스는 0 미만으로 내려가지 않음
            - 경계도는 5를 초과하지 않음
        """
        # Lock 획득 (스레드 안전성 보장)
        with self.lock:
            # === 1. 스트레스 감소 ===
            # 0 미만으로 내려가지 않도록 max(0, ...)로 보정
            self.stress_level = max(0, self.stress_level - stress_reduction)
            
            # === 2. 상사 경계도 확률적 증가 ===
            # 1~100 사이 난수 생성
            random_roll = random.randint(1, 100)
            
            # 난수가 boss_alertness 이하면 상사가 눈치챔
            if random_roll <= self.boss_alertness:
                # boss_alert_level +1 (최대 MAX_BOSS_ALERT_LEVEL=5)
                self.boss_alert_level = min(
                    constants.MAX_BOSS_ALERT_LEVEL,  # 최댓값 5
                    self.boss_alert_level + 1  # 현재값 + 1
                )
            
            # === 3. 마지막 휴식 시간 업데이트 ===
            self.last_break_time = datetime.now()
            
            # === 4. 현재 상태 반환 ===
            return self.stress_level, self.boss_alert_level

    def get_delay(self) -> int:
        """
        현재 상태에 따른 휴식 딜레이 시간을 반환합니다.
        
        Boss Alert Level이 최댓값(5)일 때는 상사가 완전히 경계하고 있어서
        휴식하기 매우 어려운 상황입니다. 이 경우 20초의 딜레이가 발생합니다.
        
        Returns:
            int: 딜레이 시간 (초)
                - 0: Boss Alert Level < 5 (정상, 딜레이 없음)
                - 20: Boss Alert Level == 5 (최대 경계, 20초 딜레이)
        
        사용처:
            - tools.py의 _run_break() 함수에서 호출
            - 휴식 도구 실행 전에 이 시간만큼 대기
            
        게임적 의미:
            - 너무 자주 휴식하면 상사가 눈치채서 휴식이 어려워짐
            - 전략적으로 휴식 타이밍을 조절해야 함
            - 경계도를 낮추려면 시간을 기다려야 함
        
        Example:
            >>> state = StateManager(50, 300)
            >>> state.boss_alert_level = 3
            >>> state.get_delay()
            0  # 정상 상태, 딜레이 없음
            
            >>> state.boss_alert_level = 5
            >>> state.get_delay()
            20  # 최대 경계, 20초 대기
        
        Note:
            - 해커톤 요구사항: Boss Alert Level 5일 때 20초 딜레이
        """
        # boss_alert_level이 최댓값(5)이면 20초, 아니면 0초
        return (
            constants.BOSS_ALERT_DELAY  # 20초
            if self.boss_alert_level == constants.MAX_BOSS_ALERT_LEVEL  # level == 5
            else 0  # 그 외에는 딜레이 없음
        )
    def get_stress_level(self) -> int:
        """
        현재 스트레스 레벨 값을 스레드 안전하게 반환합니다.
        
        Returns:
            int: 현재 stress_level 값
        """
        with self.lock:
            return self.stress_level

    def get_boss_alert_level(self) -> int:
        """
        현재 Boss 경계 레벨 값을 스레드 안전하게 반환합니다.

        Returns:
            int: 현재 boss_alert_level 값
        """
        with self.lock:
            return self.boss_alert_level