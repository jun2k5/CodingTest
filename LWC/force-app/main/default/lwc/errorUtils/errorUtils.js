/**
 * LWC가 받는 여러 모양의 오류를 사용자에게 보여 줄 문자열 배열로 바꾼다.
 * - JS Error:                 { message }
 * - Apex 예외:                { body: { message, exceptionType } }
 * - UI API(LDS) 저장 오류:     { body: { message, output: { errors: [{ message }], fieldErrors: { Name: [{ message }] } } } }
 * - 여러 건:                  { body: [{ message }, ...] }
 * - 문자열, 또는 위 오류들의 배열
 */
export function reduceErrors(errors) {
    const list = Array.isArray(errors) ? errors : [errors];
    return list
        .filter((e) => !!e)
        .flatMap((error) => {
            if (typeof error === 'string') {
                return [error];
            }
            const body = error.body;
            if (Array.isArray(body)) {
                return body.map((b) => b.message);
            }
            if (body && body.output) {
                const pageErrors = (body.output.errors || []).map((e) => e.message);
                const fieldErrors = Object.values(body.output.fieldErrors || {})
                    .flat()
                    .map((e) => e.message);
                const all = [...pageErrors, ...fieldErrors];
                if (all.length > 0) {
                    return all;
                }
            }
            if (body && typeof body.message === 'string') {
                return [body.message];
            }
            if (typeof error.message === 'string') {
                return [error.message];
            }
            return [error.statusText || '알 수 없는 오류'];
        })
        .filter((m) => !!m);
}
