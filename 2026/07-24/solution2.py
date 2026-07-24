# JadenCase 문자열 만들기
# 제출 내역
# 문제 설명
# JadenCase란 모든 단어의 첫 문자가 대문자이고, 그 외의 알파벳은 소문자인 문자열입니다. 단, 첫 문자가 알파벳이 아닐 때에는 이어지는 알파벳은 소문자로 쓰면 됩니다. (첫 번째 입출력 예 참고)
# 문자열 s가 주어졌을 때, s를 JadenCase로 바꾼 문자열을 리턴하는 함수, solution을 완성해주세요.
#
# 제한 조건
# s는 길이 1 이상 200 이하인 문자열입니다.
# s는 알파벳과 숫자, 공백문자(" ")로 이루어져 있습니다.
# 숫자는 단어의 첫 문자로만 나옵니다.
# 숫자로만 이루어진 단어는 없습니다.
# 공백문자가 연속해서 나올 수 있습니다.
# 입출력 예
# s	return
# "3people unFollowed me"	"3people Unfollowed Me"
# "for the last week"	"For The Last Week"
# ※ 공지 - 2022년 1월 14일 제한 조건과 테스트 케이스가 추가되었습니다.

def solution(s):
    upper = True
    answer = ''
    lower_s = s.lower()
    append_word = ''

    for i in lower_s:
        append_word = i
        if upper:
            append_word = i.upper()
            upper = False
        if i == " ":
            upper = True

        answer += append_word

    print(answer)

    return answer

if __name__ == '__main__':
    s = input()
    print(solution(s))

# capitalize 함수 : 문자열의 첫 글자를 대문자로 변환하고 나머지 모든 문자를 소문자로 변환하는 내장 함수

# title 함수 : 문자열의 앞글자및 공백으로 오는 첫 글자를 대문자로 변환하는 함수

# def Jaden_Case(s):
#     # 함수를 완성하세요
#     return s.title()
#
# # 아래는 테스트로 출력해 보기 위한 코드입니다.
# print(Jaden_Case("3people unFollowed me for the last week"))