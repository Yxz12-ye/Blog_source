<script setup lang="ts">
import type { Post } from 'valaxy/types'
import { useSiteConfig, useSiteStore } from 'valaxy'
import { computed, ref } from 'vue'

const props = withDefaults(defineProps<{
  type?: string
  posts?: Post[]
}>(), {})

const paginationRef = ref()
const curPage = computed(() => paginationRef.value?.curPage || 1)

const site = useSiteStore()
const siteConfig = useSiteConfig()
const pageSize = computed(() => siteConfig.value.pageSize)

const posts = computed(() => (
  props.posts || site.postList).filter(post => import.meta.env.DEV ? true : !post.hide),
)

const displayedPosts = computed(() =>
  posts.value.slice(
    (curPage.value - 1) * pageSize.value,
    curPage.value * pageSize.value,
  ),
)
</script>

<template>
  <div class="yun-post-list grid grid-cols-1 lg:grid-cols-[1fr_20rem] gap-0" w="full" p="x-4 lt-sm:0">
    <!-- 主要内容区域 -->
    <div class="flex justify-center"> <!-- 居中 -->
      <div class="w-full">
        <template v-if="!displayedPosts.length">
          <div py2 op50 text-center>
            博主还什么都没写哦～
          </div>
        </template>
        <YunPostCard v-for="route, i in displayedPosts" :key="i" :post="route" />
      </div>
    </div>
    
    <!-- 侧边栏区域 -->
    <div class="lt-lg:hidden justify-center yun-sidebar-sticky">
      <YunSidebarCard />
    </div>
  </div>

  <YunPagination
    ref="paginationRef"
    class="mt-5"
    :total="posts.length" :page-size="pageSize"
  />
</template>

<style scoped>
.yun-post-list {
  gap: 0 !important;
}

.yun-sidebar-sticky {
  padding-right: 10%;
  position: sticky;
  top: 20px; /* 距离顶部的距离，可以调整 */
  align-self: flex-start; /* 顶部对齐 */
  height: fit-content; /* 高度自适应内容 */
  max-height: calc(100vh - 40px); /* 最大高度，防止超出视口 */
  overflow-y: auto; /* 如果内容过多，允许滚动 */
}

/* 可选：添加滚动时的阴影效果 */
.yun-sidebar-sticky.scrolled {
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);
  border-radius: 8px;
  transition: box-shadow 0.3s ease;
}

/* 响应式设计 */
@media (max-width: 1024px) {
  .yun-sidebar-sticky {
    display: none; /* 在小于lg的屏幕上隐藏 */
  }
}

@media (min-width: 1200px) {
  .yun-sidebar-sticky {
    top: 30px; /* 在大屏幕上增加顶部距离 */
  }
}

/* 如果需要，可以添加滚动监听效果 */
.yun-sidebar-sticky {
  transition: all 0.3s ease;
}
</style>