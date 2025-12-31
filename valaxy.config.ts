import type { UserThemeConfig } from 'valaxy-theme-yun'
import { defineValaxyConfig } from 'valaxy'

// add icons what you will need
const safelist = [
  'i-ri-home-line',
]

/**
 * User Config
 */
export default defineValaxyConfig<UserThemeConfig>({
  // site config see site.config.ts

  theme: 'yun',

  themeConfig: {
    banner: {
      enable: true,
      title: ['Yexkr', '的', '小', '站'],
    },
    // menu:{
    //   custom:{
    //     title: '友链',
    //     url: '/links/',
    //     icon: 'i-ri-team-line',
    //   }
    // },
    nav: [
      {
        icon: 'i-ri-article-line',
        link: '/posts/',
        text: '博客文章',
        active: 'true',
      },
      {
        icon: 'i-ri-team-line',
        link: '/links/',
        text: '友链',
        active: 'true',
      },

    ],
    pages: [
      {
        name: '友链',
        url: '/links/',
        icon: 'i-ri-team-line',
        color: 'dodgerblue',
      },
    ],

    footer: {
      since: 2025,
    },
  },

  unocss: { safelist },
  components:{
    // include:[/[\\/]src[\\/]components[\\/]/,
    //   /[\\/]modified_content[\\/]/,]
  }
})
