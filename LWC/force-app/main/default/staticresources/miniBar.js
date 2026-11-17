// 예제용 아주 작은 막대그래프 라이브러리(전역 window.MiniBar를 만든다).
// 실제로는 Chart.js 같은 서드파티 라이브러리 파일을 정적 리소스로 올린다.
(function (global) {
    function render(container, data) {
        container.innerHTML = '';
        var max = Math.max.apply(null, data.map(function (d) { return d.value; }).concat([1]));
        data.forEach(function (d) {
            var bar = document.createElement('div');
            bar.className = 'mini-bar';
            bar.style.width = Math.round((d.value / max) * 100) + '%';
            bar.textContent = d.label + ' ' + d.value;
            container.appendChild(bar);
        });
        return { bars: data.length };
    }
    global.MiniBar = { render: render, version: '1.0' };
})(window);
