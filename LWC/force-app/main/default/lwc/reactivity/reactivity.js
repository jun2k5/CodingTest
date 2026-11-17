import { LightningElement, api, track } from 'lwc';

export default class Reactivity extends LightningElement {
    count = 0;                           // 원시값: 다시 대입하면 렌더링
    plain = { name: '처음' };             // 일반 필드의 객체: 내부 변경은 감지 안 됨
    @track tracked = { name: '처음' };    // @track: 내부 속성 변경도 감지
    list = ['a'];
    @track trackedList = ['a'];
    untouched = '템플릿에 없음';          // 템플릿에서 안 쓰는 필드

    renderedCallback() {
        // 렌더링 횟수 기록(관찰용). 반응형 필드가 아닌 _renders에 저장한다
        this._renders = (this._renders || 0) + 1;
    }

    @api get renders() {
        return this._renders;
    }

    get listText() {
        return this.list.join(',');
    }

    get trackedListText() {
        return this.trackedList.join(',');
    }

    @api increment() {
        this.count += 1;
    }
    @api mutatePlain() {
        this.plain.name = '변경';
    }
    @api reassignPlain() {
        this.plain = { ...this.plain, name: '재대입' };
    }
    @api mutateTracked() {
        this.tracked.name = '변경';
    }
    @api pushList() {
        this.list.push('b');
    }
    @api pushTrackedList() {
        this.trackedList.push('b');
    }
    @api changeUntouched() {
        this.untouched = '바뀜';
    }
}
