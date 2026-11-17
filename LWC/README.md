# LWC

velog 시리즈 [LWC 정리](https://velog.io/@jun2k5/lwc-00-series-intro)의 예제 코드다. SFDX 프로젝트 하나에 모든 예제 컴포넌트를 담았다.

- 검증: `@salesforce/sfdx-lwc-jest`(Jest)와 `@salesforce/eslint-config-lwc`(ESLint). org에는 배포하지 않았다.
- 실행: `npm install` 후 `npm run verify`를 실행하면 lint와 전체 테스트가 돈다.
- `force-app/main/default/classes`의 Apex는 참고 코드다. org가 없어 컴파일 검증을 하지 않았다.
- `jest-mocks/`는 테스트 전용 Mock(31번 글)이다. `force-app` 밖에 두어 배포되지 않는다.
- `manifest/package.xml`은 `sf project generate manifest`로 만든 배포 목록이다(33번 글).

| # | 묶음 | 주제 | 컴포넌트 | 글 |
|---|---|---|---|---|
| 01 | 기초 | LWC란: 웹 표준 위의 Salesforce UI 프레임워크 | [helloLwc](force-app/main/default/lwc/helloLwc) | [글](https://velog.io/@jun2k5/lwc-01-what-is-lwc) |
| 02 | 기초 | 개발 환경: sf CLI, 프로젝트 구조, 로컬 Jest | - | [글](https://velog.io/@jun2k5/lwc-02-dev-environment) |
| 03 | 기초 | 컴포넌트 구조: 번들 파일, js-meta.xml, 이름 규칙 | [componentAnatomy](force-app/main/default/lwc/componentAnatomy), [priceUtils](force-app/main/default/lwc/priceUtils) | [글](https://velog.io/@jun2k5/lwc-03-component-anatomy) |
| 04 | 기초 | 템플릿 문법: 바인딩, getter, lwc:if, for:each | [templateSyntax](force-app/main/default/lwc/templateSyntax) | [글](https://velog.io/@jun2k5/lwc-04-template-syntax) |
| 05 | 기초 | 반응성과 @track | [reactivity](force-app/main/default/lwc/reactivity) | [글](https://velog.io/@jun2k5/lwc-05-reactivity) |
| 06 | 기초 | 이벤트 처리와 폼 입력 | [formInput](force-app/main/default/lwc/formInput) | [글](https://velog.io/@jun2k5/lwc-06-events-forms) |
| 07 | 기초 | 컴포넌트 통신: @api, CustomEvent | [parentChild](force-app/main/default/lwc/parentChild), [orderItem](force-app/main/default/lwc/orderItem) | [글](https://velog.io/@jun2k5/lwc-07-component-communication) |
| 08 | 기초 | 생명주기 훅 | [lifecycle](force-app/main/default/lwc/lifecycle), [lifecycleChild](force-app/main/default/lwc/lifecycleChild) | [글](https://velog.io/@jun2k5/lwc-08-lifecycle-hooks) |
| 09 | 기초 | 스타일링: SLDS, styling hooks, Shadow DOM | [styling](force-app/main/default/lwc/styling) | [글](https://velog.io/@jun2k5/lwc-09-styling) |
| 10 | 기초 | Jest 기초 | [jestBasics](force-app/main/default/lwc/jestBasics) | [글](https://velog.io/@jun2k5/lwc-10-jest-basics) |
| 11 | 중급 | Lightning Data Service 폼 | [recordForms](force-app/main/default/lwc/recordForms) | [글](https://velog.io/@jun2k5/lwc-11-lds-record-forms) |
| 12 | 중급 | uiRecordApi | [recordApi](force-app/main/default/lwc/recordApi) | [글](https://velog.io/@jun2k5/lwc-12-ui-record-api) |
| 13 | 중급 | @wire 동작 원리 | [wireBasics](force-app/main/default/lwc/wireBasics) | [글](https://velog.io/@jun2k5/lwc-13-wire-service) |
| 14 | 중급 | Apex 연동: @wire와 명령형 호출 | [apexCall](force-app/main/default/lwc/apexCall) | [글](https://velog.io/@jun2k5/lwc-14-apex-integration) |
| 15 | 중급 | 데이터 갱신: refreshApex, notifyRecordUpdateAvailable | [dataRefresh](force-app/main/default/lwc/dataRefresh) | [글](https://velog.io/@jun2k5/lwc-15-data-refresh) |
| 16 | 중급 | 에러 처리와 토스트 | [errorToast](force-app/main/default/lwc/errorToast), [errorUtils](force-app/main/default/lwc/errorUtils) | [글](https://velog.io/@jun2k5/lwc-16-error-handling-toast) |
| 17 | 중급 | lightning-datatable | [dataTable](force-app/main/default/lwc/dataTable) | [글](https://velog.io/@jun2k5/lwc-17-datatable) |
| 18 | 중급 | NavigationMixin | [navigation](force-app/main/default/lwc/navigation) | [글](https://velog.io/@jun2k5/lwc-18-navigation) |
| 19 | 중급 | Lightning Message Service | [messageService](force-app/main/default/lwc/messageService), [lmsPublisher](force-app/main/default/lwc/lmsPublisher) | [글](https://velog.io/@jun2k5/lwc-19-lightning-message-service) |
| 20 | 중급 | 모달과 퀵 액션 | [modalAction](force-app/main/default/lwc/modalAction), [confirmModal](force-app/main/default/lwc/confirmModal) | [글](https://velog.io/@jun2k5/lwc-20-modal-quick-action) |
| 21 | 중급 | App Builder 설정 | [builderConfig](force-app/main/default/lwc/builderConfig) | [글](https://velog.io/@jun2k5/lwc-21-app-builder-config) |
| 22 | 중급 | Jest 심화 | [jestAdvanced](force-app/main/default/lwc/jestAdvanced) | [글](https://velog.io/@jun2k5/lwc-22-jest-advanced) |
| 23 | 고급 | 컴포지션 심화: slot, Light DOM, 동적 컴포넌트 | [composition](force-app/main/default/lwc/composition), [panelFrame](force-app/main/default/lwc/panelFrame), [lightCard](force-app/main/default/lwc/lightCard) | [글](https://velog.io/@jun2k5/lwc-23-composition) |
| 24 | 고급 | GraphQL wire adapter | [graphqlQuery](force-app/main/default/lwc/graphqlQuery) | [글](https://velog.io/@jun2k5/lwc-24-graphql-wire) |
| 25 | 고급 | 서드파티 라이브러리 | [thirdPartyLib](force-app/main/default/lwc/thirdPartyLib) | [글](https://velog.io/@jun2k5/lwc-25-third-party-library) |
| 26 | 고급 | 보안: LWS, XSS, Apex 권한 | [securityDemo](force-app/main/default/lwc/securityDemo) | [글](https://velog.io/@jun2k5/lwc-26-security) |
| 27 | 고급 | 성능 | [performance](force-app/main/default/lwc/performance) | [글](https://velog.io/@jun2k5/lwc-27-performance) |
| 28 | 고급 | Platform Event와 empApi | [eventStream](force-app/main/default/lwc/eventStream) | [글](https://velog.io/@jun2k5/lwc-28-platform-event-empapi) |
| 29 | 고급 | Flow 화면 컴포넌트와 Experience Cloud | [flowScreen](force-app/main/default/lwc/flowScreen) | [글](https://velog.io/@jun2k5/lwc-29-flow-screen-experience-cloud) |
| 30 | 고급 | 접근성과 다국어 | [a11yLabels](force-app/main/default/lwc/a11yLabels) | [글](https://velog.io/@jun2k5/lwc-30-accessibility-i18n) |
| 31 | 고급 | 테스트 가능한 구조: Mock 리포지토리 | [accountBoard](force-app/main/default/lwc/accountBoard), [accountRepository](force-app/main/default/lwc/accountRepository) | [글](https://velog.io/@jun2k5/lwc-31-mock-repository) |
| 32 | 고급 | 디버깅과 자주 보는 오류 | [debugDemo](force-app/main/default/lwc/debugDemo) | [글](https://velog.io/@jun2k5/lwc-32-debugging) |
| 33 | 고급 | 배포와 품질: package.xml, ESLint, CI | - | [글](https://velog.io/@jun2k5/lwc-33-deployment-quality) |
| 34 | 정리 | LWC 체크리스트와 상황별 선택표 | - | [글](https://velog.io/@jun2k5/lwc-34-checklist) |
