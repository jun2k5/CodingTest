import { createElement } from '@lwc/engine-dom';
import DataTable from 'c/dataTable';
import { updateRecord } from 'lightning/uiRecordApi';
import loadAccounts from '@salesforce/apex/AccountTableController.loadAccounts';

jest.mock('@salesforce/apex/AccountTableController.loadAccounts', () => ({ default: jest.fn() }), {
    virtual: true
});

const PAGE1 = [
    { Id: '001A', Name: '한빛상사', AnnualRevenue: 300, Rating: 'Warm' },
    { Id: '001B', Name: '가람물산', AnnualRevenue: 900, Rating: null }
];
const PAGE2 = [{ Id: '001C', Name: '나래전자', AnnualRevenue: 500, Rating: 'Cold' }];
const flushAll = () => new Promise((r) => setTimeout(r, 0));

async function mount() {
    // 호출 순서가 아니라 인자로 응답을 정한다: 테스트마다 남는 "Once" 응답이 다른 테스트로 새지 않는다
    loadAccounts.mockImplementation(({ offsetSize }) => Promise.resolve(offsetSize === 0 ? PAGE1 : PAGE2));
    const el = createElement('c-data-table', { is: DataTable });
    document.body.appendChild(el);
    await flushAll();
    return el;
}
const table = (el) => el.shadowRoot.querySelector('lightning-datatable');

describe('c-data-table', () => {
    afterEach(() => {
        while (document.body.firstChild) {
            document.body.removeChild(document.body.firstChild);
        }
        jest.clearAllMocks();
    });

    it('Apex 결과에 화면용 recordUrl을 더해 data로 넘긴다', async () => {
        const el = await mount();
        expect(table(el).data[0].recordUrl).toBe('/lightning/r/Account/001A/view');
        expect(table(el).keyField).toBe('Id');
    });

    it('sort 이벤트로 받은 필드·방향대로 복사본을 정렬한다', async () => {
        const el = await mount();
        table(el).dispatchEvent(
            new CustomEvent('sort', { detail: { fieldName: 'AnnualRevenue', sortDirection: 'desc' } })
        );
        await flushAll();
        expect(table(el).data.map((r) => r.Name)).toEqual(['가람물산', '한빛상사']);
        expect(table(el).sortedBy).toBe('AnnualRevenue');
        expect(table(el).sortedDirection).toBe('desc');
    });

    it('url 열은 Name 기준으로 정렬한다', async () => {
        const el = await mount();
        table(el).dispatchEvent(new CustomEvent('sort', { detail: { fieldName: 'recordUrl', sortDirection: 'asc' } }));
        await flushAll();
        expect(table(el).data.map((r) => r.Name)).toEqual(['가람물산', '한빛상사']);
    });

    it('save 이벤트의 draftValues로 바뀐 셀만 저장하고 편집 표시를 비운다', async () => {
        const el = await mount();
        table(el).draftValues = [{ Id: '001B', Rating: 'Hot' }];
        table(el).dispatchEvent(new CustomEvent('save', { detail: { draftValues: [{ Id: '001B', Rating: 'Hot' }] } }));
        await flushAll();
        expect(updateRecord).toHaveBeenCalledWith({ fields: { Id: '001B', Rating: 'Hot' } });
        expect(table(el).data.find((r) => r.Id === '001B').Rating).toBe('Hot');
        expect(table(el).draftValues).toEqual([]);
        expect(el.shadowRoot.querySelector('.message').textContent).toBe('1건 저장');
    });

    it('loadmore에서 다음 페이지를 붙이고, 마지막 페이지면 무한 스크롤을 끈다', async () => {
        const el = await mount();
        expect(table(el).enableInfiniteLoading).toBe(true);
        table(el).dispatchEvent(new CustomEvent('loadmore'));
        await flushAll();
        expect(loadAccounts).toHaveBeenLastCalledWith({ offsetSize: 2, pageSize: 2 });
        expect(table(el).data.map((r) => r.Id)).toEqual(['001A', '001B', '001C']);
        expect(table(el).enableInfiniteLoading).toBe(false);
        expect(table(el).isLoading).toBe(false);
    });
});
