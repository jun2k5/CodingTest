import { LightningElement, api, wire } from 'lwc';
import { getRecord, getFieldValue, getFieldDisplayValue, updateRecord, createRecord } from 'lightning/uiRecordApi';
import NAME_FIELD from '@salesforce/schema/Account.Name';
import INDUSTRY_FIELD from '@salesforce/schema/Account.Industry';
import REVENUE_FIELD from '@salesforce/schema/Account.AnnualRevenue';
import OWNER_NAME_FIELD from '@salesforce/schema/Account.Owner.Name'; // 관계 필드
import ID_FIELD from '@salesforce/schema/Account.Id';
import CONTACT_OBJECT from '@salesforce/schema/Contact';
import CONTACT_LASTNAME from '@salesforce/schema/Contact.LastName';
import CONTACT_ACCOUNT from '@salesforce/schema/Contact.AccountId';

const FIELDS = [NAME_FIELD, INDUSTRY_FIELD, REVENUE_FIELD, OWNER_NAME_FIELD];

export default class RecordApi extends LightningElement {
    @api recordId;
    record;
    error;
    status = '';

    // '$recordId': recordId가 바뀌면 다시 요청하는 반응형 파라미터(13번 글)
    @wire(getRecord, { recordId: '$recordId', fields: FIELDS })
    wiredRecord({ data, error }) {
        if (data) {
            this.record = data;
            this.error = undefined;
        } else if (error) {
            this.record = undefined;
            this.error = error.body ? error.body.message : '알 수 없는 오류';
        }
    }

    get name() {
        return getFieldValue(this.record, NAME_FIELD);
    }
    get industry() {
        return getFieldValue(this.record, INDUSTRY_FIELD) || '(없음)';
    }
    get ownerName() {
        return getFieldValue(this.record, OWNER_NAME_FIELD);
    }
    get revenueDisplay() {
        // displayValue: 사용자 로캘·통화로 서식이 적용된 값
        return getFieldDisplayValue(this.record, REVENUE_FIELD);
    }

    async handleMarkTech() {
        const fields = { [ID_FIELD.fieldApiName]: this.recordId, [INDUSTRY_FIELD.fieldApiName]: 'Technology' };
        try {
            await updateRecord({ fields });
            this.status = '업종 변경 완료';
        } catch {
            this.status = '업종 변경 실패';
        }
    }

    async handleCreateContact() {
        const recordInput = {
            apiName: CONTACT_OBJECT.objectApiName,
            fields: {
                [CONTACT_LASTNAME.fieldApiName]: this.ownerName,
                [CONTACT_ACCOUNT.fieldApiName]: this.recordId
            }
        };
        const contact = await createRecord(recordInput);
        this.status = `연락처 생성: ${contact.id}`;
    }
}
