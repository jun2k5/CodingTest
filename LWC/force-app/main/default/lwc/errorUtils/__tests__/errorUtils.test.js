import { reduceErrors } from 'c/errorUtils';

describe('c/errorUtils reduceErrors', () => {
    it('JS Error의 message를 꺼낸다', () => {
        expect(reduceErrors(new TypeError('x is undefined'))).toEqual(['x is undefined']);
    });

    it('Apex 예외는 body.message를 꺼낸다', () => {
        expect(reduceErrors({ body: { message: '검증 실패', exceptionType: 'AuraHandledException' } })).toEqual([
            '검증 실패'
        ]);
    });

    it('UI API 저장 오류는 페이지 오류와 필드 오류를 모두 꺼낸다', () => {
        const error = {
            body: {
                message: 'An error occurred while trying to update the record.',
                output: {
                    errors: [{ message: '중복 레코드가 있다' }],
                    fieldErrors: { Name: [{ message: '이름은 필수다' }] }
                }
            }
        };
        expect(reduceErrors(error)).toEqual(['중복 레코드가 있다', '이름은 필수다']);
    });

    it('body가 배열이면 각 message를 꺼낸다', () => {
        expect(reduceErrors({ body: [{ message: 'A' }, { message: 'B' }] })).toEqual(['A', 'B']);
    });

    it('여러 오류를 배열로 받아 한 목록으로 합친다', () => {
        expect(reduceErrors(['문자열 오류', null, { body: { message: '서버 오류' } }])).toEqual([
            '문자열 오류',
            '서버 오류'
        ]);
    });
});
