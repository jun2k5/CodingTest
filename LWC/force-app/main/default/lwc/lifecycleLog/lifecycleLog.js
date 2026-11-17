// 생명주기 훅이 불린 순서를 모으는 공용 모듈(예제 관찰용)
export const calls = [];
export function log(entry) {
    calls.push(entry);
}
export function reset() {
    calls.length = 0;
}
