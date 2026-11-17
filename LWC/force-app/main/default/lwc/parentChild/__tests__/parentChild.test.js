import { createElement } from '@lwc/engine-dom';
import ParentChild from 'c/parentChild';

const flush = () => Promise.resolve();

function mount() {
    const el = createElement('c-parent-child', { is: ParentChild });
    document.body.appendChild(el);
    return el;
}
const children = (el) => el.shadowRoot.querySelectorAll('c-order-item');

describe('c-parent-child', () => {
    afterEach(() => {
        while (document.body.firstChild) {
            document.body.removeChild(document.body.firstChild);
        }
    });

    it('부모 → 자식: @api 속성으로 데이터를 넘긴다', () => {
        const el = mount();
        const names = [...children(el)].map((c) => c.shadowRoot.querySelector('.name').textContent);
        expect(names).toEqual(['키보드', '마우스']);
    });

    it('자식 → 부모: CustomEvent의 detail로 데이터를 보낸다', async () => {
        const el = mount();
        children(el)[1].shadowRoot.querySelector('.select').click();
        await flush();
        expect(el.shadowRoot.querySelector('.selected').textContent).toBe('선택: 마우스');
    });

    it('부모가 자식의 @api 메서드를 호출한다', async () => {
        const el = mount();
        el.shadowRoot.querySelector('.highlight-first').click();
        await flush();
        expect(children(el)[0].shadowRoot.querySelector('.row').className).toBe('row highlighted');
        expect(children(el)[1].shadowRoot.querySelector('.row').className).toBe('row');
    });

    it('composed가 아닌 이벤트는 부모 컴포넌트 바깥으로 나가지 않는다', () => {
        const el = mount();
        const outside = jest.fn();
        document.body.addEventListener('select', outside);
        children(el)[0].shadowRoot.querySelector('.select').click();
        document.body.removeEventListener('select', outside);
        expect(outside).not.toHaveBeenCalled();
    });

    it('bubbles + composed 이벤트는 바깥(document.body)까지 전파된다', () => {
        const el = mount();
        const outside = jest.fn();
        document.body.addEventListener('itemremove', outside);
        children(el)[0].shadowRoot.querySelector('.remove').click();
        document.body.removeEventListener('itemremove', outside);
        expect(outside).toHaveBeenCalledTimes(1);
        expect(outside.mock.calls[0][0].detail).toEqual({ id: 'o1' });
    });

    it('자식은 @api로 받은 객체를 고칠 수 없다', () => {
        const el = mount();
        expect(() => children(el)[0].tryMutate()).toThrow();
    });
});
