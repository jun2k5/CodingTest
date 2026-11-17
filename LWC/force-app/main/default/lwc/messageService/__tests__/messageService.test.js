import { createElement } from '@lwc/engine-dom';
import MessageService from 'c/messageService';
import LmsPublisher from 'c/lmsPublisher';
import { publish, subscribe, unsubscribe } from 'lightning/messageService';

// 기본 스텁의 publish는 아무에게도 전달하지 않는다.
// 채널별 구독자 목록을 가진 작은 메시지 버스로 바꿔 보내는 쪽과 받는 쪽을 함께 시험한다.
jest.mock('lightning/messageService', () => {
    const { createTestWireAdapter } = require('@salesforce/wire-service-jest-util');
    const handlers = new Map();
    return {
        APPLICATION_SCOPE: Symbol('APPLICATION_SCOPE'),
        MessageContext: createTestWireAdapter(jest.fn()),
        publish: jest.fn((ctx, channel, message) => {
            (handlers.get(channel) || []).forEach((h) => h(message));
        }),
        subscribe: jest.fn((ctx, channel, handler) => {
            handlers.set(channel, [...(handlers.get(channel) || []), handler]);
            return { channel, handler };
        }),
        unsubscribe: jest.fn((sub) => {
            if (sub) {
                handlers.set(sub.channel, (handlers.get(sub.channel) || []).filter((h) => h !== sub.handler));
            }
        })
    };
});

const flush = () => Promise.resolve();

function mountBoth() {
    const receiver = createElement('c-message-service', { is: MessageService });
    const sender = createElement('c-lms-publisher', { is: LmsPublisher });
    document.body.appendChild(receiver);
    document.body.appendChild(sender); // 서로 부모·자식 관계가 아닌 형제
    return { receiver, sender };
}

describe('c-message-service (Lightning Message Service)', () => {
    afterEach(() => {
        while (document.body.firstChild) {
            document.body.removeChild(document.body.firstChild);
        }
        jest.clearAllMocks();
    });

    it('연결될 때 채널을 APPLICATION_SCOPE로 구독한다', () => {
        mountBoth();
        expect(subscribe).toHaveBeenCalledTimes(1);
        expect(subscribe.mock.calls[0][3].scope).toBeDefined();
    });

    it('관계없는 컴포넌트가 발행한 메시지를 받는다', async () => {
        const { receiver, sender } = mountBoth();
        sender.shadowRoot.querySelectorAll('.pick')[1].click();
        await flush();
        expect(publish.mock.calls[0][2]).toEqual({ recordId: '001B', source: 'lmsPublisher' });
        expect(receiver.shadowRoot.querySelector('.selected').textContent).toBe('선택된 레코드: 001B');
    });

    it('화면에서 사라지면 구독을 해제해 더는 메시지를 받지 않는다', async () => {
        const { receiver, sender } = mountBoth();
        document.body.removeChild(receiver);
        expect(unsubscribe).toHaveBeenCalledTimes(1);
        sender.shadowRoot.querySelectorAll('.pick')[0].click();
        await flush();
        expect(receiver.shadowRoot.querySelector('.selected').textContent).toBe('선택된 레코드: 없음');
    });
});
