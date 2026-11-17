import { createElement } from '@lwc/engine-dom';
import Lifecycle from 'c/lifecycle';
import { calls, reset } from 'c/lifecycleLog';

const flush = () => Promise.resolve();

describe('c-lifecycle', () => {
    beforeEach(() => reset());
    afterEach(() => {
        while (document.body.firstChild) {
            document.body.removeChild(document.body.firstChild);
        }
        jest.useRealTimers();
    });

    it('생성과 연결: 부모 → 자식 순서, 렌더링 완료: 자식 → 부모 순서', async () => {
        const el = createElement('c-lifecycle', { is: Lifecycle });
        el.label = '첫째';
        document.body.appendChild(el);
        await flush();
        expect(calls.slice(0, 6)).toEqual([
            'parent constructor',
            'parent connectedCallback (label=첫째)',
            'child constructor',
            'child connectedCallback',
            'child renderedCallback',
            'parent renderedCallback'
        ]);
    });

    it('renderedCallback은 다시 렌더링될 때마다 불린다', async () => {
        const el = createElement('c-lifecycle', { is: Lifecycle });
        document.body.appendChild(el);
        await flush();
        const before = calls.filter((c) => c === 'parent renderedCallback').length;
        el.label = '바뀜';
        await flush();
        const after = calls.filter((c) => c === 'parent renderedCallback').length;
        expect(before).toBe(2);   // 첫 렌더링 + measured 변경으로 인한 렌더링
        expect(after).toBe(before + 1);
    });

    it('DOM에서 제거하면 disconnectedCallback에서 타이머를 정리한다', async () => {
        jest.useFakeTimers();
        const el = createElement('c-lifecycle', { is: Lifecycle });
        document.body.appendChild(el);
        expect(jest.getTimerCount()).toBe(1);
        document.body.removeChild(el);
        expect(calls).toContain('parent disconnectedCallback');
        expect(calls).toContain('child disconnectedCallback');
        expect(jest.getTimerCount()).toBe(0);
    });

    it('errorCallback이 자식의 오류를 잡아 대체 화면을 보여 준다', async () => {
        const el = createElement('c-lifecycle', { is: Lifecycle });
        el.failChild = true;
        document.body.appendChild(el);
        await flush();
        expect(calls).toContain('parent errorCallback');
        expect(el.shadowRoot.querySelector('.error').textContent).toBe('오류 처리됨: 자식에서 난 오류');
    });
});
