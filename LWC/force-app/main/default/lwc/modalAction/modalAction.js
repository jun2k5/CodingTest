import { LightningElement, api } from 'lwc';
import { CloseActionScreenEvent } from 'lightning/actions';
import ConfirmModal from 'c/confirmModal';

// 레코드 페이지의 퀵 액션(화면 있는 액션)으로 쓰는 컴포넌트
export default class ModalAction extends LightningElement {
    @api recordId; // 퀵 액션도 레코드 Id를 받는다
    result = '';

    async handleDelete() {
        // 모달을 열고, 사용자가 닫을 때까지 기다린다
        const answer = await ConfirmModal.open({
            size: 'small',
            description: '레코드 삭제 확인 창', // 화면 읽기 도구용 설명
            content: `${this.recordId} 레코드를 삭제할까?`
        });
        // X 버튼이나 Esc로 닫으면 undefined가 온다
        this.result = answer === 'ok' ? '삭제 진행' : '취소됨';
    }

    handleClose() {
        // 퀵 액션 창 닫기
        this.dispatchEvent(new CloseActionScreenEvent());
    }
}
