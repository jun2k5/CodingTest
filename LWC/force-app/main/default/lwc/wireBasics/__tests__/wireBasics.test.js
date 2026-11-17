import { createElement } from '@lwc/engine-dom';
import WireBasics from 'c/wireBasics';
import { getObjectInfo } from 'lightning/uiObjectInfoApi';
import { getRecord } from 'lightning/uiRecordApi';

const flush = () => Promise.resolve();

const record = (id, name) => ({
    apiName: 'Account',
    id,
    fields: { Name: { value: name, displayValue: null } }
});

function mount() {
    const el = createElement('c-wire-basics', { is: WireBasics });
    document.body.appendChild(el);
    return el;
}
const text = (el, sel) => el.shadowRoot.querySelector(sel).textContent;

describe('c-wire-basics', () => {
    afterEach(() => {
        while (document.body.firstChild) {
            document.body.removeChild(document.body.firstChild);
        }
    });

    it('속성 wire: 데이터가 오기 전에는 data가 비어 있다', () => {
        const el = mount();
        expect(text(el, '.object-label')).toBe('불러오는 중');
    });

    it('속성 wire: emit하면 objectInfo.data로 들어온다', async () => {
        const el = mount();
        getObjectInfo.emit({ apiName: 'Account', label: '거래처' });
        await flush();
        expect(text(el, '.object-label')).toBe('거래처');
    });

    it('반응형 파라미터가 undefined여도 설정은 어댑터로 전달된다', async () => {
        mount();
        await flush();
        expect(getRecord.getLastConfig()).toEqual({
            recordId: undefined,
            fields: [{ objectApiName: 'Account', fieldApiName: 'Name' }]
        });
    });

    it('반응형 파라미터가 바뀔 때마다 새 설정으로 다시 요청한다', async () => {
        const el = mount();
        el.selectedId = '001A';
        await flush();
        expect(getRecord.getLastConfig().recordId).toBe('001A');
        el.selectedId = '001B';
        await flush();
        expect(getRecord.getLastConfig().recordId).toBe('001B');
    });

    it('함수 wire: 받은 데이터를 가공해 필드에 담는다', async () => {
        const el = mount();
        el.selectedId = '001A';
        await flush();
        getRecord.emit(record('001A', '한빛상사'));
        await flush();
        expect(text(el, '.account-name')).toBe('한빛상사');
    });
});
