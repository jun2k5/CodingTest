import { LightningElement, api } from 'lwc';

const LOADERS = {
    chart: () => import('c/chartWidget'),
    table: () => import('c/tableWidget')
};

export default class Composition extends LightningElement {
    widgetCtor;
    _widget;

    @api
    get widget() {
        return this._widget;
    }
    set widget(value) {
        this._widget = value;
        this.loadWidget(value);
    }

    async loadWidget(name) {
        const loader = LOADERS[name];
        if (!loader) {
            this.widgetCtor = undefined;
            return;
        }
        // 필요할 때 모듈을 불러온다(지연 로딩)
        const { default: ctor } = await loader();
        this.widgetCtor = ctor;
    }
}
