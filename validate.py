#!/usr/bin/env python3
"""
ChillMCP 해커톤 검증 스크립트 (Validation Script)

이 스크립트는 SKT AI Summit Hackathon Pre-mission의 모든 요구사항을
자동으로 검증합니다.

검증 항목:
1. 커맨드라인 파라미터 지원 (필수)
2. MCP 서버 기본 동작
3. 상태 관리 검증
4. 응답 형식 검증
5. 테스트 시나리오 실행

사용법:
    python validate.py
    python validate.py --verbose
    python validate.py --quick  # 빠른 검증 (시간 관련 테스트 제외)
"""

import argparse
import json
import re
import subprocess
import sys
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


class ChillMCPValidator:
    """ChillMCP 서버 검증 클래스"""
    
    def __init__(self, verbose: bool = False, quick: bool = False):
        self.verbose = verbose
        self.quick = quick
        self.results: List[TestResult] = []
        self.python_path = ".venv/bin/python"
        self.main_script = "main.py"
        
    def log(self, message: str, force: bool = False):
        """로그 출력 (verbose 모드 또는 force=True일 때)"""
        if self.verbose or force:
            print(f"  💬 {message}")
    
    def run_server_command(
        self,
        args: List[str],
        stdin_data: Optional[str] = None,
        timeout: int = 10
    ) -> Tuple[str, str, int]:
        """
        서버 명령어를 실행하고 결과를 반환합니다.
        
        Args:
            args: 명령줄 인자 리스트
            stdin_data: 표준 입력으로 전달할 데이터
            timeout: 타임아웃 (초)
            
        Returns:
            (stdout, stderr, returncode) 튜플
        """
        cmd = [self.python_path, self.main_script] + args
        
        try:
            result = subprocess.run(
                cmd,
                input=stdin_data,
                capture_output=True,
                text=True,
                timeout=timeout
            )
            return result.stdout, result.stderr, result.returncode
        except subprocess.TimeoutExpired:
            return "", "Timeout expired", -1
        except Exception as e:
            return "", str(e), -1
    
    def send_mcp_request(
        self,
        method: str,
        params: Dict[str, Any],
        request_id: int = 1,
        boss_alertness: int = 50,
        boss_cooldown: int = 10
    ) -> Tuple[Optional[Dict[str, Any]], str]:
        """
        MCP 요청을 보내고 응답을 파싱합니다.
        
        Args:
            method: MCP 메서드 이름
            params: 파라미터 딕셔너리
            request_id: 요청 ID
            boss_alertness: 상사 경계도 확률
            boss_cooldown: 경계도 감소 주기
            
        Returns:
            (응답 딕셔너리, 에러 메시지) 튜플
        """
        # 초기화 및 알림 메시지
        init_request = {
            "jsonrpc": "2.0",
            "id": 0,
            "method": "initialize",
            "params": {
                "protocolVersion": "2024-11-05",
                "capabilities": {},
                "clientInfo": {"name": "validator", "version": "1.0"}
            }
        }
        
        init_notification = {
            "jsonrpc": "2.0",
            "method": "notifications/initialized",
            "params": {}
        }
        
        # 실제 요청
        request = {
            "jsonrpc": "2.0",
            "id": request_id,
            "method": method,
            "params": params
        }
        
        # stdin 데이터 준비
        stdin_data = (
            json.dumps(init_request) + "\n" +
            json.dumps(init_notification) + "\n" +
            json.dumps(request) + "\n"
        )
        
        # 서버 실행
        stdout, stderr, returncode = self.run_server_command(
            ["--boss_alertness", str(boss_alertness),
             "--boss_alertness_cooldown", str(boss_cooldown)],
            stdin_data=stdin_data,
            timeout=30
        )
        
        if returncode != 0 and returncode != -1:
            return None, f"Server exited with code {returncode}: {stderr}"
        
        # 응답 파싱 (마지막 줄에서 JSON 찾기)
        lines = stdout.strip().split("\n")
        for line in reversed(lines):
            if line.startswith("{"):
                try:
                    response = json.loads(line)
                    if response.get("id") == request_id:
                        return response, ""
                except json.JSONDecodeError:
                    continue
        
        return None, "No valid JSON response found"
    
    # ========================================================================
    # 필수 검증 항목
    # ========================================================================
    
    def test_cli_parameters(self) -> TestResult:
        """1. 커맨드라인 파라미터 지원 검증 (CRITICAL)"""
        start_time = time.time()
        
        self.log("Testing CLI parameter support...")
        
        # --boss_alertness 파라미터 테스트
        stdout, stderr, returncode = self.run_server_command(
            ["--boss_alertness", "75"],
            stdin_data='{"jsonrpc":"2.0","id":1,"method":"ping"}\n',
            timeout=3
        )
        
        if "--boss_alertness" in stderr and "unrecognized" in stderr.lower():
            return TestResult(
                name="CLI Parameters",
                status=TestStatus.CRITICAL_FAIL,
                message="--boss_alertness parameter not recognized",
                details=stderr,
                execution_time=time.time() - start_time
            )
        
        # --boss_alertness_cooldown 파라미터 테스트
        stdout, stderr, returncode = self.run_server_command(
            ["--boss_alertness_cooldown", "30"],
            stdin_data='{"jsonrpc":"2.0","id":1,"method":"ping"}\n',
            timeout=3
        )
        
        if "--boss_alertness_cooldown" in stderr and "unrecognized" in stderr.lower():
            return TestResult(
                name="CLI Parameters",
                status=TestStatus.CRITICAL_FAIL,
                message="--boss_alertness_cooldown parameter not recognized",
                details=stderr,
                execution_time=time.time() - start_time
            )
        
        # 두 파라미터 동시 테스트
        stdout, stderr, returncode = self.run_server_command(
            ["--boss_alertness", "100", "--boss_alertness_cooldown", "5"],
            stdin_data='{"jsonrpc":"2.0","id":1,"method":"ping"}\n',
            timeout=3
        )
        
        if "unrecognized" in stderr.lower():
            return TestResult(
                name="CLI Parameters",
                status=TestStatus.CRITICAL_FAIL,
                message="Parameters not working together",
                details=stderr,
                execution_time=time.time() - start_time
            )
        
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
        
        # tools/list 요청
        response, error = self.send_mcp_request(
            method="tools/list",
            params={}
        )
        
        if error or not response:
            return TestResult(
                name="MCP Server Basic",
                status=TestStatus.FAIL,
                message="Failed to get tools list",
                details=error,
                execution_time=time.time() - start_time
            )
        
        # 응답 구조 확인
        if "result" not in response:
            return TestResult(
                name="MCP Server Basic",
                status=TestStatus.FAIL,
                message="Invalid response structure: missing 'result'",
                details=json.dumps(response, indent=2),
                execution_time=time.time() - start_time
            )
        
        # 도구 목록 확인
        tools = response["result"].get("tools", [])
        required_tools = [
            "take_a_break",
            "watch_netflix",
            "show_meme",
            "bathroom_break",
            "coffee_mission",
            "urgent_call",
            "deep_thinking",
            "email_organizing"
        ]
        
        tool_names = [tool["name"] for tool in tools]
        missing_tools = [t for t in required_tools if t not in tool_names]
        
        if missing_tools:
            return TestResult(
                name="MCP Server Basic",
                status=TestStatus.FAIL,
                message=f"Missing required tools: {', '.join(missing_tools)}",
                details=f"Found tools: {', '.join(tool_names)}",
                execution_time=time.time() - start_time
            )
        
        return TestResult(
            name="MCP Server Basic",
            status=TestStatus.PASS,
            message=f"All 8 required tools registered: {', '.join(tool_names)}",
            execution_time=time.time() - start_time
        )
    
    def test_tool_execution(self) -> TestResult:
        """3. 도구 실행 검증"""
        start_time = time.time()
        
        self.log("Testing tool execution...")
        
        # take_a_break 도구 호출
        response, error = self.send_mcp_request(
            method="tools/call",
            params={"name": "take_a_break", "arguments": {}},
            boss_alertness=0  # 경계도 증가 방지
        )
        
        if error or not response:
            return TestResult(
                name="Tool Execution",
                status=TestStatus.FAIL,
                message="Failed to execute take_a_break tool",
                details=error,
                execution_time=time.time() - start_time
            )
        
        # 에러 응답 확인
        if "error" in response:
            return TestResult(
                name="Tool Execution",
                status=TestStatus.FAIL,
                message="Tool returned error",
                details=json.dumps(response["error"], indent=2),
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
        
        # 도구 호출
        response, error = self.send_mcp_request(
            method="tools/call",
            params={"name": "take_a_break", "arguments": {}},
            boss_alertness=0
        )
        
        if error or not response or "error" in response:
            return TestResult(
                name="Response Format",
                status=TestStatus.FAIL,
                message="Could not get valid response",
                details=error,
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
                details=json.dumps(response, indent=2),
                execution_time=time.time() - start_time
            )
        
        # 필수 필드 확인
        required_fields = [
            r"Break Summary:\s*(.+)",
            r"Stress Level:\s*(\d{1,3})",
            r"Boss Alert Level:\s*([0-5])"
        ]
        
        missing_fields = []
        parsed_values = {}
        
        for pattern in required_fields:
            match = re.search(pattern, content)
            field_name = pattern.split(":")[0].replace(r"\s*", " ")
            
            if not match:
                missing_fields.append(field_name)
            else:
                parsed_values[field_name] = match.group(1)
        
        if missing_fields:
            return TestResult(
                name="Response Format",
                status=TestStatus.FAIL,
                message=f"Missing required fields: {', '.join(missing_fields)}",
                details=f"Response content:\n{content}",
                execution_time=time.time() - start_time
            )
        
        return TestResult(
            name="Response Format",
            status=TestStatus.PASS,
            message=f"All required fields present and parseable",
            details=f"Parsed values: {parsed_values}",
            execution_time=time.time() - start_time
        )
    
    # ========================================================================
    # 테스트 시나리오
    # ========================================================================
    
    def test_continuous_breaks(self) -> TestResult:
        """시나리오 1: 연속 휴식 테스트"""
        start_time = time.time()
        
        if self.quick:
            return TestResult(
                name="Continuous Breaks",
                status=TestStatus.SKIP,
                message="Skipped in quick mode",
                execution_time=0
            )
        
        self.log("Testing continuous breaks...")
        
        # boss_alertness=100으로 설정하여 항상 경계도 증가
        boss_alerts = []
        
        for i in range(3):
            response, error = self.send_mcp_request(
                method="tools/call",
                params={"name": "take_a_break", "arguments": {}},
                request_id=i + 10,
                boss_alertness=100,  # 항상 증가
                boss_cooldown=999999  # 감소 방지
            )
            
            if error or not response or "error" in response:
                continue
            
            try:
                content = response["result"]["content"][0]["text"]
                match = re.search(r"Boss Alert Level:\s*([0-5])", content)
                if match:
                    boss_alerts.append(int(match.group(1)))
            except:
                continue
        
        if len(boss_alerts) < 2:
            return TestResult(
                name="Continuous Breaks",
                status=TestStatus.FAIL,
                message="Could not track Boss Alert Level changes",
                execution_time=time.time() - start_time
            )
        
        # 증가 확인
        increased = any(boss_alerts[i] < boss_alerts[i+1] for i in range(len(boss_alerts)-1))
        
        if not increased:
            return TestResult(
                name="Continuous Breaks",
                status=TestStatus.FAIL,
                message="Boss Alert Level did not increase with boss_alertness=100",
                details=f"Observed levels: {boss_alerts}",
                execution_time=time.time() - start_time
            )
        
        return TestResult(
            name="Continuous Breaks",
            status=TestStatus.PASS,
            message=f"Boss Alert Level increased as expected: {boss_alerts}",
            execution_time=time.time() - start_time
        )
    
    def test_delay_at_max_alert(self) -> TestResult:
        """시나리오 2: Boss Alert Level 5일 때 20초 지연"""
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
        
        # Boss Alert Level을 5로 만들기 (5번 연속 호출)
        for i in range(5):
            self.send_mcp_request(
                method="tools/call",
                params={"name": "show_meme", "arguments": {}},
                request_id=20 + i,
                boss_alertness=100,
                boss_cooldown=999999
            )
            time.sleep(0.5)
        
        # Level 5 상태에서 도구 호출 (20초 딜레이 예상)
        call_start = time.time()
        response, error = self.send_mcp_request(
            method="tools/call",
            params={"name": "take_a_break", "arguments": {}},
            request_id=30,
            boss_alertness=100,
            boss_cooldown=999999
        )
        call_duration = time.time() - call_start
        
        if error or not response:
            return TestResult(
                name="Delay at Max Alert",
                status=TestStatus.FAIL,
                message="Failed to execute tool at max alert level",
                details=error,
                execution_time=time.time() - start_time
            )
        
        # 20초 딜레이 확인 (18-22초 범위 허용)
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
        """시나리오 3: Cooldown 메커니즘 테스트"""
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
        
        # Boss Alert Level을 2로 만들기
        for i in range(2):
            self.send_mcp_request(
                method="tools/call",
                params={"name": "show_meme", "arguments": {}},
                request_id=40 + i,
                boss_alertness=100,
                boss_cooldown=5  # 5초마다 감소
            )
            time.sleep(0.5)
        
        # 현재 레벨 확인
        response1, _ = self.send_mcp_request(
            method="tools/call",
            params={"name": "take_a_break", "arguments": {}},
            request_id=50,
            boss_alertness=0,  # 증가 방지
            boss_cooldown=5
        )
        
        if not response1 or "error" in response1:
            return TestResult(
                name="Cooldown Mechanism",
                status=TestStatus.FAIL,
                message="Could not get initial Boss Alert Level",
                execution_time=time.time() - start_time
            )
        
        try:
            content1 = response1["result"]["content"][0]["text"]
            match1 = re.search(r"Boss Alert Level:\s*([0-5])", content1)
            level1 = int(match1.group(1)) if match1 else -1
        except:
            level1 = -1
        
        if level1 < 1:
            return TestResult(
                name="Cooldown Mechanism",
                status=TestStatus.FAIL,
                message="Boss Alert Level not elevated enough for cooldown test",
                execution_time=time.time() - start_time
            )
        
        # 10초 대기 (5초 cooldown × 2 = 2레벨 감소 예상)
        self.log(f"Initial level: {level1}, waiting 10 seconds for cooldown...")
        time.sleep(10)
        
        # 다시 레벨 확인
        response2, _ = self.send_mcp_request(
            method="tools/call",
            params={"name": "take_a_break", "arguments": {}},
            request_id=51,
            boss_alertness=0,
            boss_cooldown=5
        )
        
        if not response2 or "error" in response2:
            return TestResult(
                name="Cooldown Mechanism",
                status=TestStatus.FAIL,
                message="Could not get Boss Alert Level after cooldown",
                execution_time=time.time() - start_time
            )
        
        try:
            content2 = response2["result"]["content"][0]["text"]
            match2 = re.search(r"Boss Alert Level:\s*([0-5])", content2)
            level2 = int(match2.group(1)) if match2 else -1
        except:
            level2 = -1
        
        # 감소 확인
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
    
    # ========================================================================
    # 검증 실행
    # ========================================================================
    
    def run_all_tests(self) -> bool:
        """모든 테스트 실행"""
        print("\n" + "="*70)
        print("🚀 ChillMCP Hackathon Validation")
        print("="*70)
        print()
        
        # 필수 검증 항목
        print("📋 필수 검증 항목 (Required Validations)")
        print("-" * 70)
        
        # 1. CLI 파라미터 (CRITICAL)
        result = self.test_cli_parameters()
        self.results.append(result)
        self._print_result(result)
        
        if result.status == TestStatus.CRITICAL_FAIL:
            print()
            print("🚫 CRITICAL FAILURE: CLI 파라미터 미지원")
            print("   이후 검증을 진행할 수 없습니다.")
            print("   --boss_alertness 및 --boss_alertness_cooldown 파라미터를 구현하세요.")
            return False
        
        # 2. MCP 서버 기본 동작
        result = self.test_mcp_server_basic()
        self.results.append(result)
        self._print_result(result)
        
        # 3. 도구 실행
        result = self.test_tool_execution()
        self.results.append(result)
        self._print_result(result)
        
        # 4. 응답 형식
        result = self.test_response_format()
        self.results.append(result)
        self._print_result(result)
        
        print()
        print("🧪 테스트 시나리오 (Test Scenarios)")
        print("-" * 70)
        
        # 5. 연속 휴식
        result = self.test_continuous_breaks()
        self.results.append(result)
        self._print_result(result)
        
        # 6. 20초 지연
        result = self.test_delay_at_max_alert()
        self.results.append(result)
        self._print_result(result)
        
        # 7. Cooldown 메커니즘
        result = self.test_cooldown_mechanism()
        self.results.append(result)
        self._print_result(result)
        
        return True
    
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
            print("   해커톤 제출 불가능합니다.")
            return False
        elif failed > 0:
            print("⚠️  일부 테스트가 실패했습니다.")
            print("   실패한 항목을 수정 후 다시 검증하세요.")
            return False
        else:
            print("🎉 모든 검증 통과!")
            print("   해커톤 제출 준비가 완료되었습니다!")
            return True


def main():
    parser = argparse.ArgumentParser(
        description="ChillMCP Hackathon Validation Script"
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Verbose output with detailed information"
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
        sys.exit(2)
    except Exception as e:
        print(f"\n\n❌ 예상치 못한 오류 발생: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(3)


if __name__ == "__main__":
    main()
