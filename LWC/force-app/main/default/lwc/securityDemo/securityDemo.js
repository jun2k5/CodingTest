import { LightningElement, api } from 'lwc';
import canEditAccounts from '@salesforce/customPermission/Edit_Accounts';

export default class SecurityDemo extends LightningElement {
    @api comment = ''; // 사용자가 입력한 값(신뢰할 수 없는 문자열)
    @api richComment = '';

    // 화면에서 버튼을 숨기는 용도일 뿐, 실제 권한 검사는 서버(Apex)가 한다
    get showEdit() {
        return !!canEditAccounts;
    }

    renderedCallback() {
        // 나쁜 예: 신뢰할 수 없는 문자열을 innerHTML로 넣으면 HTML로 해석된다
        const unsafe = this.template.querySelector('.unsafe');
        if (unsafe) {
            // eslint-disable-next-line @lwc/lwc/no-inner-html -- 위험한 예를 재현하려고 일부러 쓴다
            unsafe.innerHTML = this.comment;
        }
    }
}
