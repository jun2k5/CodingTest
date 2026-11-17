import { LightningElement, api } from 'lwc';
import { getAccountRepository } from 'c/accountRepository';

export default class AccountBoard extends LightningElement {
    // 리포지토리를 바깥에서 넣을 수 있게 열어 둔다(넣지 않으면 실제 Apex 리포지토리)
    @api repository;
    @api keyword = '한빛';
    accounts = [];
    message = '';

    get repo() {
        return this.repository || getAccountRepository();
    }

    connectedCallback() {
        this.load();
    }

    async load() {
        try {
            this.accounts = await this.repo.search(this.keyword);
            this.message = `${this.accounts.length}건`;
        } catch (e) {
            this.message = `조회 실패: ${e.message}`;
        }
    }

    // 업무 규칙: 이미 Hot이면 바꾸지 않는다
    async handleHot(event) {
        const id = event.currentTarget.dataset.id;
        const account = this.accounts.find((a) => a.id === id);
        if (account.rating === 'Hot') {
            this.message = `${account.name}은 이미 Hot`;
            return;
        }
        try {
            await this.repo.changeRating(id, 'Hot');
            await this.load(); // 저장 뒤 다시 조회
            this.message = `${account.name} → Hot`;
        } catch (e) {
            this.message = `변경 실패: ${e.message}`;
        }
    }
}
