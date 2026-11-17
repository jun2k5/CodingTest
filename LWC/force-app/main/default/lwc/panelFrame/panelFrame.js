import { LightningElement, api } from 'lwc';

// slot으로 내용을 받는 틀 컴포넌트(Shadow DOM)
export default class PanelFrame extends LightningElement {
    _slottedCount = 0;

    // 바깥에는 읽기만 열어 두고, 값은 내부 필드에서 바꾼다(@api 속성 재대입 금지 규칙)
    @api
    get slottedCount() {
        return this._slottedCount;
    }

    handleSlotChange(event) {
        // 기본 slot에 들어온 요소 수
        this._slottedCount = event.target.assignedElements().length;
    }
}
