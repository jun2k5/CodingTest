import { LightningElement, api } from 'lwc';

export default class Styling extends LightningElement {
    @api title = '스타일 예제';
    @api hasError = false;

    // 조건에 따른 클래스는 getter로 만든다
    get statusClass() {
        return this.hasError ? 'status status-error' : 'status status-ok';
    }

    get statusLabel() {
        return this.hasError ? '오류' : '정상';
    }
}
