import { createElement } from '@lwc/engine-dom';
import JestAdvanced from 'c/jestAdvanced';
import { getRecord } from 'lightning/uiRecordApi';
import countOpenCases from '@salesforce/apex/CaseStatsController.countOpenCases';

jest.mock('@salesforce/apex/CaseStatsController.countOpenCases', () => ({ default: jest.fn() }), {
    virtual: true
});

// 대기 중인 Promise와 렌더링을 모두 처리한다
const flushPromises = () => new Promise((resolve) => setTimeout(resolve, 0));

// 테스트가 원하는 시점에 끝낼 수 있는 Promise: 로딩 중 상태를 검사할 때 쓴다
function deferred() {
    let resolve;
    let reject;
    const promise = new Promise((res, rej) => {
        resolve = res;
        reject = rej;
    });
    return { promise, resolve, reject };
}

const account = (rating) => ({
    apiName: 'Account',
    id: '001A',
    fields: { Name: { value: '한빛상사', displayValue: null }, Rating: { value: rating, displayValue: null } }
});

function mount() {
    const el = createElement('c-jest-advanced', { is: JestAdvanced });
    el.recordId = '001A';
    document.body.appendChild(el);
    return el;
}
const $ = (el, sel) => el.shadowRoot.querySelector(sel);

describe('c-jest-advanced', () => {
    afterEach(() => {
        while (document.body.firstChild) {
            document.body.removeChild(document.body.firstChild);
        }
        jest.clearAllMocks(); // 호출 기록만 지운다
        // 내가 응답을 정한 모의만 초기화한다. jest.resetAllMocks()는 스텁의 getFieldValue 구현까지 지운다
        countOpenCases.mockReset();
    });

    describe('비동기 상태', () => {
        it('응답을 기다리는 동안 스피너를 보이고 버튼을 끈다', async () => {
            const pending = deferred();
            countOpenCases.mockReturnValue(pending.promise);
            const el = mount();
            $(el, '.count').click();
            await Promise.resolve();
            expect($(el, 'lightning-spinner')).not.toBeNull();
            expect($(el, '.count').disabled).toBe(true);

            pending.resolve(3); // 이제 응답이 온다
            await flushPromises();
            expect($(el, 'lightning-spinner')).toBeNull();
            expect($(el, '.cases').textContent).toBe('3');
        });

        it('Apex가 실패하면 오류를 보이고 로딩을 끝낸다', async () => {
            countOpenCases.mockRejectedValue({ body: { message: 'Insufficient access' } });
            const el = mount();
            $(el, '.count').click();
            await flushPromises();
            expect($(el, '.error').textContent).toBe('케이스 수를 세지 못했다');
            expect($(el, '.count').disabled).toBe(false);
        });

        it('wire 오류도 같은 오류 영역에 보인다', async () => {
            const el = mount();
            getRecord.error();
            await flushPromises();
            expect($(el, '.error').textContent).toBe('거래처를 불러오지 못했다');
        });
    });

    describe('wire 데이터와 Apex 결과의 조합', () => {
        it.each([
            ['Warm', 0, '낮음'],
            ['Cold', 0, '보통'],
            ['Warm', 2, '보통'],
            ['Hot', 5, '높음']
        ])('등급 %s, 케이스 %i건이면 위험도 %s', async (rating, cases, expected) => {
            countOpenCases.mockResolvedValue(cases);
            const el = mount();
            getRecord.emit(account(rating));
            await flushPromises();
            $(el, '.count').click();
            await flushPromises();
            expect($(el, '.risk').textContent).toBe(`위험도: ${expected}`);
        });

        it('Apex에 현재 recordId를 넘긴다', async () => {
            countOpenCases.mockResolvedValue(0);
            const el = mount();
            $(el, '.count').click();
            await flushPromises();
            expect(countOpenCases).toHaveBeenCalledWith({ accountId: '001A' });
        });
    });
});
