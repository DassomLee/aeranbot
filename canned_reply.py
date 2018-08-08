import random # random이라는 모듈을 불러옴
import re #정규표현식을 활용할 것이므로 불러옴
from urllib.parse import quote

import requests

import secret # secret은 토큰같은 것. 숨겨둔 머시기

generals = {  # 'generals'라는 dictionary를 생성함
    r'.*\b주사위.*': [ # '이주사위'라는 단어는 포함되지 않도록, 어절로 띄어쓸 때를 위해서 '\b주사위'로 표현함
        lambda g: '주사위를 던졌습니다 => ' + str(random.randint(1, 6)),  # lambda를 사용하는데, str으로 1-6 중 하나를 고름
    ],
    r'.*\b동전.*': [
        lambda g: '동전을 던졌습니다 => ' + random.choice(  # choice는 가중치를 줄 수 없음. 다섯 번 곱해줘서 리스트 안에서 확률을 높여줌
            ['앞면', '뒷면'] * 5 + ['옆면!?', '사라졌다!']
        ),
    ],
    r'(.+?)(이?랑|하고|와|과|,)\s+(.+?)((가|이|이?랑|하고| 중).+)?\?$': [  #
        lambda g: random.choice([
            g[0],
            g[2],
            '글쎄?',
            '모두 쬲!',
            '다 별로...',
            '정말 이 중에서 골라야 하나요?',
        ])
    ],
    r'.*\b(무엇인|무엇일|무얼|뭐가|모가|살|할|뭐|모|뭔|뭘)\s*(가요?|까요?|지요?|죠|[었였있]지요|[었였있]죠)\?$': [
        '글쎄...',
        '좀 더 고민해봐.',
        '다른 분들은 어떻게 생각하세요?',
        '난 모르겠어.',
    ],
    r'(.+?)\s+(vs|VS|Vs)\.?\s*(.+?)$': [ # versus 다음에 dot이 올 수 있을 수도 있고 없을 수도 있음 --> 꼼꼼왕!!
        lambda g: random.choice([
            g[0],
            g[2],
            '글쎄?',
            '모두 쬲!',
            '다 별로...',
            '정말 이 중에서 골라야 하나요?',
        ])
    ],
    r'(파이[썬선손쏜]|[Pp]ython)': [
        '파이썬요? 사랑입니다.',
    ],
}


mentions = {
    r'.*주소검색\s?\:(.+)$': [
        lambda g: search_naver(g[0].strip())  # strip은 양쪽 공백을 없애주는 것. r strip: 오른쪽 공백, l strip: 왼쪽 공백. enter와 띄어쓰기를 없애줌
    ],
    r'.*이름이\s+(뭐|모|뭔)(야|니|냐|에요|예요|가|가요)?\?$': [
        '내 이름은 애란봇이야. 사실은 시리보다 똑똑하지.',
        '애란봇입니다 :)',
    ],
    r'.*?(\S+[겠랬렸샀았었웠있했켰])(다|여요?|어요?)[!\.]*?$': [  # !는 다른 기능이 없음. \로 문자임을 표시해주지 않아도 됨. escape 안해도 되는 것
        '정말?',
        '그랬구나.',
        'ㅇㅇ',
        lambda g: g[0] + '어요?',
        lambda g: '왜 ' + g[0] + '어요?',
        lambda g: '어떻게 ' + g[0] + '어요?',
    ],
    r'.*': [
        '과제하기 좋은 날씨입니다.',
        '수업 피드백을 꼭 남겨주세요.',
        '맥주는 몽크 IPA',
        '웅앵웅 쵸키포키',
        '지속가능하게 갈아넣으세요.',
        '질문을 많이 해주세요. 조금이라도 궁금하면 그냥 넘어가지 마세요.',
        '컴퓨터는 맥, 휴대폰은 아이폰, 시계는 애플와치입니다. 물론 에어팟도 사야해요.',
        '파이썬은 *사랑*입니다.',
        '한번에 하기 어려우면 더 작은 조각으로 나눠서 해보세요. 중간중간 더 자주 확인하며 진행하세요.',
        '회고는 하셨나요?',
        '훌륭해요 :)',
        '코딩 속도가 너무 빠르면 얘기해주세요.',
        '통계는 중요합니다.',
        '점심 논의를 겸한 휴식시간을 15분간 가질게요.',
        '여러분, 수고하셨습니다.'
    ]
}


def reply_to_pattern(text, pattern_map):  # 함수의 매개변수가 text, pattern_map
    for pattern, replies in pattern_map.items():
        m = re.match(pattern, text)  # pattern과 text가 match되면 뽑아서 m에 넣음
        if m:  # m:은 true이면~
            reply = random.choice(replies)
            if type(reply) == str:  # 아니면~. reply의 type이 str이면
                return reply
            else:
                return reply(m.groups())
    return None
# match, search, find 세가지 종류가 있음. 각 차이점은?

def search_naver(keyword):
    encoded_keyword = quote(keyword.encode('utf-8'))
    url = "https://openapi.naver.com/v1/search/local?query=%s" % encoded_keyword
    headers = {
        "X-Naver-Client-Id": secret.NAVER_API_ID,
        "X-Naver-Client-Secret": secret.NAVER_API_SECRET,
    }
    res = requests.request("GET", url, headers=headers).json()['items']
    if len(res) == 0:
        return '"%s" 키워드로 검색한 결과가 없습니다.' % keyword
    else:
        return '\n'.join(
            "- %s: %s" % (re.sub(r'<.+?>', '', r['title']), r['roadAddress'])
            for r in res
        )
