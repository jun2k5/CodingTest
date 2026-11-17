import { LightningElement, wire } from 'lwc';
import getAccounts from '@salesforce/apex/AccountController.getAccounts';
import updateRating from '@salesforce/apex/AccountController.updateRating';

const DELAY = 300;

export default class ApexCall extends LightningElement {
    keyword = '';
    accounts = [];
    error;
    status = '';
    _timer;

    // 1. @wire: keyword가 바뀔 때마다 자동 호출 (cacheable=true 메서드만 가능)
    @wire(getAccounts, { keyword: '$keyword' })
    wiredAccounts({ data, error }) {
        if (data) {
            this.accounts = data;
            this.error = undefined;
        } else if (error) {
            this.accounts = [];
            this.error = error.body ? error.body.message : '오류';
        }
    }

    // 글자마다 서버를 부르지 않도록 입력이 멈춘 뒤 300ms 후에 keyword를 바꾼다(디바운스)
    handleKeyword(event) {
        const value = event.target.value;
        clearTimeout(this._timer);
        // eslint-disable-next-line @lwc/lwc/no-async-operation
        this._timer = setTimeout(() => {
            this.keyword = value;
        }, DELAY);
    }

    get hasAccounts() {
        return this.accounts.length > 0;
    }

    // 2. 명령형 호출: 사용자 동작에 맞춰 직접 호출하고 Promise를 받는다
    async handleHot(event) {
        const accountId = event.currentTarget.dataset.id;
        try {
            const updated = await updateRating({ accountId, rating: 'Hot' });
            this.status = `${updated.Id} 등급 변경`;
        } catch (e) {
            this.status = `변경 실패: ${e.body ? e.body.message : e.message}`;
        }
    }
}
