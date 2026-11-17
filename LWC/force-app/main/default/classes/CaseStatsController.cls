// LWC 시리즈 22번 예제용 (참고 코드: org에 배포하지 않아 컴파일 검증을 하지 않았다)
public with sharing class CaseStatsController {
    @AuraEnabled
    public static Integer countOpenCases(Id accountId) {
        return [SELECT COUNT() FROM Case WHERE AccountId = :accountId AND IsClosed = false WITH USER_MODE];
    }
}
