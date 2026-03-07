UniGroupBuy 接口规范（后端协作草案）

> 说明：本文档由前端根据当前页面和交互设计整理，作为后端开发的参考接口草案。
> 具体实现时，可以在不影响前端字段的前提下，与前端同学一起微调。

---

一、认证（Auth）相关

| 接口名称         | 方法 | 接口名          | 参数                                    |
| ---------------- | ---- | --------------- | --------------------------------------- |
| 用户登录         | POST | login           | email, password                         |
| 用户注册         | POST | register        | fullName, email, password1, password2   |
| 退出登录         | POST | logout          | /（使用当前会话，无额外参数）          |
| 获取当前登录用户 | GET  | getCurrentUser  | /（根据会话获取当前用户信息）          |

建议 URL 示例（可按项目风格调整）：

- `/api/auth/login`
- `/api/auth/register`
- `/api/auth/logout`
- `/api/auth/me`

---

 二、团购（GroupBuy）相关

 2.1 团购接口列表

| 接口名称                           | 方法 | 接口名            | 参数                                                                 |
| ---------------------------------- | ---- | ----------------- | -------------------------------------------------------------------- |
| 创建或修改团购                     | POST | editGroupBuy      | GroupBuy 对象（见下方字段说明）                                     |
| 获取团购详情                       | GET  | getGroupBuyDetail | id                                                                   |
| 分页获取团购列表（Dashboard）      | POST | getGroupBuyPage   | pageNo, pageSize, category(可选), status(可选), searchKeyword(可选) |
| 获取当前用户参与/发起的团购列表    | GET  | getMyGroupBuyList | /（从会话中识别当前用户）                                           |
| 关闭团购（可选，仅发起者使用）     | POST | closeGroupBuy     | id                                                                   |

建议 URL 示例：

- `/api/groupbuy/edit`
- `/api/groupbuy/detail`
- `/api/groupbuy/page`
- `/api/groupbuy/my-list`
- `/api/groupbuy/close`

 2.2 GroupBuy 对象字段建议

创建或修改团购时，前端期望传入的字段（JSON）：

```json
{
  "id": 1,
  "title": "Bubble Tea Happy Hour",
  "storeName": "Byres Road Tea House",
  "category": "Food",
  "deadline": "2030-06-01T18:00:00",
  "pickupInstructions": "Meet at the University of Glasgow library entrance at 6:30 PM."
}
```

字段说明：

- `id`：团购主键，修改时必填，新建时可省略或为 null
- `title`：团购标题
- `storeName`：店铺名称（示例：Byres Road Tea House）
- `category`：`Food` / `Grocery` / `Stationery` / `Other`
- `deadline`：截止时间字符串（格式前后端约定一致，如 ISO8601）
- `pickupInstructions`：取货说明

状态字段 `status`（`open` / `ordered` / `closed`）建议由后端内部维护，前端只读取。

---

 三、团购条目（Item，“Add Item” 功能）相关

 3.1 Item 接口列表

| 接口名称                         | 方法 | 接口名             | 参数                                                                    |
| -------------------------------- | ---- | ------------------ | ----------------------------------------------------------------------- |
| 添加一条团购条目（Add Item）     | POST | addGroupBuyItem    | groupBuyId, itemName, quantity, price, addedBy                          |
| 获取某个团购的条目列表           | GET  | getGroupBuyItemList| groupBuyId                                                              |
| 删除团购条目（可选，仅发起者用） | POST | deleteGroupBuyItem | itemId                                                                  |

建议 URL 示例：

- `/api/groupbuy/add-item`
- `/api/groupbuy/item-list`
- `/api/groupbuy/delete-item`

 3.2 Item 字段说明

新增 Item 时，前端期望发送的 JSON：

```json
{
  "groupBuyId": 1,
  "itemName": "Large classic milk tea",
  "quantity": "2",
  "price": "4.50",
  "addedBy": "Alex Johnson"
}
```

返回可以简单使用 201/204 状态码；如需返回内容，建议返回新建 Item 的 id 和标准化后的价格等。

---

 四、订单 / 我的订单（My Orders）相关

 4.1 接口列表

| 接口名称                         | 方法 | 接口名            | 参数             |
| -------------------------------- | ---- | ----------------- | ---------------- |
| 获取当前用户订单概览（统计信息） | GET  | getMyOrderSummary | /                |
| 分页获取当前用户订单列表         | GET  | getMyOrderList    | pageNo, pageSize |

建议 URL 示例：

- `/api/order/my-summary`
- `/api/order/my-list`

 4.2 返回数据建议

`getMyOrderSummary` 返回示例：

```json
{
  "displayName": "Alex Johnson",
  "email": "alex.johnson@example.edu",
  "joinedThisWeek": 1,
  "completedThisMonth": 2,
  "activeGroupBuys": 3,
  "completedOrders": 5,
  "estimatedSavings": "32.40"
}
```

`getMyOrderList` 返回示例：

```json
{
  "pageNo": 1,
  "pageSize": 10,
  "total": 3,
  "orders": [
    {
      "groupBuyId": 1,
      "groupBuyTitle": "Bubble Tea Happy Hour",
      "storeName": "Byres Road Tea House",
      "status": "open",
      "role": "participant",
      "itemsCount": 3,
      "totalPrice": "12.00"
    }
  ]
}
```

---

 五、用户 Profile 相关

 5.1 接口列表

| 接口名称                 | 方法 | 接口名               | 参数 |
| ------------------------ | ---- | -------------------- | ---- |
| 获取当前用户 Profile 信息 | GET  | getCurrentUserProfile| /    |
| 更新默认取货地点（可选） | POST | updatePickupLocation | pickupLocation |
| 更新通知偏好（可选）     | POST | updateNotification   | notificationPreference |

建议 URL 示例：

- `/api/user/profile`
- `/api/user/update-pickup-location`
- `/api/user/update-notification`

 5.2 Profile 返回示例

```json
{
  "initials": "AJ",
  "displayName": "Alex Johnson",
  "email": "alex.johnson@example.edu",
  "campus": "Gilmorehill Campus",
  "joinedSince": "2024-09-01",
  "preferredPickupSpot": "University of Glasgow library entrance",
  "notifications": "Email and in-app",
  "activeGroupBuys": 3,
  "completedOrders": 5,
  "estimatedSavings": "32.40"
}
```

---

 六、字段命名与前端约定

前端已经使用的表单字段名（建议后端沿用）：

- 登录：`email`, `password`, `remember`
- 注册：`full_name`, `email`, `password1`, `password2`
- 创建团购：`title`, `store_name`, `category`, `deadline`, `pickup_instructions`
- 添加 Item（JSON）：`item_name`, `quantity`, `price`, `added_by`

如果后端希望接口层统一使用驼峰命名（如 `storeName`），可以在视图中做一次转换，但模板中的表单字段名建议不要再改，以免影响现有前端逻辑。

