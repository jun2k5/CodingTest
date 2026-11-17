import { createElement } from '@lwc/engine-dom';
import EventStream from 'c/eventStream';
import { subscribe, unsubscribe, onError } from 'lightning/empApi';

const flushAll = () => new Promise((r) => setTimeout(r, 0));
const message = (replayId, orderNumber) => ({
    channel: '/event/Order_Shipped__e',
    data: { event: { replayId }, payload: { Order_Number__c: orderNumber } }
});

async function mount() {
    const el = createElement('c-event-stream', { is: EventStream });
    document.body.appendChild(el);
    await flushAll();
    return el;
}

describe('c-event-stream', () => {
    afterEach(() => {
        while (document.body.firstChild) {
            document.body.removeChild(document.body.firstChild);
        }
        jest.clearAllMocks();
    });

    it('채널을 replayId -1로 구독하고 오류 처리기를 등록한다', async () => {
        const el = await mount();
        expect(subscribe.mock.calls[0][0]).toBe('/event/Order_Shipped__e');
        expect(subscribe.mock.calls[0][1]).toBe(-1);
        expect(onError).toHaveBeenCalledTimes(1);
        expect(el.shadowRoot.querySelector('.state').textContent).toBe('수신 중');
    });

    it('이벤트가 오면 payload의 필드를 꺼내 최근 순으로 보여 준다', async () => {
        const el = await mount();
        const callback = subscribe.mock.calls[0][2]; // 구독할 때 넘긴 콜백을 꺼내 직접 호출
        callback(message(101, 'SO-1'));
        callback(message(102, 'SO-2'));
        await flushAll();
        const items = [...el.shadowRoot.querySelectorAll('.messages li')].map((li) => li.textContent);
        expect(items).toEqual(['주문 SO-2 출고', '주문 SO-1 출고']);
    });

    it('최근 5건만 유지한다', async () => {
        const el = await mount();
        const callback = subscribe.mock.calls[0][2];
        for (let i = 1; i <= 7; i++) {
            callback(message(i, `SO-${i}`));
        }
        await flushAll();
        expect(el.shadowRoot.querySelectorAll('.messages li').length).toBe(5);
    });

    it('화면에서 사라지면 구독을 해제한다', async () => {
        const sub = { id: 'sub-1' };
        subscribe.mockResolvedValueOnce(sub);
        const el = await mount();
        document.body.removeChild(el);
        expect(unsubscribe.mock.calls[0][0]).toBe(sub);
    });
});
