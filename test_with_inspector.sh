#!/bin/bash

###############################################################################
# MCP Inspector 테스트 스크립트
# 
# 이 스크립트는 ChillMCP 서버를 MCP Inspector로 테스트합니다.
# MCP Inspector는 MCP 서버의 기능을 브라우저에서 대화형으로 테스트할 수 있는 도구입니다.
#
# 사용법:
#   ./test_with_inspector.sh
#
# 필요 조건:
#   - Node.js (npx 명령어 사용)
#   - Python 가상 환경 활성화 (.venv)
###############################################################################

# 색상 정의 (터미널 출력용)
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}  ChillMCP Server - MCP Inspector 테스트${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

# 스크립트가 실행되는 디렉토리로 이동
cd "$(dirname "$0")"

# Python 가상 환경 확인
if [ ! -d ".venv" ]; then
    echo -e "${RED}❌ Error: Python 가상 환경(.venv)을 찾을 수 없습니다.${NC}"
    echo -e "${YELLOW}다음 명령어로 가상 환경을 생성하세요:${NC}"
    echo "  python3 -m venv .venv"
    echo "  source .venv/bin/activate"
    echo "  pip install -r requirements.txt"
    exit 1
fi

# Python 실행 파일 경로
PYTHON_PATH="$(pwd)/.venv/bin/python"
MAIN_PY="$(pwd)/main.py"

# 파일 존재 확인
if [ ! -f "$MAIN_PY" ]; then
    echo -e "${RED}❌ Error: main.py 파일을 찾을 수 없습니다.${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Python 환경 확인 완료${NC}"
echo -e "   Python: ${PYTHON_PATH}"
echo -e "   Script: ${MAIN_PY}"
echo ""

# 기본 설정값
BOSS_ALERTNESS=${BOSS_ALERTNESS:-50}
BOSS_COOLDOWN=${BOSS_COOLDOWN:-300}

echo -e "${BLUE}📋 서버 설정:${NC}"
echo -e "   Boss Alertness: ${BOSS_ALERTNESS} (0-100, 높을수록 상사가 잘 눈치챔)"
echo -e "   Boss Cooldown: ${BOSS_COOLDOWN}초 (상사 경계도가 1씩 감소하는 주기)"
echo ""

echo -e "${YELLOW}💡 설정 변경 방법:${NC}"
echo -e "   BOSS_ALERTNESS=100 BOSS_COOLDOWN=10 ./test_with_inspector.sh"
echo ""

# npx 명령어 확인
if ! command -v npx &> /dev/null; then
    echo -e "${RED}❌ Error: npx 명령어를 찾을 수 없습니다.${NC}"
    echo -e "${YELLOW}Node.js를 설치해주세요:${NC}"
    echo "  Ubuntu/Debian: sudo apt install nodejs npm"
    echo "  macOS: brew install node"
    exit 1
fi

echo -e "${GREEN}✅ Node.js 환경 확인 완료${NC}"
echo ""

# MCP Inspector 실행
echo -e "${BLUE}🚀 MCP Inspector 시작 중...${NC}"
echo ""
echo -e "${GREEN}브라우저가 자동으로 열립니다.${NC}"
echo -e "${YELLOW}다음 기능들을 테스트해보세요:${NC}"
echo ""
echo -e "  📌 도구 목록 (Tools):"
echo -e "     - take_a_break      : 기본 휴식 (스트레스 -10)"
echo -e "     - watch_netflix     : 넷플릭스 시청 (스트레스 -15)"
echo -e "     - show_meme         : 밈 보기 (스트레스 -5)"
echo -e "     - bathroom_break    : 화장실 휴식 (스트레스 -8)"
echo -e "     - coffee_mission    : 커피 미션 (스트레스 -12)"
echo -e "     - urgent_call       : 긴급 전화 (스트레스 -20)"
echo -e "     - deep_thinking     : 깊은 사색 (스트레스 -7)"
echo -e "     - email_organizing  : 이메일 정리 (스트레스 -3)"
echo ""
echo -e "  📊 테스트 시나리오:"
echo -e "     1. 여러 도구를 연속으로 호출해서 스트레스 감소 확인"
echo -e "     2. Boss Alert Level이 5가 되면 20초 딜레이 발생 확인"
echo -e "     3. 시간이 지나면 스트레스가 1pt/분씩 자동 증가하는지 확인"
echo ""
echo -e "${RED}종료하려면 Ctrl+C를 누르세요.${NC}"
echo ""

# MCP Inspector 실행
# --boss_alertness와 --boss_alertness_cooldown 파라미터를 서버에 전달
npx @modelcontextprotocol/inspector \
    "$PYTHON_PATH" \
    "$MAIN_PY" \
    --boss_alertness "$BOSS_ALERTNESS" \
    --boss_alertness_cooldown "$BOSS_COOLDOWN"
