#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Valaxy 博客文章模板生成器（Textual TUI 版）。

在 ``pages/posts/<当前年份>/`` 下交互式生成一篇新文章的 Markdown 模板：
frontmatter（title / date / updated / categories / tags / password /
codeHeightLimit）+ 概述 / 正文 / 总结 骨架。

运行：
    python create.py

依赖：
    pip install -r requirements.txt

界面操作：
    Enter / 主要按钮  -> 下一步
    Space            -> 勾选分类或标签
    Delete           -> 移除列表里自定义的分类或标签
    Esc              -> 返回上一步
    Ctrl+Q           -> 退出
"""

from __future__ import annotations

import asyncio
import re
from collections import OrderedDict
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import List, Optional, Tuple

try:
    import yaml
except ImportError:  # pragma: no cover - 仅在缺少依赖时触发
    raise SystemExit("缺少依赖 PyYAML，请先运行：pip install -r requirements.txt")

try:
    from textual.app import App, ComposeResult
    from textual.binding import Binding
    from textual.containers import Horizontal, VerticalScroll
    from textual.screen import Screen
    from textual.widgets import (
        Button,
        Header,
        Input,
        Label,
        SelectionList,
        Static,
        TextArea,
    )
except ImportError:  # pragma: no cover - 仅在缺少依赖时触发
    raise SystemExit("缺少依赖 Textual，请先运行：pip install -r requirements.txt")


# --------------------------------------------------------------------------- #
# 常量与纯函数
# --------------------------------------------------------------------------- #

POSTS_BASE = Path("./pages/posts")
HINTS = "Enter 下一步   Space 勾选   Esc 返回   Ctrl+Q 退出"

# 各步骤标题（用于页面顶部步骤指示）
STEPS = ("1/3 基本信息", "2/3 分类", "3/3 标签")

# Windows 文件名非法字符
_INVALID_FILENAME_CHARS = '<>:"/\\|?*'
# 输入里的分类/标签分隔符：英文逗号、中文逗号、顿号、分号
_SPLIT_PATTERN = re.compile(r"[,，、;；]+")
# 连续空白（用于文件名归一化，下划线保留）
_SPACE_PATTERN = re.compile(r"\s+")


def current_year() -> str:
    """当前年份。"""
    return datetime.now().strftime("%Y")


def now_str() -> str:
    """时间戳，格式与旧脚本保持一致。"""
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def sanitize_filename(name: str) -> str:
    """清理文件名：去掉非法字符，空白压成单个下划线。"""
    cleaned = "".join(ch for ch in name if ch not in _INVALID_FILENAME_CHARS)
    return _SPACE_PATTERN.sub("_", cleaned.strip()).strip(". ")


def default_filename(title: str, limit: int = 60) -> str:
    """由标题推导默认文件名（空白转下划线）。"""
    cleaned = "".join(ch for ch in title if ch not in _INVALID_FILENAME_CHARS)
    cleaned = _SPACE_PATTERN.sub("_", cleaned.strip())
    return cleaned[:limit].strip("._")


def post_path(filename: str, base_path: Path = POSTS_BASE) -> Path:
    """文章输出路径：pages/posts/<年份>/<文件名>.md。"""
    return Path(base_path) / current_year() / f"{filename}.md"


def ensure_output_directory(base_path: Path = POSTS_BASE) -> Path:
    """确保 pages/posts/<年份>/ 存在并返回该目录。"""
    full_path = Path(base_path) / current_year()
    full_path.mkdir(parents=True, exist_ok=True)
    return full_path


def split_items(raw: str) -> List[str]:
    """把逗号等分隔的输入拆成去重列表（保持输入顺序）。"""
    result: List[str] = []
    for part in _SPLIT_PATTERN.split(raw):
        item = part.strip()
        if item and item not in result:
            result.append(item)
    return result


def parse_frontmatter(text: str) -> Optional[dict]:
    """解析 Markdown 头部 YAML frontmatter，失败返回 None。"""
    if not text.startswith("---"):
        return None
    end = text.find("\n---", 3)
    if end == -1:
        return None
    try:
        data = yaml.safe_load(text[3:end])
    except yaml.YAMLError:
        return None
    return data if isinstance(data, dict) else None


def as_list(value) -> List[str]:
    """把 frontmatter 里的 categories / tags 归一化为字符串列表。"""
    if value is None:
        return []
    if isinstance(value, str):
        return [value.strip()] if value.strip() else []
    if isinstance(value, (list, tuple)):
        return [str(item).strip() for item in value if str(item).strip()]
    return [str(value)]


def scan_posts(posts_dir: Path = POSTS_BASE) -> Tuple[OrderedDict, OrderedDict]:
    """扫描已有文章，统计分类与标签的使用次数。

    返回 ``(categories, tags)``，均为 ``名称 -> 次数`` 的有序字典，
    按次数从多到少排列，同次数按名称排序。
    """
    category_usage: dict = {}
    tag_usage: dict = {}
    if posts_dir.exists():
        for path in sorted(posts_dir.rglob("*.md")):
            try:
                data = parse_frontmatter(
                    path.read_text(encoding="utf-8", errors="ignore")
                )
            except OSError:
                continue
            if not data:
                continue
            for name in as_list(data.get("categories")):
                category_usage[name] = category_usage.get(name, 0) + 1
            for name in as_list(data.get("tags")):
                tag_usage[name] = tag_usage.get(name, 0) + 1
    return _rank(category_usage), _rank(tag_usage)


def _rank(usage: dict) -> OrderedDict:
    """按 ``(-次数, 名称)`` 排序成有序字典。"""
    return OrderedDict(sorted(usage.items(), key=lambda item: (-item[1], item[0])))


def generate_yaml_content(
    title: str,
    categories: List[str],
    tags: List[str],
    password: Optional[str] = None,
    code_height_limit: Optional[int] = None,
) -> str:
    """生成 YAML frontmatter，字段顺序与旧脚本一致。"""
    timestamp = now_str()
    yaml_data = {
        "title": title,
        "date": timestamp,
        "updated": timestamp,
    }
    if password:
        yaml_data["password"] = password
    if code_height_limit:
        yaml_data["codeHeightLimit"] = code_height_limit
    yaml_data["categories"] = list(categories)
    yaml_data["tags"] = list(tags)
    yaml_str = yaml.dump(
        yaml_data, default_flow_style=False, allow_unicode=True, sort_keys=False
    )
    return f"---\n{yaml_str}---\n\n"


def generate_blog_post_content(draft: "PostDraft") -> str:
    """渲染完整的 Markdown 文章模板。"""
    yaml_content = generate_yaml_content(
        title=draft.title,
        categories=draft.categories,
        tags=draft.tags,
        password=draft.password,
        code_height_limit=draft.code_height_limit,
    )
    return (
        f"{yaml_content}# {draft.title}\n"
        "\n"
        "## 概述\n"
        "\n"
        "<!-- 在这里写文章概述 -->\n"
        "\n"
        "<!-- more -->\n"
        "\n"
        "## 正文\n"
        "\n"
        "<!-- 在这里开始写正文内容 -->\n"
        "\n"
        "## 总结\n"
        "\n"
        "<!-- 在这里写总结 -->\n"
        "\n"
        "---\n"
        "\n"
        "**版权声明**：本文为原创文章，转载请注明出处。\n"
    )


# --------------------------------------------------------------------------- #
# 数据模型
# --------------------------------------------------------------------------- #


@dataclass
class PostDraft:
    """一次生成过程中的全部字段。"""

    title: str = ""
    filename: str = ""
    password: str = ""
    code_height_limit: Optional[int] = None
    categories: List[str] = field(default_factory=list)
    tags: List[str] = field(default_factory=list)
    created_at: str = field(default_factory=now_str)


# --------------------------------------------------------------------------- #
# 页面基类
# --------------------------------------------------------------------------- #


class BaseScreen(Screen):
    """带页头、底部操作提示与返回 / 退出快捷键的页面基类。"""

    BINDINGS = [
        Binding("escape", "go_back", "返回", show=False),
        Binding("ctrl+q", "quit_app", "退出", show=False),
    ]

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)

    def action_quit_app(self) -> None:
        self.app.exit()

    @property
    def is_root_step(self) -> bool:
        """当前页是否已是最底层页面。

        屏幕栈第 0 层是 Textual 自带的默认 Screen，本应用的第一步位于第 1 层，
        所以在第 1 层时按 Esc 不应再返回。
        """
        stack = self.app.screen_stack
        for index, screen in enumerate(stack):
            if screen is self:
                return index <= 1
        return True

    def action_go_back(self) -> None:
        """Esc：返回上一步，第一步不响应。"""
        if self.is_root_step:
            return
        self.dismiss()


def step_bar(index: int) -> Static:
    """一行步骤指示，当前步骤用【】高亮。"""
    parts = [
        f"【{name}】" if position == index else f" {name} "
        for position, name in enumerate(STEPS)
    ]
    return Static("".join(parts), classes="steps")


# --------------------------------------------------------------------------- #
# 1/3 基本信息
# --------------------------------------------------------------------------- #


class MetadataScreen(BaseScreen):
    """标题、文件名、访问密码、代码高度限制。"""

    BINDINGS = BaseScreen.BINDINGS + [
        Binding("ctrl+n", "next_step", "下一步", show=False),
    ]

    def __init__(self, draft: Optional[PostDraft] = None) -> None:
        super().__init__()
        self.draft = draft if draft is not None else PostDraft()
        self._filename_touched = False
        # 每个输入框的“代码写入值”队列：Changed 消息是异步投递的，
        # 用队列按顺序消费，避免把代码写入误判成用户输入。
        self._expected: dict = {}

    def reset(self, draft: Optional[PostDraft] = None) -> None:
        """清空表单，用于「再写一篇」时复用本页面。"""
        self.draft = draft if draft is not None else PostDraft()
        self.refresh_values()

    def refresh_values(self) -> None:
        """把草稿里的值写回输入框，且不触发自动补全逻辑。"""
        self._filename_touched = False
        self._expected.clear()
        self._set_input("#title", self.draft.title)
        self._set_input("#filename", self.draft.filename)
        self._set_input("#password", self.draft.password)
        self._set_input(
            "#code-height",
            str(self.draft.code_height_limit) if self.draft.code_height_limit else "",
        )

    def _set_input(self, selector: str, value: str) -> None:
        """写入输入框，并登记这次写入的值，供 Changed 处理时识别。"""
        self._expected.setdefault(selector, []).append(value)
        self.query_one(selector, Input).value = value

    def compose(self) -> ComposeResult:
        yield from super().compose()
        with VerticalScroll(id="main"):
            yield step_bar(0)
            yield Static(
                f"输出目录：{POSTS_BASE.as_posix()}/{current_year()}/<文件名>.md",
                classes="muted",
            )
            yield Label("文章标题 *")
            yield Input(
                value=self.draft.title,
                placeholder="例如：关于 Rust 和 C++",
                id="title",
            )
            yield Label("文件名 *（无需扩展名）")
            yield Input(
                value=self.draft.filename,
                placeholder="例如：about_rust_and_cxx",
                id="filename",
            )
            yield Label("访问密码（可选）")
            yield Input(
                value=self.draft.password,
                placeholder="留空表示不加密",
                password=True,
                id="password",
            )
            yield Label("代码高度限制（可选，单位：行）")
            yield Input(
                value=(
                    str(self.draft.code_height_limit)
                    if self.draft.code_height_limit
                    else ""
                ),
                placeholder="例如：30，留空表示不限制",
                id="code-height",
            )
            with Horizontal(classes="buttons"):
                yield Button("下一步 ▸ 分类", variant="primary", id="next")
                yield Button("退出", id="quit")
        yield Static(HINTS, classes="hints")

    async def on_mount(self) -> None:
        self.refresh_values()
        await asyncio.sleep(0)
        self.query_one("#title", Input).focus()

    def on_input_changed(self, event: Input.Changed) -> None:
        """标题变化时自动补全文件名；用户手动改过文件名后不再覆盖。"""
        selector = f"#{event.input.id}"
        expected = self._expected.get(selector)
        if expected and expected[0] == event.value:
            # 这次变化就是代码写入产生的，不是用户输入
            expected.pop(0)
            return
        if event.input.id == "title":
            if not self._filename_touched:
                self._set_input("#filename", default_filename(event.value))
        elif event.input.id == "filename":
            # 用户自己动过文件名，之后标题再变也不覆盖
            self._filename_touched = True

    def on_input_submitted(self, event: Input.Submitted) -> None:
        focus_order = ("title", "filename", "password", "code-height")
        if event.input.id in focus_order[:-1]:
            next_index = focus_order.index(event.input.id) + 1
            self.query_one(f"#{focus_order[next_index]}", Input).focus()
        else:
            self._submit()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "next":
            self._submit()
        elif event.button.id == "quit":
            self.app.exit()

    def action_next_step(self) -> None:
        self._submit()

    def _submit(self) -> None:
        title = self.query_one("#title", Input).value.strip()
        if not title:
            self.notify("标题不能为空", severity="error")
            self.query_one("#title", Input).focus()
            return

        filename = sanitize_filename(self.query_one("#filename", Input).value)
        if not filename:
            self.notify("文件名不能为空（或只包含非法字符）", severity="error")
            self.query_one("#filename", Input).focus()
            return

        raw_height = self.query_one("#code-height", Input).value.strip()
        if raw_height and not raw_height.isdigit():
            self.notify("代码高度限制需要是数字，该项已忽略", severity="warning")
            code_height_limit = None
        else:
            code_height_limit = int(raw_height) if raw_height else None

        self.draft.title = title
        self.draft.filename = filename
        self.draft.password = self.query_one("#password", Input).value.strip()
        self.draft.code_height_limit = code_height_limit

        self.app.push_screen(CategoriesScreen(self.draft, self.app))


# --------------------------------------------------------------------------- #
# 2/3 分类
# --------------------------------------------------------------------------- #


class CategoriesScreen(BaseScreen):
    """勾选已有分类，也可以直接输入新分类。"""

    BINDINGS = BaseScreen.BINDINGS + [
        Binding("ctrl+n", "next_step", "下一步", show=False),
        Binding("delete", "remove_custom", "移除自定义分类", show=False, priority=True),
    ]

    def __init__(self, draft: PostDraft, app: "BlogCreatorApp") -> None:
        super().__init__()
        self.draft = draft
        self.blog_app = app

    def compose(self) -> ComposeResult:
        yield from super().compose()
        with VerticalScroll(id="main"):
            yield step_bar(1)
            yield Static(
                "Space 勾选 / 取消；输入新分类后回车添加；Delete 移除自定义分类。",
                classes="muted",
            )
            yield SelectionList(id="categories", compact=True)
            yield Input(placeholder="新增分类，多个用逗号分隔，回车添加", id="new-category")
            with Horizontal(classes="buttons"):
                yield Button("◂ 返回", id="back")
                yield Button("下一步 ▸ 标签", variant="primary", id="next")
        yield Static(HINTS, classes="hints")

    async def on_mount(self) -> None:
        self._rebuild()
        # 焦点与高亮都要延后设置：Textual 会在本页挂载后恢复上一页的焦点，
        # 而列表没有高亮项时 Space 是空操作。
        await asyncio.sleep(0)
        self._focus_list()

    def _focus_list(self) -> None:
        """聚焦列表，并保证有高亮项（否则 Space 无法勾选）。"""
        selection = self.query_one("#categories", SelectionList)
        if selection.option_count and selection.highlighted is None:
            selection.highlighted = 0
        selection.focus()

    def _rebuild(self, keep_selected: Optional[List[str]] = None) -> None:
        """重建分类列表（已有分类在前，本次新增的在后），并恢复勾选状态。"""
        selection = self.query_one("#categories", SelectionList)
        selected = (
            keep_selected
            if keep_selected is not None
            else (list(selection.selected) or list(self.draft.categories))
        )
        was_focused = selection.has_focus
        selection.clear_options()
        for name, count in self.blog_app.category_source.items():
            selection.add_option((f"{name}  ({count})", name))
        selection.add_options(
            (f"{name}  (新)", name)
            for name in self.draft.categories
            if name not in self.blog_app.category_source
        )
        for name in selected:
            try:
                selection.select(name)
            except Exception:  # pragma: no cover - 选项已被删除时忽略
                continue
        self.draft.categories = list(selection.selected)
        if was_focused:
            self.call_after_refresh(self._focus_list)

    def on_selection_list_selected_changed(
        self, event: SelectionList.SelectedChanged
    ) -> None:
        self.draft.categories = list(self.query_one("#categories", SelectionList).selected)

    def on_input_submitted(self, event: Input.Submitted) -> None:
        if event.input.id != "new-category":
            return
        added = False
        for name in split_items(event.value):
            self.blog_app.category_source.setdefault(name, 0)
            if name not in self.draft.categories:
                self.draft.categories.append(name)
                added = True
        event.input.value = ""
        self._rebuild(self.draft.categories)
        if added:
            self.notify("已添加并勾选分类", severity="information")
            # 焦点回到列表，方便直接勾选或按 Delete 删除
            self.call_after_refresh(self._focus_list)
        else:
            event.input.focus()

    def action_remove_custom(self) -> None:
        """Delete：仅移除本次会话新增的分类，不影响仓库里已有分类。"""
        selection = self.query_one("#categories", SelectionList)
        index = selection.highlighted
        if index is None:
            return
        name = selection.get_option_at_index(index).value
        if self.blog_app.is_scanned_category(name):
            self.notify(
                f"『{name}』是仓库里已有分类，请用 Space 取消勾选", severity="warning"
            )
            return
        selection.remove_option_at_index(index)
        self.blog_app.category_source.pop(name, None)
        if name in self.draft.categories:
            self.draft.categories.remove(name)
        self._rebuild(keep_selected=self.draft.categories)

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "back":
            self.app.pop_screen()
        elif event.button.id == "next":
            self.action_next_step()

    def action_next_step(self) -> None:
        self.draft.categories = list(self.query_one("#categories", SelectionList).selected)
        self.app.push_screen(TagsScreen(self.draft, self.app))


# --------------------------------------------------------------------------- #
# 3/3 标签
# --------------------------------------------------------------------------- #


class TagsScreen(BaseScreen):
    """独立标签页：自由添加 / 删除标签，然后勾选本次使用的标签。"""

    BINDINGS = BaseScreen.BINDINGS + [
        Binding("ctrl+n", "next_step", "预览", show=False),
        Binding("delete", "remove_custom", "移除自定义标签", show=False, priority=True),
    ]

    def __init__(self, draft: PostDraft, app: "BlogCreatorApp") -> None:
        super().__init__()
        self.draft = draft
        self.blog_app = app

    def compose(self) -> ComposeResult:
        yield from super().compose()
        with VerticalScroll(id="main"):
            yield step_bar(2)
            yield Static(
                "Space 勾选 / 取消；输入新标签后回车添加；Delete 移除自定义标签。",
                classes="muted",
            )
            yield SelectionList(id="tags", compact=True)
            yield Input(placeholder="新增标签，多个用逗号分隔，回车添加", id="new-tag")
            with Horizontal(classes="buttons"):
                yield Button("◂ 返回", id="back")
                yield Button("预览 ▸", variant="primary", id="next")
        yield Static(HINTS, classes="hints")

    async def on_mount(self) -> None:
        self._rebuild()
        # 焦点与高亮都要延后设置：Textual 会在本页挂载后恢复上一页的焦点，
        # 而列表没有高亮项时 Space 是空操作。
        await asyncio.sleep(0)
        self._focus_list()

    def _focus_list(self) -> None:
        """聚焦列表，并保证有高亮项（否则 Space 无法勾选）。"""
        selection = self.query_one("#tags", SelectionList)
        if selection.option_count and selection.highlighted is None:
            selection.highlighted = 0
        selection.focus()

    def _rebuild(self, keep_selected: Optional[List[str]] = None) -> None:
        """重建标签池（显示使用次数），并恢复勾选状态。"""
        selection = self.query_one("#tags", SelectionList)
        selected = (
            keep_selected
            if keep_selected is not None
            else (list(selection.selected) or list(self.draft.tags))
        )
        was_focused = selection.has_focus
        selection.clear_options()
        for name, count in self.blog_app.tag_source.items():
            label = f"{name}  ({count})" if count else f"{name}  (新)"
            selection.add_option((label, name))
        for name in selected:
            try:
                selection.select(name)
            except Exception:  # pragma: no cover - 选项已被删除时忽略
                continue
        self.draft.tags = list(selection.selected)
        if was_focused:
            self.call_after_refresh(self._focus_list)

    def on_selection_list_selected_changed(
        self, event: SelectionList.SelectedChanged
    ) -> None:
        self.draft.tags = list(self.query_one("#tags", SelectionList).selected)

    def on_input_submitted(self, event: Input.Submitted) -> None:
        if event.input.id != "new-tag":
            return
        added = False
        for name in split_items(event.value):
            self.blog_app.tag_source.setdefault(name, 0)
            if name not in self.draft.tags:
                self.draft.tags.append(name)
                added = True
        event.input.value = ""
        self._rebuild(self.draft.tags)
        if added:
            self.notify("已添加并勾选标签", severity="information")
            # 焦点回到列表，方便直接勾选或按 Delete 删除
            self.call_after_refresh(self._focus_list)
        else:
            event.input.focus()

    def action_remove_custom(self) -> None:
        """Delete：仅移除本次会话新增的标签，不影响仓库里已有标签。"""
        selection = self.query_one("#tags", SelectionList)
        index = selection.highlighted
        if index is None:
            return
        name = selection.get_option_at_index(index).value
        if self.blog_app.is_scanned_tag(name):
            self.notify(
                f"『{name}』是仓库里已有标签，请用 Space 取消勾选", severity="warning"
            )
            return
        selection.remove_option_at_index(index)
        self.blog_app.tag_source.pop(name, None)
        if name in self.draft.tags:
            self.draft.tags.remove(name)
        self._rebuild(keep_selected=self.draft.tags)

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "back":
            self.app.pop_screen()
        elif event.button.id == "next":
            self.action_next_step()

    def action_next_step(self) -> None:
        self.draft.tags = list(self.query_one("#tags", SelectionList).selected)
        self.app.push_screen(PreviewScreen(self.draft, self.app))


# --------------------------------------------------------------------------- #
# 预览与写入
# --------------------------------------------------------------------------- #


class PreviewScreen(BaseScreen):
    """预览 frontmatter 与输出路径，确认后写入文件。"""

    BINDINGS = BaseScreen.BINDINGS + [
        Binding("ctrl+s", "generate", "生成", show=False),
        Binding("ctrl+n", "generate", "生成", show=False),
    ]

    def __init__(self, draft: PostDraft, app: "BlogCreatorApp") -> None:
        super().__init__()
        self.draft = draft
        self.blog_app = app
        self.output_path = post_path(draft.filename)

    def compose(self) -> ComposeResult:
        yield from super().compose()
        with VerticalScroll(id="main"):
            yield Static("确认信息", classes="section-title")
            yield Static("", id="details", markup=False)
            yield Static("frontmatter 预览", classes="section-title")
            yield TextArea("", read_only=True, soft_wrap=False, id="preview")
            yield Static("", id="conflict")
            with Horizontal(classes="buttons"):
                yield Button("◂ 返回", id="back")
                yield Button("改文件名", id="rename")
                yield Button("✓ 生成文章", variant="success", id="generate")
        yield Static(HINTS, classes="hints")

    def on_mount(self) -> None:
        self._refresh()

    def _refresh(self) -> None:
        self.output_path = post_path(self.draft.filename)
        lines = [
            f"标题    ：{self.draft.title}",
            f"文件名  ：{self.draft.filename}.md",
            f"分类    ：{', '.join(self.draft.categories) or '（未选择）'}",
            f"标签    ：{', '.join(self.draft.tags) or '（未选择）'}",
            f"创建时间：{self.draft.created_at}",
        ]
        if self.draft.password:
            lines.append(f"访问密码：{self.draft.password}")
        if self.draft.code_height_limit:
            lines.append(f"代码高度限制：{self.draft.code_height_limit} 行")
        lines.append(f"输出路径：{self.output_path.as_posix()}")
        self.query_one("#details", Static).update("\n".join(lines))

        yaml_content = generate_yaml_content(
            title=self.draft.title,
            categories=self.draft.categories,
            tags=self.draft.tags,
            password=self.draft.password,
            code_height_limit=self.draft.code_height_limit,
        )
        self.query_one("#preview", TextArea).load_text(yaml_content.rstrip())

        conflict = self.query_one("#conflict", Static)
        if self.output_path.exists():
            conflict.update("⚠ 该文件已存在，继续生成将覆盖原内容。")
            conflict.add_class("-warn")
        else:
            conflict.update("该文件尚不存在，将新建文件。")
            conflict.remove_class("-warn")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "generate":
            self.action_generate()
        elif event.button.id == "back":
            self.app.pop_screen()
        elif event.button.id == "rename":
            self.app.pop_screens_above(MetadataScreen)
            self.app.notify("请修改文件名后重新进入预览", severity="information")

    def action_generate(self) -> None:
        overwritten = self.output_path.exists()
        try:
            output_dir = ensure_output_directory()
            target = output_dir / f"{self.draft.filename}.md"
            target.write_text(generate_blog_post_content(self.draft), encoding="utf-8")
        except OSError as error:
            self.notify(f"写入失败：{error}", severity="error", timeout=8)
            return
        self.app.push_screen(
            ResultScreen(self.draft, str(target), overwritten=overwritten)
        )


class ResultScreen(BaseScreen):
    """生成结果与后续操作。"""

    BINDINGS = BaseScreen.BINDINGS + [
        Binding("ctrl+n", "new_post", "再写一篇", show=False),
    ]

    def __init__(self, draft: PostDraft, output_path: str, *, overwritten: bool = False):
        super().__init__()
        self.draft = draft
        self.output_path = output_path
        self.overwritten = overwritten

    def compose(self) -> ComposeResult:
        yield from super().compose()
        with VerticalScroll(id="main"):
            yield Static("✓ 生成成功", classes="success-title")
            yield Static("", id="result-details", markup=False)
            with Horizontal(classes="buttons"):
                yield Button("再写一篇", variant="primary", id="again")
                yield Button("退出", id="quit")
        yield Static(HINTS, classes="hints")

    def on_mount(self) -> None:
        lines = [
            f"文件：{Path(self.output_path).as_posix()}",
            f"标题：{self.draft.title}",
            f"分类：{', '.join(self.draft.categories) or '（无）'}",
            f"标签：{', '.join(self.draft.tags) or '（无）'}",
        ]
        if self.overwritten:
            lines.append("提示：该文件为覆盖写入。")
        self.query_one("#result-details", Static).update("\n".join(lines))

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "again":
            self.action_new_post()
        elif event.button.id == "quit":
            self.app.exit()

    def action_new_post(self) -> None:
        self.app.start_new_post()


# --------------------------------------------------------------------------- #
# 应用
# --------------------------------------------------------------------------- #


class BlogCreatorApp(App):
    """博客模板生成器主应用。"""

    CSS = """
    Screen {
        background: $surface;
    }

    #main {
        padding: 1 2;
    }

    .steps {
        color: $accent;
        text-style: bold;
        padding-bottom: 1;
    }

    .muted {
        color: $text-muted;
        padding-bottom: 1;
    }

    .section-title {
        text-style: bold;
        color: $accent;
        padding: 1 0 0 0;
    }

    .success-title {
        text-style: bold;
        color: $success;
        padding-bottom: 1;
    }

    #details {
        padding: 0 0 1 0;
    }

    #conflict {
        color: $text-muted;
        padding: 0 0 1 0;
    }

    #conflict.-warn {
        color: $warning;
        text-style: bold;
    }

    #preview {
        height: 1fr;
        min-height: 8;
        max-height: 20;
        border: round $panel-lighten-2;
    }

    Input {
        margin-bottom: 1;
    }

    SelectionList {
        height: 1fr;
        min-height: 6;
        border: round $panel-lighten-2;
        margin-bottom: 1;
    }

    .buttons {
        height: auto;
        padding-top: 1;
    }

    .buttons Button {
        margin-right: 2;
    }

    .hints {
        dock: bottom;
        height: 1;
        padding: 0 2;
        color: $text-muted;
        background: $panel;
    }
    """

    TITLE = "Valaxy 博客模板生成器"
    SUB_TITLE = "create.py"

    def __init__(self, category_usage=None, tag_usage=None) -> None:
        super().__init__()
        self.category_usage: OrderedDict = (
            category_usage if category_usage is not None else OrderedDict()
        )
        self.tag_usage: OrderedDict = tag_usage if tag_usage is not None else OrderedDict()
        # 扫描得到的原始集合：用于判断某个分类/标签是否为仓库里已有的
        self._scanned_categories = set(self.category_usage)
        self._scanned_tags = set(self.tag_usage)
        # 本次会话可编辑的候选池（已有 + 本次新增）
        self.category_source: OrderedDict = OrderedDict(self.category_usage)
        self.tag_source: OrderedDict = OrderedDict(self.tag_usage)

    def on_mount(self) -> None:
        self.start_new_post()

    # -- 供页面调用的公共操作 ---------------------------------------------- #

    def is_scanned_category(self, name: str) -> bool:
        """该分类是否来自仓库里已有的文章。"""
        return name in self._scanned_categories

    def is_scanned_tag(self, name: str) -> bool:
        """该标签是否来自仓库里已有的文章。"""
        return name in self._scanned_tags

    def start_new_post(self) -> None:
        """清空编辑状态并回到第一步。"""
        self.pop_screens_above(MetadataScreen)
        metadata_screens = [
            screen for screen in self.screen_stack if isinstance(screen, MetadataScreen)
        ]
        if metadata_screens:
            # 复用底层的基本信息页并清空表单
            metadata_screens[0].reset()
        else:
            self.push_screen(MetadataScreen())

    def pop_screens_above(self, screen_type: type) -> None:
        """从栈顶逐个回退，直到最上层就是指定类型的页面。

        注意 ``pop_screen()`` 只是把目标屏幕弹栈并排队一次切换动画，
        这里直接在当前屏幕消息处理结束后逐个 dismiss，避免连弹时弹错对象。
        """
        to_dismiss = []
        for screen in reversed(self.screen_stack[1:]):
            if isinstance(screen, screen_type):
                break
            to_dismiss.append(screen)
        for screen in to_dismiss:
            screen.dismiss()


def main() -> None:
    """程序入口：先扫描已有分类 / 标签，再启动 TUI。"""
    category_usage, tag_usage = scan_posts()
    BlogCreatorApp(category_usage=category_usage, tag_usage=tag_usage).run()


if __name__ == "__main__":
    main()
