am4core.useTheme(am4themes_animated);
let chart = am4core.create("chartdiv", am4plugins_forceDirected.ForceDirectedTree);
let itemBubble = chart.series.push(new am4plugins_forceDirected.ForceDirectedSeries());

//itemBubble.dataSource.url = "chart_data.json";
itemBubble.data = [{
    name: 'data01',
    text: '삼성전자',
    value: 265
}, {
    name: 'data02',
    text: '엘지전자',
    value: 165
}, {
    name: 'data03',
    text: '셀트리온',
    value: 187
}, {
    name: 'data04',
    text: '추천종목1',
    value: 123
}, {
    name: 'data05',
    text: '추천종목2',
    value: 134
}, {
    name: 'data06',
    text: '추천종목3',
    value: 337
}, {
    name: 'data07',
    text: '추천종목4',
    value: 298
}, {
    name: 'data08',
    text: '추천종목5',
    value: 276
}, {
    name: 'data09',
    text: '추천종목6',
    value: 99
}, {
    name: 'data10',
    text: '추천종목7',
    value: 498
}, {
    name: 'data11',
    text: '추천종목8',
    value: 151
}, {
    name: 'data12',
    text: '추천종목9',
    value: 287
}, {
    name: 'data13',
    text: '추천종목10',
    value: 381
}, {
    name: 'data14',
    text: '추천종목11',
    value: 251
}, {
    name: 'data15',
    text: '추천종목12',
    value: 61
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
    am4core.color('#f87900'),
    am4core.color('#4baa48'),
    am4core.color('#918648'),
    am4core.color('#686ce3'),
    am4core.color('#57a8c4'),
    am4core.color('#aabc24'),
    am4core.color('#c18ae8'),
    am4core.color('#d883e8'),
    am4core.color('#4ebbe6'),
    am4core.color('#2374e8'),
    am4core.color('#8e55cd')
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
itemBubble.manyBodyStrength = 10;
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
    const tabCont = document.querySelectorAll('.bubbleContent');
    const thisCont = document.querySelector('#' + tabId);
    
    
    chart.zoomToDataItem(ev.target.dataItem, 6, true)
    $(tabCont).addClass('hidden'); // es6 호환이 안되어서 jquery  사용함 ㅠ.ㅠ 바꿔줄수 있으면 바꿔주세요.
    fadeIn(thisCont);

}, this);

