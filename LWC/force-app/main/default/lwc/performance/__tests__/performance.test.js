import { createElement } from '@lwc/engine-dom';
import Performance from 'c/performance';
import { calls, reset } from 'c/lifecycleLog';

const flush = () => Promise.resolve();
const makeRows = (n) => Array.from({ length: n }, (_, i) => ({ id: `r${i}`, amount: i }));

function mount(rows) {
    const el = createElement('c-performance', { is: Performance });
    el.rows = rows;
    document.body.appendChild(el);
    return el;
}

describe('c-performance', () => {
    beforeEach(() => reset());
    afterEach(() => {
        while (document.body.firstChild) {
            document.body.removeChild(document.body.firstChild);
        }
    });

    it('getter는 렌더링마다 다시 계산하고, 필드에 담은 값은 입력이 바뀔 때만 계산한다', async () => {
        const el = mount(makeRows(1000));
        for (let i = 0; i < 3; i++) {
            el.shadowRoot.querySelector('.tick-btn').click();
            await flush();
        }
        expect(el.computeLog).toEqual({ getter: 4, cached: 1 }); // 렌더링 4번(처음 + 3번)
        expect(el.shadowRoot.querySelector('.cached').textContent).toBe('1000건, 합계 499500');
    });

    it('큰 목록은 처음 20행만 그리고 더 보기로 늘린다', async () => {
        const el = mount(makeRows(1000));
        expect(el.shadowRoot.querySelectorAll('.rows li').length).toBe(20);
        el.shadowRoot.querySelector('.more').click();
        await flush();
        expect(el.shadowRoot.querySelectorAll('.rows li').length).toBe(40);
    });

    it('lwc:if로 접힌 영역의 자식은 열기 전까지 만들어지지 않는다', async () => {
        const el = mount(makeRows(5));
        expect(calls).not.toContain('child constructor');
        el.shadowRoot.querySelector('.toggle').click();
        await flush();
        expect(calls).toContain('child constructor');
    });
});
