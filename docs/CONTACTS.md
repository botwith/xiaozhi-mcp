# 联系人MCP使用指南

联系人MCP是一个用于管理联系人信息的工具，支持存储和管理联系人的各种联系方式，包括电话、邮箱、微信ID等，并支持场景备注（如个人、办公等）。

## 功能特性

- ✅ 存储联系人信息（姓名、电话、邮箱、微信ID、GitHub ID、X ID、生日、备注等）
- ✅ 支持场景备注（电话、邮箱、微信ID可标记为"个人"、"办公"等）
- ✅ 可扩展字段支持
- ✅ 完整的CRUD操作（创建、读取、更新、删除）
- ✅ 生日提醒功能
- ✅ 与其他MCP工具集成（如邮件MCP、电话MCP等）

## 数据模型

每个联系人包含以下字段：

### 必填字段
- `name` (string): 姓名

### 可选字段
- `phones` (array): 电话列表，每个电话包含：
  - `value` (string): 电话号码
  - `label` (string): 场景备注（如"个人"、"办公"）
- `emails` (array): 邮箱列表，每个邮箱包含：
  - `value` (string): 邮箱地址
  - `label` (string): 场景备注（如"个人"、"办公"）
- `wechat_ids` (array): 微信ID列表，每个微信ID包含：
  - `value` (string): 微信ID
  - `label` (string): 场景备注（如"个人"、"办公"）
- `github_id` (string): GitHub用户名
- `x_id` (string): X（Twitter）用户名
- `birthday` (string): 生日，格式 YYYY-MM-DD
- `notes` (string): 备注信息
- `extra_fields` (object): 扩展字段，可存储任意自定义数据

## 工具函数

### 1. get_all_contacts()

获取所有联系人列表。

**返回示例：**
```json
{
  "success": true,
  "count": 2,
  "contacts": [
    {
      "id": "uuid-123",
      "name": "张三",
      "phones": [
        {"value": "13800138000", "label": "个人"},
        {"value": "010-12345678", "label": "办公"}
      ],
      "emails": [
        {"value": "zhangsan@example.com", "label": "个人"}
      ],
      "wechat_ids": [
        {"value": "zhangsan123", "label": "个人"}
      ],
      "github_id": "zhangsan",
      "x_id": null,
      "birthday": "1990-01-01",
      "notes": "好朋友",
      "extra_fields": {}
    }
  ],
  "timestamp": "2024-01-01T12:00:00"
}
```

### 2. get_contact_by_id(contact_id)

根据联系人ID获取联系人信息。

**参数：**
- `contact_id` (string): 联系人的唯一标识ID

### 3. get_contact_by_name(name)

根据姓名获取联系人信息。

**参数：**
- `name` (string): 联系人的姓名

### 4. edit_contact(...)

创建或编辑联系人。如果提供了 `contact_id` 且该联系人存在，则更新；否则创建新联系人。

**参数：**
- `name` (string, 必填): 姓名
- `contact_id` (string, 可选): 联系人ID，如果提供且存在则更新，否则创建新联系人
- `phones` (array, 可选): 电话列表，格式：`[{"value": "13800138000", "label": "个人"}, ...]`
- `emails` (array, 可选): 邮箱列表，格式：`[{"value": "user@example.com", "label": "办公"}, ...]`
- `wechat_ids` (array, 可选): 微信ID列表，格式：`[{"value": "wechat123", "label": "个人"}, ...]`
- `github_id` (string, 可选): GitHub用户名
- `x_id` (string, 可选): X（Twitter）用户名
- `birthday` (string, 可选): 生日，格式 YYYY-MM-DD
- `notes` (string, 可选): 备注
- `extra_fields` (object, 可选): 扩展字段字典

**示例：**
```python
# 创建新联系人
edit_contact(
    name="李四",
    phones=[{"value": "13900139000", "label": "个人"}],
    emails=[{"value": "lisi@example.com", "label": "办公"}],
    birthday="1992-05-15",
    notes="同事"
)

# 更新现有联系人
edit_contact(
    contact_id="uuid-123",
    name="张三",
    phones=[{"value": "13800138000", "label": "个人"}, {"value": "010-12345678", "label": "办公"}]
)
```

### 5. delete_contact(contact_id=None, name=None)

删除指定联系人。可以通过 `contact_id` 或 `name` 来指定要删除的联系人。

**参数：**
- `contact_id` (string, 可选): 联系人的唯一标识ID（优先使用）
- `name` (string, 可选): 联系人的姓名（如果 contact_id 未提供则使用此参数）

### 6. get_birthday_contacts(today=None)

获取今天过生日的联系人列表。

**参数：**
- `today` (string, 可选): 日期字符串，格式 YYYY-MM-DD（默认为今天）

**返回示例：**
```json
{
  "success": true,
  "count": 1,
  "contacts": [
    {
      "id": "uuid-123",
      "name": "张三",
      "birthday": "1990-01-01",
      ...
    }
  ],
  "date": "2024-01-01",
  "timestamp": "2024-01-01T12:00:00"
}
```

## 使用示例

### 示例1：创建联系人

```python
# 创建包含多个联系方式的联系人
edit_contact(
    name="王五",
    phones=[
        {"value": "13800138000", "label": "个人"},
        {"value": "010-87654321", "label": "办公"}
    ],
    emails=[
        {"value": "wangwu@example.com", "label": "个人"},
        {"value": "wangwu@company.com", "label": "办公"}
    ],
    wechat_ids=[
        {"value": "wangwu123", "label": "个人"}
    ],
    github_id="wangwu",
    x_id="wangwu_twitter",
    birthday="1988-03-20",
    notes="技术专家"
)
```

### 示例2：查询今天过生日的人并发送祝福

```python
# 1. 查询今天过生日的人
birthday_result = get_birthday_contacts()

if birthday_result["success"] and birthday_result["count"] > 0:
    for contact in birthday_result["contacts"]:
        name = contact["name"]
        print(f"今天是 {name} 的生日！")
        
        # 2. 获取联系人的邮箱（优先使用个人邮箱）
        emails = contact.get("emails", [])
        personal_email = None
        for email in emails:
            if email.get("label") == "个人":
                personal_email = email["value"]
                break
        
        # 如果没有个人邮箱，使用第一个邮箱
        if not personal_email and emails:
            personal_email = emails[0]["value"]
        
        # 3. 发送生日祝福邮件（需要调用email MCP）
        if personal_email:
            send_email(
                to_email=personal_email,
                subject=f"生日快乐，{name}！",
                body=f"亲爱的{name}，祝你生日快乐，身体健康，工作顺利！"
            )
```

### 示例3：打电话给联系人

```python
# 1. 根据姓名查找联系人
contact_result = get_contact_by_name("张三")

if contact_result["success"]:
    contact = contact_result["contact"]
    
    # 2. 获取联系人的电话（优先使用个人电话）
    phones = contact.get("phones", [])
    personal_phone = None
    for phone in phones:
        if phone.get("label") == "个人":
            personal_phone = phone["value"]
            break
    
    # 如果没有个人电话，使用第一个电话
    if not personal_phone and phones:
        personal_phone = phones[0]["value"]
    
    # 3. 拨打电话（需要调用mac_app_launcher MCP）
    if personal_phone:
        call_phone_number(personal_phone)
```

## 数据存储

联系人数据存储在 SQLite 数据库中，文件路径为 `data/contacts.db`。数据库会在首次使用时自动创建。

### 数据库结构

**主表：contacts**
- `id` (TEXT PRIMARY KEY): 联系人唯一标识
- `name` (TEXT NOT NULL): 姓名
- `github_id` (TEXT): GitHub用户名
- `x_id` (TEXT): X（Twitter）用户名
- `birthday` (TEXT): 生日（YYYY-MM-DD格式）
- `notes` (TEXT): 备注
- `extra_fields` (TEXT): 扩展字段（JSON格式）
- `created_at` (TEXT): 创建时间
- `updated_at` (TEXT): 更新时间

**关联表：contact_phones**
- `id` (INTEGER PRIMARY KEY): 自增ID
- `contact_id` (TEXT): 联系人ID（外键）
- `value` (TEXT): 电话号码
- `label` (TEXT): 场景备注（如"个人"、"办公"）

**关联表：contact_emails**
- `id` (INTEGER PRIMARY KEY): 自增ID
- `contact_id` (TEXT): 联系人ID（外键）
- `value` (TEXT): 邮箱地址
- `label` (TEXT): 场景备注（如"个人"、"办公"）

**关联表：contact_wechat_ids**
- `id` (INTEGER PRIMARY KEY): 自增ID
- `contact_id` (TEXT): 联系人ID（外键）
- `value` (TEXT): 微信ID
- `label` (TEXT): 场景备注（如"个人"、"办公"）


### 优势

- ✅ **高性能查询**：使用索引加速查询，支持复杂SQL查询
- ✅ **并发安全**：支持多进程/多线程安全访问
- ✅ **数据完整性**：使用外键约束保证数据一致性
- ✅ **可扩展性**：易于添加新字段和索引
- ✅ **标准格式**：SQLite是标准数据库格式，易于备份和迁移

## 与其他MCP集成

联系人MCP可以与其他MCP工具配合使用，实现更强大的功能：

1. **与Email MCP集成**：根据联系人信息发送邮件
2. **与Mac App Launcher MCP集成**：根据联系人信息拨打电话
3. **与其他MCP集成**：通过扩展字段存储其他平台的信息

## 注意事项

1. 姓名是必填字段，其他字段都是可选的
2. 电话、邮箱、微信ID支持多个值，每个值都可以有场景备注
3. 联系人ID是自动生成的UUID，用于唯一标识每个联系人
4. 数据文件存储在 `data/contacts.json`，建议定期备份
5. 生日格式必须为 YYYY-MM-DD

## 扩展性

通过 `extra_fields` 字段，可以存储任意自定义数据，例如：
- 公司名称
- 职位
- 地址
- 其他社交平台账号
- 自定义标签

示例：
```python
edit_contact(
    name="赵六",
    extra_fields={
        "company": "ABC公司",
        "position": "高级工程师",
        "address": "北京市朝阳区",
        "linkedin": "zhaoliu"
    }
)
```
