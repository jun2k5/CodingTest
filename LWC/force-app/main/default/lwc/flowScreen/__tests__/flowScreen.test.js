import { createElement } from '@lwc/engine-dom';
import FlowScreen from 'c/flowScreen';

const flush = () => Promise.resolve();

function mount(props = {}) {
    const el = createElement('c-flow-screen', { is: FlowScreen });
    Object.assign(el, { maxDiscount: 20, ...props });
    document.body.appendChild(el);
    return el;
}

function change(el, sel, value) {
    const input = el.shadowRoot.querySelector(sel);
    input.value = value;
    input.dispatchEvent(new CustomEvent('change'));
}

describe('c-flow-screen', () => {
    afterEach(() => {
        while (document.body.firstChild) {
            document.body.removeChild(document.body.firstChild);
        }
    });

    it('입력이 바뀌면 FlowAttributeChangeEvent를 보낸다', () => {
        const el = mount();
        const handler = jest.fn();
        el.addEventListener('lightning__flowattributechange', handler);
        change(el, '.discount', '10');
        change(el, '.reason', '장기 고객');
        expect(handler).toHaveBeenCalledTimes(2);
        expect(el.discount).toBe(10);
        expect(el.reason).toBe('장기 고객');
    });

    it.each([
        [25, '', false, '할인율은 20% 이하여야 한다'],
        [10, '', false, '할인 사유를 입력하세요'],
        [10, '장기 고객', true, undefined],
        [0, '', true, undefined]
    ])('validate(): 할인 %i%%, 사유 "%s" → %s', (discount, reason, isValid, message) => {
        const el = mount();
        change(el, '.discount', String(discount));
        change(el, '.reason', reason);
        const result = el.validate();
        expect(result.isValid).toBe(isValid);
        expect(result.errorMessage).toBe(message);
    });

    it('NEXT가 가능할 때만 다음 버튼을 보이고, 누르면 Flow 내비게이션 이벤트를 보낸다', async () => {
        expect(mount({ availableActions: ['BACK'] }).shadowRoot.querySelector('.next')).toBeNull();
        const el = mount({ availableActions: ['NEXT', 'BACK'] });
        const handler = jest.fn();
        el.addEventListener('lightning__flownavigationnext', handler);
        el.shadowRoot.querySelector('.next').click();
        await flush();
        expect(handler).toHaveBeenCalledTimes(1);
    });
});
