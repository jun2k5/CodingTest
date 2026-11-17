import { LightningElement, api } from 'lwc';

// Light DOM 컴포넌트: Shadow DOM 없이 바로 문서에 그려진다
export default class LightCard extends LightningElement {
    static renderMode = 'light';
    @api text = 'Light DOM';
}
