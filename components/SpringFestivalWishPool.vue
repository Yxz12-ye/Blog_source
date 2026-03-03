<template>
  <section ref="moduleRef" class="wish-pool-module" aria-label="新年许愿池">
    <div class="festival-bg" aria-hidden="true"></div>

    <div class="pond-scene">
      <div ref="pondRef" class="pond" aria-hidden="true">
        <div class="water-highlight"></div>

        <span class="coin coin-a">💰</span>
        <span class="coin coin-b">💰</span>
        <span class="coin coin-c">🪙</span>

        <span class="petal petal-a"></span>
        <span class="petal petal-b"></span>
        <span class="petal petal-c"></span>
        <span class="leaf leaf-a"></span>
        <span class="leaf leaf-b"></span>

        <span
          v-for="koi in kois"
          :key="koi.id"
          class="koi"
          :style="{
            '--koi-top': `${koi.top}%`,
            '--koi-delay': `${koi.delay}s`,
            '--koi-duration': `${koi.duration}s`,
            '--koi-scale': koi.scale,
          }"
          aria-hidden="true"
        >
          🐟
        </span>

        <span
          v-for="ripple in ripples"
          :key="ripple.id"
          class="ripple"
          :style="{ left: ripple.left, top: ripple.top }"
        ></span>

        <div v-if="bubbleActive" class="bubble-layer" aria-hidden="true">
          <span
            v-for="bubble in bubbles"
            :key="bubble.id"
            class="bubble"
            :style="{
              left: bubble.left,
              width: `${bubble.size}px`,
              height: `${bubble.size}px`,
              animationDuration: `${bubble.duration}s`,
              animationDelay: `${bubble.delay}s`,
            }"
          ></span>
        </div>
      </div>

      <button
        ref="buttonRef"
        class="wish-btn"
        type="button"
        :disabled="isAnimating"
        @click="toggleForm"
      >
        {{ showForm ? '收起心愿笺' : '投币许愿' }}
      </button>

      <p class="guide-text">投入一枚心愿币，你的愿望会浮出水面</p>

      <Transition name="panel-fade">
        <form v-if="showForm" class="wish-form" @submit.prevent="submitWish">
          <label>
            <span>昵称（可选）</span>
            <input
              v-model.trim="nicknameInput"
              type="text"
              maxlength="12"
              placeholder="匿名"
              autocomplete="off"
            />
          </label>

          <label>
            <span>愿望（最多 30 字）</span>
            <textarea
              v-model.trim="wishInput"
              maxlength="30"
              rows="2"
              placeholder="写下你的新年愿望..."
            ></textarea>
          </label>

          <div class="form-row">
            <small>{{ wishInput.length }}/30</small>
            <button class="submit-btn" type="submit" :disabled="isAnimating">投入</button>
          </div>

          <p v-if="errorText" class="error-text">{{ errorText }}</p>
        </form>
      </Transition>

      <Transition name="note-pop">
        <div v-if="floatingWish" class="floating-note" aria-live="polite">
          {{ floatingWish }}
        </div>
      </Transition>

      <div v-if="coinAnimating" class="coin-flight-layer" aria-hidden="true">
        <span class="flying-coin" :style="coinStyle">🪙</span>
      </div>
    </div>

    <div class="list-section">
      <div class="list-head">
        <h3>愿望池</h3>
        <div class="head-actions">
          <button class="sound-btn" type="button" @click="toggleAudio">
            {{ audioOn ? '流水声：开' : '流水声：关' }}
          </button>
          <button class="clear-btn" type="button" @click="clearAll">清空所有愿望</button>
        </div>
      </div>

      <p v-if="!wishList.length" class="empty-tip">还没有愿望，快投币许愿吧～</p>

      <TransitionGroup name="wish-list" tag="ul" class="wish-list">
        <li
          v-for="item in wishList"
          :key="item.id"
          class="wish-item"
          @click="copyWish(item)"
          :title="`点击复制：${item.name}：${item.text}`"
        >
          <span>{{ item.name }}：{{ item.text }}</span>
          <button
            class="delete-btn"
            type="button"
            aria-label="删除愿望"
            @click.stop="removeWish(item.id)"
          >
            ✕
          </button>
        </li>
      </TransitionGroup>
    </div>

    <Transition name="toast-fade">
      <div v-if="copiedToast" class="copied-toast">已复制</div>
    </Transition>

    <audio
      ref="audioRef"
      preload="none"
      loop
      src="https://cdn.pixabay.com/download/audio/2022/03/15/audio_0a4f95ad2a.mp3?filename=water-stream-ambient-110347.mp3"
    ></audio>
  </section>
</template>

<script setup>
import { ref } from 'vue'

const moduleRef = ref(null)
const pondRef = ref(null)
const buttonRef = ref(null)
const audioRef = ref(null)

const showForm = ref(false)
const nicknameInput = ref('')
const wishInput = ref('')
const errorText = ref('')

const wishList = ref([])
const isAnimating = ref(false)

const ripples = ref([])
const bubbleActive = ref(false)
const bubbles = ref([])

const floatingWish = ref('')
const copiedToast = ref(false)

const coinAnimating = ref(false)
const coinStyle = ref({})

const audioOn = ref(false)

const kois = ref(
  Array.from({ length: 3 }).map((_, index) => ({
    id: `koi-${index}`,
    top: 24 + Math.random() * 52,
    delay: Math.random() * 4,
    duration: 13 + Math.random() * 7,
    scale: (0.8 + Math.random() * 0.55).toFixed(2),
  }))
)

const sleep = (ms) => new Promise((resolve) => setTimeout(resolve, ms))

function toggleForm() {
  showForm.value = !showForm.value
  errorText.value = ''
}

function createRipple() {
  const id = Date.now() + Math.random()
  ripples.value.push({ id, left: '50%', top: '50%' })
  setTimeout(() => {
    ripples.value = ripples.value.filter((item) => item.id !== id)
  }, 1300)
}

function createBubbles() {
  bubbles.value = Array.from({ length: 9 }).map((_, idx) => ({
    id: `${Date.now()}-${idx}`,
    left: `${25 + Math.random() * 50}%`,
    size: 8 + Math.round(Math.random() * 14),
    duration: 1.3 + Math.random() * 1.2,
    delay: Math.random() * 0.7,
  }))
}

function startCoinFlight() {
  const moduleEl = moduleRef.value
  const btnEl = buttonRef.value
  const pondEl = pondRef.value
  if (!moduleEl || !btnEl || !pondEl) return

  const moduleRect = moduleEl.getBoundingClientRect()
  const btnRect = btnEl.getBoundingClientRect()
  const pondRect = pondEl.getBoundingClientRect()

  const startX = btnRect.left + btnRect.width / 2 - moduleRect.left
  const startY = btnRect.top + btnRect.height / 2 - moduleRect.top
  const endX = pondRect.left + pondRect.width / 2 - moduleRect.left
  const endY = pondRect.top + pondRect.height * 0.58 - moduleRect.top

  coinStyle.value = {
    left: `${startX}px`,
    top: `${startY}px`,
    '--coin-tx': `${endX - startX}px`,
    '--coin-ty': `${endY - startY}px`,
  }

  coinAnimating.value = true
  setTimeout(() => {
    coinAnimating.value = false
  }, 950)
}

async function submitWish() {
  if (isAnimating.value) return

  const text = wishInput.value.trim()
  const name = nicknameInput.value.trim() || '匿名'

  if (!text) {
    errorText.value = '愿望不能为空'
    return
  }
  if (text.length > 30) {
    errorText.value = '愿望不能超过 30 字'
    return
  }

  errorText.value = ''
  isAnimating.value = true

  startCoinFlight()
  createRipple()
  await sleep(900)

  bubbleActive.value = true
  createBubbles()
  await sleep(1200)

  floatingWish.value = `${name}：${text}`
  await sleep(1650)

  bubbleActive.value = false
  floatingWish.value = ''
  wishList.value.unshift({ id: Date.now() + Math.random(), name, text })
  if (wishList.value.length > 10) {
    wishList.value = wishList.value.slice(0, 10)
  }

  wishInput.value = ''
  isAnimating.value = false
}

function removeWish(id) {
  wishList.value = wishList.value.filter((item) => item.id !== id)
}

async function copyWish(item) {
  const content = `${item.name}：${item.text}`
  try {
    await navigator.clipboard.writeText(content)
    copiedToast.value = true
    setTimeout(() => {
      copiedToast.value = false
    }, 1200)
  } catch {
    copiedToast.value = false
  }
}

function clearAll() {
  if (!wishList.value.length) return
  if (!window.confirm('确认清空所有愿望吗？')) return
  wishList.value = []
}

async function toggleAudio() {
  if (!audioRef.value) return
  if (!audioOn.value) {
    try {
      await audioRef.value.play()
      audioOn.value = true
    } catch {
      audioOn.value = false
    }
  } else {
    audioRef.value.pause()
    audioOn.value = false
  }
}
</script>

<style scoped>
.wish-pool-module {
  --red: #e53e3e;
  --gold: #fbbf24;
  --aqua: #6ab0e6;
  position: relative;
  max-width: 860px;
  margin: 0 auto;
  padding: 20px 16px 18px;
  border-radius: 20px;
  overflow: hidden;
  background: linear-gradient(160deg, #fff7ef 0%, #ffe8d1 52%, #fff1de 100%);
  box-shadow: 0 16px 30px rgba(229, 62, 62, 0.12);
  color: #5a2618;
}

.festival-bg {
  position: absolute;
  inset: 0;
  pointer-events: none;
  background:
    radial-gradient(circle at 12% 20%, rgba(251, 191, 36, 0.19) 0, transparent 36%),
    radial-gradient(circle at 85% 18%, rgba(229, 62, 62, 0.14) 0, transparent 34%),
    radial-gradient(circle at 50% 100%, rgba(106, 176, 230, 0.12) 0, transparent 48%);
}

.pond-scene {
  position: relative;
  z-index: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
}

.pond-scene::before {
  content: '';
  position: absolute;
  top: 10px;
  width: min(95vw, 560px);
  height: clamp(210px, 50vw, 300px);
  border-radius: 50% / 45%;
  background: radial-gradient(circle at 50% 45%, rgba(251, 191, 36, 0.14) 0%, rgba(229, 62, 62, 0.1) 55%, transparent 100%);
  pointer-events: none;
  filter: blur(1px);
}

.pond {
  position: relative;
  width: min(92vw, 520px);
  height: clamp(180px, 44vw, 270px);
  border-radius: 50% / 42%;
  border: 4px solid rgba(251, 191, 36, 0.75);
  background: radial-gradient(circle at 50% 20%, #c2e8ff 0%, #8bc9f3 34%, #4e99d9 74%, #2f6ea8 100%);
  overflow: hidden;
  box-shadow:
    inset 0 20px 32px rgba(255, 255, 255, 0.46),
    inset 0 -22px 38px rgba(9, 44, 79, 0.46),
    0 0 0 8px rgba(251, 191, 36, 0.18),
    0 16px 30px rgba(21, 76, 122, 0.28);
}

.pond::before {
  content: '';
  position: absolute;
  inset: 6px;
  border-radius: 50% / 42%;
  border: 2px solid rgba(255, 255, 255, 0.5);
  pointer-events: none;
}

.pond::after {
  content: '';
  position: absolute;
  inset: 0;
  border-radius: inherit;
  pointer-events: none;
  background: repeating-radial-gradient(
    circle at 50% 48%,
    rgba(255, 255, 255, 0.12) 0 7px,
    rgba(255, 255, 255, 0) 7px 15px
  );
  opacity: 0.34;
  animation: waveDrift 7.5s linear infinite;
}

.water-highlight {
  position: absolute;
  top: 12%;
  left: 15%;
  width: 74%;
  height: 36%;
  border-radius: 999px;
  background: linear-gradient(90deg, rgba(255, 255, 255, 0.25) 0%, rgba(255, 255, 255, 0.04) 100%);
  filter: blur(1px);
  animation: waterGlow 6.8s ease-in-out infinite;
}

.coin {
  position: absolute;
  bottom: 12%;
  font-size: 21px;
  opacity: 0.56;
  filter: saturate(1.08);
}

.coin-a {
  left: 22%;
}

.coin-b {
  left: 50%;
}

.coin-c {
  left: 68%;
}

.petal,
.leaf {
  position: absolute;
  border-radius: 999px;
}

.petal {
  width: 20px;
  height: 14px;
  background: linear-gradient(120deg, #ff8f8f 0%, #e53e3e 100%);
  box-shadow: 0 2px 8px rgba(229, 62, 62, 0.3);
  opacity: 0.92;
  animation: drift 7s ease-in-out infinite;
}

.leaf {
  width: 34px;
  height: 18px;
  background: linear-gradient(100deg, #8fd579 0%, #3f9e57 100%);
  opacity: 0.84;
  animation: drift 8.4s ease-in-out infinite;
}

.petal-a {
  top: 30%;
  left: 18%;
}

.petal-b {
  top: 42%;
  left: 72%;
  animation-delay: 0.9s;
}

.petal-c {
  top: 24%;
  left: 56%;
  animation-delay: 1.5s;
}

.leaf-a {
  top: 54%;
  left: 14%;
}

.leaf-b {
  top: 20%;
  left: 74%;
  animation-delay: 1.2s;
}

.koi {
  position: absolute;
  left: -12%;
  top: var(--koi-top);
  font-size: 18px;
  opacity: 0.58;
  transform: scale(var(--koi-scale));
  animation: koiSwim var(--koi-duration) linear var(--koi-delay) infinite;
}

.ripple {
  position: absolute;
  width: 20px;
  height: 20px;
  border: 2px solid rgba(255, 255, 255, 0.72);
  border-radius: 50%;
  transform: translate(-50%, -50%);
  animation: rippleSpread 1.25s ease-out forwards;
}

.bubble-layer {
  position: absolute;
  inset: 0;
  pointer-events: none;
}

.bubble {
  position: absolute;
  bottom: 8%;
  border-radius: 50%;
  background: radial-gradient(circle at 32% 28%, rgba(255, 255, 255, 0.95) 0%, rgba(223, 244, 255, 0.4) 60%, rgba(223, 244, 255, 0.1) 100%);
  opacity: 0;
  animation-name: bubbleRise;
  animation-timing-function: ease-out;
  animation-fill-mode: forwards;
}

.wish-btn,
.submit-btn,
.sound-btn,
.clear-btn,
.delete-btn {
  cursor: pointer;
  border: none;
}

.wish-btn {
  margin-top: 12px;
  min-height: 46px;
  min-width: 156px;
  padding: 10px 18px;
  border-radius: 999px;
  background: linear-gradient(130deg, var(--red) 0%, #c92a2a 100%);
  color: #fff8ef;
  font-size: 16px;
  font-weight: 700;
  box-shadow: 0 0 0 0 rgba(251, 191, 36, 0.56);
  animation: buttonGlow 2.2s ease-in-out infinite;
}

.wish-btn:disabled {
  opacity: 0.68;
}

.guide-text {
  margin: 10px 0 0;
  color: #7c4234;
  font-size: 14px;
}

.wish-form {
  margin-top: 12px;
  width: min(92vw, 520px);
  padding: 14px;
  border-radius: 14px;
  background: rgba(255, 255, 255, 0.72);
  backdrop-filter: blur(3px);
  box-shadow: 0 8px 20px rgba(94, 50, 16, 0.11);
}

.wish-form label {
  display: block;
  margin-bottom: 8px;
}

.wish-form span {
  display: block;
  margin-bottom: 5px;
  font-size: 13px;
}

.wish-form input,
.wish-form textarea {
  width: 100%;
  border: 1px solid rgba(124, 66, 52, 0.32);
  border-radius: 10px;
  padding: 9px 10px;
  background: rgba(255, 255, 255, 0.9);
  font-size: 14px;
  color: #4f2517;
}

.wish-form textarea {
  resize: none;
}

.form-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.form-row small {
  color: #8c5445;
}

.submit-btn {
  min-height: 40px;
  padding: 8px 18px;
  border-radius: 10px;
  background: linear-gradient(130deg, #fbbf24 0%, #de9f00 100%);
  color: #58290f;
  font-weight: 700;
}

.submit-btn:disabled {
  opacity: 0.7;
}

.error-text {
  margin: 8px 0 2px;
  color: #c53030;
  font-size: 13px;
}

.floating-note {
  position: absolute;
  left: 50%;
  top: 54%;
  transform: translate(-50%, -50%);
  max-width: min(74vw, 380px);
  padding: 10px 14px;
  border-radius: 10px;
  background: rgba(255, 250, 220, 0.92);
  border: 1px solid rgba(233, 168, 13, 0.45);
  color: #6a381e;
  box-shadow: 0 8px 16px rgba(124, 66, 52, 0.22);
  font-weight: 600;
  text-align: center;
  pointer-events: none;
}

.coin-flight-layer {
  position: absolute;
  inset: 0;
  pointer-events: none;
}

.flying-coin {
  position: absolute;
  display: inline-block;
  font-size: 28px;
  animation: coinDive 0.95s ease-in forwards;
}

.list-section {
  position: relative;
  z-index: 1;
  margin-top: 16px;
}

.list-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 10px;
  flex-wrap: wrap;
}

.list-head h3 {
  margin: 0;
  font-size: 18px;
}

.head-actions {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

.sound-btn,
.clear-btn {
  min-height: 34px;
  padding: 6px 10px;
  border-radius: 8px;
  font-size: 12px;
}

.sound-btn {
  background: rgba(106, 176, 230, 0.2);
  color: #205e8e;
}

.clear-btn {
  background: rgba(229, 62, 62, 0.12);
  color: #b33737;
}

.empty-tip {
  margin: 12px 0 2px;
  color: #8c5445;
}

.wish-list {
  margin: 12px 0 0;
  padding: 0;
  list-style: none;
  display: grid;
  gap: 8px;
  max-height: 312px;
  overflow: auto;
}

.wish-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 10px;
  padding: 10px 12px;
  border-radius: 12px;
  background: rgba(255, 255, 255, 0.55);
  border: 1px solid rgba(251, 191, 36, 0.35);
  backdrop-filter: blur(2px);
  transition: transform 0.2s ease, box-shadow 0.2s ease;
  cursor: pointer;
  word-break: break-word;
}

.wish-item:hover {
  transform: scale(1.015);
  box-shadow: 0 6px 18px rgba(94, 50, 16, 0.11);
}

.delete-btn {
  width: 26px;
  height: 26px;
  border-radius: 50%;
  background: rgba(229, 62, 62, 0.14);
  color: #bf2d2d;
  flex-shrink: 0;
}

.copied-toast {
  position: fixed;
  left: 50%;
  bottom: 34px;
  transform: translateX(-50%);
  z-index: 30;
  padding: 8px 12px;
  border-radius: 999px;
  background: rgba(40, 30, 20, 0.82);
  color: #fff;
  font-size: 13px;
}

.panel-fade-enter-active,
.panel-fade-leave-active,
.toast-fade-enter-active,
.toast-fade-leave-active,
.note-pop-enter-active,
.note-pop-leave-active {
  transition: all 0.26s ease;
}

.panel-fade-enter-from,
.panel-fade-leave-to,
.toast-fade-enter-from,
.toast-fade-leave-to {
  opacity: 0;
  transform: translateY(-6px);
}

.note-pop-enter-from,
.note-pop-leave-to {
  opacity: 0;
  transform: translate(-50%, -40%) scale(0.9);
}

.wish-list-enter-active,
.wish-list-leave-active {
  transition: all 0.3s ease;
}

.wish-list-enter-from,
.wish-list-leave-to {
  opacity: 0;
  transform: translateY(10px) scale(0.96);
}

@keyframes waterGlow {
  0%,
  100% {
    transform: translateX(-2%) scale(1);
    opacity: 0.42;
  }
  50% {
    transform: translateX(2%) scale(1.05);
    opacity: 0.66;
  }
}

@keyframes drift {
  0%,
  100% {
    transform: translate3d(0, 0, 0) rotate(-3deg);
  }
  50% {
    transform: translate3d(10px, -4px, 0) rotate(5deg);
  }
}

@keyframes rippleSpread {
  0% {
    opacity: 0.82;
    width: 16px;
    height: 16px;
  }
  100% {
    opacity: 0;
    width: 200px;
    height: 200px;
  }
}

@keyframes coinDive {
  0% {
    opacity: 1;
    transform: translate(-50%, -50%) translate(0, 0) scale(1) rotate(0deg);
  }
  80% {
    opacity: 1;
    transform: translate(-50%, -50%) translate(var(--coin-tx), var(--coin-ty)) scale(0.35) rotate(520deg);
  }
  100% {
    opacity: 0;
    transform: translate(-50%, -50%) translate(var(--coin-tx), calc(var(--coin-ty) + 8px)) scale(0.1) rotate(620deg);
  }
}

@keyframes bubbleRise {
  0% {
    transform: translateY(0) scale(0.7);
    opacity: 0;
  }
  30% {
    opacity: 0.88;
  }
  100% {
    transform: translateY(-135px) scale(1.12);
    opacity: 0;
  }
}

@keyframes buttonGlow {
  0%,
  100% {
    box-shadow: 0 0 0 0 rgba(251, 191, 36, 0.5);
  }
  60% {
    box-shadow: 0 0 0 11px rgba(251, 191, 36, 0.04);
  }
}

@keyframes koiSwim {
  0% {
    transform: translateX(0) scale(var(--koi-scale));
    opacity: 0;
  }
  10%,
  90% {
    opacity: 0.56;
  }
  100% {
    transform: translateX(125%) scale(var(--koi-scale));
    opacity: 0;
  }
}

@keyframes waveDrift {
  0% {
    transform: scale(1) translateY(0);
  }
  50% {
    transform: scale(1.03) translateY(2px);
  }
  100% {
    transform: scale(1) translateY(0);
  }
}

@media (max-width: 700px) {
  .wish-pool-module {
    padding: 14px 10px 14px;
    border-radius: 14px;
  }

  .guide-text {
    font-size: 13px;
    text-align: center;
    padding: 0 4px;
  }

  .wish-btn {
    min-width: 170px;
  }

  .floating-note {
    top: 56%;
    font-size: 13px;
  }

  .wish-list {
    max-height: 270px;
  }

  .koi {
    font-size: 15px;
    opacity: 0.46;
  }
}

@media (prefers-reduced-motion: reduce) {
  .wish-btn,
  .water-highlight,
  .petal,
  .leaf,
  .koi,
  .ripple,
  .bubble,
  .flying-coin {
    animation-duration: 0.01ms !important;
    animation-iteration-count: 1 !important;
  }
}
</style>
