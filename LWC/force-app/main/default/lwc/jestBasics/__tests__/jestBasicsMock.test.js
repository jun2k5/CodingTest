import { createElement } from '@lwc/engine-dom';
import JestBasics from 'c/jestBasics';
import { formatKrw } from 'c/priceUtils';

// 의존 모듈을 가짜로 바꾼다: 이 파일의 테스트에서만 적용
jest.mock('c/priceUtils', () => ({
    formatKrw: jest.fn((v) => `[${v}]`)
}));

describe('c-jest-basics (모듈 모의)', () => {
    afterEach(() => {
        while (document.body.firstChild) {
            document.body.removeChild(document.body.firstChild);
        }
    });

    it('jest.mock으로 c/priceUtils를 바꾸면 가짜 결과가 그려진다', () => {
        const el = createElement('c-jest-basics', { is: JestBasics });
        document.body.appendChild(el);
        expect(el.shadowRoot.querySelector('.total').textContent).toBe('합계 [0]');
        expect(formatKrw).toHaveBeenCalledWith(0);
    });
});
