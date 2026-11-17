import { LightningElement, wire } from 'lwc';
import { subscribe, unsubscribe, MessageContext, APPLICATION_SCOPE } from 'lightning/messageService';
import RECORD_SELECTED from '@salesforce/messageChannel/RecordSelected__c';

// 받는 쪽: 채널을 구독하고, 화면에서 사라질 때 구독을 해제한다
export default class MessageService extends LightningElement {
    selectedId = '없음';
    subscription = null;

    @wire(MessageContext)
    messageContext;

    connectedCallback() {
        if (!this.subscription) {
            this.subscription = subscribe(
                this.messageContext,
                RECORD_SELECTED,
                (message) => this.handleMessage(message),
                { scope: APPLICATION_SCOPE } // 활성 영역 밖(다른 탭·유틸리티 바)의 메시지도 받기
            );
        }
    }

    disconnectedCallback() {
        unsubscribe(this.subscription);
        this.subscription = null;
    }

    handleMessage(message) {
        this.selectedId = message.recordId;
    }
}
