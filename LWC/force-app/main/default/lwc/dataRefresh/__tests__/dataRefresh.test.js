import { createElement } from '@lwc/engine-dom';
import DataRefresh from 'c/dataRefresh';
import { refreshApex } from '@salesforce/apex';
import { notifyRecordUpdateAvailable } from 'lightning/uiRecordApi';
import getAccounts from '@salesforce/apex/AccountController.getAccounts';
import updateRating from '@salesforce/apex/AccountController.updateRating';

jest.mock('@salesforce/apex', () => ({ refreshApex: jest.fn(() => Promise.resolve()) }), { virtual: true });
jest.mock(
    '@salesforce/apex/AccountController.getAccounts',
    () => {
        const { createApexTestWireAdapter } = require('@salesforce/sfdx-lwc-jest');
        return { default: createApexTestWireAdapter(jest.fn()) };
    },
    { virtual: true }
);
jest.mock('@salesforce/apex/AccountController.updateRating', () => ({ default: jest.fn() }), {
    virtual: true
});

const ACCOUNTS = [{ Id: '001A', Name: '한빛상사', Rating: 'Warm' }];
const flushAll = () => new Promise((r) => setTimeout(r, 0));

describe('c-data-refresh', () => {
    afterEach(() => {
        while (document.body.firstChild) {
            document.body.removeChild(document.body.firstChild);
        }
        jest.clearAllMocks();
    });

    async function mountWithData() {
        const el = createElement('c-data-refresh', { is: DataRefresh });
        document.body.appendChild(el);
        getAccounts.emit(ACCOUNTS);
        await flushAll();
        return el;
    }

    it('저장 후 refreshApex에 wire가 넣어 준 값 전체를 넘긴다', async () => {
        updateRating.mockResolvedValue({ Id: '001A', Rating: 'Hot' });
        const el = await mountWithData();
        el.shadowRoot.querySelector('.hot').click();
        await flushAll();
        expect(refreshApex).toHaveBeenCalledTimes(1);
        expect(refreshApex.mock.calls[0][0].data).toEqual(ACCOUNTS);
    });

    it('LDS 캐시에 바뀐 레코드 Id를 알린다', async () => {
        updateRating.mockResolvedValue({ Id: '001A', Rating: 'Hot' });
        const el = await mountWithData();
        el.shadowRoot.querySelector('.hot').click();
        await flushAll();
        expect(notifyRecordUpdateAvailable).toHaveBeenCalledWith([{ recordId: '001A' }]);
    });

    it('RefreshEvent(lightning__refresh)를 페이지로 보낸다', async () => {
        updateRating.mockResolvedValue({ Id: '001A', Rating: 'Hot' });
        const el = await mountWithData();
        const onRefresh = jest.fn();
        document.body.addEventListener('lightning__refresh', onRefresh);
        el.shadowRoot.querySelector('.hot').click();
        await flushAll();
        document.body.removeEventListener('lightning__refresh', onRefresh);
        expect(onRefresh).toHaveBeenCalledTimes(1);
        expect(el.shadowRoot.querySelector('.status').textContent).toBe('새로 고침 완료');
    });

    it('새 데이터가 오면 목록이 바뀐다', async () => {
        const el = await mountWithData();
        getAccounts.emit([{ Id: '001A', Name: '한빛상사', Rating: 'Hot' }]);
        await flushAll();
        expect(el.shadowRoot.querySelector('.rating').textContent).toBe('Hot');
    });
});
