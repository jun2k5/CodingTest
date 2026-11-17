import { formatKrw } from 'c/priceUtils';

describe('c/priceUtils', () => {
    it('천 단위 구분 기호와 원을 붙인다', () => {
        expect(formatKrw(1234567)).toBe('1,234,567원');
    });
});
