<template>
  <div class="lottery-container">
    <div class="card">
      <h1 class="title">🎊 双十一超级大抽奖 🎊</h1>
      <p class="subtitle">100% 中奖率，人人有份！</p>

      <div class="prize-display">
        <div v-if="!spinning && !prize" class="placeholder">
          点击下方按钮开始抽奖
        </div>
        <div v-else-if="spinning" class="spinning prize-icon">
          🎰
        </div>
        <div v-else-if="prize">
          <div class="prize-icon">{{ prize.icon }}</div>
          <div class="prize-text">{{ prize.name }}</div>
        </div>
      </div>

      <button 
        class="btn" 
        @click="startLottery" 
        :disabled="spinning || claimed"
        v-if="!prize || claimed">
        {{ claimed ? '已参与抽奖' : (spinning ? '抽奖中...' : '立即抽奖') }}
      </button>

      <button 
        class="btn btn-claim" 
        @click="claimPrize"
        v-if="prize && !claimed">
        💰 立即领取奖品
      </button>

      <div class="countdown" v-if="!claimed">
        剩余名额：<span class="remaining-count">{{ remaining }}</span> 个
      </div>
    </div>

    <div class="modal" v-if="showModal" @click="closeModal">
      <div class="modal-content" @click.stop>
        <div class="modal-icon">{{ modalContent.icon }}</div>
        <div class="modal-title">{{ modalContent.title }}</div>
        <div class="modal-text" v-html="modalContent.text"></div>
        <button class="btn" @click="closeModal">{{ modalContent.buttonText }}</button>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'DoublelevenLottery',
  data() {
    return {
      spinning: false,
      prize: null,
      claimed: false,
      showModal: false,
      remaining: 9999,
      modalContent: {},
      countdownInterval: null,
      prizes: [
        { name: 'iPhone 15 Pro Max', icon: '📱', probability: 0.01 },
        { name: '戴森吹风机', icon: '💨', probability: 0.02 },
        { name: '现金红包 ¥1000', icon: '💰', probability: 0.03 },
        { name: 'AirPods Pro', icon: '🎧', probability: 0.04 },
        { name: '购物券 ¥500', icon: '🎫', probability: 0.1 },
        { name: '免单券', icon: '🎁', probability: 0.2 },
        { name: '幸运大奖', icon: '🎉', probability: 0.6 }
      ],
      funnyMessages: [
        {
          icon: '😏',
          title: '想得美！',
          text: '你以为真的有奖品？<br>这年头连商家都不相信童话了！<br><br>不过别灰心，再买点东西<br>说不定下次能中呢~（才怪）',
          buttonText: '我就知道'
        },
        {
          icon: '🤪',
          title: '恭喜你中奖啦！',
          text: '奖品是：<strong>一个深深的套路</strong><br><br>双十一最大的奖品<br>就是让你觉得自己省钱了<br>实际上花了更多钱 🤑',
          buttonText: '太真实了'
        },
        {
          icon: '😂',
          title: '领奖失败',
          text: '系统检测到你还不够穷<br>不符合领奖条件<br><br>建议：先把购物车清空<br>明年再来试试',
          buttonText: '哈哈哈哈'
        },
        {
          icon: '🙃',
          title: '奖品已过期',
          text: '很遗憾地通知你<br>该奖品已于昨天过期<br><br>（其实从来就没存在过）<br>欢迎明年双十一再来！',
          buttonText: '明年见'
        },
        {
          icon: '🎭',
          title: '中奖需知',
          text: '领取此奖品需要：<br>1. 转发500个群<br>2. 集齐88个赞<br>3. 支付99元手续费<br><br>还要继续吗？',
          buttonText: '算了算了'
        },
        {
          icon: '🤑',
          title: '温馨提示',
          text: '奖品已发放到你的账户<br><br>查看路径：<br>我的 → 优惠券 → 已过期 → 回收站<br>→ 404 Not Found',
          buttonText: '好家伙'
        }
      ]
    };
  },
  methods: {
    startLottery() {
      if (this.spinning) return;
      
      this.spinning = true;
      this.prize = null;

      // 模拟剩余名额快速减少
      const reduceInterval = setInterval(() => {
        this.remaining = Math.max(1, this.remaining - Math.floor(Math.random() * 50));
      }, 100);

      setTimeout(() => {
        clearInterval(reduceInterval);
        this.spinning = false;
        this.prize = this.getRandomPrize();
        this.remaining = Math.floor(Math.random() * 100) + 1;
      }, 2000);
    },
    getRandomPrize() {
      const random = Math.random();
      let cumulative = 0;
      
      for (let prize of this.prizes) {
        cumulative += prize.probability;
        if (random <= cumulative) {
          return prize;
        }
      }
      return this.prizes[this.prizes.length - 1];
    },
    claimPrize() {
      this.claimed = true;
      this.modalContent = this.funnyMessages[
        Math.floor(Math.random() * this.funnyMessages.length)
      ];
      this.showModal = true;
    },
    closeModal() {
      this.showModal = false;
    }
  },
  mounted() {
    // 模拟实时减少名额
    this.countdownInterval = setInterval(() => {
      if (this.remaining > 100 && !this.spinning) {
        this.remaining -= Math.floor(Math.random() * 3);
      }
    }, 3000);
  },
  beforeUnmount() {
    if (this.countdownInterval) {
      clearInterval(this.countdownInterval);
    }
  }
};
</script>

<style scoped>
.lottery-container {
  min-height: 100vh;
  display: flex;
  justify-content: center;
  align-items: center;
  padding: 20px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  font-family: 'Microsoft YaHei', Arial, sans-serif;
}

.card {
  width: 100%;
  max-width: 500px;
  background: white;
  border-radius: 20px;
  padding: 40px 30px;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
  text-align: center;
}

.title {
  font-size: 28px;
  font-weight: bold;
  color: #ff4757;
  margin-bottom: 10px;
  text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.1);
}

.subtitle {
  color: #666;
  margin-bottom: 30px;
  font-size: 14px;
}

.prize-display {
  background: linear-gradient(135deg, #ffd700 0%, #ffed4e 100%);
  border-radius: 15px;
  padding: 40px 20px;
  margin-bottom: 30px;
  min-height: 150px;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  position: relative;
  overflow: hidden;
}

.prize-display::before {
  content: '🎉';
  position: absolute;
  font-size: 100px;
  opacity: 0.1;
  animation: rotate 10s linear infinite;
}

@keyframes rotate {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

.placeholder {
  color: #666;
}

.prize-icon {
  font-size: 60px;
  margin-bottom: 15px;
  animation: bounce 1s ease infinite;
}

@keyframes bounce {
  0%, 100% { transform: translateY(0); }
  50% { transform: translateY(-10px); }
}

.prize-text {
  font-size: 24px;
  font-weight: bold;
  color: #ff4757;
  text-shadow: 1px 1px 2px rgba(0, 0, 0, 0.1);
}

.spinning {
  animation: spin 0.5s linear infinite;
}

@keyframes spin {
  from { transform: rotate(0deg) scale(1); }
  to { transform: rotate(360deg) scale(1.1); }
}

.btn {
  background: linear-gradient(135deg, #ff6b6b 0%, #ff4757 100%);
  color: white;
  border: none;
  border-radius: 50px;
  padding: 15px 50px;
  font-size: 18px;
  font-weight: bold;
  cursor: pointer;
  transition: all 0.3s ease;
  box-shadow: 0 5px 15px rgba(255, 71, 87, 0.4);
  margin: 10px;
}

.btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 20px rgba(255, 71, 87, 0.6);
}

.btn:active {
  transform: translateY(0);
}

.btn:disabled {
  background: #ccc;
  cursor: not-allowed;
  box-shadow: none;
}

.btn-claim {
  background: linear-gradient(135deg, #5f27cd 0%, #341f97 100%);
  box-shadow: 0 5px 15px rgba(95, 39, 205, 0.4);
  animation: pulse 2s ease infinite;
}

@keyframes pulse {
  0%, 100% { transform: scale(1); }
  50% { transform: scale(1.05); }
}

.btn-claim:hover {
  box-shadow: 0 8px 20px rgba(95, 39, 205, 0.6);
}

.countdown {
  font-size: 14px;
  color: #999;
  margin-top: 20px;
}

.remaining-count {
  color: #ff4757;
  font-weight: bold;
}

.modal {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(0, 0, 0, 0.7);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
  animation: fadeIn 0.3s ease;
}

@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}

.modal-content {
  background: white;
  border-radius: 20px;
  padding: 40px 30px;
  max-width: 90%;
  width: 400px;
  text-align: center;
  animation: slideIn 0.3s ease;
}

@keyframes slideIn {
  from { transform: translateY(-50px); opacity: 0; }
  to { transform: translateY(0); opacity: 1; }
}

.modal-icon {
  font-size: 80px;
  margin-bottom: 20px;
}

.modal-title {
  font-size: 24px;
  font-weight: bold;
  color: #ff4757;
  margin-bottom: 15px;
}

.modal-text {
  color: #666;
  line-height: 1.6;
  margin-bottom: 25px;
}

@media (max-width: 480px) {
  .card {
    padding: 30px 20px;
  }

  .title {
    font-size: 24px;
  }

  .btn {
    padding: 12px 40px;
    font-size: 16px;
  }
}
</style>
