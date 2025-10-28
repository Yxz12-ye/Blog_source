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
    <div class="lt-lg:hidden justify-center yun-side-card">
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
.yun-side-card {
  padding-right: 10%;
}
</style>
