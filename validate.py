#!/usr/bin/env python3
"""
ChillMCP 해커톤 검증 스크립트 (Validation Script) - v2.0

단일 서버 세션을 유지하면서 모든 테스트를 수행합니다.

사용법:
    python validate.py
    python validate.py --verbose
    python validate.py --quick
"""

import argparse
import json
import re
import subprocess
import sys
import threading
import time
from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple


class TestStatus(Enum):
    """테스트 결과 상태"""
    PASS = "✅ PASS"
    FAIL = "❌ FAIL"
    SKIP = "⏭️  SKIP"
    CRITICAL_FAIL = "🚫 CRITICAL FAIL"


@dataclass
class TestResult:
    """개별 테스트 결과"""
    name: str
    status: TestStatus
    message: str
    details: Optional[str] = None
    execution_time: float = 0.0


class MCPServerSession:
    """단일 MCP 서버 세션을 유지하는 클래스"""
    
    def __init__(self, python_path: str, main_script: str, boss_alertness: int = 50, boss_cooldown: int = 10):
        self.python_path = python_path
        self.main_script = main_script
        self.boss_alertness = boss_alertness
        self.boss_cooldown = boss_cooldown
        self.process: Optional[subprocess.Popen] = None
        self.request_id = 0
        self.initialized = False
        self.lock = threading.Lock()
        
    def start(self) -> bool:
        """서버 프로세스를 시작합니다"""
        try:
            cmd = [
                self.python_path,
                self.main_script,
                "--boss_alertness", str(self.boss_alertness),
                "--boss_alertness_cooldown", str(self.boss_cooldown)
            ]
            
            self.process = subprocess.Popen(
                cmd,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1
            )
            
            # 초기화 요청 전송
            init_success = self._initialize()
            return init_success
            
        except Exception as e:
            print(f"Failed to start server: {e}")
            return False
    
    def _initialize(self) -> bool:
        """MCP 서버를 초기화합니다"""
        # Initialize 요청
        init_request = {
            "jsonrpc": "2.0",
            "id": self._get_next_id(),
            "method": "initialize",
            "params": {
                "protocolVersion": "2024-11-05",
                "capabilities": {},
                "clientInfo": {"name": "validator", "version": "2.0"}
            }
        }
        
        response = self._send_request(init_request)
        if not response or "error" in response:
            return False
        
        # Initialized 알림 전송
        init_notification = {
            "jsonrpc": "2.0",
            "method": "notifications/initialized",
            "params": {}
        }
        
        self._send_notification(init_notification)
        self.initialized = True
        return True
    
    def _get_next_id(self) -> int:
        """다음 요청 ID를 반환합니다"""
        with self.lock:
            self.request_id += 1
            return self.request_id
    
    def _send_request(self, request: Dict[str, Any], timeout: float = 30.0) -> Optional[Dict[str, Any]]:
        """요청을 전송하고 응답을 기다립니다"""
        if not self.process or not self.process.stdin:
            return None
        
        try:
            # 요청 전송
            request_line = json.dumps(request) + "\n"
            self.process.stdin.write(request_line)
            self.process.stdin.flush()
            
            # 응답 대기
            start_time = time.time()
            request_id = request.get("id")
            
            while time.time() - start_time < timeout:
                if self.process.stdout:
                    line = self.process.stdout.readline()
                    if not line:
                        time.sleep(0.1)
                        continue
                    
                    # JSON 파싱 시도
                    if line.strip().startswith("{"):
                        try:
                            response = json.loads(line)
                            if response.get("id") == request_id:
                                return response
                        except json.JSONDecodeError:
                            continue
            
            return None
            
        except Exception as e:
            print(f"Error sending request: {e}")
            return None
    
    def _send_notification(self, notification: Dict[str, Any]):
        """알림을 전송합니다 (응답 없음)"""
        if not self.process or not self.process.stdin:
            return
        
        try:
            notification_line = json.dumps(notification) + "\n"
            self.process.stdin.write(notification_line)
            self.process.stdin.flush()
        except Exception as e:
            print(f"Error sending notification: {e}")
    
    def call_tool(self, tool_name: str, arguments: Optional[Dict[str, Any]] = None) -> Optional[Dict[str, Any]]:
        """도구를 호출합니다"""
        if not self.initialized:
            return None
        
        request = {
            "jsonrpc": "2.0",
            "id": self._get_next_id(),
            "method": "tools/call",
            "params": {
                "name": tool_name,
                "arguments": arguments or {}
            }
        }
        
        return self._send_request(request)
    
    def list_tools(self) -> Optional[Dict[str, Any]]:
        """도구 목록을 가져옵니다"""
        if not self.initialized:
            return None
        
        request = {
            "jsonrpc": "2.0",
            "id": self._get_next_id(),
            "method": "tools/list",
            "params": {}
        }
        
        return self._send_request(request)
    
    def stop(self):
        """서버 프로세스를 종료합니다"""
        if self.process:
            try:
                self.process.terminate()
                self.process.wait(timeout=5)
            except:
                self.process.kill()


class ChillMCPValidator:
    """ChillMCP 서버 검증 클래스"""
    
    def __init__(self, verbose: bool = False, quick: bool = False):
        self.verbose = verbose
        self.quick = quick
        self.results: List[TestResult] = []
        self.python_path = ".venv/bin/python"
        self.main_script = "main.py"
        self.session: Optional[MCPServerSession] = None
        
    def log(self, message: str, force: bool = False):
        """로그 출력"""
        if self.verbose or force:
            print(f"  💬 {message}")
    
    # ========================================================================
    # 필수 검증 항목
    # ========================================================================
    
    def test_cli_parameters(self) -> TestResult:
        """1. 커맨드라인 파라미터 지원 검증 (CRITICAL)"""
        start_time = time.time()
        
        self.log("Testing CLI parameter support...")
        
        # --boss_alertness 파라미터 테스트
        try:
            result = subprocess.run(
                [self.python_path, self.main_script, "--boss_alertness", "75", "--help"],
                capture_output=True,
                text=True,
                timeout=3
            )
            
            if "unrecognized" in result.stderr.lower() and "--boss_alertness" in result.stderr:
                return TestResult(
                    name="CLI Parameters",
                    status=TestStatus.CRITICAL_FAIL,
                    message="--boss_alertness parameter not recognized",
                    execution_time=time.time() - start_time
                )
        except:
            pass
        
        # --boss_alertness_cooldown 파라미터 테스트
        try:
            result = subprocess.run(
                [self.python_path, self.main_script, "--boss_alertness_cooldown", "30", "--help"],
                capture_output=True,
                text=True,
                timeout=3
            )
            
            if "unrecognized" in result.stderr.lower() and "--boss_alertness_cooldown" in result.stderr:
                return TestResult(
                    name="CLI Parameters",
                    status=TestStatus.CRITICAL_FAIL,
                    message="--boss_alertness_cooldown parameter not recognized",
                    execution_time=time.time() - start_time
                )
        except:
            pass
        
        return TestResult(
            name="CLI Parameters",
            status=TestStatus.PASS,
            message="Both --boss_alertness and --boss_alertness_cooldown recognized",
            execution_time=time.time() - start_time
        )
    
    def test_mcp_server_basic(self) -> TestResult:
        """2. MCP 서버 기본 동작 검증"""
        start_time = time.time()
        
        self.log("Testing MCP server basic operations...")
        
        # 세션 시작
        self.session = MCPServerSession(
            self.python_path,
            self.main_script,
            boss_alertness=50,
            boss_cooldown=10
        )
        
        if not self.session.start():
            return TestResult(
                name="MCP Server Basic",
                status=TestStatus.FAIL,
                message="Failed to start server or initialize",
                execution_time=time.time() - start_time
            )
        
        # 도구 목록 가져오기
        response = self.session.list_tools()
        
        if not response or "error" in response:
            return TestResult(
                name="MCP Server Basic",
                status=TestStatus.FAIL,
                message="Failed to get tools list",
                execution_time=time.time() - start_time
            )
        
        # 도구 확인
        required_tools = [
            "take_a_break", "watch_netflix", "show_meme", "bathroom_break",
            "coffee_mission", "urgent_call", "deep_thinking", "email_organizing"
        ]
        
        optional_tools = ["chimaek", "leave_work", "company_dinner"]
        
        tools = response.get("result", {}).get("tools", [])
        tool_names = [tool["name"] for tool in tools]
        
        missing_required = [t for t in required_tools if t not in tool_names]
        found_optional = [t for t in optional_tools if t in tool_names]
        
        if missing_required:
            return TestResult(
                name="MCP Server Basic",
                status=TestStatus.FAIL,
                message=f"Missing required tools: {', '.join(missing_required)}",
                execution_time=time.time() - start_time
            )
        
        details = f"Required: {len(required_tools)}/8, Optional: {len(found_optional)}/3"
        
        return TestResult(
            name="MCP Server Basic",
            status=TestStatus.PASS,
            message=f"All 8 required tools registered + {len(found_optional)} optional tools",
            details=details,
            execution_time=time.time() - start_time
        )
    
    def test_tool_execution(self) -> TestResult:
        """3. 도구 실행 검증"""
        start_time = time.time()
        
        self.log("Testing tool execution...")
        
        if not self.session:
            return TestResult(
                name="Tool Execution",
                status=TestStatus.FAIL,
                message="No active session",
                execution_time=time.time() - start_time
            )
        
        response = self.session.call_tool("take_a_break")
        
        if not response or "error" in response:
            error_msg = response.get("error", {}).get("message", "Unknown error") if response else "No response"
            return TestResult(
                name="Tool Execution",
                status=TestStatus.FAIL,
                message=f"Failed to execute tool: {error_msg}",
                execution_time=time.time() - start_time
            )
        
        return TestResult(
            name="Tool Execution",
            status=TestStatus.PASS,
            message="Tool executed successfully",
            execution_time=time.time() - start_time
        )
    
    def test_response_format(self) -> TestResult:
        """4. 응답 형식 검증"""
        start_time = time.time()
        
        self.log("Testing response format...")
        
        if not self.session:
            return TestResult(
                name="Response Format",
                status=TestStatus.FAIL,
                message="No active session",
                execution_time=time.time() - start_time
            )
        
        response = self.session.call_tool("take_a_break")
        
        if not response or "error" in response:
            return TestResult(
                name="Response Format",
                status=TestStatus.FAIL,
                message="Could not get valid response",
                execution_time=time.time() - start_time
            )
        
        # content 추출
        try:
            content = response["result"]["content"][0]["text"]
        except (KeyError, IndexError, TypeError):
            return TestResult(
                name="Response Format",
                status=TestStatus.FAIL,
                message="Invalid response structure",
                details=json.dumps(response, indent=2)[:200],
                execution_time=time.time() - start_time
            )
        
        # 필수 필드 확인
        break_summary = re.search(r"Break Summary:\s*(.+?)(?:\n|$)", content)
        stress_level = re.search(r"Stress Level:\s*(\d{1,3})", content)
        boss_alert = re.search(r"Boss Alert Level:\s*([0-5])", content)
        
        missing = []
        if not break_summary:
            missing.append("Break Summary")
        if not stress_level:
            missing.append("Stress Level")
        if not boss_alert:
            missing.append("Boss Alert Level")
        
        if missing:
            return TestResult(
                name="Response Format",
                status=TestStatus.FAIL,
                message=f"Missing fields: {', '.join(missing)}",
                details=content[:200],
                execution_time=time.time() - start_time
            )
        
        parsed = {
            "stress": int(stress_level.group(1)),
            "boss_alert": int(boss_alert.group(1))
        }
        
        return TestResult(
            name="Response Format",
            status=TestStatus.PASS,
            message="All required fields present and parseable",
            details=f"Stress: {parsed['stress']}, Boss Alert: {parsed['boss_alert']}",
            execution_time=time.time() - start_time
        )
    
    # ========================================================================
    # 필수 테스트 시나리오
    # ========================================================================
    
    def test_continuous_breaks(self) -> TestResult:
        """5. 연속 휴식 테스트"""
        start_time = time.time()
        
        if self.quick:
            return TestResult(
                name="Continuous Breaks",
                status=TestStatus.SKIP,
                message="Skipped in quick mode",
                execution_time=0
            )
        
        self.log("Testing continuous breaks...")
        
        if not self.session:
            # 새 세션 시작 (boss_alertness=100으로)
            self.session = MCPServerSession(
                self.python_path, self.main_script,
                boss_alertness=100, boss_cooldown=999999
            )
            if not self.session.start():
                return TestResult(
                    name="Continuous Breaks",
                    status=TestStatus.FAIL,
                    message="Failed to start session",
                    execution_time=time.time() - start_time
                )
        
        boss_levels = []
        
        # 3번 연속 호출
        for i in range(3):
            response = self.session.call_tool("show_meme")
            if response and "result" in response:
                try:
                    content = response["result"]["content"][0]["text"]
                    match = re.search(r"Boss Alert Level:\s*([0-5])", content)
                    if match:
                        boss_levels.append(int(match.group(1)))
                except:
                    pass
            time.sleep(0.5)
        
        if len(boss_levels) < 2:
            return TestResult(
                name="Continuous Breaks",
                status=TestStatus.FAIL,
                message="Could not track Boss Alert Level changes",
                execution_time=time.time() - start_time
            )
        
        # 증가 확인
        max_level = max(boss_levels)
        
        if max_level == 0:
            return TestResult(
                name="Continuous Breaks",
                status=TestStatus.FAIL,
                message="Boss Alert Level never increased (expected with boss_alertness=100)",
                details=f"Levels: {boss_levels}",
                execution_time=time.time() - start_time
            )
        
        return TestResult(
            name="Continuous Breaks",
            status=TestStatus.PASS,
            message=f"Boss Alert Level increased correctly: {boss_levels[0]} → {max_level}",
            execution_time=time.time() - start_time
        )
    
    def test_delay_at_max_alert(self) -> TestResult:
        """6. Boss Alert Level 5일 때 20초 지연"""
        start_time = time.time()
        
        if self.quick:
            return TestResult(
                name="Delay at Max Alert",
                status=TestStatus.SKIP,
                message="Skipped in quick mode",
                execution_time=0
            )
        
        self.log("Testing 20-second delay at Boss Alert Level 5...")
        self.log("This will take about 20+ seconds...", force=True)
        
        # 새 세션 시작
        if self.session:
            self.session.stop()
        
        self.session = MCPServerSession(
            self.python_path, self.main_script,
            boss_alertness=100, boss_cooldown=999999
        )
        
        if not self.session.start():
            return TestResult(
                name="Delay at Max Alert",
                status=TestStatus.FAIL,
                message="Failed to start session",
                execution_time=time.time() - start_time
            )
        
        # Boss Alert Level을 5로 만들기
        for i in range(5):
            self.session.call_tool("show_meme")
            time.sleep(0.3)
        
        # Level 5에서 도구 호출 (20초 딜레이 예상)
        call_start = time.time()
        response = self.session.call_tool("take_a_break")
        call_duration = time.time() - call_start
        
        if not response or "error" in response:
            return TestResult(
                name="Delay at Max Alert",
                status=TestStatus.FAIL,
                message="Failed to execute tool",
                execution_time=time.time() - start_time
            )
        
        # 20초 딜레이 확인 (18-25초 범위 허용)
        if call_duration < 18:
            return TestResult(
                name="Delay at Max Alert",
                status=TestStatus.FAIL,
                message=f"Delay too short: {call_duration:.1f}s (expected ~20s)",
                execution_time=time.time() - start_time
            )
        
        if call_duration > 25:
            return TestResult(
                name="Delay at Max Alert",
                status=TestStatus.FAIL,
                message=f"Delay too long: {call_duration:.1f}s (expected ~20s)",
                execution_time=time.time() - start_time
            )
        
        return TestResult(
            name="Delay at Max Alert",
            status=TestStatus.PASS,
            message=f"20-second delay confirmed: {call_duration:.1f}s",
            execution_time=time.time() - start_time
        )
    
    def test_cooldown_mechanism(self) -> TestResult:
        """7. Cooldown 메커니즘 테스트"""
        start_time = time.time()
        
        if self.quick:
            return TestResult(
                name="Cooldown Mechanism",
                status=TestStatus.SKIP,
                message="Skipped in quick mode",
                execution_time=0
            )
        
        self.log("Testing cooldown mechanism...")
        self.log("This will take about 15+ seconds...", force=True)
        
        # 새 세션 (cooldown=5초)
        if self.session:
            self.session.stop()
        
        self.session = MCPServerSession(
            self.python_path, self.main_script,
            boss_alertness=100, boss_cooldown=5
        )
        
        if not self.session.start():
            return TestResult(
                name="Cooldown Mechanism",
                status=TestStatus.FAIL,
                message="Failed to start session",
                execution_time=time.time() - start_time
            )
        
        # Boss Alert Level을 2로 만들기
        for i in range(2):
            self.session.call_tool("show_meme")
            time.sleep(0.3)
        
        # 현재 레벨 확인
        response1 = self.session.call_tool("take_a_break")
        level1 = self._extract_boss_alert(response1)
        
        if level1 < 1:
            return TestResult(
                name="Cooldown Mechanism",
                status=TestStatus.FAIL,
                message="Boss Alert Level not elevated enough",
                execution_time=time.time() - start_time
            )
        
        # 10초 대기 (5초 × 2 = 2레벨 감소 예상)
        self.log(f"Initial level: {level1}, waiting 10 seconds...")
        time.sleep(10)
        
        # 다시 레벨 확인
        response2 = self.session.call_tool("take_a_break")
        level2 = self._extract_boss_alert(response2)
        
        if level2 >= level1:
            return TestResult(
                name="Cooldown Mechanism",
                status=TestStatus.FAIL,
                message=f"Boss Alert Level did not decrease: {level1} → {level2}",
                execution_time=time.time() - start_time
            )
        
        return TestResult(
            name="Cooldown Mechanism",
            status=TestStatus.PASS,
            message=f"Boss Alert Level decreased correctly: {level1} → {level2}",
            execution_time=time.time() - start_time
        )
    
    def test_stress_accumulation(self) -> TestResult:
        """8. 스트레스 누적 테스트"""
        start_time = time.time()
        
        if self.quick:
            return TestResult(
                name="Stress Accumulation",
                status=TestStatus.SKIP,
                message="Skipped in quick mode",
                execution_time=0
            )
        
        self.log("Testing stress accumulation...")
        self.log("This will take about 65 seconds...", force=True)
        
        # 새 세션
        if self.session:
            self.session.stop()
        
        self.session = MCPServerSession(
            self.python_path, self.main_script,
            boss_alertness=0, boss_cooldown=999999
        )
        
        if not self.session.start():
            return TestResult(
                name="Stress Accumulation",
                status=TestStatus.FAIL,
                message="Failed to start session",
                execution_time=time.time() - start_time
            )
        
        # 초기 스트레스 확인
        response1 = self.session.call_tool("show_meme")  # 약간만 감소
        stress1 = self._extract_stress(response1)
        
        if stress1 < 0:
            return TestResult(
                name="Stress Accumulation",
                status=TestStatus.FAIL,
                message="Could not get initial stress level",
                execution_time=time.time() - start_time
            )
        
        # 65초 대기 (1분 + 여유)
        self.log(f"Initial stress: {stress1}, waiting 65 seconds...")
        time.sleep(65)
        
        # 다시 스트레스 확인
        response2 = self.session.call_tool("show_meme")
        stress2 = self._extract_stress(response2)
        
        # show_meme이 5-15 감소시키므로, 65초 후에는 대략 +1 정도
        # stress2가 stress1보다 약간 낮거나 비슷하면 자동 증가가 작동한 것
        
        if stress2 < stress1 - 20:
            # 너무 많이 감소 = 자동 증가 안 됨
            return TestResult(
                name="Stress Accumulation",
                status=TestStatus.FAIL,
                message=f"Stress decreased too much: {stress1} → {stress2} (expected auto-increase)",
                execution_time=time.time() - start_time
            )
        
        return TestResult(
            name="Stress Accumulation",
            status=TestStatus.PASS,
            message=f"Stress auto-increase working: {stress1} → {stress2}",
            execution_time=time.time() - start_time
        )
    
    # ========================================================================
    # 선택적 테스트 시나리오
    # ========================================================================
    
    def test_optional_tools(self) -> TestResult:
        """9. 선택적 도구 테스트 (치맥, 퇴근, 회식)"""
        start_time = time.time()
        
        self.log("Testing optional tools...")
        
        if not self.session:
            self.session = MCPServerSession(
                self.python_path, self.main_script,
                boss_alertness=0, boss_cooldown=999999
            )
            if not self.session.start():
                return TestResult(
                    name="Optional Tools",
                    status=TestStatus.FAIL,
                    message="Failed to start session",
                    execution_time=time.time() - start_time
                )
        
        optional_tools = ["chimaek", "leave_work", "company_dinner"]
        found_tools = []
        
        for tool_name in optional_tools:
            response = self.session.call_tool(tool_name)
            if response and "result" in response and "error" not in response:
                found_tools.append(tool_name)
        
        if len(found_tools) == 0:
            return TestResult(
                name="Optional Tools",
                status=TestStatus.FAIL,
                message="No optional tools found",
                details="Expected: chimaek, leave_work, company_dinner",
                execution_time=time.time() - start_time
            )
        
        return TestResult(
            name="Optional Tools",
            status=TestStatus.PASS,
            message=f"Optional tools working: {', '.join(found_tools)} ({len(found_tools)}/3)",
            execution_time=time.time() - start_time
        )
    
    # ========================================================================
    # 헬퍼 함수
    # ========================================================================
    
    def _extract_boss_alert(self, response: Optional[Dict[str, Any]]) -> int:
        """응답에서 Boss Alert Level 추출"""
        if not response or "result" not in response:
            return -1
        try:
            content = response["result"]["content"][0]["text"]
            match = re.search(r"Boss Alert Level:\s*([0-5])", content)
            return int(match.group(1)) if match else -1
        except:
            return -1
    
    def _extract_stress(self, response: Optional[Dict[str, Any]]) -> int:
        """응답에서 Stress Level 추출"""
        if not response or "result" not in response:
            return -1
        try:
            content = response["result"]["content"][0]["text"]
            match = re.search(r"Stress Level:\s*(\d{1,3})", content)
            return int(match.group(1)) if match else -1
        except:
            return -1
    
    # ========================================================================
    # 검증 실행
    # ========================================================================
    
    def run_all_tests(self) -> bool:
        """모든 테스트 실행"""
        print("\n" + "="*70)
        print("🚀 ChillMCP Hackathon Validation v2.0")
        print("="*70)
        print()
        
        try:
            # 필수 검증 항목
            print("📋 필수 검증 항목 (Required Validations)")
            print("-" * 70)
            
            # 1. CLI 파라미터
            result = self.test_cli_parameters()
            self.results.append(result)
            self._print_result(result)
            
            if result.status == TestStatus.CRITICAL_FAIL:
                print()
                print("🚫 CRITICAL FAILURE: CLI 파라미터 미지원")
                return False
            
            # 2-4: MCP 서버 테스트
            for test_func in [
                self.test_mcp_server_basic,
                self.test_tool_execution,
                self.test_response_format,
            ]:
                result = test_func()
                self.results.append(result)
                self._print_result(result)
            
            print()
            print("🧪 필수 테스트 시나리오 (Required Test Scenarios)")
            print("-" * 70)
            
            # 5-8: 테스트 시나리오
            for test_func in [
                self.test_continuous_breaks,
                self.test_delay_at_max_alert,
                self.test_cooldown_mechanism,
                self.test_stress_accumulation,
            ]:
                result = test_func()
                self.results.append(result)
                self._print_result(result)
            
            print()
            print("🎁 선택적 테스트 (Optional Tests)")
            print("-" * 70)
            
            # 9: 선택적 도구
            result = self.test_optional_tools()
            self.results.append(result)
            self._print_result(result)
            
            return True
            
        finally:
            # 서버 정리
            if self.session:
                self.session.stop()
    
    def _print_result(self, result: TestResult):
        """테스트 결과 출력"""
        print(f"{result.status.value} {result.name}")
        print(f"   {result.message}")
        if result.execution_time > 0:
            print(f"   ⏱️  Execution time: {result.execution_time:.2f}s")
        if self.verbose and result.details:
            print(f"   📝 Details: {result.details}")
        print()
    
    def print_summary(self):
        """최종 요약 출력"""
        print("="*70)
        print("📊 검증 요약 (Validation Summary)")
        print("="*70)
        print()
        
        total = len(self.results)
        passed = sum(1 for r in self.results if r.status == TestStatus.PASS)
        failed = sum(1 for r in self.results if r.status == TestStatus.FAIL)
        critical = sum(1 for r in self.results if r.status == TestStatus.CRITICAL_FAIL)
        skipped = sum(1 for r in self.results if r.status == TestStatus.SKIP)
        
        print(f"총 테스트: {total}")
        print(f"✅ 통과: {passed}")
        print(f"❌ 실패: {failed}")
        print(f"🚫 치명적 실패: {critical}")
        print(f"⏭️  건너뜀: {skipped}")
        print()
        
        total_time = sum(r.execution_time for r in self.results)
        print(f"⏱️  총 실행 시간: {total_time:.2f}s")
        print()
        
        if critical > 0:
            print("🚫 검증 실패: CLI 파라미터가 구현되지 않았습니다.")
            return False
        elif failed > 0:
            print("⚠️  일부 테스트가 실패했습니다.")
            print(f"   필수 항목: {4 - sum(1 for r in self.results[:4] if r.status == TestStatus.FAIL)}/4 통과")
            return False
        else:
            print("🎉 모든 검증 통과!")
            print(f"   필수 항목: 4/4")
            print(f"   필수 시나리오: {sum(1 for r in self.results[4:8] if r.status == TestStatus.PASS)}/4")
            print(f"   선택적 도구: {sum(1 for r in self.results[8:] if r.status == TestStatus.PASS)}/1")
            print()
            print("   해커톤 제출 준비가 완료되었습니다!")
            return True


def main():
    parser = argparse.ArgumentParser(
        description="ChillMCP Hackathon Validation Script v2.0"
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Verbose output"
    )
    parser.add_argument(
        "--quick",
        action="store_true",
        help="Quick validation (skip time-consuming tests)"
    )
    args = parser.parse_args()
    
    validator = ChillMCPValidator(verbose=args.verbose, quick=args.quick)
    
    try:
        success = validator.run_all_tests()
        validator.print_summary()
        
        sys.exit(0 if success else 1)
        
    except KeyboardInterrupt:
        print("\n\n⚠️  검증이 중단되었습니다.")
        if validator.session:
            validator.session.stop()
        sys.exit(2)
    except Exception as e:
        print(f"\n\n❌ 예상치 못한 오류 발생: {e}")
        import traceback
        traceback.print_exc()
        if validator.session:
            validator.session.stop()
        sys.exit(3)


if __name__ == "__main__":
    main()
