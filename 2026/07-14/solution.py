# 최댓값과 최솟값

# 문제 설명
# 문자열 s에는 공백으로 구분된 숫자들이 저장되어 있습니다. str에 나타나는 숫자 중 최소값과 최대값을 찾아 이를 "(최소값) (최대값)"형태의 문자열을 반환하는 함수, solution을 완성하세요.
# 예를들어 s가 "1 2 3 4"라면 "1 4"를 리턴하고, "-1 -2 -3 -4"라면 "-4 -1"을 리턴하면 됩니다.
#
# 제한 조건
# s에는 둘 이상의 정수가 공백으로 구분되어 있습니다.
# 입출력 예
# s	return
# "1 2 3 4"	"1 4"
# "-1 -2 -3 -4"	"-4 -1"
# "-1 -1"	"-1 -1"


def solution(s):
    number = list(map(int, s.split()))
    max = number[0]
    min = number[0]

    for i in number:
        if i > max:
            max = i
        if i < min:
            min = i

    answer = str(min) + ' ' + str(max)
    return answer

### 문제 해석 및 풀이 ###

# 문자열을 split() 함수를 이용해 배열로 만들고
# map()함수로 각각의 요소를 number 라는 정수형 리스트에 저장한다.
# 그 뒤는 최소, 최대값을 구한 뒤 str 형변환을 통해 min과 max를 정답 형태에 맞게
# 결합한 뒤, 결과를 반환한다.