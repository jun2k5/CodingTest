import { createElement } from '@lwc/engine-dom';
import ApexCall from 'c/apexCall';
import getAccounts from '@salesforce/apex/AccountController.getAccounts';
import updateRating from '@salesforce/apex/AccountController.updateRating';

// @wire로 쓰는 Apex 메서드: 테스트용 wire adapter로 바꾼다
jest.mock(
    '@salesforce/apex/AccountController.getAccounts',
    () => {
        const { createApexTestWireAdapter } = require('@salesforce/sfdx-lwc-jest');
        return { default: createApexTestWireAdapter(jest.fn()) };
    },
    { virtual: true }
);

// 명령형으로 쓰는 Apex 메서드: 일반 jest.fn
jest.mock('@salesforce/apex/AccountController.updateRating', () => ({ default: jest.fn() }), {
    virtual: true
});

const ACCOUNTS = [
    { Id: '001A', Name: '한빛상사', Rating: 'Warm' },
    { Id: '001B', Name: '한빛물산', Rating: null }
];
const flush = () => Promise.resolve();

function mount() {
    const el = createElement('c-apex-call', { is: ApexCall });
    document.body.appendChild(el);
    return el;
}

describe('c-apex-call', () => {
    afterEach(() => {
        while (document.body.firstChild) {
            document.body.removeChild(document.body.firstChild);
        }
        jest.clearAllMocks();
        jest.useRealTimers();
    });

    it('입력이 멈춘 뒤 300ms가 지나야 wire 파라미터가 바뀐다', async () => {
        jest.useFakeTimers();
        const el = mount();
        const input = el.shadowRoot.querySelector('.keyword');
        ['한', '한빛'].forEach((v) => {
            input.value = v;
            input.dispatchEvent(new CustomEvent('change'));
        });
        jest.advanceTimersByTime(299);
        await flush();
        expect(getAccounts.getLastConfig()).toEqual({ keyword: '' });
        jest.advanceTimersByTime(1);
        await flush();
        expect(getAccounts.getLastConfig()).toEqual({ keyword: '한빛' });
    });

    it('wire 결과를 목록으로 그린다', async () => {
        const el = mount();
        getAccounts.emit(ACCOUNTS);
        await flush();
        const names = [...el.shadowRoot.querySelectorAll('.name')].map((n) => n.textContent);
        expect(names).toEqual(['한빛상사', '한빛물산']);
    });

    it('wire 오류는 error.body.message를 보여 준다', async () => {
        const el = mount();
        getAccounts.error({ message: '쿼리 권한 없음' });
        await flush();
        expect(el.shadowRoot.querySelector('.error').textContent).toBe('쿼리 권한 없음');
    });

    it('명령형 호출에 인자를 객체로 넘기고 결과를 받는다', async () => {
        updateRating.mockResolvedValue({ Id: '001B', Rating: 'Hot' });
        const el = mount();
        getAccounts.emit(ACCOUNTS);
        await flush();
        el.shadowRoot.querySelectorAll('.hot')[1].click();
        await new Promise((r) => setTimeout(r, 0));
        expect(updateRating).toHaveBeenCalledWith({ accountId: '001B', rating: 'Hot' });
        expect(el.shadowRoot.querySelector('.status').textContent).toBe('001B 등급 변경');
    });

    it('명령형 호출이 실패하면 서버 메시지를 보여 준다', async () => {
        updateRating.mockRejectedValue({ body: { message: '검증 규칙 위반' } });
        const el = mount();
        getAccounts.emit(ACCOUNTS);
        await flush();
        el.shadowRoot.querySelector('.hot').click();
        await new Promise((r) => setTimeout(r, 0));
        expect(el.shadowRoot.querySelector('.status').textContent).toBe('변경 실패: 검증 규칙 위반');
    });
});
