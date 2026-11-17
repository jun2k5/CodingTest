import { createElement } from '@lwc/engine-dom';
import HelloLwc from 'c/helloLwc';

describe('c-hello-lwc', () => {
    afterEach(() => {
        while (document.body.firstChild) {
            document.body.removeChild(document.body.firstChild);
        }
    });

    it('기본값으로 인사한다', () => {
        const el = createElement('c-hello-lwc', { is: HelloLwc });
        document.body.appendChild(el);
        const p = el.shadowRoot.querySelector('.greeting');
        expect(p.textContent).toBe('Hello, World!');
    });

    it('@api 속성을 바꾸면 다시 렌더링한다', async () => {
        const el = createElement('c-hello-lwc', { is: HelloLwc });
        document.body.appendChild(el);
        el.name = 'LWC';
        await Promise.resolve();
        expect(el.shadowRoot.querySelector('.greeting').textContent).toBe('Hello, LWC!');
    });
});
