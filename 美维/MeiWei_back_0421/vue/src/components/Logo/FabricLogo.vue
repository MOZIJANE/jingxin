<template>
  <div class="fabric-logo">
    <div class="fabric-bg"></div>
    <div class="fabric-layer-3">
      <div></div>
    </div>
    <div class="fabric-layer-2">
      <div></div>
    </div>
    <div class="fabric-layer-1">
      <div></div>
    </div>
    <div class="fabric-layer-0">
      <div></div>
    </div>
  </div>
</template>

<style scoped>
body {
  background: #000;
}

.fabric-logo{
  position:relative;
  height:230px;
  margin-bottom:20px;
  margin-top:20px
}
.fabric-logo .fabric-bg{
  /* background:url("https://get.fabric.io/assets/fabric-logo-210af7e14986c60f3862c46a29c4984b.png") center top no-repeat; */
  height:300px;
  opacity:0;
  transition:opacity 5s
}
.fabric-logo .fabric-bg.fadeIn{
  opacity:1
}
.fabric-logo .fabric-layer-0,
.fabric-logo .fabric-layer-1,
.fabric-logo .fabric-layer-2,
.fabric-logo .fabric-layer-3{
  position:absolute;
  top:0;
  left:50%;
  transition:opacity 1s;opacity:0
}
.fabric-logo .fabric-layer-0.fadeOut,
.fabric-logo .fabric-layer-1.fadeOut,
.fabric-logo .fabric-layer-2.fadeOut,
.fabric-logo .fabric-layer-3.fadeOut{
  opacity:0
}
.fabric-logo .fabric-layer-0{
  z-index:0;
  top:175px;
  opacity:.5;
  transform-origin:0% 100%;
  animation:bouncedown 1s ease 1s forwards
}
.fabric-logo .fabric-layer-0>div{
  opacity:0;
  transform-origin:0% 0%;
  animation-name:spinvert;
  animation-duration:.5s;
  animation-delay:1s;
  animation-fill-mode:forwards;
  animation-timing-function:ease;
  animation-iteration-count:1
}
.fabric-logo .fabric-layer-0>div:after{
  content:'';
  display:block;
  background:rgba(0,0,0,0.6);
  width:55px;
  height:55px;
  border-radius:4px;
  transform:translateX(-50%) rotateX(45deg) rotateZ(45deg);
  box-shadow:0px 0px 14px 16px rgba(0,0,0,0.6)
}
.fabric-logo .fabric-layer-1{
  z-index:1;
  top:126px;
  opacity:1;
  transform-origin:0% 100%;
  animation:bounce 1s ease 1s forwards
}
.fabric-logo .fabric-layer-1>div{
  opacity:0;
  transform-origin:0% 0%;
  animation-name:spinvert;
  animation-duration:.5s;
  animation-delay:1s;
  animation-fill-mode:forwards;
  animation-timing-function:ease;
  animation-iteration-count:1
}
.fabric-logo .fabric-layer-1>div:after{
  content:'';
  display:block;
  background:#00479d;
  width:104px;
  height:104px;
  border-radius:15px;
  transform:translateX(-50%) rotateX(49deg) rotateZ(45deg);
  border-right:1px solid #004ba6;
  border-bottom:1px solid #004ba6;
  box-shadow:3px 3px 7px -1px rgba(0,0,0,0.2)
}
.fabric-logo .fabric-layer-2{
  z-index:2;
  top:53px;
  opacity:1;
  transform:translateY(30px);
  animation:bounce 1s ease 1.5s forwards;
  transition-timing-function:cubic-bezier(0.215, 0.61, 0.355, 1);
  transform-origin:0% 100%
}
.fabric-logo .fabric-layer-2>div{
  opacity:0;
  transform-origin:0% 0%;
  animation-name:spinvert;
  animation-duration:.5s;
  animation-delay:1.5s;
  animation-fill-mode:forwards;
  animation-timing-function:ease;
  animation-iteration-count:1
}
.fabric-logo .fabric-layer-2>div:after{
  content:'';
  display:block;
  background:#55acee;
  width:148px;
  height:148px;
  border-radius:23px;
  transform:translateX(-50%) rotateX(49deg) rotateZ(45deg);
  border-right:1px solid #63baf8;
  border-bottom:1px solid #63baf8;box-shadow:3px 3px 7px -1px rgba(0,0,0,0.2)
}
.fabric-logo .fabric-layer-3{
  z-index:3;
  opacity:0.8;
  top:-11px;
  transform:translate3d(0, 30px, 0);
  animation-name:bounce;
  animation-duration:1s;
  animation-timing-function:ease;
  animation-delay:2s;
  animation-fill-mode:forwards;
  transition-timing-function:cubic-bezier(0.215, 0.61, 0.355, 1);
  transform-origin:0% 100%
}
.fabric-logo .fabric-layer-3>div{
  opacity:0;
  transform-origin:0% 0%;
  animation-name:spinvert;
  animation-duration:.5s;
  animation-delay:2s;
  animation-fill-mode:forwards;
  animation-timing-function:ease;
  animation-iteration-count:1
}
.fabric-logo .fabric-layer-3>div:after{
  content:'';
  display:block;
  width:175px;
  height:175px;
  border-radius:25px;
  transform:translateX(-50%) rotateX(48deg) rotateZ(45deg);
  border-top:1px solid #63baf8;
  border-right:1px solid #63baf8;
  border-bottom:1px solid #63baf8;
  box-shadow:3px 3px 7px -1px rgba(0,0,0,0.2);
  border:1px solid #fff;
  background:#216193;
  background:linear-gradient(135deg,
  rgba(10,80,139,0.6) 0%,
  rgba(41,105,159,0.6) 42%,
  rgba(182,213,233,0.7) 100%
  );
  }
@keyframes appear{
  0%{
    opacity:0
  }
  100%{
    opacity:1
  }
}
@keyframes spinvert{
  0%{
    opacity:.5;
    transform:translateY(50px) rotateY(0deg) rotateX(0deg) scale(0.8, 0.8)
  }
  100%{
    opacity:1;
    transform:translateY(0px) rotateY(180deg) rotateX(0deg) scale(1, 1)
  }
}
@keyframes bounce{
  0%{
    transform:translate3d(0, 30px, 0)
  }
  5%{
    transform:translate3d(0, -25px, 0)
  }
  10%{
    transform:translate3d(0, 15px, 0)
  }
  15%{
    transform:translate3d(0, -15px, 0)
  }
  20%{
    transform:translate3d(0, 10px, 0)
  }
  25%{
    transform:translate3d(0, -10px, 0)
  }
  30%{
    transform:translate3d(0, 5px, 0)
  }
  35%{
    transform:translate3d(0, -5px, 0)
  }
  40%{
    transform:translate3d(0, 5px, 0)
  }
  45%{
    transform:translate3d(0, -3px, 0)
  }
  50%{
    transform:translate3d(0, 3px, 0)
  }
  55%{
    transform:translate3d(0, -3px, 0)
  }
  60%{
    transform:translate3d(0, 3px, 0)
  }
  65%{
    transform:translate3d(0, -1px, 0)
  }
  80%{
    transform:translate3d(0, 1px, 0)
  }
  100%{
    transform:translate3d(0, 0px, 0)
  }
}
@keyframes bouncedown{
  0%{transform:translate3d(0, -30px, 0) scale(1.3);opacity:0.6}
  5%{transform:translate3d(0, 25px, 0) scale(0.85);opacity:0.3}
  10%{transform:translate3d(0, -15px, 0) scale(1.15);opacity:.6}
  15%{transform:translate3d(0, 15px, 0) scale(0.85);opacity:.3}
  20%{transform:translate3d(0, -10px, 0) scale(1.1);opacity:.55}
  25%{transform:translate3d(0, 10px, 0) scale(0.9);opacity:.35}
  30%{transform:translate3d(0, -5px, 0) scale(1.05);opacity:.55}
  35%{transform:translate3d(0, 5px, 0) scale(0.95);opacity:.4}
  40%{transform:translate3d(0, -5px, 0) scale(1.05);opacity:.55}
  45%{transform:translate3d(0, 3px, 0) scale(0.97);opacity:.4}
  50%{transform:translate3d(0, -3px, 0) scale(1.03);opacity:.55}
  55%{transform:translate3d(0, 3px, 0) scale(0.97);opacity:.4}
  60%{transform:translate3d(0, -3px, 0) scale(1.03);opacity:.55}
  65%{transform:translate3d(0, 1px, 0) scale(0.99);opacity:.45}
  80%{transform:translate3d(0, -1px, 0) scale(1.01);opacity:.5}
  100%{transform:translate3d(0, 0px, 0) scale(1);opacity:.5}
}
@keyframes shake{
  0%{transform:translate3d(30px, 0, 0)}
  5%{transform:translate3d(-25px, 0, 0)}
  10%{transform:translate3d(15px, 0, 0)}
  15%{transform:translate3d(-15px, 0, 0)}
  20%{transform:translate3d(10px, 0, 0)}
  25%{transform:translate3d(-10px, 0, 0)}
  30%{transform:translate3d(5px, 0, 0)}
  35%{transform:translate3d(0px, 0, 0)}
  40%{transform:translate3d(5px, 0, 0)}
  45%{transform:translate3d(-3px, 0, 0)}
  50%{transform:translate3d(3px, 0, 0)}
  55%{transform:translate3d(-3px, 0, 0)}
  60%{transform:translate3d(3px, 0, 0)}
  65%{transform:translate3d(-1px, 0, 0)}
  80%{transform:translate3d(1px, 0, 0)}
  100%{transform:translate3d(0px, 0, 0)
  }
}
</style>

