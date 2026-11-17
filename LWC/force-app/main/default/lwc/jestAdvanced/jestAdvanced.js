import { LightningElement, api, wire } from 'lwc';
import { getRecord, getFieldValue } from 'lightning/uiRecordApi';
import countOpenCases from '@salesforce/apex/CaseStatsController.countOpenCases';
import NAME_FIELD from '@salesforce/schema/Account.Name';
import TIER_FIELD from '@salesforce/schema/Account.Rating';

export default class JestAdvanced extends LightningElement {
    @api recordId;
    account;
    caseCount;
    loading = false;
    error;

    @wire(getRecord, { recordId: '$recordId', fields: [NAME_FIELD, TIER_FIELD] })
    wiredAccount({ data, error }) {
        this.account = data;
        this.error = error ? '거래처를 불러오지 못했다' : undefined;
    }

    get name() {
        return this.account ? getFieldValue(this.account, NAME_FIELD) : '';
    }

    // 등급과 미해결 케이스 수로 위험도를 계산한다
    get risk() {
        if (this.caseCount === undefined) {
            return '-';
        }
        const rating = this.account ? getFieldValue(this.account, TIER_FIELD) : null;
        if (this.caseCount >= 5) {
            return '높음';
        }
        if (this.caseCount >= 2 || rating === 'Cold') {
            return '보통';
        }
        return '낮음';
    }

    async handleCount() {
        this.loading = true;
        this.error = undefined;
        try {
            this.caseCount = await countOpenCases({ accountId: this.recordId });
        } catch {
            this.error = '케이스 수를 세지 못했다';
        } finally {
            this.loading = false;
        }
    }
}
