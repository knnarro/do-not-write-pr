import os
import json
import re
import sys
from openai import OpenAI


def generate_pr_description(diff, api_key):
    # 테스트 모드 확인 (API 키가 'test_'로 시작하는 경우)
    if api_key.startswith("test_"):
        return {
            "title": "[TEST] 테스트 PR 생성",
            "body": "### ✅ 테스트\n- 이것은 테스트 PR 설명입니다.\n- 실제 API 호출 없이 생성되었습니다."
        }
    
    client = OpenAI(api_key=api_key)
    
    system_prompt = """
    너는 코드 변경사항을 분석해서 명확하고 구조화된 PR(Pull Request) 제목과 본문을 만드는 전문가야.
    다음 규칙을 엄격하게 따라야 해:
    1. 모든 응답은 반드시 한국어로 작성할 것
    2. 반드시 '[TYPE] 설명' 형식의 제목 사용할 것 (TYPE은 FEAT, FIX, DOCS, STYLE, REFACTOR, TEST, BUILD, CI, CHORE, REVERT 중 하나)
    3. 반드시 완벽한 JSON 형식으로 응답할 것 (title과 body만 포함하는 단순 구조)
    4. 본문은 반드시 '### 이모티콘 소제목' 형식으로 시작하는 섹션들로 구성할 것
    
    이 규칙들을 어기는 경우 너의 응답은 완전히 쓸모없게 되니까 절대 어기지 말아야 해.
    """
    
    prompt = f"""
    {diff}
    위는 코드의 변경 사항에 대한 Git diff야. diff를 보고 적절한 PR 제목과 본문을 만들어줘.

    ⚠️ 중요한 요구사항 ⚠️
    1. 응답은 반드시 한국어로 작성해야 함
    2. 제목은 반드시 '[TYPE] 변경 사항 요약' 형식이어야 함
    3. 반드시 완벽한 JSON 형식으로 응답해야 함

    제목 형식: '[TYPE] 변경 사항 요약'
    여기서 TYPE은 FEAT, FIX, DOCS, STYLE, REFACTOR, TEST, BUILD, CI, CHORE, REVERT 중 하나여야 해.
    예를 들어,
    [FEAT] 기능 추가
    [FIX] 버그 수정
    [DOCS] 문서 수정
    [STYLE] 코드 스타일 수정
    [REFACTOR] 코드 리팩토링
    [TEST] 테스트 코드 추가
    [BUILD] 빌드 시스템 변경
    [CI] CI 변경
    [CHORE] 기타 사항 변경
    [REVERT] 되돌리기
    너가 diff를 보고 적절한 TYPE을 선택하면 된단다.

    본문은 큰 변경 사항과 그에 대한 설명을 간단하게 적어줘.
    변경 사항은 h3 소제목으로 적어주고 소제목 앞에 적절한 이모티콘을 설정해주면 좋을 것 같아.
    예를 들어,
    ### ✨ 새로운 기능 추가
    - 새로운 기능에 대한 설명 1
    - 새로운 기능에 대한 설명 2

    ### 🐛 버그 수정
    - 버그 수정에 대한 설명 1
    - 버그 수정에 대한 설명 2
    이렇게 적어줘.
    본문은 깔끔하게 소제목과 소제목에 대한 설명만 있으면 돼. 다른 텍스트는 필요 없어.
    그리고 시작할 때 'PR 본문:'이라는 텍스트도 필요 없어. 바로 소제목으로 시작하자.

    ⚠️ 다시 한번 강조하자면 ⚠️
    나는 너의 답변을 json으로 파싱해서 제목과 본문을 추출할거야. 
    그니까 꼭 아래와 같은 완벽한 json 형식으로 답변해줘.
    {{
        "title": "[FEAT] 새로운 기능 추가",
        "body": "### ✨ 새로운 기능 추가\\n- 새로운 기능에 대한 설명 1\\n- 새로운 기능에 대한 설명 2"
    }}

    마지막으로, 다음 세 가지는 절대 어기지 말아야 할 규칙이야:
    1. 제목의 형식은 '[TYPE] 변경 사항 요약'이어야 함
    2. 제목과 본문은 반드시 한국어로 작성해야 함
    3. 응답 형식은 반드시 유효한 JSON이어야 함 (추가 문구 없이)
    """
    
    response = client.chat.completions.create(
        model="gpt-4-turbo",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": prompt}
        ],
        temperature=0.6,
        max_tokens=500,
        response_format={"type": "json_object"}
    )
    content = response.choices[0].message.content
    
    try:
        result = json.loads(content)
        return result
    except json.JSONDecodeError:
        return {"title": "PR", "body": content}

if len(sys.argv) < 2:
    print(json.dumps({
        "title": "Error",
        "body": "OpenAI API key is required as a command line argument"
    }))
    sys.exit(1)

api_key = sys.argv[1]

try:
    # 파일에서 diff 읽기
    with open("code.diff", "r") as f:
        diff = f.read()
        
    # diff가 비어있는 경우 테스트 데이터 사용
    if not diff.strip():
        diff = "diff --git a/test.txt b/test.txt\nindex 1234567..abcdefg 100644\n--- a/test.txt\n+++ b/test.txt\n@@ -1,3 +1,4 @@\n Line 1\n Line 2\n+This is a new line\n Line 3"
    
    # PR 설명 생성
    result = generate_pr_description(diff, api_key)
    
    # 결과 출력
    print(json.dumps(result, ensure_ascii=False))
except Exception as e:
    print(json.dumps({
        "title": "Error generating PR description",
        "body": f"An error occurred: {str(e)}."
    })) 