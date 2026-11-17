import { LightningElement } from 'lwc';
import { updateRecord } from 'lightning/uiRecordApi';
import loadAccounts from '@salesforce/apex/AccountTableController.loadAccounts';

const PAGE_SIZE = 2;

const COLUMNS = [
    { label: '거래처', fieldName: 'recordUrl', type: 'url', sortable: true,
      typeAttributes: { label: { fieldName: 'Name' }, target: '_self' } },
    { label: '매출', fieldName: 'AnnualRevenue', type: 'currency', sortable: true,
      typeAttributes: { currencyCode: 'KRW' } },
    { label: '등급', fieldName: 'Rating', type: 'text', editable: true }
];

export default class DataTable extends LightningElement {
    columns = COLUMNS;
    rows = [];
    draftValues = [];
    sortedBy;
    sortedDirection = 'asc';
    allLoaded = false;
    message = '';

    get notAllLoaded() {
        return !this.allLoaded;
    }

    connectedCallback() {
        this.loadMore();
    }

    // Apex 결과에 화면용 필드(recordUrl)를 더한다
    toRow(acc) {
        return { ...acc, recordUrl: `/lightning/r/Account/${acc.Id}/view` };
    }

    async loadMore(target) {
        if (target) {
            target.isLoading = true;
        }
        const page = await loadAccounts({ offsetSize: this.rows.length, pageSize: PAGE_SIZE });
        this.rows = [...this.rows, ...page.map((a) => this.toRow(a))];
        if (page.length < PAGE_SIZE) {
            this.allLoaded = true; // 더 없으면 무한 스크롤을 끈다
        }
        if (target) {
            target.isLoading = false;
        }
    }

    handleLoadMore(event) {
        this.loadMore(event.target);
    }

    handleSort(event) {
        const { fieldName, sortDirection } = event.detail;
        // url 열은 실제 값(Name) 기준으로 정렬한다
        const key = fieldName === 'recordUrl' ? 'Name' : fieldName;
        const dir = sortDirection === 'asc' ? 1 : -1;
        this.rows = [...this.rows].sort((a, b) => {
            const x = a[key] ?? '';
            const y = b[key] ?? '';
            return (x > y ? 1 : x < y ? -1 : 0) * dir;
        });
        this.sortedBy = fieldName;
        this.sortedDirection = sortDirection;
    }

    async handleSave(event) {
        const drafts = event.detail.draftValues; // [{ Id, Rating }, ...] 바뀐 셀만
        try {
            await Promise.all(drafts.map((fields) => updateRecord({ fields })));
            // 화면 데이터에 반영하고 편집 표시(draftValues)를 비운다
            const byId = new Map(drafts.map((d) => [d.Id, d]));
            this.rows = this.rows.map((r) => (byId.has(r.Id) ? { ...r, ...byId.get(r.Id) } : r));
            this.draftValues = [];
            this.message = `${drafts.length}건 저장`;
        } catch {
            this.message = '저장 실패';
        }
    }
}
