// LWC 시리즈 14번 예제용 Apex 컨트롤러 (참고 코드: 이 시리즈는 org에 배포하지 않아 컴파일 검증을 하지 않았다)
public with sharing class AccountController {
    // cacheable=true: 읽기 전용. @wire로 호출할 수 있고 결과가 클라이언트에 캐시된다
    @AuraEnabled(cacheable=true)
    public static List<Account> getAccounts(String keyword) {
        if (String.isBlank(keyword)) {
            return new List<Account>();
        }
        String pattern = '%' + keyword + '%';
        return [
            SELECT Id, Name, Rating
            FROM Account
            WHERE Name LIKE :pattern
            WITH USER_MODE
            ORDER BY Name
            LIMIT 20
        ];
    }

    // 데이터를 바꾸는 메서드는 cacheable로 만들 수 없다. 명령형으로만 호출한다
    @AuraEnabled
    public static Account updateRating(Id accountId, String rating) {
        Account acc = new Account(Id = accountId, Rating = rating);
        update as user acc;
        return acc;
    }
}
