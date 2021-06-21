# REST API REFERENCE 接口文档

## USER MODULE

``` javascript
/**
 * Menu
 */
// get menu
url: '/menu',
method: 'GET',
request: {
  headers: { session: '5b023b17df46cb1930c23cd4' },
},
response: {
  pages: [
    {
      name: 'devices',
      path: '/devices',
      title: '设备管理',
      icon: 'box',
      hidden: false,
      children: [
        {
          name: 'rfid',
          path: '/rfid',
          title: '设备RFID',
          icon: 'card',
          hidden: false
        }
      ]
    }
  ]
}

/**
 * user login
 */
url: '/auth/login',
method: 'POST',
request: {
  body: {
    domain: 'comba',
    user: 'ycat',
    password: 'abcd1234'
  }
},
response: {
  session: 'xxxxxxxxxx',
  id: '5aeff9e7df46cb14587097cc',
  name: '姚舜',
  dept: '智能制造事业部',
  loginTime: '2018-05-21 01:49:25',
  role: ['5afa86f2a84fd72d8c5a5248', '5afa8932a84fd72d8c5a5249', '5afa895da84fd72d8c5a524a']
}

/**
 * user info
 */
// get info
url: '/auth/userInfo'
method: 'GET',
request: {
  headers: { session: '5b023b17df46cb1930c23cd4' },
  params: { user: 'ycat', method: 'query' }
}
response: {
  data: {
    _id: '5aeff9e7df46cb14587097cc', // required readonly invisible
    uname: 'ycat', // required readonly
    name: '姚舜',
    title: 'CTO',
    company: '京信通信',
    department: '智能制造事业部',
    telephone: '020-131321',
    mobile: '13888888888',
    email: 'chenruitong@comba.com.cn',
    address: '神舟路'
    // address: {
    //   country: 'China',
    //   province: '广东省',
    //   city: '广州市',
    //   district: '天河区',
    //   street: '神舟路',
    //   street_no: '10',
    // }
  }
}
// update info
url: '/auth/userInfo',
method: 'POST',
request: {
  headers: { session: '5b023b17df46cb1930c23cd4' },
  params: { user: 'ycat', method: 'update' },
  body: {
    _id: '5aeff9e7df46cb14587097cc',
    uname: 'ycat',
    name: '姚舜',
    title: 'CTO',
    company: '京信通信',
    department: '智能制造事业部',
    telephone: '020-131321',
    mobile: '13888888888',
    email: 'chenruitong@comba.com.cn',
    address: '神舟路'
   }
}

/**
 * user logout
 */
url: 'auth/logout',
method: 'POST',
request: {
  headers: { session: '5b023b17df46cb1930c23cd4' }
}

/**
 * user register
 */
url: '/auth/register',
method: 'POST',
request: {
  user: 'tonychen',
  email: 'tonychen@comba.com.cn',
  password: '88888888'
}
```

## META DATA TABLE MODULE

```javascript
/**
 * meta data table
 */
url: '/table'
method: 'GET',
request: {
  params: { table: 'table name' }
}
response: {
  meta: [],
  data: [],
  title: '表标题'
}
```
