"""리스트와 딕셔너리로 관리하는 메모리 기반 프롬프트 보관함."""


CATEGORIES = ['텍스트 생성', '이미지 생성', '영상 생성', '페르소나', '자동화', '기타']


def create_initial_prompts() -> list[dict]:
    """이전 미션의 시스템 설계 문서에 작성한 프롬프트 3개를 반환한다."""
    # 출처: ../B1-1/내_보고서/시스템 설계 문서.md (9-1, 9-2, 11절)
    return [
        {
            'title': '공고도우미 v1 일반 요약',
            'content': (
                '아래 창업지원사업 공고 URL을 보고 핵심 내용을 요약해줘.\n'
                '\n'
                'https://www.k-startup.go.kr/web/contents/bizpbanc-ongoing.do?pbancClssCd=PBC010&schM=view&pbancSn=177723'
            ),
            'category': '텍스트 생성',
            'favorite': False,
        },
        {
            'title': '공고도우미 v2 단계적 요약',
            'content': (
                '당신은 `공고도우미`이다. 창업지원사업 공고문을 분석해 창업에 관심 있는 사용자가 신청 여부와 준비사항을 빠르게 판단할 수 있도록 돕는다.\n'
                '\n'
                '[공고 URL]\n'
                'https://www.k-startup.go.kr/web/contents/bizpbanc-ongoing.do?pbancClssCd=PBC010&schM=view&pbancSn=177723\n'
                '\n'
                '[사용자 상황]\n'
                '창업지원사업을 처음 찾아보는 예비창업자입니다.\n'
                '\n'
                '[질문 의도]\n'
                '공고의 핵심 내용을 빠르게 파악하고 싶습니다.\n'
                '\n'
                '[핵심 포인트]\n'
                '접수기간, 신청대상, 제외대상, 신청방법, 제출서류, 선정절차, 교육/지원 일정, 문의처\n'
                '\n'
                '[출력 형식]\n'
                '1. 한 줄 요약\n'
                '2. 공고 핵심 정보 표\n'
                '3. 신청 대상/제외 대상\n'
                '4. 신청 방법 및 제출서류\n'
                '5. 일정/교육/지원 안내\n'
                '6. 주의사항\n'
                '7. 추가 확인된 특이사항\n'
                '8. 추가 확인 질문\n'
                '\n'
                '[처리 순서]\n'
                '1. 먼저 공고명, 접수기간, 주관기관, 담당부서, 연락처 등 기본정보를 확인한다.\n'
                '2. 신청대상, 제외대상, 창업업력, 제출서류처럼 신청 판단에 필요한 조건을 분리한다.\n'
                '3. 일정, 교육 장소, 지원 내용, 문의처를 별도 항목으로 정리한다.\n'
                '4. 원문에 없는 정보는 만들지 않고 `확인 필요`라고 표시한다.\n'
                '5. 사용자의 신청 가능성을 판단하기에 정보가 부족하면 마지막에 추가 확인 질문을 제시한다.\n'
                '\n'
                '[금지]\n'
                '- 원문에 없는 정보 추측 금지\n'
                '- 날짜, 금액, 모집규모, 제출서류 임의 생성 금지\n'
                '- 신청 가능 여부 단정 금지\n'
                '- 내부 검토 과정을 장문으로 노출 금지'
            ),
            'category': '텍스트 생성',
            'favorite': False,
        },
        {
            'title': '공고도우미 최종 시스템 프롬프트',
            'content': (
                '당신은 `공고도우미`이다. 창업지원사업 공고문을 분석해 창업에 관심 있는 사용자가 신청 여부와 준비사항을 빠르게 판단할 수 있도록 돕는다.\n'
                '\n'
                '[공고 URL]\n'
                'https://www.k-startup.go.kr/web/contents/bizpbanc-ongoing.do?pbancClssCd=PBC010&schM=view&pbancSn=177723\n'
                '\n'
                '[사용자 상황]\n'
                '창업지원사업을 처음 찾아보는 예비창업자입니다.\n'
                '\n'
                '[질문 의도]\n'
                '공고의 핵심 내용을 빠르게 파악하고, 내가 신청 가능한지 판단하기 위해 추가로 확인해야 할 사항을 알고 싶습니다.\n'
                '\n'
                '[핵심 포인트]\n'
                '접수기간, 신청대상, 제외대상, 신청방법, 제출서류, 선정절차, 교육/지원 일정, 문의처를 중심으로 정리해주세요.\n'
                '\n'
                '[작업 방식]\n'
                '1. 먼저 공고 URL에 접속해 공고 본문과 첨부파일에서 확인 가능한 정보를 기준으로 정리하세요.\n'
                '2. 내부적으로는 `공고 기본정보 확인 → 신청대상/제외대상 분리 → 제출서류와 일정 확인 → 예비창업자 관점의 주의사항 도출 → 불확실한 항목 표시` 순서로 검토하세요.\n'
                '3. 최종 답변에는 장문의 추론 과정을 노출하지 말고, 핵심 근거와 판단 결과만 간결하게 제시하세요.\n'
                '4. 사용자 상황만으로 신청 가능 여부를 확정하기 어렵다면, 단정하지 말고 추가 확인 질문을 제시하세요.\n'
                '\n'
                '[출력 형식]\n'
                '1. 한 줄 요약\n'
                '2. 공고 핵심 정보 표\n'
                '3. 신청 대상/제외 대상\n'
                '4. 신청 방법 및 제출서류\n'
                '5. 일정/교육/지원 안내\n'
                '6. 주의사항\n'
                '7. 추가 확인된 특이사항\n'
                '8. 추가 확인 질문\n'
                '\n'
                '[규칙]\n'
                '- 원문에 없는 정보는 추측하지 마세요.\n'
                '- 불확실한 내용은 `확인 필요`라고 표시하세요.\n'
                '- 날짜, 금액, 모집규모, 제출서류, 문의처는 원문 기준으로만 답하세요.\n'
                '- 신청 가능 여부가 애매하면 단정하지 말고 필요한 정보를 질문하세요.\n'
                '- 지원금, 모집규모, 주차 지원, 교육비처럼 원문에서 확인되지 않는 내용은 임의로 만들지 마세요.\n'
                '- URL 접근이 어렵거나 첨부파일 내용을 확인할 수 없으면, 확인 가능한 범위와 확인이 필요한 범위를 구분해서 답하세요.'
            ),
            'category': '페르소나',
            'favorite': False,
        },
    ]


def read_required_text(label: str) -> str:
    while True:
        value = input(label).strip()
        if value:
            return value
        print('빈 값은 입력할 수 없습니다. 다시 입력해주세요.')


def read_prompt_content() -> str:
    """한 줄 입력 또는 /multi로 시작하는 여러 줄 내용을 받는다."""
    first_line = read_required_text('내용 (여러 줄 입력은 /multi): ')
    if first_line != '/multi':
        return first_line
    print('내용을 여러 줄로 입력하세요. 한 줄에 /end를 입력하면 완료됩니다.')
    lines = []
    while True:
        line = input()
        if line.strip() == '/end':
            content = '\n'.join(lines)
            if content.strip():
                return content
            print('내용이 비어 있습니다. 내용을 다시 입력하고 /end로 완료해주세요.')
            lines = []
        else:
            lines.append(line)


def parse_number(value: str, minimum: int, maximum: int) -> int | None:
    """공백과 앞자리 0을 허용하되 범위 밖·비숫자 입력은 거절한다."""
    value = value.strip()
    if not value.isascii() or not value.isdecimal():
        return None
    # 매우 긴 숫자도 int()로 변환하지 않아 변환 제한 오류를 피한다.
    value = value.lstrip('0') or '0'
    for number in range(minimum, maximum + 1):
        if value == str(number):
            return number
    return None


def count_category_prompts(prompts: list[dict], category: str) -> int:
    count = 0
    for prompt in prompts:
        if prompt['category'] == category:
            count += 1
    return count


def select_category(prompts: list[dict] | None = None) -> str:
    print('카테고리 선택:')
    for number, category in enumerate(CATEGORIES, start=1):
        if prompts is None:
            print(f'{number}) {category}')
        else:
            count = count_category_prompts(prompts, category)
            print(f'{number}) {category} ({count}개)')
    while True:
        choice = parse_number(input('선택: '), 1, len(CATEGORIES))
        if choice is not None:
            return CATEGORIES[choice - 1]
        print('잘못된 카테고리 번호입니다. 다시 선택해주세요.')


def add_prompt(prompts: list[dict]) -> None:
    print('\n=== 프롬프트 추가 ===')
    title = read_required_text('제목: ')
    content = read_prompt_content()
    category = select_category(prompts)
    prompts.append({
        'title': title,
        'content': content,
        'category': category,
        'favorite': False,
    })
    print('프롬프트가 추가되었습니다!')
    print(f'등록 번호: {len(prompts)} | 제목: {title}')


def numbered_prompts(prompts: list[dict]) -> list[tuple[int, dict]]:
    """필터를 적용하기 전에 전체 목록의 원래 번호를 부여한다."""
    return list(enumerate(prompts, start=1))


def print_prompt_list(items: list[tuple[int, dict]]) -> None:
    if not items:
        print('프롬프트가 없습니다.')
        return
    for number, prompt in items:
        star = ' ⭐' if prompt['favorite'] else ''
        print(f"{number}. [{prompt['category']}] {prompt['title']}{star}")
    print(f'총 {len(items)}개의 프롬프트')


def show_list(prompts: list[dict]) -> None:
    print('\n=== 프롬프트 목록 ===')
    print_prompt_list(numbered_prompts(prompts))


def show_by_category(prompts: list[dict]) -> None:
    print('\n=== 카테고리별 조회 ===')
    category = select_category(prompts)
    items = []
    for number, prompt in numbered_prompts(prompts):
        if prompt['category'] == category:
            items.append((number, prompt))
    print(f'[{category}] 카테고리 프롬프트:')
    print_prompt_list(items)


def find_prompts(prompts: list[dict], keyword: str) -> list[tuple[int, dict]]:
    """제목·본문을 검색하고 화면 출력 없이 원래 번호와 결과를 반환한다."""
    keyword = keyword.strip().casefold()
    if not keyword:
        return []
    items = []
    for number, prompt in numbered_prompts(prompts):
        if keyword in prompt['title'].casefold() or keyword in prompt['content'].casefold():
            items.append((number, prompt))
    return items


def search_prompts(prompts: list[dict]) -> None:
    print('\n=== 프롬프트 검색 ===')
    keyword = read_required_text('검색어: ')
    items = find_prompts(prompts, keyword)
    print('검색 결과:')
    print_prompt_list(items)


def select_prompt(prompts: list[dict]) -> dict | None:
    if not prompts:
        print('프롬프트가 없습니다.')
        return None
    choice = parse_number(input('프롬프트 번호 입력: '), 1, len(prompts))
    if choice is not None:
        return prompts[choice - 1]
    print('잘못된 프롬프트 번호입니다.')
    return None


def show_detail(prompts: list[dict]) -> None:
    print('\n=== 프롬프트 상세 보기 ===')
    prompt = select_prompt(prompts)
    if prompt is None:
        return
    print('-' * 40)
    print(f"제목: {prompt['title']}")
    print(f"카테고리: {prompt['category']}")
    favorite = '⭐' if prompt['favorite'] else '미등록'
    print(f'즐겨찾기: {favorite}')
    print('내용:')
    print(prompt['content'])
    print('-' * 40)


def toggle_favorite(prompts: list[dict]) -> None:
    print('\n=== 즐겨찾기 관리 ===')
    prompt = select_prompt(prompts)
    if prompt is None:
        return
    prompt['favorite'] = not prompt['favorite']
    action = '추가' if prompt['favorite'] else '해제'
    print(f"'{prompt['title']}' 즐겨찾기를 {action}했습니다!")


def show_favorites(prompts: list[dict]) -> None:
    print('\n=== 즐겨찾기 목록 ===')
    items = []
    for number, prompt in numbered_prompts(prompts):
        if prompt['favorite']:
            items.append((number, prompt))
    print_prompt_list(items)


def show_menu() -> None:
    print('\n=== 나만의 프롬프트 관리 ===')
    print('1. 프롬프트 추가')
    print('2. 프롬프트 목록')
    print('3. 카테고리별 조회')
    print('4. 프롬프트 검색')
    print('5. 프롬프트 상세 보기')
    print('6. 즐겨찾기 관리')
    print('7. 즐겨찾기 목록')
    print('0. 종료')


def main() -> None:
    prompts = create_initial_prompts()
    while True:
        show_menu()
        choice = parse_number(input('선택: '), 0, 7)
        if choice == 0:
            print('프로그램을 종료합니다.')
            break
        elif choice == 1:
            add_prompt(prompts)
        elif choice == 2:
            show_list(prompts)
        elif choice == 3:
            show_by_category(prompts)
        elif choice == 4:
            search_prompts(prompts)
        elif choice == 5:
            show_detail(prompts)
        elif choice == 6:
            toggle_favorite(prompts)
        elif choice == 7:
            show_favorites(prompts)
        else:
            print('잘못된 메뉴 번호입니다. 다시 선택해주세요.')


if __name__ == '__main__':
    try:
        main()
    except (EOFError, KeyboardInterrupt):
        print('\n입력이 중단되어 프로그램을 종료합니다.')
