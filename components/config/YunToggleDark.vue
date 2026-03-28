<script lang="ts" setup>
import { useAppStore } from 'valaxy'
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'

const props = defineProps<{
  transition?: boolean
}>()

const appStore = useAppStore()
const { t } = useI18n()

const themeTitle = computed(() => {
  return appStore.isDark ? t('button.toggle_light') : t('button.toggle_dark')
})

const styles = computed(() => {
  return {
    color: appStore.isDark ? '' : '#f1cb64',
  }
})

function toggleWithStableTransition(event: MouseEvent) {
  if (!document.startViewTransition) {
    appStore.toggleDark()
    return
  }

  const x = event.clientX
  const y = event.clientY
  const endRadius = Math.hypot(
    Math.max(x, innerWidth - x),
    Math.max(y, innerHeight - y),
  )

  const transition = document.startViewTransition(() => {
    appStore.toggleDark()
  })

  transition.ready.then(() => {
    const clipPath = [
      `circle(0px at ${x}px ${y}px)`,
      `circle(${endRadius}px at ${x}px ${y}px)`,
    ]

    document.documentElement.animate(
      {
        clipPath,
      },
      {
        duration: 300,
        easing: 'ease-in',
        pseudoElement: '::view-transition-new(root)',
      },
    )
  })
}

function toggle(event: MouseEvent) {
  props.transition ? toggleWithStableTransition(event) : appStore.toggleDark()
}
</script>

<template>
  <button
    class="yun-icon-btn"
    :title="themeTitle"
    :style="styles"
    @mousedown.prevent="() => {}"
    @click="toggle"
  >
    <div i="ri-sun-line dark:ri-moon-line" />
  </button>
</template>
