import { createElement } from '@lwc/engine-dom';
import Styling from 'c/styling';

const flush = () => Promise.resolve();

function mount(props = {}) {
    const el = createElement('c-styling', { is: Styling });
    Object.assign(el, props);
    document.body.appendChild(el);
    return el;
}

describe('c-styling', () => {
    let pageStyle;

    beforeEach(() => {
        // 페이지(바깥) 전역 CSS
        pageStyle = document.createElement('style');
        pageStyle.textContent = '.title { color: rgb(0, 0, 255); }';
        document.head.appendChild(pageStyle);
    });

    afterEach(() => {
        pageStyle.remove();
        while (document.body.firstChild) {
            document.body.removeChild(document.body.firstChild);
        }
    });

    it('컴포넌트 CSS는 바깥 요소로 새어 나가지 않는다', () => {
        const outside = document.createElement('p');
        outside.className = 'title';
        document.body.appendChild(outside);
        const el = mount();
        expect(getComputedStyle(el.shadowRoot.querySelector('.title')).color).toBe('rgb(255, 0, 0)');
        expect(getComputedStyle(outside).color).toBe('rgb(0, 0, 255)');
    });

    it(':host 규칙은 컴포넌트 태그 자체에 적용된다', () => {
        const el = mount();
        expect(getComputedStyle(el).display).toBe('block');
    });

    it('조건에 따라 getter가 클래스를 바꾼다', async () => {
        const el = mount();
        expect(el.shadowRoot.querySelector('.status').className).toBe('status status-ok');
        el.hasError = true;
        await flush();
        const status = el.shadowRoot.querySelector('.status');
        expect(status.className).toBe('status status-error');
        expect(getComputedStyle(status).fontWeight).toBe('700');
    });
});
