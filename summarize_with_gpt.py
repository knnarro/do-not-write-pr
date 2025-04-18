import os
import json
import re
import sys
from openai import OpenAI


def generate_pr_description(diff, api_key):
    
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

    참고로 제목과 본문의 내용의 언어는 한국어야.

    마지막으로 너는 반드시 아래와 같은 json 형식으로 답변해줘.
    {{
        "title": "[FEAT] 새로운 기능 추가",
        "body": "### ✨ 새로운 기능 추가\n- 새로운 기능에 대한 설명 1\n- 새로운 기능에 대한 설명 2"
    }}
    """
    
    
    response = client.chat.completions.create(
        model="gpt-4-turbo",
        messages=[
            {"role": "system", "content": "너는 리뷰어가 이해하기 쉬운 PR의 제목과 본문을 만들어주는 헬퍼야."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.8,
        max_tokens=500
    )
    content = response.choices[0].message.content
    result = json.loads(content)
    return result

if len(sys.argv) < 2:
    print(json.dumps({
        "title": "Error",
        "body": "OpenAI API key is required as a command line argument"
    }))
    sys.exit(1)

api_key = sys.argv[1]

with open("code.diff", "r") as f:
    diff = f.read()

try:
    result = generate_pr_description(diff, api_key)
    title_split = result["title"].split(":", 1)[1].strip()
    body_split = result["body"].split(":", 1)[1].strip()
    result["title"] = title_split if len(title_split) > 0 else result["title"]
    result["body"] = body_split if len(body_split) > 0 else result["body"]
    print(json.dumps(result))
except Exception as e:
    print(json.dumps({
        "title": "Error generating PR description",
        "body": f"An error occurred: {str(e)}.\nResult: {result}"
    })) 