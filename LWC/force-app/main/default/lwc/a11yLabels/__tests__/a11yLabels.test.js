import { createElement } from '@lwc/engine-dom';
import A11yLabels from 'c/a11yLabels';

// 라벨·i18n 값은 Jest에서 직접 정한다(실제로는 사용자 언어·로캘에 따라 org가 넣어 준다)
jest.mock('@salesforce/label/c.Cart_Title', () => ({ default: '장바구니' }), { virtual: true });
jest.mock('@salesforce/label/c.Cart_Item_Count', () => ({ default: '장바구니에 {0}개' }), { virtual: true });
jest.mock('@salesforce/label/c.Cart_Remove', () => ({ default: '{0} 삭제' }), { virtual: true });
jest.mock('@salesforce/i18n/locale', () => ({ default: 'ko-KR' }), { virtual: true });
jest.mock('@salesforce/i18n/currency', () => ({ default: 'KRW' }), { virtual: true });

const flush = () => Promise.resolve();

function mount() {
    const el = createElement('c-a11y-labels', { is: A11yLabels });
    document.body.appendChild(el);
    return el;
}

describe('c-a11y-labels', () => {
    afterEach(() => {
        while (document.body.firstChild) {
            document.body.removeChild(document.body.firstChild);
        }
    });

    it('하드코딩 대신 Custom Label을 쓰고 {0} 자리에 값을 끼운다', () => {
        const el = mount();
        expect(el.shadowRoot.querySelector('.title').textContent).toBe('장바구니');
        expect(el.shadowRoot.querySelector('.status').textContent).toBe('장바구니에 2개');
    });

    it('통화는 사용자 로캘과 통화 코드로 서식을 맞춘다', () => {
        const el = mount();
        const prices = [...el.shadowRoot.querySelectorAll('.price')].map((p) => p.textContent);
        expect(prices).toEqual(['₩45,000', '₩19,000']);
    });

    it('아이콘 버튼마다 무엇을 하는지 alternative-text를 준다', () => {
        const el = mount();
        const buttons = el.shadowRoot.querySelectorAll('lightning-button-icon');
        expect([...buttons].map((b) => b.alternativeText)).toEqual(['키보드 삭제', '마우스 삭제']);
    });

    it('상태 문구는 aria-live 영역에서 바뀐다', async () => {
        const el = mount();
        expect(el.shadowRoot.querySelector('.status').getAttribute('aria-live')).toBe('polite');
        el.shadowRoot.querySelector('lightning-button-icon').click();
        await flush();
        expect(el.shadowRoot.querySelector('.status').textContent).toBe('장바구니에 1개');
    });
});
