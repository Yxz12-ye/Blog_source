<script lang="ts" setup>
import { defineArticle, useSchemaOrg } from '@unhead/schema-org/vue'

import dayjs from 'dayjs'
import { useFrontmatter, useSiteConfig, useValaxyI18n } from 'valaxy'

const siteConfig = useSiteConfig()
const frontmatter = useFrontmatter()

const { $t, $tO } = useValaxyI18n()
const article: Parameters<typeof defineArticle>[0] = {
  '@type': 'BlogPosting',
  'headline': $tO(frontmatter.value.title),
  'description': $tO(frontmatter.value.description),
  'author': [
    {
      name: $t(siteConfig.value.author.name),
      url: siteConfig.value.author.link,
    },
  ],
  'datePublished': dayjs(frontmatter.value.date || '').toDate(),
  'dateModified': dayjs(frontmatter.value.updated || '').toDate(),
}

const image = frontmatter.value.image || frontmatter.value.cover
if (image)
  article.image = image

useSchemaOrg(
  defineArticle(article),
)
</script>

<template>
  <YunLayoutWrapper class="custom-layout">
    <div class="main-content-expanded">
      <RouterView v-slot="{ Component }">
        <component :is="Component">
          <template #main-header-after>
            <YunMainHeaderAfter />
          </template>
          <template #main-content-after>
            <YunMainContentAfter />
          </template>
          <template #aside-custom>
            <slot name="aside-custom" />
          </template>
        </component>
      </RouterView>
    </div>
    <div class="yun-post-right">
      <YunLayoutRight />
    </div>
    
  </YunLayoutWrapper>
</template>

<style scoped>
.custom-layout {
  max-width: 100% !important;
  gap: 2rem !important;
}

.main-content-expanded {
  flex: 1;
  min-width: 0;
  width: 100%;
  padding-left: 5%;
}

.yun-post-right {
  padding-right: 1%;
}
</style>
