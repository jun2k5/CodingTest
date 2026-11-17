import { LightningElement, api } from 'lwc';
import { ShowToastEvent } from 'lightning/platformShowToastEvent';
import { updateRecord } from 'lightning/uiRecordApi';
import { reduceErrors } from 'c/errorUtils';

export default class ErrorToast extends LightningElement {
    @api recordId;
    errorMessages = [];
    saving = false;

    get hasErrors() {
        return this.errorMessages.length > 0;
    }

    async handleSave() {
        this.saving = true;
        this.errorMessages = [];
        try {
            await updateRecord({ fields: { Id: this.recordId, Rating: 'Hot' } });
            this.toast('저장 완료', '등급을 Hot으로 바꿨다', 'success');
        } catch (error) {
            this.errorMessages = reduceErrors(error);
            // 오류 토스트는 사용자가 닫을 때까지 남긴다(sticky)
            this.toast('저장 실패', this.errorMessages.join(', '), 'error', 'sticky');
        } finally {
            this.saving = false; // 성공·실패와 무관하게 버튼을 다시 켠다
        }
    }

    toast(title, message, variant, mode = 'dismissible') {
        this.dispatchEvent(new ShowToastEvent({ title, message, variant, mode }));
    }
}
