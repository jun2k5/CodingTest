import { LightningElement } from 'lwc';

export default class FormInput extends LightningElement {
    form = { customer: '', email: '', quantity: 1 };
    memo = '';
    result = '';

    // name 속성으로 어느 입력인지 구분해 핸들러 하나로 처리
    handleChange(event) {
        const { name, value } = event.target;
        this.form = { ...this.form, [name]: value };
    }

    handleQuantity(event) {
        // currentTarget: 핸들러를 단 요소, dataset: data-* 값(문자열)
        const delta = Number(event.currentTarget.dataset.delta);
        const quantity = Math.max(1, this.form.quantity + delta);
        this.form = { ...this.form, quantity };
    }

    handleMemo(event) {
        this.memo = event.target.value;
    }

    get memoLength() {
        return this.memo.length;
    }

    handleSubmit() {
        // 모든 lightning-input의 검증 메시지를 표시하고 결과를 모은다
        const allValid = [...this.template.querySelectorAll('lightning-input')].reduce(
            (valid, input) => input.reportValidity() && valid,
            true
        );
        this.result = allValid
            ? `${this.form.customer}님 ${this.form.quantity}개 주문`
            : '입력값을 확인하세요';
    }
}
