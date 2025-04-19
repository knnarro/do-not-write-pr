import os
import json
import re
import sys
from openai import OpenAI


def generate_pr_description(diff, api_key, language):
    client = OpenAI(api_key=api_key)
    
    system_prompt = f"""
    너는 코드 변경사항을 분석해서 명확하고 구조화된 PR(Pull Request) 제목과 본문을 만드는 전문가야.
    다음 규칙을 엄격하게 따라야 해:
    1. 모든 응답의 언어는 반드시 "{language}"로 작성할 것
    2. 반드시 '[TYPE] 설명' 형식의 제목 사용할 것 (TYPE은 FEAT, FIX, DOCS, STYLE, REFACTOR, TEST, BUILD, CI, CHORE, REVERT 중 하나)
    3. 반드시 완벽한 JSON 형식으로 응답할 것 (title과 body만 포함하는 단순 구조)
    
    이 규칙들을 어기는 경우 너의 응답은 완전히 쓸모없게 되니까 절대 어기지 말아야 해.
    """
    
    prompt = f"""
    {diff}
    위는 코드의 변경 사항에 대한 Git diff야. diff를 보고 적절한 PR 제목과 본문을 만들어줘.

    ⚠️ 중요한 요구사항 ⚠️
    1. 응답은 반드시 {language} 언어로 작성해야 함
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

    본문은 '이 PR은 아래의 변경 사항을 포함하고 있습니다.'라는 의미의 시작 문구로 시작해.
    그 다음 큰 변경 사항과 그에 대한 설명을 간단하게 적어줘.
    변경 사항은 h3 소제목으로 적어주고 소제목 앞에 적절한 이모티콘을 설정해주면 좋을 것 같아.
    예를 들어,
    ### ✨ 새로운 기능 추가
    - 새로운 기능에 대한 설명 1
    - 새로운 기능에 대한 설명 2

    ### 🐛 버그 수정
    - 버그 수정에 대한 설명 1
    - 버그 수정에 대한 설명 2
    이렇게 적어줘.

    변경 사항을 다 썼다면 PR을 마무리하는 내용을 줄글로 적어줘.
    마무리 내용은 이 PR의 의의, 영향, 주의 깊게 검토하면 좋은 부분들을 적어주면 좋을 것 같아.

    ⚠️ 다시 한번 강조하자면 ⚠️
    나는 너의 답변을 json으로 파싱해서 제목과 본문을 추출할거야. 
    그니까 꼭 아래와 같은 완벽한 json 형식으로 답변해줘.
    {{
        "title": "[FEAT] 새로운 기능 추가",
        "body": "이 PR은 아래의 변경 사항을 포함하고 있습니다.\\n### ✨ 새로운 기능 추가\\n- 새로운 기능에 대한 설명 1"
    }}

    마지막으로, 다음 세 가지는 절대 어기지 말아야 할 규칙이야:
    1. 제목과 본문은 반드시 {language} 언어로 작성해야 함
    2. 제목의 형식은 '[TYPE] 변경 사항 요약'이어야 함
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
        response_format={"type":"json_object"}
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
language = sys.argv[2]

try:
    with open("code.diff", "r") as f:
        diff = f.read()
    
    result = generate_pr_description(diff, api_key, language)
    print(json.dumps(result, ensure_ascii=False))
except Exception as e:
    print(json.dumps({
        "title": "Error generating PR description",
        "body": f"An error occurred: {str(e)}."
    })) 