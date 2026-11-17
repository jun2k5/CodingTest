import { ApexAccountRepository, toDomain } from 'c/accountRepository';
import getAccounts from '@salesforce/apex/AccountController.getAccounts';
import updateRating from '@salesforce/apex/AccountController.updateRating';

// 실제 리포지토리는 Apex 호출과 변환만 맡으므로, 여기서만 Apex를 모의한다
jest.mock('@salesforce/apex/AccountController.getAccounts', () => ({ default: jest.fn() }), { virtual: true });
jest.mock('@salesforce/apex/AccountController.updateRating', () => ({ default: jest.fn() }), { virtual: true });

describe('c/accountRepository (실제 구현)', () => {
    afterEach(() => jest.clearAllMocks());

    it('Apex 필드 이름을 도메인 객체로 바꾸고 빈 등급을 채운다', () => {
        expect(toDomain({ Id: '001A', Name: '한빛상사', Rating: null })).toEqual({
            id: '001A',
            name: '한빛상사',
            rating: '없음'
        });
    });

    it('search는 getAccounts에 keyword를 넘기고 결과를 변환한다', async () => {
        getAccounts.mockResolvedValue([{ Id: '001A', Name: '한빛상사', Rating: 'Warm' }]);
        const result = await new ApexAccountRepository().search('한빛');
        expect(getAccounts).toHaveBeenCalledWith({ keyword: '한빛' });
        expect(result).toEqual([{ id: '001A', name: '한빛상사', rating: 'Warm' }]);
    });

    it('changeRating은 Apex 파라미터 이름으로 바꿔 호출한다', async () => {
        updateRating.mockResolvedValue({});
        await new ApexAccountRepository().changeRating('001A', 'Hot');
        expect(updateRating).toHaveBeenCalledWith({ accountId: '001A', rating: 'Hot' });
    });
});
