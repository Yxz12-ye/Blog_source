import os
import yaml
from datetime import datetime
from typing import List, Optional

def get_user_input(prompt: str, required: bool = True, default: str = "", is_list: bool = False) -> any:
    """
    获取用户输入，支持必填项、默认值和列表输入
    """
    while True:
        try:
            if default:
                user_input = input(f"{prompt} (默认: {default}): ").strip()
                if not user_input:
                    user_input = default
            else:
                user_input = input(f"{prompt}: ").strip()
            
            # 检查必填项
            if required and not user_input:
                print("此项为必填项，请重新输入！")
                continue
            
            # 处理列表输入
            if is_list and user_input:
                return [item.strip() for item in user_input.split(',') if item.strip()]
            
            return user_input
            
        except KeyboardInterrupt:
            print("\n程序已终止")
            exit(0)
        except Exception as e:
            print(f"输入错误: {e}")

def generate_yaml_content(title: str, categories: List[str], tags: List[str], 
                         password: Optional[str] = None, code_height_limit: Optional[int] = None) -> str:
    """
    生成YAML格式的元数据
    """
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    yaml_data = {
        'title': title,
        'date': current_time,
        'updated': current_time,
    }
    
    # 可选字段
    if password:
        yaml_data['password'] = password
    if code_height_limit:
        yaml_data['codeHeightLimit'] = code_height_limit
    
    # 分类和标签
    yaml_data['categories'] = categories
    yaml_data['tags'] = tags
    
    # 转换为YAML格式
    yaml_str = yaml.dump(yaml_data, default_flow_style=False, allow_unicode=True, sort_keys=False)
    return f"---\n{yaml_str}---\n\n"

def ensure_output_directory(base_path: str = "./pages/posts") -> str:
    """
    确保输出目录存在，创建按年份分组的目录
    返回完整的输出路径
    """
    try:
        # 获取当前年份
        current_year = datetime.now().strftime("%Y")
        
        # 创建完整路径
        full_path = os.path.join(base_path, current_year)
        
        # 如果目录不存在则创建
        if not os.path.exists(full_path):
            os.makedirs(full_path, exist_ok=True)
            print(f"📁 创建目录: {full_path}")
        
        return full_path
        
    except Exception as e:
        print(f"❌ 创建目录时出错: {e}")
        # 如果出错，使用当前目录作为备选
        return "."

def generate_blog_post():
    """
    主函数：生成博客文章模板
    """
    print("=" * 50)
    print("博客模板生成器")
    print("=" * 50)
    
    # 获取基础信息
    filename = get_user_input("请输入文件名（无需扩展名）", required=True)
    title = get_user_input("请输入文章标题", required=True)
    
    # 获取分类（支持多个）
    print("\n分类设置（可输入多个，用逗号分隔）")
    categories_input = get_user_input("请输入分类", required=True, is_list=True)
    
    # 获取标签（支持多个）
    print("\n标签设置（可输入多个，用逗号分隔）")
    tags_input = get_user_input("请输入标签", required=True, is_list=True)
    
    # 获取可选参数
    print("\n可选参数设置（直接回车可跳过）")
    password = get_user_input("请输入访问密码（可选）", required=False)
    
    code_height_limit_input = get_user_input("请输入代码高度限制（可选，单位：行）", required=False)
    code_height_limit = None
    if code_height_limit_input and code_height_limit_input.isdigit():
        code_height_limit = int(code_height_limit_input)
    
    # 生成YAML元数据
    yaml_content = generate_yaml_content(
        title=title,
        categories=categories_input,
        tags=tags_input,
        password=password if password else None,
        code_height_limit=code_height_limit
    )
    
    # 生成Markdown内容
    markdown_content = f"""{yaml_content}# {title}

## 概述

<!-- 在这里写文章概述 -->

<!-- more -->

## 正文

<!-- 在这里开始写正文内容 -->

## 总结

<!-- 在这里写总结 -->

---

**版权声明**：本文为原创文章，转载请注明出处。

"""
    
    # 确保输出目录存在
    output_dir = ensure_output_directory()
    current_year = datetime.now().strftime("%Y")
    
    # 构建完整的输出路径
    output_filename = os.path.join(output_dir, f"{filename}.md")
    
    # 相对路径显示（用于输出信息）
    relative_path = os.path.relpath(output_filename, start=".")
    
    # 检查文件是否已存在
    if os.path.exists(output_filename):
        overwrite = input(f"文件 '{relative_path}' 已存在，是否覆盖？(y/n): ").strip().lower()
        if overwrite != 'y':
            print("操作已取消")
            return
    
    try:
        with open(output_filename, 'w', encoding='utf-8') as f:
            f.write(markdown_content)
        
        print(f"\n✅ 博客模板已成功生成：{relative_path}")
        print(f"📝 标题：{title}")
        print(f"📂 分类：{', '.join(categories_input)}")
        print(f"🏷️  标签：{', '.join(tags_input)}")
        print(f"📅 创建时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"📁 输出目录：{output_dir}")
        
        if password:
            print(f"🔒 访问密码：{password}")
        if code_height_limit:
            print(f"📏 代码高度限制：{code_height_limit}行")
            
    except Exception as e:
        print(f"❌ 生成文件时出错：{e}")

def main():
    """
    主程序入口
    """
    try:
        # 检查是否安装了PyYAML
        import yaml
    except ImportError:
        print("错误：需要安装PyYAML库")
        print("请运行：pip install PyYAML")
        return
    
    # 显示输出目录信息
    current_year = datetime.now().strftime("%Y")
    print(f"📁 输出目录将自动设置为：./pages/posts/{current_year}/")
    
    while True:
        generate_blog_post()
        
        print("\n" + "=" * 50)
        again = input("是否继续生成新的模板？(y/n): ").strip().lower()
        if again != 'y':
            print("感谢使用博客模板生成器！")
            break

if __name__ == "__main__":
    main()