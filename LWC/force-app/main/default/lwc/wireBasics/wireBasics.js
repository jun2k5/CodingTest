import { LightningElement, api, wire } from 'lwc';
import { getObjectInfo } from 'lightning/uiObjectInfoApi';
import { getRecord, getFieldValue } from 'lightning/uiRecordApi';
import ACCOUNT_OBJECT from '@salesforce/schema/Account';
import NAME_FIELD from '@salesforce/schema/Account.Name';

export default class WireBasics extends LightningElement {
    @api selectedId; // 처음에는 undefined

    // 1. 속성(property)에 wire: { data, error } 객체가 그대로 들어온다
    @wire(getObjectInfo, { objectApiName: ACCOUNT_OBJECT })
    objectInfo;

    // 2. 함수에 wire: 데이터를 받아 가공하거나 다른 필드에 나눠 담을 때
    account;
    error;

    @wire(getRecord, { recordId: '$selectedId', fields: [NAME_FIELD] })
    wiredAccount({ data, error }) {
        if (data) {
            this.account = data;
            this.error = undefined;
        } else if (error) {
            this.account = undefined;
            this.error = error;
        }
    }

    get objectLabel() {
        return this.objectInfo.data ? this.objectInfo.data.label : '불러오는 중';
    }

    get accountName() {
        return this.account ? getFieldValue(this.account, NAME_FIELD) : '선택 없음';
    }
}
