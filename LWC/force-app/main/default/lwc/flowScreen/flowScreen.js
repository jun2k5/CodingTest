import { LightningElement, api } from 'lwc';
import { FlowAttributeChangeEvent, FlowNavigationNextEvent } from 'lightning/flowSupport';

export default class FlowScreen extends LightningElement {
    @api maxDiscount = 30;
    _discount = 0;
    _reason = '';

    // Flow가 넣어 주는 값은 setter로 받고, 컴포넌트 안에서는 내부 필드를 바꾼다(@api 재대입 금지 규칙)
    @api
    get discount() {
        return this._discount;
    }
    set discount(value) {
        this._discount = value;
    }

    @api
    get reason() {
        return this._reason;
    }
    set reason(value) {
        this._reason = value;
    }
    @api availableActions = []; // Flow가 넣어 준다: 이 화면에서 가능한 이동(NEXT, BACK, FINISH 등)

    handleDiscount(event) {
        this._discount = Number(event.target.value);
        // Flow 변수에 값이 바뀌었다고 알린다(속성 이름, 새 값)
        this.dispatchEvent(new FlowAttributeChangeEvent('discount', this._discount));
    }

    handleReason(event) {
        this._reason = event.target.value;
        this.dispatchEvent(new FlowAttributeChangeEvent('reason', this._reason));
    }

    // Flow가 "다음"으로 넘어가기 전에 호출한다
    @api
    validate() {
        if (this.discount > this.maxDiscount) {
            return { isValid: false, errorMessage: `할인율은 ${this.maxDiscount}% 이하여야 한다` };
        }
        if (this.discount > 0 && !this.reason) {
            return { isValid: false, errorMessage: '할인 사유를 입력하세요' };
        }
        return { isValid: true };
    }

    get canGoNext() {
        return this.availableActions.includes('NEXT');
    }

    handleNext() {
        // 컴포넌트 안의 버튼으로 Flow를 다음 화면으로 넘긴다
        this.dispatchEvent(new FlowNavigationNextEvent());
    }
}
