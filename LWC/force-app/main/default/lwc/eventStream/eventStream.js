import { LightningElement } from 'lwc';
import { subscribe, unsubscribe, onError } from 'lightning/empApi';

const CHANNEL = '/event/Order_Shipped__e';

export default class EventStream extends LightningElement {
    messages = [];
    connected = false;
    lastError;
    subscription;

    connectedCallback() {
        // 스트리밍 오류(연결 끊김 등) 처리기 등록
        onError((error) => {
            this.lastError = JSON.stringify(error);
        });
        // replayId -1: 구독 이후 새 이벤트만 받는다(-2: 보관 중인 이벤트부터)
        subscribe(CHANNEL, -1, (message) => this.handleMessage(message)).then((sub) => {
            this.subscription = sub;
            this.connected = true;
        });
    }

    get stateLabel() {
        return this.connected ? '수신 중' : '연결 중';
    }

    disconnectedCallback() {
        if (this.subscription) {
            unsubscribe(this.subscription, () => {});
        }
    }

    handleMessage(message) {
        // 메시지 모양: { channel, data: { event: { replayId }, payload: { 필드__c: 값 } } }
        const { payload, event } = message.data;
        this.messages = [
            { key: event.replayId, text: `주문 ${payload.Order_Number__c} 출고` },
            ...this.messages
        ].slice(0, 5); // 최근 5건만 유지
    }
}
