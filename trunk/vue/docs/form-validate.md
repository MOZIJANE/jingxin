# FORM VALIDATE 表单校验

## Types 类型清单

Indicates the `type` of validator to use. Recognised type values are:

```javascript
/**
* `string`: Must be of type `string`. `This is the default type.`
* `number`: Must be of type `number`.
* `boolean`: Must be of type `boolean`.
* `integer`: Must be of type `number` and an integer.
* `float`: Must be of type `number` and a floating point number.
* `enum`: Value must exist in the `enum`.
* `date`: Value must be valid as determined by `Date`
* `url`: Must be of type `url`.
* `hex`: Must be of type `hex`.
* `email`: Must be of type `email`.
* `remote`: Must be of type `url` and it is a validate api.
*/

rules: {
  userId: [
    { required: true, message: '字段为必填项的示例', trigger: 'blur' },
    { type: 'string', pattern: /^tony[1-3]$/, message: '这是一个有正则表达式的字符串的示例', trigger: 'blur' },
  ],
  password: [
    { required: true, message: '字段为必填项的示例', trigger: 'blur' },
    { type: 'string', min: 6, max: 20, message: '这是一个有长度要求字符串的示例', trigger: 'blur' },
  ],
  email: [
    { type: 'email', message: '这是一个email格式的示例', trigger: 'blur' }
  ],
  remoteValidate: [
    { type: 'remote', url: 'http://comba.com:8000/api/remote/check-validate', trigger: 'blur' }
  ],
  role: [
    { type: 'enum', list: ['admin', 'user', 'guest'], message: '这是一个枚举的示例', trigger: 'blur' }
  ]
}
```