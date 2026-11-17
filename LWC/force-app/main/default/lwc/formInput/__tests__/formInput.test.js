import { createElement } from '@lwc/engine-dom';
import FormInput from 'c/formInput';

const flush = () => Promise.resolve();

function mount() {
    const el = createElement('c-form-input', { is: FormInput });
    document.body.appendChild(el);
    return el;
}

// lightning-input은 Jest에서 스텁이라 실제로 값을 입력할 수 없다.
// value를 넣고 change 이벤트를 직접 보내 사용자의 입력을 흉내 낸다.
function typeInto(el, name, value) {
    // name은 @api 속성(property)이라 HTML 속성 선택자 [name=...]로는 찾을 수 없다
    const input = [...el.shadowRoot.querySelectorAll('lightning-input')].find((i) => i.name === name);
    input.value = value;
    input.dispatchEvent(new CustomEvent('change'));
}

describe('c-form-input', () => {
    afterEach(() => {
        while (document.body.firstChild) {
            document.body.removeChild(document.body.firstChild);
        }
        jest.clearAllMocks();
    });

    it('name 속성으로 입력란을 구분해 하나의 핸들러로 처리한다', async () => {
        const el = mount();
        typeInto(el, 'customer', '홍길동');
        typeInto(el, 'email', 'hong@example.com');
        await flush();
        const inputs = el.shadowRoot.querySelectorAll('lightning-input');
        expect(inputs[0].value).toBe('홍길동');
        expect(inputs[1].value).toBe('hong@example.com');
    });

    it('data-delta 값으로 수량을 바꾸고 1 아래로는 내려가지 않는다', async () => {
        const el = mount();
        const [minus, plus] = el.shadowRoot.querySelectorAll('.qty lightning-button');
        plus.click();
        plus.click();
        await flush();
        expect(el.shadowRoot.querySelector('.quantity').textContent).toBe('3');
        minus.click();
        minus.click();
        minus.click();
        await flush();
        expect(el.shadowRoot.querySelector('.quantity').textContent).toBe('1');
    });

    it('네이티브 input은 input 이벤트로 글자마다 반영한다', async () => {
        const el = mount();
        const memo = el.shadowRoot.querySelector('.memo');
        memo.value = '빨리';
        memo.dispatchEvent(new CustomEvent('input'));
        await flush();
        expect(el.shadowRoot.querySelector('.memo-length').textContent).toBe('메모 2자');
    });

    it('하나라도 검증에 실패하면 주문하지 않는다', async () => {
        const el = mount();
        const [name, email] = el.shadowRoot.querySelectorAll('lightning-input');
        name.reportValidity = jest.fn(() => false);
        email.reportValidity = jest.fn(() => true);
        el.shadowRoot.querySelector('.submit').click();
        await flush();
        expect(el.shadowRoot.querySelector('.result').textContent).toBe('입력값을 확인하세요');
        expect(email.reportValidity).toHaveBeenCalled();   // 실패 뒤에도 나머지 입력란 메시지를 표시
    });

    it('모두 통과하면 주문 문장을 만든다', async () => {
        const el = mount();
        typeInto(el, 'customer', '홍길동');
        el.shadowRoot.querySelectorAll('lightning-input').forEach((i) => {
            i.reportValidity = jest.fn(() => true);
        });
        el.shadowRoot.querySelector('.submit').click();
        await flush();
        expect(el.shadowRoot.querySelector('.result').textContent).toBe('홍길동님 1개 주문');
    });
});
