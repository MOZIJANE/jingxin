import request from '@/request';
// import { compareAgv } from '@/utils/utils';

const apiMenu = '/menu';
const apiAlarm = '/alarm';
const apiUser = '/auth';

/**
 * get menu module
 */

export async function getMenu() {
  return request.get(`${apiMenu}/load`);
}


/**
 * alarm module
 */

export async function getAlarms() {
  return request.get(`${apiAlarm}/count`);
}

export async function getAlarmInfo(level) {
  return request.get(`${apiAlarm}/levelInfo`, {
    params: { level },
  });
}


/**
 * user module
 */

export async function login(domain, user, password) {
  return request.post(`${apiUser}/login`, {
    domain,
    user,
    password,
  });
}

export async function logout() {
  return request.post(`${apiUser}/logout`);
}

export async function getInfo(info) {
  return request({
    url: `${apiUser}/userInfo`,
    method: 'GET',
    params: { method: 'update' },
    data: { ...info },
  });
}


/**
 * bigtable module
 */

export async function getBigTable(table) {
  return request.get(`/monitor/bigtable?table=${table}`);
}


/**
 * real time chart module
 */

export async function getRealTimeChart(url, dateRangeLastSec, dateRangeRequestId) {
  const options = {
    method: 'GET',
    headers: { 'content-type': 'application/x-www-form-urlencoded' },
    url,
    params: {
      dateRangeLastSec,
      dateRangeRequestId,
    },
  };
  return request(options);
}

/**
 * global devices
 */

export async function getDevices() {
  return request.get('/global/devices');
}

/**
 * AGV CONTROL SERVICES
 */

export async function getAgvList() {
  return request.get('/factory/agvlist');
}

/**
 * agv 请求 AGV 准备上料
 */
export async function requestAgv() {
  return request.post('/agv/request');
}

export async function getFloors() {
  return request.get('map/floor');
}

export async function getMapStatic(floorId) {
  return request.get(`/map/load?floor=${floorId}`);
}

export async function getMapLock(floorId) {
  return request.get(`/map/lock?floor=${floorId}`);
}

export async function getMapDynamic(floorId) {
  return request.get(`/map/working?floor=${floorId}`);
}

export async function getMapHistory(floorId) {
  return request.get(`/map/worked?floor=${floorId}`);
}

export async function getPositionInfo(floorId) {
  return request.get(`/agv/position?floor=${floorId}`);
}

export async function wmqttCreate({ session, maxSize, timeSec }) {
  return request.get('wmqtt/create', {
    params: {
      session,
      maxSize,
      timeSec,
    },
  });
}

export async function getCADInfo(floorId) {
  return request.get('map/get', {
    params: {
      name: floorId,
    },
  });
}

export async function saveCADInfo(pName, pScale, pOffsetX, pOffsetY, pRotateX, pRotateY, pTheta) {
  return request.get('map/save', {
    params: {
      name: pName,
      scale: pScale,
      offsetX: pOffsetX,
      offsetY: pOffsetY,
      rotateX: pRotateX,
      rotateY: pRotateY,
      theta: pTheta,
    },
  });
}

/**
 * @param {string} topic ['agv/battery', 'map/block', 'map/working']
 */
export async function wmqttRegister({ session, topic }) {
  return request.get('wmqtt/register', {
    params: {
      session,
      topic,
    },
  });
}

export async function wmqttGet(session) {
  return request.get('wmqtt/get', {
    params: {
      session,
    },
  });
}

export async function wmqtt($vm, { session, topics, maxSize = 10, timeSec = 1200, frequency = 1000 }) {
  const createResult = await wmqttCreate({ session, maxSize, timeSec });

  if (createResult && createResult.errorno === 0) {
    topics.forEach(async (topic) => {
      await wmqttRegister({ session, topic });
    });

    $vm.wmqtt.intervals = setInterval(async () => {
      const getResult = await wmqttGet(session);

      if (!getResult || getResult.errorno === -1001) {
        clearInterval($vm.wmqtt.intervals);
        wmqtt({ session, topics, maxSize, timeSec, frequency });
      } else {
        const { data, topic } = getResult;
        if (topic) {
          const arr = topic.split('/');
          const key = `${arr[0]}/${arr[2]}`;
          // const specialTopics = ['scadaTask', 'basket', 'add', 'status'];
          // if (specialTopics.includes(arr[2])) {
          $vm.wmqtt[key] = data;
          // eslint-disable-next-line
          // console.log(arr[2], data);
          // }
          // else {
          //   $vm.wmqtt[key] = data.sort(compareAgv);
          // }
        }
      }
    }, frequency);
  }
}

export async function getAgvStatus(agv) {
  return request.get('/agv/status', {
    params: { agv },
  });
}

export async function getTaskList(floorId) {
  return request.get('/agv/tasklist', {
    params: { floorId },
  });
}

export async function getBasketList(floorId) {
  return request.get('/agv/agvs', {
    params: { floorId },
  });
}

export async function getAgvStatusList(floorId) {
  return request.get(`/agv/agvStatusList?mapId=${floorId}`);
}

export async function getTableData(table) {
  return request.get('/scadaCtrl/object', {
    params: {
      table,
      method: 'query',
    },
  });
}

export async function callAgv({ type, sn, eid }) {
  return request.get('/agv/action', {
    params: { type, sn, eid },
  });
}

/**
 * agv 设置料框
 */
export async function setTrays({ sn, basket }) {
  return request.post('/agv/basket', {
    sn,
    basket,
  });
}

export async function resetBasket({ agvId, basket }) {
  return request.post('/agv/resetBasket', {
    agvId,
    basket,
  });
}

/**
 * scada cncFeed
 */
export async function cncFeed({
  type,
  sn,
  eid,
  pos,
  gid1,
  gid2,
}) {
  return request.get('/scada/cncFeed', {
    params: {
      type,
      sn,
      eid,
      pos,
      gid1,
      gid2,
    },
  });
}

export async function binFeed({
  type,
  sn,
  eid,
  gid1,
  gid2,
}) {
  return request.get('/scada/binFeed', {
    params: {
      type,
      sn,
      eid,
      gid1,
      gid2,
    },
  });
}

export async function cncPreparation({ type, sn, gid }) {
  return request.get('/scada/preparation', {
    params: { type, sn, gid },
  });
}

export async function cncLoad({ type, sn, eid, pos }) {
  return request.get('/scada/cncLoad', {
    params: { type, sn, eid, pos },
  });
}

export async function cncUnload({ type, sn, eid, pos, gid }) {
  return request.get('/scada/cncUnload', {
    params: { type, sn, eid, pos, gid },
  });
}

export async function agvUnlock(agv) {
  return request.get('/agv/release', {
    params: { agv },
  });
}

export async function agvGoHome(agv) {
  return request.get('/agv/goHome', {
    params: {
      agv,
      getLock: true,
    },
  });
}

/**
 * feed 手动叫料
 */
export async function getSeats() {
  return request.get('/agv/seat');
}

export async function setFeed({ seat1, location1, floorId1, direction1, seat2, location2, floorId2, direction2 }) {
  return request.post('/agv/feed', {
    seat1,
    location1,
    floorId1,
    direction1,
    seat2,
    location2,
    floorId2,
    direction2,
  });
}

export async function getAgv() {
  return request.get('/agv/agvList');
}
