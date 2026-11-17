import { LightningElement, api } from 'lwc';
import { formatKrw } from 'c/priceUtils';      // 다른 번들의 모듈
import { LABEL_PREFIX } from './constants';     // 같은 번들 안의 추가 파일

export default class ComponentAnatomy extends LightningElement {
    @api title = '상품';
    @api price = 0;

    get formattedPrice() {
        return `${LABEL_PREFIX} ${formatKrw(this.price)}`;
    }
}
