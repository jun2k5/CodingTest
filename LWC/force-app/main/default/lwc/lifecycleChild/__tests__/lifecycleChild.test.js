import { createElement } from '@lwc/engine-dom';
import LifecycleChild from 'c/lifecycleChild';
import { calls, reset } from 'c/lifecycleLog';

describe('c-lifecycle-child', () => {
    beforeEach(() => reset());
    afterEach(() => {
        while (document.body.firstChild) {
            document.body.removeChild(document.body.firstChild);
        }
    });

    it('단독으로 붙이면 constructor → connected → rendered 순서다', () => {
        const el = createElement('c-lifecycle-child', { is: LifecycleChild });
        el.label = '단독';
        document.body.appendChild(el);
        expect(calls).toEqual(['child constructor', 'child connectedCallback', 'child renderedCallback']);
    });
});
