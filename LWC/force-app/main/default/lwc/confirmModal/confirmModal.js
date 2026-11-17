import { api } from 'lwc';
import LightningModal from 'lightning/modal';

// LightningModal을 상속한 컴포넌트가 곧 모달이다
export default class ConfirmModal extends LightningModal {
    @api content; // open()에 넘긴 값이 @api 속성으로 들어온다

    handleOk() {
        this.close('ok'); // open()이 돌려준 Promise가 이 값으로 끝난다
    }

    handleCancel() {
        this.close('cancel');
    }
}
