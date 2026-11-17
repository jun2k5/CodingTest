import { LightningElement, api } from 'lwc';

export default class BuilderConfig extends LightningElement {
    // App Builder 속성 패널 값이 들어오는 @api 속성(js-meta.xml의 property와 이름이 같아야 한다)
    @api cardTitle = '최근 활동';
    @api maxItems = 5;
    @api showIcons = false; // Boolean @api 속성의 기본값은 false로 둔다
    @api density = 'comfy';

    // 레코드 페이지에 올리면 플랫폼이 자동으로 넣어 준다(js-meta.xml에 적을 필요 없음)
    @api recordId;
    @api objectApiName;

    get context() {
        return this.recordId ? `${this.objectApiName} ${this.recordId}` : '레코드 페이지 아님';
    }

    get visibleItems() {
        const all = ['통화', '메일', '회의', '메모', '작업', '이벤트'];
        // App Builder 값은 숫자 범위 밖이나 문자열로 올 수도 있어 방어한다
        const n = Math.min(Math.max(parseInt(this.maxItems, 10) || 1, 1), all.length);
        return all.slice(0, n).map((label) => ({ label, key: label }));
    }

    get listClass() {
        return this.density === 'compact' ? 'list compact' : 'list';
    }
}
