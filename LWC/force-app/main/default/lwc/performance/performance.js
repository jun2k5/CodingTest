import { LightningElement, api } from 'lwc';

const PAGE = 20;

export default class Performance extends LightningElement {
    _log = { getter: 0, cached: 0 }; // 관찰용 계산 횟수(템플릿에서 쓰지 않음)
    tick = 0;           // 화면의 다른 부분을 바꾸는 값(다시 렌더링 유발)
    showDetail = false; // 접힌 영역
    visibleCount = PAGE;
    _rows = [];
    summary = '';       // 데이터가 바뀔 때 한 번만 계산해 담는 필드

    @api
    get rows() {
        return this._rows;
    }
    set rows(value) {
        this._rows = value || [];
        this.summary = this.computeSummary('cached'); // 입력이 바뀔 때만 계산
    }

    computeSummary(kind) {
        this._log[kind] += 1;
        const total = this._rows.reduce((sum, r) => sum + r.amount, 0);
        return `${this._rows.length}건, 합계 ${total}`;
    }

    @api get computeLog() {
        return { ...this._log };
    }

    // 나쁜 예: 렌더링마다 전체 배열을 다시 계산하는 getter
    get summaryByGetter() {
        return this.computeSummary('getter');
    }

    // 큰 목록은 보이는 만큼만 그린다
    get visibleRows() {
        return this._rows.slice(0, this.visibleCount);
    }

    get hasMore() {
        return this.visibleCount < this._rows.length;
    }

    handleTick() {
        this.tick += 1;
    }

    handleMore() {
        this.visibleCount += PAGE;
    }

    toggleDetail() {
        this.showDetail = !this.showDetail;
    }
}
