import { LightningElement, api } from 'lwc';

// 자주 만나는 실행 중 오류를 일부러 재현하는 컴포넌트(디버깅 학습용)
export default class DebugDemo extends LightningElement {
    @api config = { label: '처음' };
    @api mode = 'safe';
    account; // 아직 데이터가 오지 않은 상태(undefined)
    count = 0;

    // 1. 데이터가 오기 전에 깊은 속성을 읽는다
    get unsafeName() {
        return this.account.fields.Name.value;
    }

    // 고친 예: 옵셔널 체이닝과 기본값
    get safeName() {
        return this.account?.fields?.Name?.value ?? '불러오는 중';
    }

    get name() {
        return this.mode === 'unsafe' ? this.unsafeName : this.safeName;
    }

    // 2. 부모가 넘긴 @api 객체를 고친다
    @api mutateConfig() {
        this.config.label = '바꿈';
    }

    // 3. function 콜백에서 this를 잃는다
    @api startBrokenTimer() {
        // eslint-disable-next-line @lwc/lwc/no-async-operation
        setTimeout(function () {
            this.count += 1; // 여기의 this는 컴포넌트가 아니다
        }, 0);
    }

    // 고친 예: 화살표 함수는 바깥 this를 쓴다
    @api startTimer() {
        // eslint-disable-next-line @lwc/lwc/no-async-operation
        setTimeout(() => {
            this.count += 1;
        }, 0);
    }

    // 4. 프록시 객체를 콘솔에 찍으면 내용 대신 Proxy가 보인다. 펼쳐서 찍는다
    @api snapshot() {
        return JSON.parse(JSON.stringify(this.config));
    }
}
