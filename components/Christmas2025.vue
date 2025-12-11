<template>
  <!-- 
    修复点 1: 
    @touchstart.prevent.stop="handleAction" 
    .prevent 阻止默认滚动/缩放
    .stop 阻止事件冒泡
  -->
  <div 
    class="snowman-game-wrapper" 
    @mousedown="handleAction" 
    @touchstart.prevent.stop="handleAction"
  >
    <!-- 背景装饰 -->
    <div class="background-decor">
      <div class="moon"></div>
      <div class="snow-particle" v-for="n in 20" :key="n"></div>
    </div>

    <!-- 游戏区域 -->
    <div class="game-viewport">
      <div class="game-world" :style="worldStyle">
        
        <!-- 已经堆好的雪块 -->
        <div 
          v-for="(block, index) in stack" 
          :key="index"
          class="snow-block"
          :class="{ 'base-block': index === 0, 'perfect-glow': block.isPerfect }"
          :style="{ 
            width: block.width + 'px', 
            left: block.left + 'px',
            bottom: (index * blockHeight) + 'px',
            height: blockHeight + 'px',
            zIndex: index
          }"
        >
          <span v-if="index > 0 && index % 3 === 0" class="button-decor">⚫</span>
        </div>

        <!-- 当前正在移动的雪块 -->
        <div 
          v-if="isPlaying && currentBlock"
          class="snow-block active-block"
          :style="{ 
            width: currentBlock.width + 'px', 
            left: currentBlock.left + 'px',
            bottom: (stack.length * blockHeight) + 'px',
            height: blockHeight + 'px'
          }"
        >
          <div class="face-preview">
            <span class="eye">.</span><span class="eye">.</span>
          </div>
        </div>

        <!-- 失败时的帽子 -->
        <div 
          v-if="!isPlaying && stack.length > 0" 
          class="top-hat"
          :style="{
            left: (stack[stack.length-1].left + stack[stack.length-1].width/2 - 20) + 'px',
            bottom: (stack.length * blockHeight) + 'px'
          }"
        >
          🎩
        </div>
      </div>
    </div>

    <!-- UI 界面 -->
    <div class="ui-layer">
      <div v-if="isPlaying" class="score-board">{{ score }} 层</div>
      
      <transition name="fade-menu">
        <div v-if="showResult" class="menu-overlay">
          <h2 class="game-title">⛄ 雪人堆堆乐 ⛄</h2>
          
          <div class="result-box">
             <p class="final-score">最终高度: {{ score }} 层</p>
             <p class="high-score">最高记录: {{ highScore }}</p>
             <div class="comment">{{ getComment(score) }}</div>
          </div>

          <!-- 
            修复点 2: 按钮也需要处理 touchstart，防止点击穿透或无响应 
            .stop 防止触发外层的 handleAction
          -->
          <button 
            class="start-btn" 
            @click.stop="startGame" 
            @touchstart.stop="startGame"
          >
            {{ score > 0 ? '再堆一个' : '开始堆雪人' }}
          </button>
          <p class="tips">点击屏幕放置雪块</p>
        </div>
      </transition>

      <transition name="fade">
        <div v-if="showPerfectText" class="perfect-text">完美!</div>
      </transition>
    </div>
  </div>
</template>

<script>
export default {
  name: 'SnowmanGame',
  data() {
    return {
      isPlaying: false,
      showResult: true,
      
      score: 0,
      highScore: 0,
      
      gameWidth: 300,
      blockHeight: 40,
      baseWidth: 200,
      moveSpeed: 2,
      
      stack: [],
      currentBlock: null,
      
      worldOffset: 0,
      worldScale: 1,
      
      animationFrame: null,
      showPerfectText: false,
      perfectTimer: null
    };
  },
  computed: {
    worldStyle() {
      return {
        transform: `translateY(${this.worldOffset}px) scale(${this.worldScale})`,
        transformOrigin: 'bottom center'
      };
    }
  },
  mounted() {
    const saved = localStorage.getItem('snowman-highscore');
    if (saved) this.highScore = parseInt(saved);
    window.addEventListener('keydown', this.handleKeydown);
    
    // 初始化时根据屏幕宽度调整 gameWidth，适配手机屏幕
    if (window.innerWidth < 400) {
      this.gameWidth = window.innerWidth - 40; // 留出边距
    }
    
    this.stack = [{ width: this.baseWidth, left: (this.gameWidth - this.baseWidth) / 2 }];
  },
  beforeDestroy() {
    this.stopGame(true);
    window.removeEventListener('keydown', this.handleKeydown);
  },
  methods: {
    startGame() {
      // 防止重复触发
      if (this.isPlaying) return;

      // 1. 先隐藏菜单，让玩家感觉到点击生效了
      this.showResult = false;

      // 2. 重置数据
      this.stack = [
        { width: this.baseWidth, left: (this.gameWidth - this.baseWidth) / 2, isPerfect: false }
      ];
      this.score = 0;
      this.worldOffset = 0;
      this.worldScale = 1;
      this.moveSpeed = 2;
      
      // --- 核心修复点 ---
      // 延迟 300ms 再将 isPlaying 设为 true。
      // 在这 300ms 内，如果发生了“点击穿透”，handleAction 会因为 isPlaying 为 false 而直接 return，
      // 从而忽略掉那个错误的点击。
      setTimeout(() => {
        this.spawnNextBlock();
        this.isPlaying = true;
        this.gameLoop();
      }, 300);
    },

    stopGame(forceSkip = false) {
      this.isPlaying = false;
      cancelAnimationFrame(this.animationFrame);
      
      if (this.score > this.highScore) {
        this.highScore = this.score;
        localStorage.setItem('snowman-highscore', this.highScore);
      }

      if (forceSkip) return;

      setTimeout(() => {
        this.performOverviewZoom();
      }, 600);
    },

    performOverviewZoom() {
      const totalHeight = (this.stack.length + 2) * this.blockHeight;
      const viewportHeight = 500;
      const padding = 40; 

      if (totalHeight > (viewportHeight - padding)) {
        const scale = (viewportHeight - padding) / totalHeight;
        this.worldScale = scale;
      } else {
        this.worldScale = 1;
      }
      
      this.worldOffset = 0;

      setTimeout(() => {
        this.showResult = true;
      }, 1000);
    },

    handleAction(e) {
      // 兼容性处理：如果是触摸事件，阻止默认行为
      if (e && e.type === 'touchstart') {
        // e.preventDefault(); // 已在模板中使用 .prevent
      }

      if (this.showResult) return;
      if (!this.isPlaying) return;
      
      this.placeBlock();
    },

    handleKeydown(e) {
      if (e.code === 'Space') {
e.preventDefault();
        if (this.showResult) {
          this.startGame();
        } else {
          this.handleAction();
        }
      }
    },

    spawnNextBlock() {
      const prevBlock = this.stack[this.stack.length - 1];
      this.currentBlock = {
        width: prevBlock.width,
        left: 0,
        direction: 1 
      };
    },

    gameLoop() {
      if (!this.isPlaying) return;

      const maxLeft = this.gameWidth - this.currentBlock.width;
      
      this.currentBlock.left += this.moveSpeed * this.currentBlock.direction;

      if (this.currentBlock.left >= maxLeft) {
        this.currentBlock.left = maxLeft;
        this.currentBlock.direction = -1;
      } else if (this.currentBlock.left <= 0) {
        this.currentBlock.left = 0;
        this.currentBlock.direction = 1;
      }

      this.animationFrame = requestAnimationFrame(this.gameLoop);
    },

    placeBlock() {
      const prevBlock = this.stack[this.stack.length - 1];
      const current = this.currentBlock;
      
      const diff = current.left - prevBlock.left;
      const absDiff = Math.abs(diff);
      
      if (absDiff > current.width) {
        this.stopGame();
        return;
      }

      let newWidth = current.width - absDiff;
      let newLeft = current.left;
      let isPerfect = false;

      if (absDiff < 3) {
        newWidth = current.width;
        newLeft = prevBlock.left;
        isPerfect = true;
        this.triggerPerfectEffect();
      } else {
        if (diff > 0) {
          newLeft = current.left;
        } else {
          newLeft = prevBlock.left;
        }
      }

      this.stack.push({
        width: newWidth,
        left: newLeft,
        isPerfect
      });

      this.score++;
      if (this.score % 5 === 0) this.moveSpeed += 0.5;

      if (this.stack.length > 4) {
        this.worldOffset = (this.stack.length - 4) * this.blockHeight;
      }

      this.spawnNextBlock();
    },

    triggerPerfectEffect() {
      this.showPerfectText = true;
      if (this.perfectTimer) clearTimeout(this.perfectTimer);
      this.perfectTimer = setTimeout(() => {
        this.showPerfectText = false;
      }, 800);
    },

    getComment(score) {
      if (score < 3) return "刚开始堆就倒了...";
      if (score < 10) return "是个不错的雪墩子！";
      if (score < 20) return "这雪人真高！";
      return "你是堆雪人之神！";
    }
  }
};
</script>

<style scoped>
.snowman-game-wrapper {
  position: relative;
  width: 100%;
  max-width: 400px;
  height: 600px;
  margin: 0 auto;
  background: linear-gradient(to bottom, #0f2027, #203a43, #2c5364);
  overflow: hidden;
  border-radius: 12px;
  
  /* 修复点 3: 关键 CSS 属性，优化移动端体验 */
  user-select: none; /* 禁止选中文本 */
  -webkit-user-select: none;
  touch-action: none; /* 禁止浏览器默认手势(如双击缩放、滚动) */
  -webkit-tap-highlight-color: transparent; /* 去除点击高亮背景 */
  
  font-family: 'Arial', sans-serif;
  color: white;
  box-shadow: 0 10px 30px rgba(0,0,0,0.5);
}

.background-decor {
  position: absolute;
  top: 0; left: 0; width: 100%; height: 100%;
  pointer-events: none;
}
.moon {
  position: absolute;
  top: 30px; right: 30px;
  width: 50px; height: 50px;
  background: #fdfbf7;
  border-radius: 50%;
  box-shadow: 0 0 20px #fdfbf7;
}

.game-viewport {
  position: absolute;
  bottom: 0;
  left: 0;
  width: 100%;
  height: 500px;
  overflow: hidden;
  pointer-events: none; /* 让点击穿透到 wrapper */
}

.game-world {
  position: absolute;
  bottom: 0;
  left: 0;
  width: 100%;
  height: 100%;
  transition: transform 1s cubic-bezier(0.25, 0.46, 0.45, 0.94);
  transform-style: preserve-3d; 
}

.snow-block {
  position: absolute;
  background: #fff;
  border-radius: 4px;
  box-shadow: inset -5px -5px 10px rgba(0,0,0,0.1);
  transition: background 0.2s;
}

.base-block {
  border-radius: 10px 10px 4px 4px;
  background: #eef2f3;
}

.active-block {
  background: #f0f8ff;
  box-shadow: 0 0 10px rgba(255, 255, 255, 0.8);
}

.perfect-glow {
  background: #d4fc79;
  box-shadow: 0 0 15px #d4fc79;
}

.button-decor {
  position: absolute;
  left: 50%;
  top: 50%;
  transform: translate(-50%, -50%);
  font-size: 12px;
  color: #333;
}

.face-preview {
  display: flex;
  justify-content: center;
  gap: 10px;
  padding-top: 5px;
  color: #333;
  font-weight: bold;
}

.top-hat {
  position: absolute;
  font-size: 40px;
  z-index: 100;
  animation: dropIn 0.5s cubic-bezier(0.175, 0.885, 0.32, 1.275);
}

@keyframes dropIn {
  from { transform: translateY(-50px) scale(0.5); opacity: 0; }
  to { transform: translateY(0) scale(1); opacity: 1; }
}

.ui-layer {
  position: absolute;
  top: 0; left: 0; width: 100%; height: 100%;
  pointer-events: none;
  z-index: 200;
}

.score-board {
  position: absolute;
  top: 20px;
  left: 20px;
  font-size: 24px;
  font-weight: bold;
  text-shadow: 0 2px 4px rgba(0,0,0,0.5);
}

.menu-overlay {
  position: absolute;
  top: 0; left: 0; width: 100%; height: 100%;
  background: rgba(0, 0, 0, 0.7);
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  pointer-events: auto;
  backdrop-filter: blur(5px);
}

.game-title {
  font-size: 32px;
  margin-bottom: 30px;
  color: #a8edea;
}

.result-box {
  background: rgba(255,255,255,0.1);
  padding: 20px;
  border-radius: 10px;
  text-align: center;
  margin-bottom: 30px;
  border: 1px solid rgba(255,255,255,0.2);
}

.final-score { font-size: 28px; margin: 10px 0; font-weight: bold; }
.high-score { font-size: 16px; color: #ccc; }
.comment { margin-top: 15px; color: #fed6e3; font-style: italic; }

.start-btn {
  padding: 15px 40px;
  font-size: 20px;
  background: #ff6b6b;
  color: white;
  border: none;
  border-radius: 30px;
  cursor: pointer;
  transition: transform 0.1s, background 0.2s;
  box-shadow: 0 5px 15px rgba(255, 107, 107, 0.4);
  /* 确保按钮在移动端容易点击 */
  touch-action: manipulation;
}
.start-btn:active { transform: scale(0.95); }
.start-btn:hover { background: #ff5252; }

.tips { margin-top: 20px; font-size: 14px; opacity: 0.7; }

.perfect-text {
  position: absolute;
  top: 15%;
  left: 50%;
  transform: translateX(-50%);
  font-size: 36px;
  color: #ffd700;
  font-weight: bold;
  text-shadow: 0 0 10px rgba(255, 215, 0, 0.8);
}

.fade-menu-enter-active, .fade-menu-leave-active { transition: opacity 0.5s; }
.fade-menu-enter, .fade-menu-leave-to { opacity: 0; }

.fade-enter-active, .fade-leave-active { transition: opacity 0.3s, transform 0.3s; }
.fade-enter { opacity: 0; transform: translate(-50%, 20px); }
.fade-leave-to { opacity: 0; transform: translate(-50%, -20px); }

.snow-particle {
  position: absolute;
  background: white;
  border-radius: 50%;
  opacity: 0.6;
  width: 4px; height: 4px;
  top: -10px;
  animation: fall linear infinite;
}
.snow-particle:nth-child(odd) { width: 6px; height: 6px; animation-duration: 4s; }
.snow-particle:nth-child(even) { animation-duration: 6s; animation-delay: 1s; }
@keyframes fall {
  to { transform: translateY(600px); }
}
</style>
