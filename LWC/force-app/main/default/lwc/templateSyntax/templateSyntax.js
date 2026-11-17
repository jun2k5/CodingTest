import { LightningElement, api } from 'lwc';

export default class TemplateSyntax extends LightningElement {
    @api userName = '김';
    @api isLoading = false;
    @api products = [];

    // 템플릿에는 식을 쓸 수 없으므로 계산은 getter로 한다
    get greeting() {
        return `${this.userName}님, 안녕하세요`;
    }

    get itemCount() {
        return this.products.length;
    }

    get isEmpty() {
        return this.products.length === 0;
    }

    // 표시용 값(클래스 이름 등)은 JS에서 미리 만들어 둔다
    get items() {
        return this.products.map((p) => ({
            ...p,
            cssClass: p.soldOut ? 'item sold-out' : 'item'
        }));
    }
}
