import { createElement } from '@lwc/engine-dom';
import DebugDemo from 'c/debugDemo';

function create(props = {}) {
    const el = createElement('c-debug-demo', { is: DebugDemo });
    Object.assign(el, props);
    return el;
}

describe('c-debug-demo: 자주 보는 오류 재현', () => {
    afterEach(() => {
        while (document.body.firstChild) {
            document.body.removeChild(document.body.firstChild);
        }
        jest.useRealTimers();
    });

    it('데이터가 오기 전 깊은 속성 접근: Cannot read properties of undefined', () => {
        // 렌더링 중 오류는 appendChild 호출자에게 던져지지 않고 window의 error 이벤트로 보고된다
        const errors = [];
        const onError = (e) => {
            errors.push(e.error.message);
            e.preventDefault();
        };
        window.addEventListener('error', onError);
        const quiet = jest.spyOn(console, 'error').mockImplementation(() => {});
        document.body.appendChild(create({ mode: 'unsafe' }));
        window.removeEventListener('error', onError);
        quiet.mockRestore();
        expect(errors).toEqual(["Cannot read properties of undefined (reading 'fields')"]);
    });

    it('옵셔널 체이닝으로 고치면 대체 문구가 보인다', () => {
        const el = create();
        document.body.appendChild(el);
        expect(el.shadowRoot.querySelector('.name').textContent).toBe('불러오는 중');
    });

    it("부모가 넘긴 @api 객체 수정: 'set' on proxy 오류", () => {
        const el = create({ config: { label: '부모 값' } });
        document.body.appendChild(el);
        expect(() => el.mutateConfig()).toThrow("'set' on proxy: trap returned falsish for property 'label'");
    });

    it('function 콜백 안의 this는 컴포넌트가 아니다', () => {
        jest.useFakeTimers();
        const el = create();
        document.body.appendChild(el);
        el.startBrokenTimer();
        expect(() => jest.runAllTimers()).toThrow(TypeError);
    });

    it('화살표 함수로 고치면 컴포넌트 필드가 바뀐다', async () => {
        jest.useFakeTimers();
        const el = create();
        document.body.appendChild(el);
        el.startTimer();
        jest.runAllTimers();
        await Promise.resolve();
        expect(el.shadowRoot.querySelector('.count').textContent).toBe('1');
    });

    it('프록시 객체는 JSON으로 펼쳐서 확인한다', () => {
        const el = create({ config: { label: '설정', nested: { a: 1 } } });
        document.body.appendChild(el);
        expect(el.snapshot()).toEqual({ label: '설정', nested: { a: 1 } });
    });
});
