// HTML 파일이 없는 "서비스 컴포넌트": 다른 컴포넌트가 import해서 쓰는 순수 모듈
export function formatKrw(value) {
    return `${Number(value).toLocaleString('ko-KR')}원`;
}
