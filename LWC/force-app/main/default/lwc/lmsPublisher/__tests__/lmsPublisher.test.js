import { createElement } from '@lwc/engine-dom';
import LmsPublisher from 'c/lmsPublisher';
import { publish } from 'lightning/messageService';

describe('c-lms-publisher', () => {
    afterEach(() => {
        while (document.body.firstChild) {
            document.body.removeChild(document.body.firstChild);
        }
        jest.clearAllMocks();
    });

    it('버튼을 누르면 채널에 recordId를 담아 발행한다', () => {
        const el = createElement('c-lms-publisher', { is: LmsPublisher });
        document.body.appendChild(el);
        el.shadowRoot.querySelector('.pick').click();
        expect(publish).toHaveBeenCalledTimes(1);
        expect(publish.mock.calls[0][2]).toEqual({ recordId: '001A', source: 'lmsPublisher' });
    });
});
