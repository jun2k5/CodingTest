// LWC 시리즈 17번 예제용 (참고 코드: org에 배포하지 않아 컴파일 검증을 하지 않았다)
public with sharing class AccountTableController {
    // 무한 스크롤용 페이지 조회. OFFSET은 최대 2,000까지만 쓸 수 있다
    @AuraEnabled
    public static List<Account> loadAccounts(Integer offsetSize, Integer pageSize) {
        return [
            SELECT Id, Name, AnnualRevenue, Rating
            FROM Account
            WITH USER_MODE
            ORDER BY Name
            LIMIT :pageSize
            OFFSET :offsetSize
        ];
    }
}
