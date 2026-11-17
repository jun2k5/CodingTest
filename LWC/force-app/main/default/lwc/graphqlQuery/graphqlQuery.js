import { LightningElement, api, wire } from 'lwc';
import { gql, graphql } from 'lightning/graphql';

export default class GraphqlQuery extends LightningElement {
    @api minRevenue = 0;
    accounts = [];
    errors;
    refreshFn;

    @wire(graphql, {
        query: gql`
            query bigAccounts($minRevenue: Currency, $pageSize: Int) {
                uiapi {
                    query {
                        Account(
                            where: { AnnualRevenue: { gte: $minRevenue } }
                            orderBy: { AnnualRevenue: { order: DESC } }
                            first: $pageSize
                        ) {
                            edges {
                                node {
                                    Id
                                    Name { value }
                                    AnnualRevenue { value displayValue }
                                    Owner { Name { value } }
                                }
                            }
                            totalCount
                        }
                    }
                }
            }
        `,
        variables: '$variables' // getter 결과가 바뀌면 다시 조회
    })
    wiredAccounts({ data, errors, refresh }) {
        this.refreshFn = refresh;
        if (data) {
            // 응답은 uiapi.query.오브젝트.edges[].node 구조이고, 필드 값은 { value }에 들어 있다
            this.accounts = data.uiapi.query.Account.edges.map(({ node }) => ({
                id: node.Id,
                name: node.Name.value,
                revenue: node.AnnualRevenue.displayValue,
                owner: node.Owner.Name.value
            }));
            this.errors = undefined;
        }
        if (errors) {
            this.errors = errors.map((e) => e.message).join(', ');
        }
    }

    get variables() {
        return { minRevenue: this.minRevenue, pageSize: 5 };
    }

    async handleRefresh() {
        if (this.refreshFn) {
            await this.refreshFn();
        }
    }
}
