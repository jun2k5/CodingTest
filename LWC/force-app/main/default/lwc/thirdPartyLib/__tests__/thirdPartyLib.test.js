import { createElement } from '@lwc/engine-dom';
import ThirdPartyLib from 'c/thirdPartyLib';
import { loadScript } from 'lightning/platformResourceLoader';

const flushAll = () => new Promise((r) => setTimeout(r, 0));
const DATA = [
    { label: 'A', value: 10 },
    { label: 'B', value: 5 }
];

function mount() {
    const el = createElement('c-third-party-lib', { is: ThirdPartyLib });
    el.data = DATA;
    document.body.appendChild(el);
    return el;
}

describe('c-third-party-lib', () => {
    beforeAll(() => {
        // 정적 리소스 대신 테스트에서 실제 스크립트를 실행해 window.MiniBar를 만든다
        require('../../../staticresources/miniBar.js');
    });

    afterEach(() => {
        while (document.body.firstChild) {
            document.body.removeChild(document.body.firstChild);
        }
        jest.clearAllMocks();
    });

    it('정적 리소스 URL로 loadScript를 한 번만 호출한다', async () => {
        const el = mount();
        await flushAll();
        el.data = [...DATA]; // 다시 렌더링되어도
        await flushAll();
        expect(loadScript).toHaveBeenCalledTimes(1);
        expect(loadScript.mock.calls[0][1]).toBe('miniBar'); // Jest에서 resourceUrl import는 이름 문자열이 된다
    });

    it('로드가 끝나면 lwc:dom="manual" 영역에 라이브러리가 그린다', async () => {
        const el = mount();
        await flushAll();
        const bars = el.shadowRoot.querySelectorAll('.chart .mini-bar');
        expect([...bars].map((b) => b.style.width)).toEqual(['100%', '50%']);
        expect(el.shadowRoot.querySelector('.status').textContent).toBe('완료');
    });

    it('로드에 실패하면 이유를 보여 준다', async () => {
        loadScript.mockRejectedValueOnce(new Error('404'));
        const el = mount();
        await flushAll();
        expect(el.shadowRoot.querySelector('.status').textContent).toBe('라이브러리 로드 실패: 404');
    });
});
