#!/bin/bash

###############################################################################
# Boss Alert Level 5 딜레이 테스트 스크립트
#
# Boss Alert Level을 5까지 올린 후 20초 딜레이가 발생하는지 테스트합니다.
###############################################################################

echo "🧪 Boss Alert Level 5 딜레이 테스트"
echo "===================================="
echo ""
echo "서버 시작 중... (boss_alertness=100으로 설정)"
echo ""

# 서버 실행 (boss_alertness=100이면 항상 경계도 증가)
(.venv/bin/python main.py --boss_alertness 100 --boss_alertness_cooldown 300 << 'EOF'
{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2024-11-05","capabilities":{},"clientInfo":{"name":"test","version":"1.0"}}}
{"jsonrpc":"2.0","method":"notifications/initialized"}
{"jsonrpc":"2.0","id":2,"method":"tools/call","params":{"name":"take_a_break","arguments":{}}}
{"jsonrpc":"2.0","id":3,"method":"tools/call","params":{"name":"take_a_break","arguments":{}}}
{"jsonrpc":"2.0","id":4,"method":"tools/call","params":{"name":"take_a_break","arguments":{}}}
{"jsonrpc":"2.0","id":5,"method":"tools/call","params":{"name":"take_a_break","arguments":{}}}
{"jsonrpc":"2.0","id":6,"method":"tools/call","params":{"name":"take_a_break","arguments":{}}}
{"jsonrpc":"2.0","id":7,"method":"tools/call","params":{"name":"take_a_break","arguments":{}}}
EOF
) 2>&1 | grep -E "(WARNING|Boss Alert|Wait|⏰|대기)" | head -20

echo ""
echo "✅ 테스트 완료!"
echo ""
echo "예상 결과:"
echo "  1-5번 휴식: Boss Alert Level 0→1→2→3→4→5 증가"
echo "  6번 휴식: ⚠️ WARNING 로그 + 20초 대기 + ⏰ 응답 메시지"
