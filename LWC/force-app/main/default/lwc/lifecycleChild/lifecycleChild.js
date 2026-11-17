import { LightningElement, api } from 'lwc';
import { log } from 'c/lifecycleLog';

export default class LifecycleChild extends LightningElement {
    @api label;
    @api shouldFail = false;

    constructor() {
        super();
        log('child constructor');
    }
    connectedCallback() {
        log('child connectedCallback');
        if (this.shouldFail) {
            throw new Error('자식에서 난 오류');
        }
    }
    renderedCallback() {
        log('child renderedCallback');
    }
    disconnectedCallback() {
        log('child disconnectedCallback');
    }
}
