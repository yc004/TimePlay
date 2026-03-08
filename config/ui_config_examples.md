# UI配置示例

## 当前配置（默认）

当前使用的配置在 `config/ui_config.json`

## 预设配置示例

### 1. 超大字体模式（推荐用于投影仪/大屏幕）

适合3-5米距离观看

```json
{
  "calendar_view": {
    "fonts": {
      "weekday_header": {"size": 28, "weight": "bold", "color": "white"},
      "task_name": {"size": 26, "weight": "bold", "color": "#1976D2"},
      "time_display": {"size": 22, "weight": "bold", "color": "#555"},
      "time_label": {"size": 24, "weight": "bold", "color": "#1976D2"},
      "playlist_content": {"size": 20, "weight": "normal", "color": "#444"},
      "empty_cell": {"size": 40, "color": "#BDBDBD"}
    },
    "layout": {
      "grid_spacing": 3,
      "task_block_padding": 15,
      "task_block_spacing": 12,
      "content_line_height": 2.0,
      "time_column_min_width": 100,
      "time_column_max_width": 120,
      "header_min_height": 50,
      "header_max_height": 60,
      "cell_min_height": 100
    }
  }
}
```

### 2. 标准模式（推荐用于普通显示器）

适合1-2米距离观看

```json
{
  "calendar_view": {
    "fonts": {
      "weekday_header": {"size": 20, "weight": "bold", "color": "white"},
      "task_name": {"size": 20, "weight": "bold", "color": "#1976D2"},
      "time_display": {"size": 16, "weight": "bold", "color": "#555"},
      "time_label": {"size": 18, "weight": "bold", "color": "#1976D2"},
      "playlist_content": {"size": 15, "weight": "normal", "color": "#444"},
      "empty_cell": {"size": 32, "color": "#BDBDBD"}
    },
    "layout": {
      "grid_spacing": 2,
      "task_block_padding": 12,
      "task_block_spacing": 10,
      "content_line_height": 1.8,
      "time_column_min_width": 90,
      "time_column_max_width": 110,
      "header_min_height": 45,
      "header_max_height": 55,
      "cell_min_height": 80
    }
  }
}
```

### 3. 紧凑模式（推荐用于小屏幕/笔记本）

适合近距离观看

```json
{
  "calendar_view": {
    "fonts": {
      "weekday_header": {"size": 14, "weight": "bold", "color": "white"},
      "task_name": {"size": 14, "weight": "bold", "color": "#1976D2"},
      "time_display": {"size": 12, "weight": "bold", "color": "#555"},
      "time_label": {"size": 13, "weight": "bold", "color": "#1976D2"},
      "playlist_content": {"size": 11, "weight": "normal", "color": "#444"},
      "empty_cell": {"size": 20, "color": "#BDBDBD"}
    },
    "layout": {
      "grid_spacing": 1,
      "task_block_padding": 8,
      "task_block_spacing": 6,
      "content_line_height": 1.5,
      "time_column_min_width": 70,
      "time_column_max_width": 90,
      "header_min_height": 35,
      "header_max_height": 40,
      "cell_min_height": 60
    }
  }
}
```

### 4. 深色主题

```json
{
  "calendar_view": {
    "colors": {
      "playlist_bg": "#263238",
      "playlist_border": "#4CAF50",
      "video_bg": "#37474F",
      "video_border": "#FBC02D",
      "web_bg": "#455A64",
      "web_border": "#03A9F4",
      "empty_cell_bg": "#1E1E1E",
      "empty_cell_border": "#424242",
      "header_bg": "#1976D2",
      "header_border": "#0D47A1",
      "corner_bg": "#0D47A1",
      "corner_border": "#01579B",
      "time_label_bg": "#263238",
      "time_label_border": "#37474F"
    }
  }
}
```

### 5. 浅色主题（高对比度）

```json
{
  "calendar_view": {
    "colors": {
      "playlist_bg": "#F1F8E9",
      "playlist_border": "#689F38",
      "video_bg": "#FFF3E0",
      "video_border": "#F57C00",
      "web_bg": "#E0F7FA",
      "web_border": "#0097A7",
      "empty_cell_bg": "#FFFFFF",
      "empty_cell_border": "#BDBDBD",
      "header_bg": "#1976D2",
      "header_border": "#0D47A1",
      "corner_bg": "#1976D2",
      "corner_border": "#0D47A1",
      "time_label_bg": "#E3F2FD",
      "time_label_border": "#90CAF9"
    }
  }
}
```

### 6. 无图标模式

```json
{
  "calendar_view": {
    "content": {
      "max_playlist_items": 5,
      "filename_max_length": 30,
      "show_icons": false,
      "icons": {
        "video": "",
        "image": "",
        "web": "",
        "unknown": ""
      }
    }
  }
}
```

### 7. 显示更多内容

```json
{
  "calendar_view": {
    "content": {
      "max_playlist_items": 10,
      "filename_max_length": 30,
      "show_icons": true,
      "icons": {
        "video": "🎬",
        "image": "🖼️",
        "web": "🌐",
        "unknown": "📄"
      }
    }
  }
}
```

## 快速切换配置

### 方法1: 直接替换

1. 备份当前配置
   ```bash
   copy config\ui_config.json config\ui_config.json.backup
   ```

2. 复制上面的示例配置到 `config/ui_config.json`

3. 重启应用

### 方法2: 合并配置

只修改需要的部分，保留其他配置不变。

例如，只想改字体大小：

```json
{
  "calendar_view": {
    "fonts": {
      "weekday_header": {"size": 24, "weight": "bold", "color": "white"},
      "task_name": {"size": 24, "weight": "bold", "color": "#1976D2"}
    }
  }
}
```

## 自定义配置建议

### 字体大小建议

| 使用场景 | 标题 | 内容 | 说明 |
|---------|------|------|------|
| 投影仪/大屏 | 24-28px | 18-22px | 远距离观看 |
| 普通显示器 | 18-22px | 14-18px | 中距离观看 |
| 笔记本 | 14-16px | 11-13px | 近距离观看 |

### 颜色选择建议

- **背景色**: 使用浅色，避免过于鲜艳
- **边框色**: 比背景色深一些，形成对比
- **文字色**: 深色，确保可读性
- **对比度**: 背景和文字对比度至少4.5:1

### 布局间距建议

- **网格间距**: 1-3px
- **内边距**: 8-15px
- **元素间距**: 6-12px
- **行高**: 1.5-2.0

## 测试配置

修改配置后，运行测试：

```bash
python test_ui_config.py
```

查看配置是否正确加载。

## 恢复默认配置

如果配置出现问题，可以删除配置文件，系统会自动使用默认配置：

```bash
del config\ui_config.json
```

或者从备份恢复：

```bash
copy config\ui_config.json.backup config\ui_config.json
```

---

**提示**: 修改配置前建议先备份，逐步调整参数，每次修改后测试效果。
