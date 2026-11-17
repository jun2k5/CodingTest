import { createElement } from '@lwc/engine-dom';
import ErrorToast from 'c/errorToast';
import { updateRecord } from 'lightning/uiRecordApi';

const flushAll = () => new Promise((r) => setTimeout(r, 0));

function mount() {
    const el = createElement('c-error-toast', { is: ErrorToast });
    el.recordId = '001A';
    document.body.appendChild(el);
    return el;
}

describe('c-error-toast', () => {
    afterEach(() => {
        while (document.body.firstChild) {
            document.body.removeChild(document.body.firstChild);
        }
        jest.clearAllMocks();
    });

    it('성공하면 success 토스트를 보낸다', async () => {
        const el = mount();
        const onToast = jest.fn();
        el.addEventListener('lightning__showtoast', onToast); // ShowToastEvent의 이벤트 이름
        el.shadowRoot.querySelector('.save').click();
        await flushAll();
        expect(onToast).toHaveBeenCalledTimes(1);
        expect(onToast.mock.calls[0][0].detail).toEqual({
            title: '저장 완료',
            message: '등급을 Hot으로 바꿨다',
            variant: 'success',
            mode: 'dismissible'
        });
    });

    it('UI API 저장 오류를 풀어 목록과 sticky 오류 토스트로 보여 준다', async () => {
        updateRecord.mockRejectedValueOnce({
            body: {
                message: 'An error occurred while trying to update the record.',
                output: { errors: [], fieldErrors: { Rating: [{ message: '이 값으로 바꿀 권한이 없다' }] } }
            }
        });
        const el = mount();
        const onToast = jest.fn();
        el.addEventListener('lightning__showtoast', onToast);
        el.shadowRoot.querySelector('.save').click();
        await flushAll();
        expect(el.shadowRoot.querySelector('.errors li').textContent).toBe('이 값으로 바꿀 권한이 없다');
        expect(onToast.mock.calls[0][0].detail.variant).toBe('error');
        expect(onToast.mock.calls[0][0].detail.mode).toBe('sticky');
    });

    it('실패해도 finally에서 버튼을 다시 켠다', async () => {
        updateRecord.mockRejectedValueOnce(new Error('네트워크 오류'));
        const el = mount();
        el.shadowRoot.querySelector('.save').click();
        await flushAll();
        expect(el.shadowRoot.querySelector('.save').disabled).toBe(false);
    });
});
