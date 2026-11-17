import { createElement } from '@lwc/engine-dom';
import BuilderConfig from 'c/builderConfig';

function mount(props = {}) {
    const el = createElement('c-builder-config', { is: BuilderConfig });
    Object.assign(el, props);
    document.body.appendChild(el);
    return el;
}

describe('c-builder-config', () => {
    afterEach(() => {
        while (document.body.firstChild) {
            document.body.removeChild(document.body.firstChild);
        }
    });

    it('App Builder에서 넣은 값이 @api 속성으로 들어온다', () => {
        const el = mount({ cardTitle: '활동 3건', maxItems: 3, density: 'compact' });
        expect(el.shadowRoot.querySelector('lightning-card').title).toBe('활동 3건');
        expect(el.shadowRoot.querySelectorAll('li').length).toBe(3);
        expect(el.shadowRoot.querySelector('ul').className).toBe('list compact');
    });

    it('레코드 페이지에서는 recordId와 objectApiName이 자동으로 들어온다', () => {
        const el = mount({ recordId: '001A', objectApiName: 'Account' });
        expect(el.shadowRoot.querySelector('.context').textContent).toBe('Account 001A');
    });

    it('앱 페이지처럼 recordId가 없으면 그 상황을 처리한다', () => {
        const el = mount();
        expect(el.shadowRoot.querySelector('.context').textContent).toBe('레코드 페이지 아님');
    });

    it('범위를 벗어난 값이나 문자열 숫자도 안전하게 처리한다', () => {
        expect(mount({ maxItems: '2' }).shadowRoot.querySelectorAll('li').length).toBe(2);
        expect(mount({ maxItems: 99 }).shadowRoot.querySelectorAll('li').length).toBe(6);
    });

    it('Boolean 속성은 기본 false라 아이콘이 없다가 켜면 보인다', () => {
        expect(mount().shadowRoot.querySelector('.icon')).toBeNull();
        expect(mount({ showIcons: true }).shadowRoot.querySelector('.icon')).not.toBeNull();
    });
});
