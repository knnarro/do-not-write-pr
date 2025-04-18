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
    
    prompt = f"""
    {diff}
    위는 코드의 변경 사항에 대한 Git diff야. diff를 보고 적절한 PR 제목과 본문을 만들어줘.

    제목은 '[TYPE] 변경 사항 요약'이라는 형식이어야 해,
    TYPE은 FEAT, FIX, DOCS, STYLE, REFACTOR, TEST, BUILD, CI, CHORE, REVERT 중 하나여야 해.
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

    너는 반드시 아래와 같은 json 형식으로 답변해야 해.
    {{
        "title": "[FEAT] 새로운 기능 추가",
        "body": "### ✨ 새로운 기능 추가\n- 새로운 기능에 대한 설명 1\n- 새로운 기능에 대한 설명 2"
    }}
    나는 너의 답변을 json으로 파싱해서 제목과 본문을 추출할거야. 그니까 꼭 완벽한 json 형식으로 답변해줘.

    마지막으로 한 번 더 강조할게. 이건 꼭 지켜줬으면 해.
    1. 제목의 형식을 반드시 지켜줘. '[TYPE] 변경 사항 요약' 기억하지?
    2. 제목과 본문의 언어는 '한국어'로 작성해줘.
    3. 답변의 형식은 json.loads() 함수로 파싱할 수 있어야 해.
    """
    
    response = client.chat.completions.create(
        model="gpt-4-turbo",
        messages=[
            {"role": "system", "content": "너는 리뷰어가 이해하기 쉬운 PR의 제목과 본문을 만들어주는 헬퍼야."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.5,
        max_tokens=500
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