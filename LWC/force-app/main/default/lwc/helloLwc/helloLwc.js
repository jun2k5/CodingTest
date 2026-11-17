import { LightningElement, api } from 'lwc';

export default class HelloLwc extends LightningElement {
    @api name = 'World';

    get greeting() {
        return `Hello, ${this.name}!`;
    }
}
