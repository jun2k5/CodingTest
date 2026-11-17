import { LightningElement, api } from 'lwc';
import NAME_FIELD from '@salesforce/schema/Account.Name';
import INDUSTRY_FIELD from '@salesforce/schema/Account.Industry';
import DESCRIPTION_FIELD from '@salesforce/schema/Account.Description';

export default class RecordForms extends LightningElement {
    @api recordId;                    // 레코드 페이지에 올리면 자동으로 들어온다
    @api objectApiName = 'Account';

    // 필드는 문자열 대신 스키마 import로 참조한다 (필드 삭제·이름 변경을 배포 시점에 잡는다)
    quickFields = [NAME_FIELD, INDUSTRY_FIELD];
    nameField = NAME_FIELD;
    industryField = INDUSTRY_FIELD;
    descriptionField = DESCRIPTION_FIELD;
    message = '';

    // 저장 직전에 값을 고친다: 기본 제출을 막고 고친 값으로 다시 제출
    handleSubmit(event) {
        event.preventDefault();
        const fields = { ...event.detail.fields };
        if (!fields.Description) {
            fields.Description = '설명 없음';
        }
        this.template.querySelector('lightning-record-edit-form').submit(fields);
    }

    handleSuccess(event) {
        this.message = `저장 완료: ${event.detail.id}`;
    }

    handleError(event) {
        this.message = `저장 실패: ${event.detail.message}`;
    }
}
