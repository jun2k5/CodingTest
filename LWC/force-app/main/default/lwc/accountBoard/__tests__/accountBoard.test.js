import { createElement } from '@lwc/engine-dom';
import AccountBoard from 'c/accountBoard';
import { MockAccountRepository } from '../../../../../../jest-mocks/mockAccountRepository';

const flushAll = () => new Promise((r) => setTimeout(r, 0));
const SEED = [
    { id: '001A', name: '한빛상사', rating: 'Warm' },
    { id: '001B', name: '한빛물산', rating: 'Hot' },
    { id: '001C', name: '가람전자', rating: 'Cold' }
];

// Apex를 모의하지 않는다: Mock 리포지토리를 @api로 넣는다
async function mount(repository) {
    const el = createElement('c-account-board', { is: AccountBoard });
    el.repository = repository;
    document.body.appendChild(el);
    await flushAll();
    return el;
}
const labels = (el) => [...el.shadowRoot.querySelectorAll('.label')].map((l) => l.textContent);
const message = (el) => el.shadowRoot.querySelector('.message').textContent;

describe('c-account-board (Mock 리포지토리)', () => {
    afterEach(() => {
        while (document.body.firstChild) {
            document.body.removeChild(document.body.firstChild);
        }
    });

    it('리포지토리가 준 도메인 객체를 그대로 그린다', async () => {
        const el = await mount(new MockAccountRepository(SEED));
        expect(labels(el)).toEqual(['한빛상사 (Warm)', '한빛물산 (Hot)']);
        expect(message(el)).toBe('2건');
    });

    it('Hot으로 바꾸면 리포지토리 상태가 바뀌고 다시 조회한 결과가 보인다', async () => {
        const repo = new MockAccountRepository(SEED);
        const el = await mount(repo);
        el.shadowRoot.querySelectorAll('.hot')[0].click();
        await flushAll();
        expect(labels(el)).toEqual(['한빛상사 (Hot)', '한빛물산 (Hot)']);
        expect(repo.calls).toEqual([
            ['search', '한빛'],
            ['changeRating', '001A', 'Hot'],
            ['search', '한빛']
        ]);
    });

    it('업무 규칙: 이미 Hot이면 저장을 호출하지 않는다', async () => {
        const repo = new MockAccountRepository(SEED);
        const el = await mount(repo);
        el.shadowRoot.querySelectorAll('.hot')[1].click();
        await flushAll();
        expect(message(el)).toBe('한빛물산은 이미 Hot');
        expect(repo.calls.filter((c) => c[0] === 'changeRating')).toEqual([]);
    });

    it('저장이 실패하면 메시지를 보이고 화면 데이터는 그대로다', async () => {
        const repo = new MockAccountRepository(SEED);
        const el = await mount(repo);
        repo.failOnce('검증 규칙 위반');
        el.shadowRoot.querySelectorAll('.hot')[0].click();
        await flushAll();
        expect(message(el)).toBe('변경 실패: 검증 규칙 위반');
        expect(labels(el)).toEqual(['한빛상사 (Warm)', '한빛물산 (Hot)']);
    });
});
