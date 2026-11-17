import { createElement } from '@lwc/engine-dom';
import SecurityDemo from 'c/securityDemo';

// 사용자 정의 권한 import는 Jest에서 직접 값을 정한다
jest.mock('@salesforce/customPermission/Edit_Accounts', () => ({ default: true }), { virtual: true });

const ATTACK = '<img src=x onerror="window.__hacked = true">';

function mount(props) {
    const el = createElement('c-security-demo', { is: SecurityDemo });
    Object.assign(el, props);
    document.body.appendChild(el);
    return el;
}

describe('c-security-demo', () => {
    afterEach(() => {
        while (document.body.firstChild) {
            document.body.removeChild(document.body.firstChild);
        }
    });

    it('템플릿 바인딩은 HTML을 글자 그대로 보여 준다', () => {
        const el = mount({ comment: ATTACK });
        const safe = el.shadowRoot.querySelector('.safe');
        expect(safe.textContent).toBe(ATTACK);
        expect(safe.querySelector('img')).toBeNull();
    });

    it('innerHTML은 같은 문자열을 실제 요소로 만든다(위험)', () => {
        const el = mount({ comment: ATTACK });
        expect(el.shadowRoot.querySelector('.unsafe img')).not.toBeNull();
    });

    it('서식 있는 텍스트는 lightning-formatted-rich-text에 값으로 넘긴다', () => {
        const el = mount({ richComment: '<b>굵게</b>' });
        expect(el.shadowRoot.querySelector('.rich').value).toBe('<b>굵게</b>');
    });

    it('사용자 정의 권한이 있으면 수정 버튼을 보인다', () => {
        const el = mount({});
        expect(el.shadowRoot.querySelector('.edit')).not.toBeNull();
    });
});
