import { defineSiteConfig } from 'valaxy'

export default defineSiteConfig({
  url: 'https://blog.yexkr.top/',
  lang: 'zh-CN',
  title: '关于本站❤️',
  author: {
    name: 'Yexkr',
    avatar: 'https://pic1.imgdb.cn/item/683a6b0758cb8da5c81e771d.jpg',
    status: {
      emoji: '🤔',
      message: 'Thinking...',
    }
  },
  subtitle: '继服务器跑路, 电脑被格后重新搭建的博客',
  description: '这里是我的个人博客, 文章在下方哦😚',
  social: [
    {
      name: 'RSS',
      link: '/atom.xml',
      icon: 'i-ri-rss-line',
      color: 'orange',
    },
    {
      name: 'GitHub',
      link: 'https://github.com/Yxz12-ye',
      icon: 'i-ri-github-line',
      color: '#6e5494',
    },
    {
      name: 'Travelling',
      link: 'https://www.travellings.cn/go.html',
      icon: 'i-ri-train-line',
      color: 'var(--va-c-text)',
    },
  ],

  search: {
    enable: false,
  },

  sponsor: {
    enable: true,
    title: '感谢你的喜欢!',
  },
})
