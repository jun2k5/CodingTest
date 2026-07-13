# 문제 설명
# 괄호가 바르게 짝지어졌다는 것은 '(' 문자로 열렸으면 반드시 짝지어서 ')' 문자로 닫혀야 한다는 뜻입니다. 예를 들어
#
# "()()" 또는 "(())()" 는 올바른 괄호입니다.
# ")()(" 또는 "(()(" 는 올바르지 않은 괄호입니다.
# '(' 또는 ')' 로만 이루어진 문자열 s가 주어졌을 때, 문자열 s가 올바른 괄호이면 true를 return 하고, 올바르지 않은 괄호이면 false를 return 하는 solution 함수를 완성해 주세요.
#
# 제한사항
# 문자열 s의 길이 : 100,000 이하의 자연수
# 문자열 s는 '(' 또는 ')' 로만 이루어져 있습니다.
# 입출력 예
# s	answer
# "()()"	true
# "(())()"	true
# ")()("	false
# "(()("	false
# 입출력 예 설명
# 입출력 예 #1,2,3,4
# 문제의 예시와 같습니다.

def solution(s):
    answer = True
    left_count = 0

    for word in s:
        if word == "(":
            left_count += 1

        if word == ")":
            if left_count == 0:
                return False
            else:
                left_count -= 1

    if left_count != 0:
        return False

    return True

### 문제 해석 및 풀이 ###

# 우선 solution 함수에 들어올 문자열을 첫번째부터 순서대로 검사한다. line 25: for word in s:
# "(" 여는 괄호의 개수를 저장하는 left_count 변수를 만들고, "(" 여는 괄호가 들어올때마다 증가시킨다.
# "(" 여는 괄호가 있다면 뒤에 ")" 닫는 괄호가 와야하며, ")" 닫는 괄호가 먼저올 시 (left_count == 0) 바로 False를 반환한다.
# ")" 닫는 괄호가 들어오면 괄호의 짝이 완성됐으므로 left_count를 1 감소시키고 다시 루프검사를 실시한다.
# 루프 검사를 통과하면 0으로 마무리되어야하는데, 오버플로우나 다른 버그가 발생할 수 있으므로 left_count가 0인지 검사한다. line 35: if left_count != 0:
# 모든 검사가 완료되면 True를 반환한다.