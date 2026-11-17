import { LightningElement, api, wire } from 'lwc';
import { refreshApex } from '@salesforce/apex';
import { notifyRecordUpdateAvailable } from 'lightning/uiRecordApi';
import { RefreshEvent } from 'lightning/refresh';
import getAccounts from '@salesforce/apex/AccountController.getAccounts';
import updateRating from '@salesforce/apex/AccountController.updateRating';

export default class DataRefresh extends LightningElement {
    @api keyword = '한빛';
    accounts = [];
    status = '';
    wiredAccountsResult; // refreshApex에 넘길 "wire가 넣어 준 값 전체"

    @wire(getAccounts, { keyword: '$keyword' })
    wiredAccounts(result) {
        this.wiredAccountsResult = result; // { data, error }를 쪼개기 전에 통째로 보관
        if (result.data) {
            this.accounts = result.data;
        }
    }

    async handleHot(event) {
        const accountId = event.currentTarget.dataset.id;
        await updateRating({ accountId, rating: 'Hot' });

        // 1. Apex wire 캐시 새로 고침: 이 컴포넌트의 목록을 다시 받는다
        await refreshApex(this.wiredAccountsResult);

        // 2. LDS 캐시에 "이 레코드가 바뀌었다"고 알림: getRecord·레코드 페이지가 새 값을 받는다
        await notifyRecordUpdateAvailable([{ recordId: accountId }]);

        // 3. 페이지의 표준 컴포넌트에도 새로 고침 요청
        this.dispatchEvent(new RefreshEvent());

        this.status = '새로 고침 완료';
    }
}
