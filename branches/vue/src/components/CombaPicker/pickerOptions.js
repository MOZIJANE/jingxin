const now = new Date();
const oneDay = 1000 * 60 * 60 * 24;

const shortcuts = [
  {
    text: '上一天',
    onClick(picker) {
      const start = new Date(
        now.getFullYear(),
        now.getMonth(),
        now.getDate(),
        0,
        0,
        0,
      );
      const end = new Date(
        now.getFullYear(),
        now.getMonth(),
        now.getDate(),
        23,
        59,
        59,
      );
      start.setTime(start.getTime() - oneDay);
      end.setTime(end.getTime() - oneDay);
      picker.$emit('pick', [start, end]);
    },
  },
  {
    text: '最近一周',
    onClick(picker) {
      const start = new Date(
        now.getFullYear(),
        now.getMonth(),
        now.getDate(),
        0,
        0,
        0,
      );
      const end = new Date(
        now.getFullYear(),
        now.getMonth(),
        now.getDate(),
        23,
        59,
        59,
      );
      start.setTime(start.getTime() - oneDay * 7);
      picker.$emit('pick', [start, end]);
    },
  },
  {
    text: '最近一个月',
    onClick(picker) {
      const start = new Date(
        now.getFullYear(),
        now.getMonth(),
        now.getDate(),
        0,
        0,
        0,
      );
      const end = new Date(
        now.getFullYear(),
        now.getMonth(),
        now.getDate(),
        23,
        59,
        59,
      );
      start.setTime(start.getTime() - oneDay * 30);
      picker.$emit('pick', [start, end]);
    },
  },
  {
    text: '最近三个月',
    onClick(picker) {
      const start = new Date(
        now.getFullYear(),
        now.getMonth(),
        now.getDate(),
        0,
        0,
        0,
      );
      const end = new Date(
        now.getFullYear(),
        now.getMonth(),
        now.getDate(),
        23,
        59,
        59,
      );
      start.setTime(start.getTime() - oneDay * 90);
      picker.$emit('pick', [start, end]);
    },
  },
  {
    text: '最近半年',
    onClick(picker) {
      const start = new Date(
        now.getFullYear(),
        now.getMonth(),
        now.getDate(),
        0,
        0,
        0,
      );
      const end = new Date(
        now.getFullYear(),
        now.getMonth(),
        now.getDate(),
        23,
        59,
        59,
      );
      start.setTime(start.getTime() - oneDay * 180);
      picker.$emit('pick', [start, end]);
    },
  },
  {
    text: '最近一年',
    onClick(picker) {
      const start = new Date(
        now.getFullYear(),
        now.getMonth(),
        now.getDate(),
        0,
        0,
        0,
      );
      const end = new Date(
        now.getFullYear(),
        now.getMonth(),
        now.getDate(),
        23,
        59,
        59,
      );
      start.setTime(start.getTime() - oneDay * 365);
      picker.$emit('pick', [start, end]);
    },
  },
];

export default shortcuts;
