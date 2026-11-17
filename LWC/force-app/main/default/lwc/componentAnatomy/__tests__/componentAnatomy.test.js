import { createElement } from '@lwc/engine-dom';
import ComponentAnatomy from 'c/componentAnatomy';

describe('c-component-anatomy', () => {
    afterEach(() => {
        while (document.body.firstChild) {
            document.body.removeChild(document.body.firstChild);
        }
    });

    it('폴더 이름 componentAnatomy는 c-component-anatomy 태그가 된다', () => {
        const el = createElement('c-component-anatomy', { is: ComponentAnatomy });
        document.body.appendChild(el);
        expect(el.tagName.toLowerCase()).toBe('c-component-anatomy');
    });

    it('같은 번들 파일과 다른 번들 모듈을 import해서 쓴다', () => {
        const el = createElement('c-component-anatomy', { is: ComponentAnatomy });
        el.price = 15000;
        document.body.appendChild(el);
        expect(el.shadowRoot.querySelector('.price').textContent).toBe('가격: 15,000원');
    });

    it('document.querySelector는 Shadow DOM 안의 요소를 찾지 못한다', () => {
        const el = createElement('c-component-anatomy', { is: ComponentAnatomy });
        document.body.appendChild(el);
        expect(document.querySelector('.title')).toBeNull();
        expect(el.shadowRoot.querySelector('.title').textContent).toBe('상품');
    });
});
