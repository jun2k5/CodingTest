import { LightningElement, wire } from 'lwc';
import { publish, MessageContext } from 'lightning/messageService';
import RECORD_SELECTED from '@salesforce/messageChannel/RecordSelected__c';

// 보내는 쪽: 목록에서 레코드를 고르면 채널에 메시지를 발행한다
export default class LmsPublisher extends LightningElement {
    accounts = [
        { Id: '001A', Name: '한빛상사' },
        { Id: '001B', Name: '가람물산' }
    ];

    @wire(MessageContext)
    messageContext;

    handleSelect(event) {
        const payload = { recordId: event.currentTarget.dataset.id, source: 'lmsPublisher' };
        publish(this.messageContext, RECORD_SELECTED, payload);
    }
}
