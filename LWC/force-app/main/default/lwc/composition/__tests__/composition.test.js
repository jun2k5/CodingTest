import { createElement } from '@lwc/engine-dom';
import Composition from 'c/composition';

const flushAll = () => new Promise((r) => setTimeout(r, 0));

function mount(props = {}) {
    const el = createElement('c-composition', { is: Composition });
    Object.assign(el, props);
    document.body.appendChild(el);
    return el;
}

describe('c-composition', () => {
    afterEach(() => {
        while (document.body.firstChild) {
            document.body.removeChild(document.body.firstChild);
        }
    });

    it('이름 있는 slot과 기본 slot에 내용이 배치된다', () => {
        const el = mount();
        const panel = el.shadowRoot.querySelector('c-panel-frame');
        const slots = panel.shadowRoot.querySelectorAll('slot');
        const byName = Object.fromEntries([...slots].map((s) => [s.name || 'default', s.assignedElements()]));
        expect(byName.title.map((n) => n.className)).toEqual(['custom-title']);
        expect(byName.default.map((n) => n.textContent)).toEqual(['본문 1', '본문 2']);
        expect(byName.footer.length).toBe(1);
    });

    it('slot에 넣은 요소는 부모(composition)의 Shadow DOM에 속한다', () => {
        const el = mount();
        // 부모 템플릿에서 찾을 수 있다
        expect(el.shadowRoot.querySelectorAll('.content').length).toBe(2);
        // 틀 컴포넌트의 shadowRoot 안에서는 찾을 수 없다
        const panel = el.shadowRoot.querySelector('c-panel-frame');
        expect(panel.shadowRoot.querySelector('.content')).toBeNull();
    });

    it('slotchange 이벤트로 들어온 요소 수를 알 수 있다', async () => {
        const el = mount();
        await flushAll();
        expect(el.shadowRoot.querySelector('c-panel-frame').slottedCount).toBe(2);
    });

    it('Light DOM 컴포넌트는 shadowRoot가 없고 안의 요소가 바깥에서 보인다', () => {
        const el = mount();
        const light = el.shadowRoot.querySelector('c-light-card');
        expect(light.shadowRoot).toBeNull();
        expect(el.shadowRoot.querySelector('.light-text').textContent).toBe('가벼운 카드');
    });

    it('lwc:is로 실행 중에 불러온 컴포넌트를 그린다', async () => {
        const el = mount({ widget: 'chart' });
        await flushAll();
        // 동적 컴포넌트의 태그 이름에 기대지 않고, 감싼 영역의 첫 자식으로 찾는다
        const area = () => el.shadowRoot.querySelector('.dynamic-area');
        expect(area().firstElementChild.shadowRoot.querySelector('.widget').textContent).toBe('차트 위젯');

        el.widget = 'table';
        await flushAll();
        expect(area().children.length).toBe(1);
        expect(area().firstElementChild.shadowRoot.querySelector('.widget').textContent).toBe('표 위젯');

        el.widget = 'none';
        await flushAll();
        expect(area().children.length).toBe(0);
    });
});
