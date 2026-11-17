// 테스트 전용 Mock 리포지토리: 서버 대신 메모리 배열로 같은 약속(search, changeRating)을 지킨다.
// force-app 밖에 두어 org에 배포되지 않는다.
export class MockAccountRepository {
    constructor(accounts = []) {
        this.accounts = accounts.map((a) => ({ ...a }));
        this.calls = [];
        this.failNext = null;
    }

    async search(keyword) {
        this.calls.push(['search', keyword]);
        this.throwIfFailing();
        return this.accounts.filter((a) => a.name.includes(keyword)).map((a) => ({ ...a }));
    }

    async changeRating(id, rating) {
        this.calls.push(['changeRating', id, rating]);
        this.throwIfFailing();
        const target = this.accounts.find((a) => a.id === id);
        if (!target) {
            throw new Error(`없는 거래처: ${id}`);
        }
        target.rating = rating;
    }

    // 다음 호출 한 번을 실패시킨다
    failOnce(message) {
        this.failNext = message;
    }

    throwIfFailing() {
        if (this.failNext) {
            const message = this.failNext;
            this.failNext = null;
            throw new Error(message);
        }
    }
}
