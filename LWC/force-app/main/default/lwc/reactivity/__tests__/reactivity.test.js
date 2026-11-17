import { createElement } from '@lwc/engine-dom';
import Reactivity from 'c/reactivity';

const flush = () => Promise.resolve();

function mount() {
    const el = createElement('c-reactivity', { is: Reactivity });
    document.body.appendChild(el);
    return el;
}
const text = (el, sel) => el.shadowRoot.querySelector(sel).textContent;

describe('c-reactivity', () => {
    afterEach(() => {
        while (document.body.firstChild) {
            document.body.removeChild(document.body.firstChild);
        }
    });

    it('원시값 필드를 다시 대입하면 다시 렌더링한다', async () => {
        const el = mount();
        el.increment();
        expect(text(el, '.count')).toBe('0');   // 아직 그리지 않음(비동기)
        await flush();
        expect(text(el, '.count')).toBe('1');
    });

    it('일반 필드 객체의 내부 속성을 바꾸면 화면이 그대로다', async () => {
        const el = mount();
        el.mutatePlain();
        await flush();
        expect(text(el, '.plain')).toBe('처음');
    });

    it('객체를 새로 만들어 대입하면 다시 렌더링한다', async () => {
        const el = mount();
        el.reassignPlain();
        await flush();
        expect(text(el, '.plain')).toBe('재대입');
    });

    it('@track 객체는 내부 속성 변경도 감지한다', async () => {
        const el = mount();
        el.mutateTracked();
        await flush();
        expect(text(el, '.tracked')).toBe('변경');
    });

    it('일반 필드 배열에 push하면 화면이 그대로다', async () => {
        const el = mount();
        el.pushList();
        await flush();
        expect(text(el, '.list')).toBe('a');
    });

    it('@track 배열에 push하면 다시 렌더링한다', async () => {
        const el = mount();
        el.pushTrackedList();
        await flush();
        expect(text(el, '.tracked-list')).toBe('a,b');
    });

    it('다른 이유로 다시 렌더링되면 바뀐 내부 값이 그때 함께 보인다', async () => {
        const el = mount();
        el.mutatePlain();
        await flush();
        expect(text(el, '.plain')).toBe('처음');
        el.increment();
        await flush();
        expect(text(el, '.plain')).toBe('변경');
    });

    it('여러 번 바꿔도 다음 렌더링에서 한 번에 반영한다', async () => {
        const el = mount();
        const before = el.renders;
        el.increment();
        el.increment();
        el.increment();
        await flush();
        expect(text(el, '.count')).toBe('3');
        expect(el.renders - before).toBe(1);
    });

    it('템플릿에서 쓰지 않는 필드를 바꾸면 렌더링하지 않는다', async () => {
        const el = mount();
        const before = el.renders;
        el.changeUntouched();
        await flush();
        expect(el.renders - before).toBe(0);
    });
});
