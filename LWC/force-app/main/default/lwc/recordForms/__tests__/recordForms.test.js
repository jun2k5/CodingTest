import { createElement } from '@lwc/engine-dom';
import RecordForms from 'c/recordForms';

const flush = () => Promise.resolve();
const RECORD_ID = '001000000000001AAA';

function mount() {
    const el = createElement('c-record-forms', { is: RecordForms });
    el.recordId = RECORD_ID;
    document.body.appendChild(el);
    return el;
}

describe('c-record-forms', () => {
    afterEach(() => {
        while (document.body.firstChild) {
            document.body.removeChild(document.body.firstChild);
        }
    });

    it('스키마 import는 Jest에서 오브젝트·필드 이름을 가진 객체가 된다', () => {
        const el = mount();
        const form = el.shadowRoot.querySelector('.quick-form');
        expect(form.fields).toEqual([
            { objectApiName: 'Account', fieldApiName: 'Name' },
            { objectApiName: 'Account', fieldApiName: 'Industry' }
        ]);
    });

    it('recordId와 objectApiName을 세 폼에 그대로 넘긴다', () => {
        const el = mount();
        ['.quick-form', '.edit-form', '.view-form'].forEach((sel) => {
            const form = el.shadowRoot.querySelector(sel);
            expect(form.recordId).toBe(RECORD_ID);
            expect(form.objectApiName).toBe('Account');
        });
    });

    it('submit을 가로채 빈 설명을 채운 뒤 다시 제출한다', () => {
        const el = mount();
        const form = el.shadowRoot.querySelector('.edit-form');
        form.submit = jest.fn();
        const submitEvent = new CustomEvent('submit', {
            cancelable: true,
            detail: { fields: { Name: '한빛상사', Description: '' } }
        });
        form.dispatchEvent(submitEvent);
        expect(submitEvent.defaultPrevented).toBe(true);
        expect(form.submit).toHaveBeenCalledWith({ Name: '한빛상사', Description: '설명 없음' });
    });

    it('success와 error 이벤트로 결과를 표시한다', async () => {
        const el = mount();
        const form = el.shadowRoot.querySelector('.edit-form');
        form.dispatchEvent(new CustomEvent('success', { detail: { id: RECORD_ID } }));
        await flush();
        expect(el.shadowRoot.querySelector('.message').textContent).toBe(`저장 완료: ${RECORD_ID}`);
        form.dispatchEvent(new CustomEvent('error', { detail: { message: '필수 필드 누락' } }));
        await flush();
        expect(el.shadowRoot.querySelector('.message').textContent).toBe('저장 실패: 필수 필드 누락');
    });
});
