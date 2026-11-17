import { createElement } from '@lwc/engine-dom';
import ModalAction from 'c/modalAction';
import ConfirmModal from 'c/confirmModal';
import { mockClose } from 'lightning/modal';

// sfdx-lwc-jest에는 lightning/modal, lightning/actions 스텁이 없어 직접 만든다
jest.mock(
    'lightning/modal',
    () => {
        const { LightningElement } = require('lwc');
        const mockClose = jest.fn(); // close() 호출을 기록(컴포넌트 prototype은 바꿀 수 없다)
        class LightningModal extends LightningElement {
            close(result) {
                mockClose(result);
            }
        }
        LightningModal.open = jest.fn();
        return { __esModule: true, default: LightningModal, mockClose };
    },
    { virtual: true }
);
jest.mock(
    'lightning/actions',
    () => ({
        CloseActionScreenEvent: class extends CustomEvent {
            constructor() {
                super('close');
            }
        }
    }),
    { virtual: true }
);

const flushAll = () => new Promise((r) => setTimeout(r, 0));

function mount() {
    const el = createElement('c-modal-action', { is: ModalAction });
    el.recordId = '001A';
    document.body.appendChild(el);
    return el;
}

describe('c-modal-action', () => {
    afterEach(() => {
        while (document.body.firstChild) {
            document.body.removeChild(document.body.firstChild);
        }
        jest.clearAllMocks();
    });

    it('open()에 크기·설명·@api 값을 넘긴다', async () => {
        ConfirmModal.open.mockResolvedValue('ok');
        const el = mount();
        el.shadowRoot.querySelector('.delete').click();
        await flushAll();
        expect(ConfirmModal.open).toHaveBeenCalledWith({
            size: 'small',
            description: '레코드 삭제 확인 창',
            content: '001A 레코드를 삭제할까?'
        });
        expect(el.shadowRoot.querySelector('.result').textContent).toBe('삭제 진행');
    });

    it('X나 Esc로 닫으면(undefined) 취소로 처리한다', async () => {
        ConfirmModal.open.mockResolvedValue(undefined);
        const el = mount();
        el.shadowRoot.querySelector('.delete').click();
        await flushAll();
        expect(el.shadowRoot.querySelector('.result').textContent).toBe('취소됨');
    });

    it('닫기 버튼은 CloseActionScreenEvent를 보낸다', () => {
        const el = mount();
        const onClose = jest.fn();
        el.addEventListener('close', onClose);
        el.shadowRoot.querySelector('.close').click();
        expect(onClose).toHaveBeenCalledTimes(1);
    });
});

describe('c-confirm-modal', () => {
    afterEach(() => {
        while (document.body.firstChild) {
            document.body.removeChild(document.body.firstChild);
        }
    });

    it('버튼에 따라 close()에 다른 값을 넘긴다', () => {
        const modal = createElement('c-confirm-modal', { is: ConfirmModal });
        modal.content = '삭제할까?';
        document.body.appendChild(modal);
        expect(modal.shadowRoot.querySelector('.content').textContent).toBe('삭제할까?');
        modal.shadowRoot.querySelector('.ok').click();
        modal.shadowRoot.querySelector('.cancel').click();
        expect(mockClose.mock.calls.map((c) => c[0])).toEqual(['ok', 'cancel']);
    });
});
