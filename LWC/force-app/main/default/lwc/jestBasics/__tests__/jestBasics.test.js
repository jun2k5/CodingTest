import { createElement } from '@lwc/engine-dom';
import JestBasics from 'c/jestBasics';

// 렌더링이 끝날 때까지 기다리는 도우미
const flush = () => Promise.resolve();

describe('c-jest-basics', () => {
    // 테스트마다 DOM을 비워 서로 영향을 주지 않게 한다
    afterEach(() => {
        while (document.body.firstChild) {
            document.body.removeChild(document.body.firstChild);
        }
        jest.clearAllMocks();
    });

    function mount(props = {}) {
        const el = createElement('c-jest-basics', { is: JestBasics });
        Object.assign(el, props);          // @api 속성은 appendChild 전에 넣는다
        document.body.appendChild(el);     // 이때 connectedCallback과 첫 렌더링
        return el;
    }

    describe('렌더링', () => {
        it('처음에는 합계 0원이고 초기화 버튼이 비활성이다', () => {
            const el = mount();
            expect(el.shadowRoot.querySelector('.total').textContent).toBe('합계 0원');
            expect(el.shadowRoot.querySelector('.reset').disabled).toBe(true);
        });

        it('@api step이 버튼 라벨에 반영된다', () => {
            const el = mount({ step: 500 });
            expect(el.shadowRoot.querySelector('.add').textContent).toBe('+500');
        });
    });

    describe('사용자 동작', () => {
        it('클릭하면 다음 렌더링 뒤에 합계가 바뀐다', async () => {
            const el = mount();
            el.shadowRoot.querySelector('.add').click();
            el.shadowRoot.querySelector('.add').click();
            await flush();
            expect(el.shadowRoot.querySelector('.total').textContent).toBe('합계 2,000원');
            expect(el.shadowRoot.querySelector('.reset').disabled).toBe(false);
        });

        it('jest.fn으로 보낸 이벤트와 detail을 검사한다', () => {
            const el = mount({ step: 300 });
            const handler = jest.fn();
            el.addEventListener('totalchange', handler);
            el.shadowRoot.querySelector('.add').click();
            expect(handler).toHaveBeenCalledTimes(1);
            expect(handler.mock.calls[0][0].detail).toEqual({ total: 300 });
        });
    });
});
