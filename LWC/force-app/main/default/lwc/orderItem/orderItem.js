import { LightningElement, api } from 'lwc';

export default class OrderItem extends LightningElement {
    @api item;               // 부모가 넘겨준 데이터(읽기 전용)
    highlighted = false;

    // 부모가 호출할 수 있는 공개 메서드
    @api highlight() {
        this.highlighted = true;
    }

    get rowClass() {
        return this.highlighted ? 'row highlighted' : 'row';
    }

    handleSelect() {
        // 기본값: bubbles false, composed false → 이 요소를 직접 듣는 부모만 받는다
        this.dispatchEvent(new CustomEvent('select', { detail: { id: this.item.id } }));
    }

    handleRemove() {
        // bubbles + composed: 부모의 Shadow DOM 경계를 넘어 더 바깥까지 전파
        this.dispatchEvent(
            new CustomEvent('itemremove', { detail: { id: this.item.id }, bubbles: true, composed: true })
        );
    }

    @api tryMutate() {
        this.item.qty = 99;  // 읽기 전용 객체 → 오류
    }
}
