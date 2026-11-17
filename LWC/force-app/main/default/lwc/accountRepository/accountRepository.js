// 데이터 접근 계층: 컴포넌트는 Apex를 직접 부르지 않고 이 리포지토리를 통해 데이터를 다룬다
import getAccounts from '@salesforce/apex/AccountController.getAccounts';
import updateRating from '@salesforce/apex/AccountController.updateRating';

// Apex 응답(Salesforce 필드 이름)을 화면이 쓰는 도메인 객체로 바꾼다
export function toDomain(row) {
    return { id: row.Id, name: row.Name, rating: row.Rating || '없음' };
}

/**
 * 리포지토리가 지켜야 할 약속(인터페이스)
 *   search(keyword: string): Promise<Array<{id, name, rating}>>
 *   changeRating(id: string, rating: string): Promise<void>
 */
export class ApexAccountRepository {
    async search(keyword) {
        const rows = await getAccounts({ keyword });
        return rows.map(toDomain);
    }

    async changeRating(id, rating) {
        await updateRating({ accountId: id, rating });
    }
}

let instance;
export function getAccountRepository() {
    if (!instance) {
        instance = new ApexAccountRepository();
    }
    return instance;
}
