<script>
/* eslint-disable */

import moment from 'moment';
import { getToken } from '@/utils/auth';
export default {
  name: 'FormItemList',
  props: {
    url: String,
    columns: {
      type: Array,
    },
    row: {
      type: Object,
    },
    formItemStyle: {
      type: Object,
    },
    optionsLoaded: {
      type: Object,
      default() {
        return {};
      },
    },
  },
  data() {
    return {
      formLabelWidth: '120px',
    };
  },
  methods: {
    formatDate(val) {
      if (val === null) {
        return new Date();
      } else {
        return new Date(val);
      }
    },
    handleBlur(vm, id, picker) {
      if (picker) {
        const val = vm.picker.date;
        const { editCtrl: { type } } = this.columns.find(col => col.id === id);
        if (type === 'datetimePicker') {
          this.row[id] = moment(val).format('YYYY-MM-DD HH:mm:ss');
        } else if (type === 'datePicker') {
          this.row[id] = moment(val).format('YYYY-MM-DD');
        } else if (type === 'timePicker') {
          this.row[id] = moment(val).format('HH:mm:ss');
        }
      }
    },
    handleInputChange(val, id) {
      this.row[id] = val;
    },
    handleTimeInputChange(val, id) {
      this.row[id] = new Date(val);
    },
    smartElOptions(id) {
      const { columns, row, url } = this;
      const selectMeta = columns.find(col => col.id === id);
      // const subUrl = url.substring(7);
      let api = `${selectMeta.editCtrl.url}`;
      api = selectMeta.editCtrl.parentId
        ? `${api}&parentId=${row[selectMeta.editCtrl.parentId]}`
        : api;
      let list = [];
      if (
        this.optionsLoaded &&
        this.optionsLoaded[id] &&
        !selectMeta.editCtrl.parentId
      ) {
        list = this.optionsLoaded[id];
      } else {
        const xhr = new XMLHttpRequest();
        xhr.open('GET', api, false);
        xhr.setRequestHeader('Session', getToken() || '');
        xhr.setRequestHeader('Location', location.hash.replace('#', ''));
        xhr.send(null);
        if (xhr.status === 200) {
          list = JSON.parse(xhr.responseText).list;
          // if (list.length === 1) {
          //   row[id] = list[0].value;
          // }
          this.$emit('load-options', { id, list });
        }
      }
      const { multiple } = columns.find(col => id === col.id).editCtrl.attr;
      if (multiple) {
        const selectedList = list.filter(option => {
          if (Array.isArray(row[id])) {
            return row[id].includes(option.label);
          }
          return false;
        });
        if (selectedList.length !== 0) {
          const arr = [];
          selectedList.forEach(option => {
            arr.push(option.value);
          });
          row[id] = arr;
        }
      } else {
        const selectedList = list.filter(option => row[id] === option.label);
        if (selectedList.length !== 0) {
          row[id] = selectedList[0].value;
        }
      }
      const options = list.map(option => {
        return (
          <el-option
            key={option.value}
            value={option.value}
            label={option.label}
          />
        );
      });
      return options;
    },
    smartFormItem(createElement) {
      const { row, url, columns, formatDate } = this;
      return columns.map(col => {
        const {
          editCtrl: { type, attr },
          id,
          name,
          rules = [],
          readonly
        } = col;
        if (rules.length !== 0) {
          rules.forEach(rule => {
            if ('pattern' in rule) {
              const pattern = new RegExp(rule.pattern);
              rule = { ...rule, pattern };
            }
          });
        }
        if ('activeText' in attr && !('activeValue' in attr)) {
          attr.activeValue = attr.activeText;
          attr.inactiveValue = attr.inactiveText;
        }
        let props = attr;
        const disabled = readonly ? true : false;
        let children = [];
        let smartInput;
        let value = row[id];
        let picker = false;
        if (type === 'inputNumber') {
          smartInput = 'el-input-number';
        } else if (type === 'slider') {
          smartInput = 'el-slider';
        } else if (type === 'switch') {
          smartInput = 'el-switch';
        } else if (type === 'select') {
          smartInput = 'el-select';
          children = this.smartElOptions(id);
        } else if (type === 'datetimePicker') {
          smartInput = 'el-date-picker';
          if (props) {
            props.type = 'datetime';
          } else {
            props = { type: 'datetime' };
          }
          value = formatDate(value);
          this.row[id] = moment(value).format('YYYY-MM-DD HH:mm:ss');
          picker = true;
        } else if (type === 'datePicker') {
          smartInput = 'el-date-picker';
          value = formatDate(value);
          picker = true;
        } else if (type === 'timePicker') {
          smartInput = 'el-time-picker';
          const [h, m, s] = value.split(':');
          const date = new Date();
          date.setHours(h);
          date.setMinutes(m);
          date.setSeconds(s);
          value = formatDate(date);
          picker = true;
        } else {
          smartInput = 'el-input';
        }
        return createElement(
          'el-form-item',
          {
            style: this.formItemStyle,
            props: {
              disabled,
              label: name,
              prop: id,
              rules,
            },
          },
          [
            createElement(
              smartInput,
              {
                style: {
                  width: `${ parseFloat(this.formItemStyle.width) * parseFloat(this.formItemStyle.totalWidth) / 100 - 180 }px`,
                },
                ref: id,
                attrs: {
                  ...props,
                },
                props: {
                  ...props,
                  disabled,
                  value,
                },
                on: {
                  blur: evt => this.handleBlur(evt, id, picker),
                  change: val => this.handleInputChange(val, id),
                  input: val => this.handleInputChange(val, id),
                },
              },
              children,
            )
          ]
        );
      });
    },
  },
  render(h) {
    return h(
      'el-form',
      {
        props: {
          inline: true,
          labelWidth: this.formLabelWidth,
          model: this.row,
        },
        on: {
          input(event) {
            this.$emit('input', event.target.value);
          },
        },
      },
      this.smartFormItem(h),
    );
  },
};
</script>
