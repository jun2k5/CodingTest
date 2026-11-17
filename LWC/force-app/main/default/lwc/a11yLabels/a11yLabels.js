import { LightningElement } from 'lwc';
import LOCALE from '@salesforce/i18n/locale';
import CURRENCY from '@salesforce/i18n/currency';
import TITLE from '@salesforce/label/c.Cart_Title';
import ITEM_COUNT from '@salesforce/label/c.Cart_Item_Count';
import REMOVE from '@salesforce/label/c.Cart_Remove';

// 라벨의 {0}, {1} 자리에 값을 끼운다
function format(label, ...args) {
    return label.replace(/\{(\d+)\}/g, (_, i) => args[i]);
}

export default class A11yLabels extends LightningElement {
    labels = { title: TITLE };
    items = [
        { id: 'i1', name: '키보드', price: 45000 },
        { id: 'i2', name: '마우스', price: 19000 }
    ];

    get countMessage() {
        return format(ITEM_COUNT, this.items.length);
    }

    get rows() {
        // 숫자·통화는 사용자 로캘과 org 통화로 서식을 맞춘다
        const fmt = new Intl.NumberFormat(LOCALE, { style: 'currency', currency: CURRENCY });
        return this.items.map((item) => ({
            ...item,
            priceText: fmt.format(item.price),
            removeLabel: format(REMOVE, item.name) // 화면 읽기 도구용: "무엇을" 지우는지까지 말한다
        }));
    }

    handleRemove(event) {
        const id = event.currentTarget.dataset.id;
        this.items = this.items.filter((i) => i.id !== id);
    }
}
