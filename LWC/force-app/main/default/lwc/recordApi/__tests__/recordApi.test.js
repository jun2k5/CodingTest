import { createElement } from '@lwc/engine-dom';
import RecordApi from 'c/recordApi';
import { getRecord, updateRecord, createRecord } from 'lightning/uiRecordApi';

const mockRecord = require('./data/getRecord.json');
const flush = () => Promise.resolve();
// Promise 처리와 렌더링이 모두 끝날 때까지 기다린다(매크로태스크 한 번)
const flushAll = () => new Promise((resolve) => setTimeout(resolve, 0));
const RECORD_ID = '001000000000001AAA';

function mount() {
    const el = createElement('c-record-api', { is: RecordApi });
    el.recordId = RECORD_ID;
    document.body.appendChild(el);
    return el;
}
const text = (el, sel) => el.shadowRoot.querySelector(sel).textContent;

describe('c-record-api', () => {
    afterEach(() => {
        while (document.body.firstChild) {
            document.body.removeChild(document.body.firstChild);
        }
        jest.clearAllMocks();
    });

    it('wire 파라미터로 recordId와 필드 목록을 넘긴다', async () => {
        mount();
        await flush();   // 반응형 파라미터는 연결 뒤 비동기로 어댑터에 전달된다
        expect(getRecord.getLastConfig()).toEqual({
            recordId: RECORD_ID,
            fields: [
                { objectApiName: 'Account', fieldApiName: 'Name' },
                { objectApiName: 'Account', fieldApiName: 'Industry' },
                { objectApiName: 'Account', fieldApiName: 'AnnualRevenue' },
                { objectApiName: 'Account', fieldApiName: 'Owner.Name' }
            ]
        });
    });

    it('getFieldValue로 일반·관계 필드를, getFieldDisplayValue로 서식 값을 읽는다', async () => {
        const el = mount();
        getRecord.emit(mockRecord);
        await flush();
        expect(text(el, '.name')).toBe('한빛상사');
        expect(text(el, '.industry')).toBe('(없음)');
        expect(text(el, '.owner')).toBe('담당: 김담당');
        expect(text(el, '.revenue')).toBe('매출: KRW 1,500,000');
    });

    it('wire 오류를 받으면 메시지를 보여 준다', async () => {
        const el = mount();
        getRecord.error({ message: '레코드에 접근할 수 없다' });
        await flush();
        expect(text(el, '.error')).toBe('레코드에 접근할 수 없다');
    });

    it('updateRecord에는 Id와 바꿀 필드만 넘긴다', async () => {
        const el = mount();
        getRecord.emit(mockRecord);
        await flush();
        el.shadowRoot.querySelector('.update').click();
        await flushAll();
        expect(updateRecord).toHaveBeenCalledWith({ fields: { Id: RECORD_ID, Industry: 'Technology' } });
        expect(text(el, '.status')).toBe('업종 변경 완료');
    });

    it('updateRecord가 실패하면 실패를 표시한다', async () => {
        updateRecord.mockRejectedValueOnce(new Error('권한 없음'));
        const el = mount();
        getRecord.emit(mockRecord);
        await flush();
        el.shadowRoot.querySelector('.update').click();
        await flushAll();
        expect(text(el, '.status')).toBe('업종 변경 실패');
    });

    it('createRecord에는 apiName과 fields를 넘기고 새 Id를 받는다', async () => {
        createRecord.mockResolvedValueOnce({ id: '003000000000009AAA' });
        const el = mount();
        getRecord.emit(mockRecord);
        await flush();
        el.shadowRoot.querySelector('.create').click();
        await flushAll();
        expect(createRecord).toHaveBeenCalledWith({
            apiName: 'Contact',
            fields: { LastName: '김담당', AccountId: RECORD_ID }
        });
        expect(text(el, '.status')).toBe('연락처 생성: 003000000000009AAA');
    });
});
