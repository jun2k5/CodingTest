import { LightningElement, api, wire } from 'lwc';
import { NavigationMixin, CurrentPageReference } from 'lightning/navigation';
import { encodeDefaultFieldValues } from 'lightning/pageReferenceUtils';

// NavigationMixin으로 클래스를 감싸면 this[NavigationMixin.Navigate]를 쓸 수 있다
export default class Navigation extends NavigationMixin(LightningElement) {
    @api recordId = '001A';
    recordUrl;
    tab = '없음';

    // 현재 페이지 정보(URL의 상태 값 등)를 구독한다
    @wire(CurrentPageReference)
    setPageRef(pageRef) {
        if (pageRef && pageRef.state) {
            // 사용자 정의 상태 값은 c__ 접두사를 붙여야 URL에 남는다
            this.tab = pageRef.state.c__tab || '없음';
        }
    }

    get recordPageRef() {
        return {
            type: 'standard__recordPage',
            attributes: { recordId: this.recordId, objectApiName: 'Account', actionName: 'view' }
        };
    }

    async connectedCallback() {
        // 이동하지 않고 URL만 만든다(<a href>에 쓰기)
        this.recordUrl = await this[NavigationMixin.GenerateUrl](this.recordPageRef);
    }

    goRecord(event) {
        event.preventDefault(); // <a>의 기본 이동 대신 Lightning 내비게이션 사용
        this[NavigationMixin.Navigate](this.recordPageRef);
    }

    goNewAccount() {
        this[NavigationMixin.Navigate]({
            type: 'standard__objectPage',
            attributes: { objectApiName: 'Account', actionName: 'new' },
            // 새 레코드 기본값: 객체를 정해진 문자열 형식으로 인코딩해 넘긴다
            state: { defaultFieldValues: encodeDefaultFieldValues({ Rating: 'Hot', Name: '새 거래처' }) }
        });
    }

    goAccountList() {
        this[NavigationMixin.Navigate]({
            type: 'standard__objectPage',
            attributes: { objectApiName: 'Account', actionName: 'list' },
            state: { filterName: 'Recent' }
        });
    }

    goExternal() {
        this[NavigationMixin.Navigate]({
            type: 'standard__webPage',
            attributes: { url: 'https://developer.salesforce.com' }
        });
    }
}
