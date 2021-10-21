am4core.useTheme(am4themes_animated);
let chart = am4core.create("chartdiv", am4plugins_forceDirected.ForceDirectedTree);
let itemBubble = chart.series.push(new am4plugins_forceDirected.ForceDirectedSeries())

let plus = '#fb5360';
let minus = '#3e72ed';


//itemBubble.dataSource.url = "chart_data.json";
itemBubble.data = [{
    name: 'data01',
    text: '삼성전자\n아무개',
    value: 131543,
    color: plus
}, {
    name: 'data02',
    text: '엘지전자',
    value: 16785,
    color: plus
}, {
    name: 'data03',
    text: '셀트리온',
    value: 9871,
    color: plus
}, {
    name: 'data04',
    text: '추천종목',
    value: 78561,
    color: minus
}, {
    name: 'data05',
    text: '추천종목2',
    value: 8762,
    color: minus
}, {
    name: 'data06',
    text: '추천종목2',
    value: 8161,
    color: minus
}, {
    name: 'data07',
    text: '추천종목2',
    value: 5761,
    color: minus
}, {
    name: 'data08',
    text: '추천종목2',
    value: 6761,
    color: minus
}, {
    name: 'data09',
    text: '추천종목2',
    value: 761,
    color: minus
}, {
    name: 'data10',
    text: '추천종목2',
    value: 871,
    color: minus
}];

itemBubble.dataFields.linkWith = "linkWith";
itemBubble.dataFields.name = "name";
itemBubble.dataFields.id = "name";
itemBubble.dataFields.value = "value";
//itemBubble.dataFields.color = "color";
itemBubble.colors.list = [
    am4core.color('#fb5360'),
    am4core.color('#fa5f6b'),
    am4core.color('#f56772'),
    am4core.color('#f77983'),
    am4core.color('#fa8790'),
    am4core.color('#ffb2b9'),
    am4core.color('#fa8790'),
    am4core.color('#fa8790'),
    am4core.color('#fa8790'),
    am4core.color('#fa8790'),
    am4core.color('#618ae8'),
    am4core.color('#5883e8'),
    am4core.color('#4e7be6'),
    am4core.color('#4374e8'),
    am4core.color('#3e72ed')
];
//itemBubble.dataFields.children = "children";
itemBubble.links.template.distance = 1;
//itemBubble.nodes.template.tooltipText = "{name}";
itemBubble.nodes.template.fillOpacity = 1;
itemBubble.nodes.template.outerCircle.scale = 1;

itemBubble.nodes.template.label.text = "[font-size:16 line-height:20]{text}"
//itemBubble.fontSize = 20;
itemBubble.nodes.template.label.hideOversized = true;
itemBubble.nodes.template.label.truncate = true;
itemBubble.links.template.disabled = true;
itemBubble.minRadius = am4core.percent(10);
itemBubble.maxRadius = am4core.percent(20);
itemBubble.manyBodyStrength = -5;
itemBubble.links.template.strokeOpacity = 0;
itemBubble.fontFamily = 'Noto Sans KR';
itemBubble.nodes.template.cursorOverStyle = am4core.MouseCursorStyle.pointer;


function fadeIn(el, display) {
    if (el.classList.contains('hidden')) {
        el.classList.remove('hidden');
    }
    el.style.opacity = 0;
    el.style.display = display || "block";

    (function fade() {
        var val = parseFloat(el.style.opacity);
        if (!((val += .1) > 1)) {
            el.style.opacity = val;
            requestAnimationFrame(fade);
        }
    })();
}


itemBubble.nodes.template.events.on("hit", function (ev) {
    const tabId = ev.target.dataItem.dataContext.name;
    const tabCont = document.querySelectorAll('.itemRmdBox');
    const thisCont = document.querySelector('#' + tabId);


    chart.zoomToDataItem(ev.target.dataItem, 6, true)
    $(tabCont).addClass('hidden'); // es6 호환이 안되어서 jquery  사용함 ㅠ.ㅠ 바꿔줄수 있으면 바꿔주세요.
    fadeIn(thisCont);

}, this);

