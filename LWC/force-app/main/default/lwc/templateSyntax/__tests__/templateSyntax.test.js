import { createElement } from '@lwc/engine-dom';
import TemplateSyntax from 'c/templateSyntax';

const PRODUCTS = [
    { id: 'p1', name: '키보드', soldOut: false },
    { id: 'p2', name: '마우스', soldOut: true },
    { id: 'p3', name: '모니터', soldOut: false }
];

function mount(props = {}) {
    const el = createElement('c-template-syntax', { is: TemplateSyntax });
    Object.assign(el, props);
    document.body.appendChild(el);
    return el;
}

describe('c-template-syntax', () => {
    afterEach(() => {
        while (document.body.firstChild) {
            document.body.removeChild(document.body.firstChild);
        }
    });

    it('getter 결과를 바인딩한다', () => {
        const el = mount({ userName: '이', products: PRODUCTS });
        expect(el.shadowRoot.querySelector('.greeting').textContent).toBe('이님, 안녕하세요');
        expect(el.shadowRoot.querySelector('.count').textContent).toBe('상품 3개');
    });

    it('lwc:if → lwc:elseif → lwc:else 순서로 하나만 그린다', () => {
        expect(mount({ isLoading: true }).shadowRoot.querySelector('.state').textContent).toBe('불러오는 중');
        expect(mount({ products: [] }).shadowRoot.querySelector('.state').textContent).toBe('상품이 없다');
        expect(mount({ products: PRODUCTS }).shadowRoot.querySelector('.state')).toBeNull();
    });

    it('for:each는 배열 순서대로 그리고 클래스도 바인딩한다', () => {
        const lis = mount({ products: PRODUCTS }).shadowRoot.querySelectorAll('.list li');
        expect(Array.from(lis).map((li) => li.textContent)).toEqual(['키보드', '마우스', '모니터']);
        expect(lis[1].className).toBe('item sold-out');
    });

    it('iterator는 first와 last를 알려 준다', () => {
        const lis = mount({ products: PRODUCTS }).shadowRoot.querySelectorAll('.ordered li');
        expect(lis[0].querySelector('.badge').textContent).toBe('처음');
        expect(lis[1].querySelector('.badge')).toBeNull();
        expect(lis[2].querySelector('.badge').textContent).toBe('끝');
    });
});
