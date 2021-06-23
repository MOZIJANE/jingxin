# DATE PICKER 日期控件

## TYPE 时间跨度类型

- **date** 24小时
- **week** 星期一到星期日
- **month** 一号至月底
- **year** 一月至十二月
- **dates**
  - **<1year** 每十天
  - **<1month** 每天
  - **<24hour** 每半小时
  - **<6hour** 每十五分钟

```javascript
url: '/date/picker',
method: 'GET',
request: {
  headers: { session: 'xxxxxxxxxx' },
  params: {
    type: 'date',
    start: '2018-05-24T16:00:00.000Z',
    end: '2018-05-25T15:59:59.999Z'
  }
},
response: {
  errorno: 0,
  options: {
    title: {},
    legend: {},
    xAxis: {},
    yAxis: {},
    dataset: { source: [] },
    series: [],
  }
}
```