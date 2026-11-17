import { LightningElement, api } from 'lwc';
import { log } from 'c/lifecycleLog';

export default class Lifecycle extends LightningElement {
    @api label = '자식';
    @api failChild = false;
    hasError = false;
    errorMessage;
    measured = '';
    _intervalId;
    _measuredOnce = false;

    constructor() {
        super();
        // 여기서는 아직 @api 값도, 템플릿도 없다
        log('parent constructor');
    }

    connectedCallback() {
        // DOM에 붙었다: @api 값을 쓸 수 있고, 데이터 요청·구독을 시작하는 곳
        log(`parent connectedCallback (label=${this.label})`);
        // eslint-disable-next-line @lwc/lwc/no-async-operation -- 정리(disconnectedCallback) 예제용 타이머
        this._intervalId = setInterval(() => {}, 1000);
    }

    renderedCallback() {
        // 렌더링이 끝났다: DOM을 읽을 수 있다. 렌더링마다 불리므로 한 번만 할 일은 플래그로 막는다
        log('parent renderedCallback');
        if (!this._measuredOnce) {
            this._measuredOnce = true;
            const child = this.template.querySelector('c-lifecycle-child');
            this.measured = child ? '자식 렌더링 확인' : '자식 없음';
        }
    }

    disconnectedCallback() {
        // DOM에서 빠졌다: 타이머·구독 정리
        log('parent disconnectedCallback');
        clearInterval(this._intervalId);
    }

    errorCallback(error) {
        // 자식(하위 트리)에서 난 오류를 잡는다
        log('parent errorCallback');
        this.hasError = true;
        this.errorMessage = error.message;
    }
}
