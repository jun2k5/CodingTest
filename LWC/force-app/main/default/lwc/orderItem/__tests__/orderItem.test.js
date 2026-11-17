import { createElement } from '@lwc/engine-dom';
import OrderItem from 'c/orderItem';

describe('c-order-item', () => {
    afterEach(() => {
        while (document.body.firstChild) {
            document.body.removeChild(document.body.firstChild);
        }
    });

    it('선택 버튼을 누르면 select 이벤트에 id를 담아 보낸다', () => {
        const el = createElement('c-order-item', { is: OrderItem });
        el.item = { id: 'o9', name: '펜', qty: 3 };
        document.body.appendChild(el);
        const handler = jest.fn();
        el.addEventListener('select', handler);
        el.shadowRoot.querySelector('.select').click();
        expect(handler.mock.calls[0][0].detail).toEqual({ id: 'o9' });
    });
});
