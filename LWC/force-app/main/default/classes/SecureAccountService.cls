// LWC 시리즈 26번 예제용 (참고 코드: org에 배포하지 않아 컴파일 검증을 하지 않았다)
public with sharing class SecureAccountService {          // with sharing: 레코드 공유 규칙 적용
    @AuraEnabled(cacheable=true)
    public static List<Account> listAccounts() {
        // WITH USER_MODE: 오브젝트·필드 권한이 없으면 예외
        return [SELECT Id, Name, AnnualRevenue FROM Account WITH USER_MODE ORDER BY Name LIMIT 50];
    }

    @AuraEnabled(cacheable=true)
    public static List<Account> listAccountsLenient() {
        // stripInaccessible: 권한 없는 필드만 지우고 나머지는 돌려준다
        List<Account> rows = [SELECT Id, Name, AnnualRevenue FROM Account ORDER BY Name LIMIT 50];
        return (List<Account>) Security.stripInaccessible(AccessType.READABLE, rows).getRecords();
    }

    @AuraEnabled
    public static void rename(Id accountId, String name) {
        // 사용자 권한으로 DML (권한 없으면 예외)
        Database.update(new Account(Id = accountId, Name = name), AccessLevel.USER_MODE);
    }
}
