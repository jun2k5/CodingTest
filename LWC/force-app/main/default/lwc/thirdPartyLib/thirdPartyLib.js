import { LightningElement, api } from 'lwc';
import { loadScript } from 'lightning/platformResourceLoader';
import MINI_BAR from '@salesforce/resourceUrl/miniBar';

export default class ThirdPartyLib extends LightningElement {
    @api data = [];
    status = '불러오는 중';
    _initialized = false;

    renderedCallback() {
        // 라이브러리는 한 번만 불러온다(renderedCallback은 렌더링마다 불린다)
        if (this._initialized) {
            return;
        }
        this._initialized = true;
        loadScript(this, MINI_BAR)
            .then(() => {
                this.draw();
                this.status = '완료';
            })
            .catch((error) => {
                this.status = `라이브러리 로드 실패: ${error.message}`;
            });
    }

    draw() {
        // lwc:dom="manual" 영역에만 라이브러리가 DOM을 직접 만든다
        const container = this.template.querySelector('.chart');
        window.MiniBar.render(container, this.data);
    }
}
