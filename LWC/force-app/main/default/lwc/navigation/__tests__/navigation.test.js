import { createElement } from '@lwc/engine-dom';
import Navigation from 'c/navigation';
import { CurrentPageReference, mockNavigate, mockGenerateUrl } from 'lightning/navigation';
import { encodeDefaultFieldValues } from 'lightning/pageReferenceUtils';

// 기본 스텁은 Navigate가 아무것도 하지 않으므로, 넘긴 PageReference를 기록하는 모의로 바꾼다
jest.mock('lightning/navigation', () => {
    const { createTestWireAdapter } = require('@salesforce/wire-service-jest-util');
    const Navigate = Symbol('Navigate');
    const GenerateUrl = Symbol('GenerateUrl');
    const mockNavigate = jest.fn();
    const mockGenerateUrl = jest.fn(() => Promise.resolve('/lightning/r/Account/001A/view'));
    const NavigationMixin = (Base) =>
        class extends Base {
            [Navigate](pageRef, replace) {
                mockNavigate(pageRef, replace);
            }
            [GenerateUrl](pageRef) {
                return mockGenerateUrl(pageRef);
            }
        };
    NavigationMixin.Navigate = Navigate;
    NavigationMixin.GenerateUrl = GenerateUrl;
    return {
        NavigationMixin,
        CurrentPageReference: createTestWireAdapter(jest.fn()),
        mockNavigate,
        mockGenerateUrl
    };
});

const flushAll = () => new Promise((r) => setTimeout(r, 0));

async function mount() {
    const el = createElement('c-navigation', { is: Navigation });
    document.body.appendChild(el);
    await flushAll();
    return el;
}

describe('c-navigation', () => {
    afterEach(() => {
        while (document.body.firstChild) {
            document.body.removeChild(document.body.firstChild);
        }
        jest.clearAllMocks();
    });

    it('GenerateUrl로 만든 URL을 링크 href에 넣는다', async () => {
        const el = await mount();
        expect(mockGenerateUrl).toHaveBeenCalledWith({
            type: 'standard__recordPage',
            attributes: { recordId: '001A', objectApiName: 'Account', actionName: 'view' }
        });
        expect(el.shadowRoot.querySelector('.record-link').getAttribute('href')).toBe('/lightning/r/Account/001A/view');
    });

    it('링크 클릭은 기본 이동을 막고 레코드 페이지로 Navigate한다', async () => {
        const el = await mount();
        const click = new CustomEvent('click', { cancelable: true });
        el.shadowRoot.querySelector('.record-link').dispatchEvent(click);
        expect(click.defaultPrevented).toBe(true);
        expect(mockNavigate.mock.calls[0][0].type).toBe('standard__recordPage');
    });

    it('새 레코드 페이지에 인코딩한 기본값을 state로 넘긴다', async () => {
        encodeDefaultFieldValues.mockReturnValue('Rating=Hot,Name=...');
        const el = await mount();
        el.shadowRoot.querySelector('.new').click();
        expect(encodeDefaultFieldValues).toHaveBeenCalledWith({ Rating: 'Hot', Name: '새 거래처' });
        expect(mockNavigate).toHaveBeenCalledWith(
            {
                type: 'standard__objectPage',
                attributes: { objectApiName: 'Account', actionName: 'new' },
                state: { defaultFieldValues: 'Rating=Hot,Name=...' }
            },
            undefined
        );
    });

    it('목록 뷰와 외부 URL도 PageReference 하나로 표현한다', async () => {
        const el = await mount();
        el.shadowRoot.querySelector('.list').click();
        el.shadowRoot.querySelector('.external').click();
        expect(mockNavigate.mock.calls.map((c) => c[0].type)).toEqual(['standard__objectPage', 'standard__webPage']);
        expect(mockNavigate.mock.calls[0][0].state).toEqual({ filterName: 'Recent' });
    });

    it('CurrentPageReference의 c__ 상태 값을 읽는다', async () => {
        const el = await mount();
        CurrentPageReference.emit({ type: 'standard__navItemPage', attributes: {}, state: { c__tab: 'orders' } });
        await flushAll();
        expect(el.shadowRoot.querySelector('.tab').textContent).toBe('탭: orders');
    });
});
