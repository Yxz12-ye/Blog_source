<template>
  <div class="friend-card-horizontal">
    <div class="card-avatar">
      <div class="avatar-container">
        <img :src="avatar" :alt="name + '的头像'" class="avatar">
      </div>
    </div>
    
    <div class="card-content">
      <div class="card-main">
        <h3 class="blog-name">{{ name }}</h3>
        <p class="blog-url">{{ url }}</p>
        <div class="message">
          {{ message }}
        </div>
      </div>
      
      <a :href="fullUrl" class="visit-btn" target="_blank">
        <span>访问博客</span>
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor">
          <path d="M10 6H6a2 2 0 0 0-2 2v10a2 2 0 0 0 2 2h10a2 2 0 0 0 2-2v-4M14 4h6m0 0v6m0-6L10 14"/>
        </svg>
      </a>
    </div>
  </div>
</template>

<script>
export default {
  name: 'FriendCardHorizontal',
  props: {
    avatar: {
      type: String,
      required: true
    },
    name: {
      type: String,
      required: true
    },
    url: {
      type: String,
      required: true
    },
    message: {
      type: String,
      required: true
    }
  },
  computed: {
    fullUrl() {
      return this.url.startsWith('http') ? this.url : `https://${this.url}`
    }
  }
}
</script>

<style scoped>
.friend-card-horizontal {
  display: flex;
  align-items: center;
  background: white;
  border-radius: 12px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
  padding: 20px;
  transition: all 0.3s ease;
  border: 1px solid #f0f0f0;
  max-width: 500px;
  margin: 15px 0;
}

.friend-card-horizontal:hover {
  transform: translateY(-3px);
  box-shadow: 0 8px 30px rgba(0, 0, 0, 0.12);
}

.card-avatar {
  flex-shrink: 0;
  margin-right: 20px;
}

.avatar-container {
  width: 70px;
  height: 70px;
  border-radius: 50%;
  overflow: hidden;
  border: 3px solid #e8e8e8;
  background: #f8f9fa;
  display: flex;
  align-items: center;
  justify-content: center;
}

.avatar {
  width: 100%;
  height: 100%;
  object-fit: cover;
  display: block;
}

.card-content {
  flex: 1;
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 15px;
}

.card-main {
  flex: 1;
}

.blog-name {
  font-size: 1.2rem;
  font-weight: 600;
  color: #2c3e50;
  margin: 0 0 5px 0;
}

.blog-url {
  font-size: 0.85rem;
  color: #6c757d;
  margin: 0 0 10px 0;
  word-break: break-all;
}

.message {
  font-size: 0.9rem;
  color: #555;
  line-height: 1.5;
  margin: 0;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.visit-btn {
  display: flex;
  align-items: center;
  gap: 6px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  padding: 8px 16px;
  border-radius: 6px;
  text-decoration: none;
  font-size: 0.85rem;
  font-weight: 500;
  transition: all 0.3s ease;
  flex-shrink: 0;
  white-space: nowrap;
}

.visit-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);
}

.visit-btn svg {
  transition: transform 0.3s ease;
}

.visit-btn:hover svg {
  transform: translateX(2px);
}

/* 响应式设计 */
@media (max-width: 768px) {
  .friend-card-horizontal {
    padding: 15px;
    max-width: 100%;
  }
  
  .avatar-container {
    width: 60px;
    height: 60px;
  }
  
  .card-avatar {
    margin-right: 15px;
  }
  
  .card-content {
    flex-direction: column;
    align-items: flex-start;
    gap: 12px;
  }
  
  .visit-btn {
    align-self: flex-end;
  }
}

@media (max-width: 480px) {
  .friend-card-horizontal {
    flex-direction: column;
    text-align: center;
    padding: 20px;
  }
  
  .card-avatar {
    margin-right: 0;
    margin-bottom: 15px;
  }
  
  .card-content {
    align-items: center;
    text-align: center;
  }
  
  .visit-btn {
    align-self: center;
  }
}
</style>