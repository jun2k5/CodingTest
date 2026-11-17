import { createElement } from '@lwc/engine-dom';
import GraphqlQuery from 'c/graphqlQuery';
import { graphql } from 'lightning/graphql';

const flushAll = () => new Promise((r) => setTimeout(r, 0));

const RESPONSE = {
    uiapi: {
        query: {
            Account: {
                edges: [
                    {
                        node: {
                            Id: '001A',
                            Name: { value: '한빛상사' },
                            AnnualRevenue: { value: 900, displayValue: 'KRW 900' },
                            Owner: { Name: { value: '김담당' } }
                        }
                    }
                ],
                totalCount: 1
            }
        }
    }
};

function mount(props = {}) {
    const el = createElement('c-graphql-query', { is: GraphqlQuery });
    Object.assign(el, props);
    document.body.appendChild(el);
    return el;
}

describe('c-graphql-query', () => {
    afterEach(() => {
        while (document.body.firstChild) {
            document.body.removeChild(document.body.firstChild);
        }
    });

    it('variables getter를 반응형으로 넘기고, 값이 바뀌면 다시 조회한다', async () => {
        const el = mount({ minRevenue: 100 });
        await flushAll();
        expect(graphql.getLastConfig().variables).toEqual({ minRevenue: 100, pageSize: 5 });
        el.minRevenue = 500;
        await flushAll();
        expect(graphql.getLastConfig().variables).toEqual({ minRevenue: 500, pageSize: 5 });
    });

    it('edges[].node의 { value }를 화면용 객체로 펼친다', async () => {
        const el = mount();
        graphql.emit(RESPONSE);
        await flushAll();
        expect(el.shadowRoot.querySelector('.accounts li').textContent).toBe('한빛상사 / KRW 900 / 김담당');
    });

    it('오류는 error가 아니라 errors 배열로 온다', async () => {
        const el = mount();
        graphql.emitErrors([{ message: 'Field AnnualRevenue is not accessible' }]);
        await flushAll();
        expect(el.shadowRoot.querySelector('.errors').textContent).toBe('Field AnnualRevenue is not accessible');
    });

    it('결과에 들어 있는 refresh 함수로 다시 조회한다', async () => {
        const refresh = jest.fn(() => Promise.resolve());
        const el = mount();
        graphql.emit(RESPONSE, undefined, refresh);
        await flushAll();
        el.shadowRoot.querySelector('.refresh').click();
        await flushAll();
        expect(refresh).toHaveBeenCalledTimes(1);
    });
});
