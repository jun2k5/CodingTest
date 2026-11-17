import { LightningElement, api } from 'lwc';
import { formatKrw } from 'c/priceUtils';

export default class JestBasics extends LightningElement {
    @api step = 1000;
    total = 0;

    get totalLabel() {
        return `합계 ${formatKrw(this.total)}`;
    }

    get isZero() {
        return this.total === 0;
    }

    handleAdd() {
        this.total += this.step;
        this.dispatchEvent(new CustomEvent('totalchange', { detail: { total: this.total } }));
    }

    handleReset() {
        this.total = 0;
        this.dispatchEvent(new CustomEvent('totalchange', { detail: { total: 0 } }));
    }
}
