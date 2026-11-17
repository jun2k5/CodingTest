// LWC 시리즈 28번 예제용 (참고 코드: org에 배포하지 않아 컴파일 검증을 하지 않았다)
public with sharing class OrderShippedPublisher {
    public static void publish(String orderNumber) {
        Database.SaveResult result = EventBus.publish(new Order_Shipped__e(Order_Number__c = orderNumber));
        if (!result.isSuccess()) {
            System.debug(LoggingLevel.ERROR, result.getErrors());
        }
    }
}
