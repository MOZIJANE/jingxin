/* eslint-disable no-param-reassign */
export const translate2d = {
  bind(el, binding) {
    el.onmousedown = (e) => {
      const x0 = e.clientX;
      const y0 = e.clientY;
      document.onmousemove = ({ clientX, clientY }) => {
        const dx = clientX - x0;
        const dy = clientY - y0;
        binding.value({
          x0,
          y0,
          dx,
          dy,
        });
      };
      document.onmouseup = () => {
        document.onmousemove = null;
        document.onmouseup = null;
      };
    };
  },
};

export const drag = {
  bind(el, binding) {
    el.onmousedown = (e) => {
      el.style.cursor = 'move';
      const x0 = e.clientX;
      const y0 = e.clientY;
      const { cx, cy } = e.target.attributes;
      const cx0 = Number(cx.value);
      const cy0 = Number(cy.value);
      document.onmousemove = ({ clientX, clientY, pageX, pageY }) => {
        const dx = clientX - x0;
        const dy = clientY - y0;
        // 将此时的位置传出去
        binding.value({
          x: pageX,
          y: pageY,
          x0,
          y0,
          cx0,
          cy0,
          dx,
          dy,
        });
      };
      document.onmouseup = () => {
        el.style.cursor = 'pointer';
        document.onmousemove = null;
        document.onmouseup = null;
      };
    };
  },
};

export const dragMap = {
  bind(el, binding) {
    el.onmousedown = (e) => {
      const x0 = e.clientX;
      const y0 = e.clientY;
      document.onmousemove = ({ clientX, clientY }) => {
        const dx = clientX - x0;
        const dy = clientY - y0;
        // 将此时的位置传出去
        binding.value({
          dx,
          dy,
        });
      };
      document.onmouseup = () => {
        document.onmousemove = null;
        document.onmouseup = null;
      };
    };
  },
};
