import { LightningElement } from 'lwc';

export default class ParentChild extends LightningElement {
    items = [
        { id: 'o1', name: '키보드', qty: 1 },
        { id: 'o2', name: '마우스', qty: 2 }
    ];
    selectedId;

    get selectedName() {
        const found = this.items.find((i) => i.id === this.selectedId);
        return found ? found.name : '없음';
    }

    handleSelect(event) {
        this.selectedId = event.detail.id;   // 자식이 보낸 데이터
    }

    highlightFirst() {
        // 자식의 @api 메서드 호출
        this.template.querySelector('c-order-item').highlight();
    }
}
