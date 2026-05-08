---
AIGC:
    ContentProducer: Minimax Agent AI
    ContentPropagator: Minimax Agent AI
    Label: AIGC
    ProduceID: 343cd0303b43296c80ea82a32d47ce99
    PropagateID: 343cd0303b43296c80ea82a32d47ce99
    ReservedCode1: 3044022071376643b810cefe700cfd5c0b46d84fdb2c30dfe85a4eac453b3ffcd7671ba702200d0fcb9aee37053e5f2137c3975f31692a57487774be34e923c16c602af8180f
    ReservedCode2: 304402202c70dc35a41164e4f278891d5a1cb451406cc000a0af0164c65b390361e1882202200c721985e4b9715eb103cff9a30c04f94db7d0c2de2d8cb91917e8f25c9c2ccd
---

# 🎓 RabbitMQ 消息队列完全教程

> 从零开始学习消息队列，理解核心概念，掌握 RabbitMQ 实战技能

---

## 📚 目录

1. [什么是消息队列？为什么要用它？](#第一章-什么是消息队列为什么要用它)
2. [RabbitMQ 核心概念详解](#第二章-rabbitmq核心概念详解)
3. [快速上手：安装和连接](#第三章-快速上手安装和连接)
4. [生产者与消费者：最简单的方式](#第四章-生产者与消费者最简单的方式)
5. [工作队列：多个工人分担任务](#第五章-工作队列多个工人分担任务)
6. [交换机：消息的智能路由](#第六章-交换机消息的智能路由)
7. [主题交换机：用通配符匹配消息](#第七章-主题交换机用通配符匹配消息)
8. [实战项目：构建订单处理系统](#第八章-实战项目构建订单处理系统)
9. [最佳实践与常见问题](#第九章-最佳实践与常见问题)

---

# 第一章：什么是消息队列？为什么要用它？

## 🤔 先思考一个问题

想象你在一家餐厅点餐：

**没有消息队列的情况：**
```
你 → 跟服务员说话 → 服务员亲自去厨房盯着厨师做菜 → 等厨师做完 → 服务员端给你
```

问题在哪？
- 服务员要一直等着，不能做其他事
- 如果客人很多，服务员忙不过来
- 如果厨师做菜很慢，所有人都在等

**有消息队列的情况：**
```
你 → 把订单交给前台收银 → 收银员转身继续接待下一位客人
              ↓
         厨房收到订单（先进先出排队）
              ↓
         厨师按顺序做菜
              ↓
         菜做好了，有人通知你来取
```

这样前台可以同时接待很多人，厨房有条不紊地工作。

---

## 💡 什么是消息队列？

**消息队列（Message Queue）** 就像餐厅的前台收银系统：

- 你把"订单"（消息）交给队列
- 队列会按顺序保存这些订单
- 其他人（消费者）可以从队列中取出订单来处理

**核心特点：**
1. **解耦**：发送者和接收者不需要知道对方的存在
2. **异步**：发送消息后可以立即返回，不用等待处理完成
3. **削峰填谷**：高峰期积累的请求会慢慢被处理，不会系统崩溃
4. **可靠性**：消息会持久保存，不会丢失

---

## 🏢 什么时候需要消息队列？

### 场景1：用户注册后发送欢迎邮件

```
❌ 没有队列：
用户点击注册 → 系统注册 → 发送邮件 → 返回成功
               ↓
          如果邮件服务器慢，用户要等很久

✅ 有队列：
用户点击注册 → 系统注册 → 发到队列 → 立即返回"注册成功"
                        ↓
                   后台发送邮件（用户无感知等待）
```

### 场景2：处理大量图片上传

```
❌ 没有队列：
用户上传100张图片 → 系统一张张处理 → 用户等待5分钟

✅ 有队列：
用户上传100张图片 → 图片进入队列 → 立即返回"上传成功"
                                   ↓
                              5个后台worker同时处理
                              1分钟完成
```

### 场景3：支付系统

```
用户支付 → 扣款 → 发货通知 → 积分入账 → 发短信 → 发邮件

如果用同步方式：任何一个环节出错，整个支付就失败了

用队列方式：每个环节独立，一个失败不影响其他
```

---

## 📊 消息队列 vs 直接调用

| 对比项 | 直接调用 | 消息队列 |
|--------|----------|----------|
| 耦合度 | 高（调用方和被调用方紧密耦合） | 低（通过队列通信） |
| 性能 | 同步等待 | 异步处理 |
| 可靠性 | 失败即失败 | 可以重试 |
| 扩展性 | 难扩展 | 容易增加消费者 |
| 适用场景 | 简单同步操作 | 复杂异步流程 |

---

## 🎯 小结

- 消息队列就像餐厅的前台，让"点餐"和"做菜"解耦
- 它实现了异步处理，提高系统整体效率
- 它可以削峰填谷，让系统在高峰期不会崩溃
- 它提高了系统的可靠性和可扩展性

---

# 第二章：RabbitMQ核心概念详解

## 🐇 RabbitMQ 是什么？

RabbitMQ 是一个实现了 AMQP（高级消息队列协议）的消息中间件。

简单理解：它是那个帮你管理"消息队列"的软件/服务。

同类产品还有：Kafka、Redis 队列、ActiveMQ 等。

---

## 🏗️ 核心架构图

```
┌─────────┐         ┌────────────┐         ┌─────────┐
│ 生产者   │ ──────→ │   交换机    │ ──────→ │  队列   │
│ Producer│         │  Exchange   │         │  Queue  │
└─────────┘         └────────────┘         └────┬────┘
                                               ↓
                                         ┌───────────┐
                                         │  消费者    │
                                         │  Consumer  │
                                         └───────────┘
```

### 用餐厅来理解：

- **生产者(Producer)** = 顾客（点餐的人）
- **交换机(Exchange)** = 前台收银员（决定订单去哪）
- **队列(Queue)** = 厨房的排队单子（按顺序等待处理）
- **消费者(Consumer)** = 厨师（处理订单的人）

---

## 📦 详细解释每个概念

### 1. 生产者 (Producer)

生产者是**发送消息的程序/代码**。

```
# 生产者的工作：
1. 创建消息
2. 把消息发送到 RabbitMQ
3. 发送完成后继续做其他事（异步）
```

### 2. 消费者 (Consumer)

消费者是**接收和处理消息的程序/代码**。

```
# 消费者的死循环：
while True:
    从队列取一个消息
    处理消息
    告诉 RabbitMQ "处理完了"（确认）
```

### 3. 队列 (Queue)

队列是**存储消息的容器**。

```
特点：
- 先进先出（FIFO）：先来的消息先被处理
- 可以存储任意类型的消息
- 可以设置消息过期时间
- 可以设置队列长度限制
```

### 4. 交换机 (Exchange)

交换机是**消息的分配中心**，决定消息应该去哪个队列。

```
交换机的工作：
接收消息 → 根据规则决定 → 发到哪个队列
```

### 5. 绑定 (Binding)

绑定是**连接交换机和队列的规则**。

```
交换机 ──绑定规则──→ 队列
例如：绑定规则说"所有日志消息去 error_queue"
```

### 6. 路由键 (Routing Key)

路由键是**消息的一个标签**，用于交换机决定消息去哪。

```
类似于：快递单上的"收件地址"
交换机根据路由键+绑定规则 决定消息去哪个队列
```

---

## 🔄 消息的完整流向

```
1. 生产者发送消息
   消息内容 + 路由键 → 交换机

2. 交换机接收消息
   查看绑定规则，找到匹配的队列

3. 消息进入队列
   按先进先出顺序等待

4. 消费者从队列取消息
   取到消息后开始处理

5. 消费者确认处理完成
   消息从队列中删除
```

---

## 🎯 四种交换机类型

| 类型 | 说明 | 比喻 |
|------|------|------|
| **direct** | 精确匹配路由键 | 快递按精确地址配送 |
| **fanout** | 广播到所有绑定的队列 | 广播通知，所有人同时收到 |
| **topic** | 按模式匹配路由键 | 物流分拣，支持通配符 |
| **headers** | 按消息头属性匹配 | 按包裹标签分类 |

---

## 📝 简单记忆法

```
生产者是"发快递的人"
交换机是"分拣中心"
队列是"快递暂存区"
消费者是"收件人"
路由键是"快递单上的地址"
```

---

# 第三章：快速上手：安装和连接

## 🐳 第一步：启动 RabbitMQ

有三种方式，推荐使用 Docker：

### 方式1：Docker（推荐）

```bash
docker run -d \
  --name rabbitmq \
  -p 5672:5672 \
  -p 15672:15672 \
  rabbitmq:management
```

启动后：
- 连接地址：`localhost:5672`
- 管理界面：`http://localhost:15672`（用户名/密码：guest/guest）

### 方式2：直接安装

```bash
# macOS
brew install rabbitmq
brew services start rabbitmq

# Ubuntu/Debian
sudo apt-get install rabbitmq-server
sudo systemctl start rabbitmq
```

### 方式3：云服务

可以使用 CloudAMQP 等托管服务，无需安装。

---

## 📦 第二步：安装 Python 库

```bash
pip install pika
```

`pika` 是 Python 中最常用的 RabbitMQ 客户端库。

---

## 🔗 第三步：连接到 RabbitMQ

让我们先写一个最简单的方式连接：

```python
import pika

# 创建连接（连接到本地RabbitMQ）
connection = pika.BlockingConnection(
    pika.ConnectionParameters('localhost')
)

# 创建一个通道（Channel）
# 通道就像电话中的通话线路
channel = connection.channel()

print("✅ 成功连接到 RabbitMQ！")

# 关闭连接
connection.close()
```

**运行结果：**
```
✅ 成功连接到 RabbitMQ！
```

如果看到这行字，说明连接成功了！

---

## 🔧 连接参数详解

```python
connection = pika.BlockingConnection(
    pika.ConnectionParameters(
        host='localhost',      # RabbitMQ 服务器地址
        port=5672,            # 端口号（默认5672）
        virtual_host='/',     # 虚拟主机（类似数据库的database）
        credentials=pika.PlainCredentials(
            username='guest',    # 用户名
            password='guest'      # 密码
        )
    )
)
```

---

## 💡 连接失败？检查清单

| 问题 | 解决方法 |
|------|----------|
| 连接被拒绝 | 确认 RabbitMQ 已启动：`docker ps` |
| 连接超时 | 检查端口是否正确：`netstat -an \| grep 5672` |
| 认证失败 | 检查用户名密码是否正确 |
| 防火墙阻止 | 开放 5672 和 15672 端口 |

---

# 第四章：生产者与消费者：最简单的方式

## 🎯 这一章学什么

实现最简单的一对一式消息传递：

```
生产者 ──────────→ 队列 ──────────→ 消费者
   发送消息        存储消息        接收消息
```

---

## 📤 生产者：发送消息

```python
import pika

# 1. 建立连接
connection = pika.BlockingConnection(
    pika.ConnectionParameters('localhost')
)
channel = connection.channel()

# 2. 声明队列（如果不存在则创建）
# durable=True 表示队列持久化，重启后不会丢失
channel.queue_declare(queue='hello', durable=True)

# 3. 发送消息
message = 'Hello World!'
channel.basic_publish(
    exchange='',              # 空字符串表示使用默认交换机
    routing_key='hello',      # 路由键 = 队列名
    body=message.encode()     # 消息内容（需要编码为bytes）
)

print(f"📤 已发送消息: {message}")

# 4. 关闭连接
connection.close()
```

**运行结果：**
```
📤 已发送消息: Hello World!
```

---

## 📥 消费者：接收消息

```python
import pika

# 1. 建立连接
connection = pika.BlockingConnection(
    pika.ConnectionParameters('localhost')
)
channel = connection.channel()

# 2. 声明队列（确保队列存在）
channel.queue_declare(queue='hello', durable=True)

# 3. 定义处理函数
def callback(ch, method, properties, body):
    """当收到消息时，这个函数会被调用"""
    message = body.decode()  # 解码消息
    print(f"📥 收到消息: {message}")

    # 手动确认消息已处理
    ch.basic_ack(delivery_tag=method.delivery_tag)

# 4. 开始监听队列
channel.basic_consume(
    queue='hello',
    on_message_callback=callback
)

print("📡 正在等待消息... 按 Ctrl+C 退出")

# 5. 开始消费（进入循环）
channel.start_consuming()
```

**运行结果：**
```
📡 正在等待消息... 按 Ctrl+C 退出
📥 收到消息: Hello World!
```

---

## 🔄 完整的发送-接收流程

```python
# 终端1：启动消费者
# python consumer.py

# 终端2：发送消息
# python producer.py

# 你会看到：
# 终端1: 📥 收到消息: Hello World!
```

---

## 📋 消息确认机制

为什么要"确认"？

```
场景：消费者收到消息，处理到一半崩溃了

如果没有确认：消息丢失了
如果有确认：RabbitMQ知道消息没处理完，会重新投递
```

```python
def callback(ch, method, properties, body):
    try:
        # 处理消息
        process_message(body)
        # 成功：确认消息
        ch.basic_ack(delivery_tag=method.delivery_tag)
    except Exception as e:
        # 失败：拒绝消息，可以选择重新入队
        ch.basic_nack(delivery_tag=method.delivery_tag, requeue=True)
```

---

## ⚠️ 常见问题

### Q1: 消息发送成功但消费者没收到？

检查：
- 队列名是否一致（注意大小写）
- 消费者是否先启动（消费者会创建队列）
- 交换机和路由键是否正确

### Q2: 消息丢失怎么办？

解决方案：
1. 队列设置 `durable=True`（持久化）
2. 消息设置 `delivery_mode=2`（持久化）
3. 使用手动确认（`auto_ack=False`）

```python
channel.basic_publish(
    exchange='',
    routing_key='hello',
    body=message,
    properties=pika.BasicProperties(
        delivery_mode=2  # 消息持久化
    )
)
```

---

# 第五章：工作队列：多个工人分担任务

## 🎯 这一章学什么

场景：有很多任务需要处理，一个工人太慢，需要多个工人同时工作。

```
生产者是"派单人"
工作队列是"任务池"
多个消费者是"工人们"

工人1 ───→ 处理任务1 ───→ 处理任务4 ───→ ...
工人2 ───→ 处理任务2 ───→ 处理任务5 ───→ ...
工人3 ───→ 处理任务3 ───→ 处理任务6 ───→ ...
```

---

## 🔧 发送任务消息

```python
import pika
import json

connection = pika.BlockingConnection(
    pika.ConnectionParameters('localhost')
)
channel = connection.channel()

# 声明任务队列
channel.queue_declare(queue='task_queue', durable=True)

# 模拟发送多个任务
tasks = [
    {"task_id": 1, "type": "发送邮件", "data": "user@example.com"},
    {"task_id": 2, "type": "生成报表", "data": "2024-01"},
    {"task_id": 3, "type": "压缩图片", "data": "photo.jpg"},
]

for task in tasks:
    message = json.dumps(task)
    channel.basic_publish(
        exchange='',
        routing_key='task_queue',
        body=message.encode(),
        properties=pika.BasicProperties(
            delivery_mode=2,  # 持久化
        )
    )
    print(f"📤 已发送任务: {task['task_id']} - {task['type']}")

connection.close()
```

---

## 👷 启动多个工人

```python
import pika
import json
import time
import random

def worker(worker_name):
    """工人程序"""
    connection = pika.BlockingConnection(
        pika.ConnectionParameters('localhost')
    )
    channel = connection.channel()

    # 声明队列
    channel.queue_declare(queue='task_queue', durable=True)

    # 关键设置：同一时间只处理一个任务
    # 这样可以实现"公平分配"
    channel.basic_qos(prefetch_count=1)

    def callback(ch, method, properties, body):
        task = json.loads(body.decode())
        print(f"👷 {worker_name} 收到任务: {task['task_id']} - {task['type']}")

        # 模拟处理时间
        processing_time = random.randint(1, 3)
        time.sleep(processing_time)

        print(f"✅ {worker_name} 完成任务 {task['task_id']}，耗时 {processing_time}秒")

        # 确认消息
        ch.basic_ack(delivery_tag=method.delivery_tag)

    channel.basic_consume(
        queue='task_queue',
        on_message_callback=callback
    )

    print(f"👷 {worker_name} 已就绪，等待任务...")
    channel.start_consuming()

# 启动3个工人
if __name__ == '__main__':
    worker("工人A")
```

---

## 🧪 测试

```bash
# 终端1：启动工人A
python worker.py
# 输出: 👷 工人A 已就绪，等待任务...

# 终端2：启动工人B
python worker.py
# 输出: 👷 工人B 已就绪，等待任务...

# 终端3：启动工人C
python worker.py
# 输出: 👷 工人C 已就绪，等待任务...

# 终端4：发送任务
python send_tasks.py
# 输出:
# 📤 已发送任务: 1 - 发送邮件
# 📤 已发送任务: 2 - 生成报表
# 📤 已发送任务: 3 - 压缩图片
```

你会看到三个工人**轮流**接收任务。

---

## 📊 工作队列的特点

| 特点 | 说明 |
|------|------|
| **轮询分发** | 每个消息只分给一个消费者 |
| **公平分发** | 谁空闲谁拿任务 |
| **持久化** | 任务不会因工人崩溃而丢失 |
| **背压控制** | 防止工人过载（prefetch_count） |

---

## 💡 为什么要设置 prefetch_count=1？

```python
# 没有限制的情况：
# 假设有3个任务，2个工人
# 工人A很快处理完，工人B还在忙
# 但RabbitMQ可能把3个任务都给了工人A

# 有 prefetch_count=1 的情况：
# 工人A处理完任务1后，才能拿到任务2
# 工人B处理完任务2后，才能拿到任务3
# 实现真正的负载均衡
```

---

# 第六章：交换机：消息的智能路由

## 🎯 这一章学什么

之前的例子都用的是"默认交换机"（空字符串）。

现在学习如何使用**有名字的交换机**，实现更智能的消息路由。

---

## 🏭 交换机类型

```
┌─────────────────────────────────────────────────────────────┐
│                        交换机类型                            │
├─────────────┬─────────────┬─────────────┬───────────────────┤
│   direct    │   fanout     │   topic     │     headers       │
│  精确匹配    │   广播      │   模式匹配   │    属性匹配       │
└─────────────┴─────────────┴─────────────┴───────────────────┘
```

---

## 1️⃣ fanout 交换机（广播）

### 场景：系统通知

所有订阅者都能收到消息，类似于"广播"。

```
              ┌──────────────┐
              │   交换机     │
              │  (fanout)   │
              └──────┬───────┘
                     │
        ┌────────────┼────────────┐
        ↓            ↓            ↓
   ┌─────────┐  ┌─────────┐  ┌─────────┐
   │ 邮件通知 │  │ 短信通知 │  │ 站内通知 │
   └─────────┘  └─────────┘  └─────────┘
```

### 发送者代码

```python
import pika

connection = pika.BlockingConnection(
    pika.ConnectionParameters('localhost')
)
channel = connection.channel()

# 声明fanout交换机
channel.exchange_declare(
    exchange='notifications',    # 交换机名字
    exchange_type='fanout'       # 类型：广播
)

# 发送通知（不需要指定路由键，fanout会忽略）
message = "系统将于今晚8点进行维护"
channel.basic_publish(
    exchange='notifications',    # 指定交换机
    routing_key='',              # fanout模式下忽略
    body=message.encode()
)

print(f"📢 广播发送: {message}")
connection.close()
```

### 接收者代码

```python
import pika

def subscriber(queue_name, notification_type):
    connection = pika.BlockingConnection(
        pika.ConnectionParameters('localhost')
    )
    channel = connection.channel()

    # 声明队列
    channel.queue_declare(queue=queue_name, durable=True)

    # 绑定队列到交换机（fanout不需要路由键）
    channel.queue_bind(
        exchange='notifications',
        queue=queue_name
    )

    def callback(ch, method, properties, body):
        print(f"📧 {notification_type} 收到通知: {body.decode()}")
        ch.basic_ack(delivery_tag=method.delivery_tag)

    channel.basic_consume(
        queue=queue_name,
        on_message_callback=callback
    )

    print(f"👂 {notification_type} 已订阅，等待通知...")
    channel.start_consuming()

# 启动三个订阅者
if __name__ == '__main__':
    subscriber('email_queue', '邮件系统')
    # 或 subscriber('sms_queue', '短信系统')
    # 或 subscriber('web_queue', '站内信')
```

---

## 2️⃣ direct 交换机（精确匹配）

### 场景：日志系统

根据日志级别发送到不同的队列。

```
              ┌──────────────┐
              │   交换机     │
              │  (direct)   │
              └──────┬───────┘
                     │
        ┌────────────┼────────────┐
        ↓            ↓            ↓
       info        warning      error
        ↓            ↓            ↓
   ┌─────────┐  ┌─────────┐  ┌─────────┐
   │ info    │  │ warning │  │  error  │
   │ _queue  │  │ _queue  │  │  _queue │
   └─────────┘  └─────────┘  └─────────┘
```

### 发送者代码

```python
import pika

connection = pika.BlockingConnection(
    pika.ConnectionParameters('localhost')
)
channel = connection.channel()

# 声明direct交换机
channel.exchange_declare(
    exchange='logs',
    exchange_type='direct'
)

# 声明多个队列并绑定
queues = {
    'info_queue': 'info',
    'warning_queue': 'warning',
    'error_queue': 'error',
}

for queue, routing_key in queues.items():
    channel.queue_declare(queue=queue, durable=True)
    channel.queue_bind(
        exchange='logs',
        queue=queue,
        routing_key=routing_key
    )

# 发送不同级别的日志
logs = [
    ('info', '用户张三登录了系统'),
    ('warning', '磁盘空间不足80%'),
    ('error', '数据库连接失败'),
]

for level, message in logs:
    channel.basic_publish(
        exchange='logs',
        routing_key=level,    # 关键：路由键决定去哪个队列
        body=message.encode()
    )
    print(f"📝 [{level.upper()}] {message}")

connection.close()
```

### 接收者代码

```python
import pika

# 只接收 error 级别的日志
level = 'error'

connection = pika.BlockingConnection(
    pika.ConnectionParameters('localhost')
)
channel = connection.channel()

channel.queue_declare(queue=f'{level}_queue', durable=True)
channel.queue_bind(
    exchange='logs',
    queue=f'{level}_queue',
    routing_key=level
)

def callback(ch, method, properties, body):
    print(f"🚨 收到错误日志: {body.decode()}")
    ch.basic_ack(delivery_tag=method.delivery_tag)

channel.basic_consume(
    queue=f'{level}_queue',
    on_message_callback=callback
)

print(f"👂 监控 {level} 级别日志...")
channel.start_consuming()
```

---

## 📊 交换机对比

| 交换机类型 | 路由规则 | 典型场景 |
|-----------|---------|----------|
| **fanout** | 发送到所有绑定的队列 | 系统通知、广播 |
| **direct** | 精确匹配路由键 | 日志分级、分类处理 |
| **topic** | 模式匹配路由键 | 复杂路由规则 |
| **headers** | 匹配消息头属性 | 特殊路由需求 |

---

# 第七章：主题交换机：用通配符匹配消息

## 🎯 这一章学什么

topic 交换机是最灵活的交换机，支持**通配符匹配**。

---

## 🎭 通配符规则

| 符号 | 含义 | 示例 |
|------|------|------|
| `*` | 精确匹配**一个**单词 | `*.orange.*` 匹配 `quick.orange.rabbit` |
| `#` | 匹配**零个或多个**单词 | `lazy.#` 匹配 `lazy`、`lazy.orange`、`lazy.a.b.c` |

**单词定义**：由点(`.`)分隔的字符串

```
# 路由键示例：
quick.orange.rabbit    → 3个单词
lazy                    → 1个单词
quick.orange.new.rabbit → 4个单词
```

---

## 🏢 场景：物流系统

```
交换机接收路由键：
  <城市>.<仓库>.<商品类型>

例如：
  beijing.warehouse1.electronics
  shanghai.warehouse2.clothing
  beijing.warehouse1.clothing
```

### 绑定规则

| 队列 | 绑定键 | 匹配示例 |
|------|--------|----------|
| electronics_queue | `*.electronics.*` | beijing.warehouse1.electronics |
| beijing_queue | `beijing.#` | beijing.warehouse1.*、beijing.warehouse2.* |
| all_warehouse1 | `*.warehouse1.*` | beijing.warehouse1.*、shanghai.warehouse1.* |
| everything | `#` | 所有路由键 |

---

## 📤 发送者代码

```python
import pika

connection = pika.BlockingConnection(
    pika.ConnectionParameters('localhost')
)
channel = connection.channel()

# 声明topic交换机
channel.exchange_declare(
    exchange='logistics',
    exchange_type='topic'
)

# 模拟发送物流消息
messages = [
    ('beijing.warehouse1.electronics', '北京仓1: 电视机 10台'),
    ('shanghai.warehouse2.clothing', '上海仓2: 衣服 100件'),
    ('beijing.warehouse1.clothing', '北京仓1: 衣服 50件'),
    ('shenzhen.warehouse1.electronics', '深圳仓1: 手机 200台'),
]

for routing_key, message in messages:
    channel.basic_publish(
        exchange='logistics',
        routing_key=routing_key,
        body=message.encode()
    )
    print(f"📦 [{routing_key}] {message}")

connection.close()
```

---

## 📥 接收者代码

```python
import pika

def logistics_consumer(queue_name, binding_key):
    """物流消费者"""
    connection = pika.BlockingConnection(
        pika.ConnectionParameters('localhost')
    )
    channel = connection.channel()

    channel.exchange_declare(
        exchange='logistics',
        exchange_type='topic'
    )

    channel.queue_declare(queue=queue_name, durable=True)
    channel.queue_bind(
        exchange='logistics',
        queue=queue_name,
        routing_key=binding_key
    )

    def callback(ch, method, properties, body):
        print(f"📥 {queue_name} 收到: {body.decode()}")
        ch.basic_ack(delivery_tag=method.delivery_tag)

    channel.basic_consume(
        queue=queue_name,
        on_message_callback=callback
    )

    print(f"👂 {queue_name} 监听: {binding_key}")
    channel.start_consuming()

# 运行不同的消费者
if __name__ == '__main__':
    # 监听所有电子产品
    # logistics_consumer('electronics_queue', '*.electronics.*')

    # 监听北京的所有物流
    # logistics_consumer('beijing_queue', 'beijing.#')

    # 监听1号仓库
    # logistics_consumer('warehouse1_queue', '*.warehouse1.*')

    # 监听所有（总控台）
    logistics_consumer('all_queue', '#')
```

---

## 💡 topic 的实际应用

### 1. 物联网设备日志

```
路由键格式: <设备类型>.<设备ID>.<日志级别>

示例:
  sensor.temperature_001.warning
  sensor.humidity_003.error
  camera.front_door.info
```

### 2. 电商订单

```
路由键格式: <订单状态>.<支付方式>.<地区>

示例:
  created.wechat.beijing
  paid.alipay.shanghai
  shipped.credit_card.guangzhou
```

---

# 第八章：实战项目：构建订单处理系统

## 🎯 项目需求

构建一个订单处理系统，包含以下功能：

```
用户下单 → 库存检查 → 支付处理 → 发货通知 → 数据分析
```

---

## 📊 系统架构

```
                    ┌──────────────┐
                    │   订单交换机  │
                    │   (topic)    │
                    └──────┬───────┘
                           │
        ┌──────────────────┼──────────────────┐
        ↓                  ↓                  ↓
   ┌─────────┐       ┌─────────┐       ┌─────────┐
   │ 库存    │       │ 支付    │       │ 通知    │
   │ 处理    │       │ 处理    │       │ 服务    │
   └─────────┘       └─────────┘       └─────────┘
                           │
                    ┌─────────┐
                    │ 数据    │
                    │ 分析    │
                    └─────────┘
```

---

## 📤 订单服务（生产者）

```python
import pika
import json
import time

class OrderPublisher:
    def __init__(self):
        self.connection = pika.BlockingConnection(
            pika.ConnectionParameters('localhost')
        )
        self.channel = self.connection.channel()

        # 声明交换机
        self.channel.exchange_declare(
            exchange='orders',
            exchange_type='topic'
        )

        # 声明所有需要的队列
        self.queues = [
            'inventory_queue',
            'payment_queue',
            'notification_queue',
            'analytics_queue'
        ]

        for queue in self.queues:
            self.channel.queue_declare(queue=queue, durable=True)

        # 绑定队列
        bindings = [
            ('inventory_queue', 'order.created'),      # 下单时检查库存
            ('payment_queue', 'payment.process'),       # 支付处理
            ('notification_queue', 'order.*'),          # 所有订单事件都通知
            ('analytics_queue', '#')                    # 所有事件（用于分析）
        ]

        for queue, routing_key in bindings:
            self.channel.queue_bind(
                exchange='orders',
                queue=queue,
                routing_key=routing_key
            )

    def create_order(self, order_id, user_id, items, total_amount):
        """创建订单"""
        order = {
            'order_id': order_id,
            'user_id': user_id,
            'items': items,
            'total_amount': total_amount,
            'status': 'created',
            'timestamp': time.strftime('%Y-%m-%d %H:%M:%S')
        }

        # 发布订单创建事件
        self.publish('order.created', order)

        # 发布支付请求
        payment_request = {
            'order_id': order_id,
            'amount': total_amount,
            'timestamp': time.strftime('%Y-%m-%d %H:%M:%S')
        }
        self.publish('payment.process', payment_request)

        return order

    def publish(self, routing_key, message):
        """发布消息"""
        self.channel.basic_publish(
            exchange='orders',
            routing_key=routing_key,
            body=json.dumps(message).encode(),
            properties=pika.BasicProperties(
                delivery_mode=2  # 持久化
            )
        )
        print(f"📤 发送: [{routing_key}] {message}")

    def close(self):
        self.connection.close()


# 测试
if __name__ == '__main__':
    publisher = OrderPublisher()

    # 创建测试订单
    order = publisher.create_order(
        order_id='ORD20240101001',
        user_id='USER001',
        items=[
            {'name': 'iPhone 15', 'quantity': 1, 'price': 7999},
            {'name': 'AirPods Pro', 'quantity': 1, 'price': 1899}
        ],
        total_amount=9898
    )

    publisher.close()
```

---

## 👷 消费者服务

### 库存服务

```python
import pika
import json

def inventory_service():
    connection = pika.BlockingConnection(
        pika.ConnectionParameters('localhost')
    )
    channel = connection.channel()

    channel.queue_declare(queue='inventory_queue', durable=True)
    channel.queue_bind(
        exchange='orders',
        queue='inventory_queue',
        routing_key='order.created'
    )

    def callback(ch, method, properties, body):
        order = json.loads(body.decode())
        print(f"📦 库存服务收到订单: {order['order_id']}")

        # 模拟检查库存
        for item in order['items']:
            print(f"   检查 {item['name']} 库存: 充足")

        print(f"✅ 订单 {order['order_id']} 库存检查通过")
        ch.basic_ack(delivery_tag=method.delivery_tag)

    channel.basic_consume(
        queue='inventory_queue',
        on_message_callback=callback
    )

    print("📦 库存服务已启动，等待订单...")
    channel.start_consuming()

inventory_service()
```

### 支付服务

```python
import pika
import json

def payment_service():
    connection = pika.BlockingConnection(
        pika.ConnectionParameters('localhost')
    )
    channel = connection.channel()

    channel.queue_declare(queue='payment_queue', durable=True)
    channel.queue_bind(
        exchange='orders',
        queue='payment_queue',
        routing_key='payment.process'
    )

    def callback(ch, method, properties, body):
        payment = json.loads(body.decode())
        print(f"💰 支付服务收到请求: 订单 {payment['order_id']}, 金额 ¥{payment['amount']}")

        # 模拟支付处理
        print(f"   正在调用支付接口...")
        print(f"✅ 支付成功!")

        ch.basic_ack(delivery_tag=method.delivery_tag)

    channel.basic_consume(
        queue='payment_queue',
        on_message_callback=callback
    )

    print("💰 支付服务已启动，等待支付请求...")
    channel.start_consuming()

payment_service()
```

### 通知服务

```python
import pika
import json

def notification_service():
    connection = pika.BlockingConnection(
        pika.ConnectionParameters('localhost')
    )
    channel = connection.channel()

    channel.queue_declare(queue='notification_queue', durable=True)
    channel.queue_bind(
        exchange='orders',
        queue='notification_queue',
        routing_key='order.*'
    )

    def callback(ch, method, properties, body):
        message = json.loads(body.decode())
        routing_key = method.routing_key

        print(f"📢 通知服务收到 [{routing_key}] 事件")

        # 模拟发送通知
        if 'order_id' in message:
            print(f"   📱 发送短信通知: 您的订单 {message['order_id']} 已确认")
            print(f"   📧 发送邮件通知: 订单确认邮件")

        ch.basic_ack(delivery_tag=method.delivery_tag)

    channel.basic_consume(
        queue='notification_queue',
        on_message_callback=callback
    )

    print("📢 通知服务已启动，等待事件...")
    channel.start_consuming()

notification_service()
```

---

## 🧪 测试完整流程

```bash
# 终端1-4：启动4个服务
python inventory_service.py
python payment_service.py
python notification_service.py
python analytics_service.py

# 终端5：创建订单
python order_publisher.py
```

**预期输出：**
```
📤 发送: [order.created] {'order_id': 'ORD20240101001', ...}
📤 发送: [payment.process] {'order_id': 'ORD20240101001', 'amount': 9898, ...}

📦 库存服务收到订单: ORD20240101001
   检查 iPhone 15 库存: 充足
   检查 AirPods Pro 库存: 充足
✅ 订单 ORD20240101001 库存检查通过

💰 支付服务收到请求: 订单 ORD20240101001, 金额 ¥9898
   正在调用支付接口...
✅ 支付成功!

📢 通知服务收到 [order.created] 事件
   📱 发送短信通知: 您的订单 ORD20240101001 已确认
   📧 发送邮件通知: 订单确认邮件

📢 通知服务收到 [payment.process] 事件
   📱 发送短信通知: 您的订单 ORD20240101001 支付成功
```

---

# 第九章：最佳实践与常见问题

## ✅ 最佳实践

### 1. 连接管理

```python
# ❌ 不推荐：每次发送都创建连接
def send_message(message):
    connection = pika.BlockingConnection(...)
    channel = connection.channel()
    channel.basic_publish(...)
    connection.close()

# ✅ 推荐：复用连接
connection = pika.BlockingConnection(...)
channel = connection.channel()

def send_message(message):
    channel.basic_publish(...)  # 使用已建立的连接
```

### 2. 消息持久化

```python
# 队列持久化
channel.queue_declare(queue='my_queue', durable=True)

# 消息持久化
channel.basic_publish(
    ...,
    properties=pika.BasicProperties(
        delivery_mode=2  # 持久化
    )
)
```

### 3. 消费者确认

```python
# ❌ 自动确认（可能丢失消息）
channel.basic_consume(queue='my_queue', auto_ack=True)

# ✅ 手动确认（确保消息处理完成）
channel.basic_consume(queue='my_queue', auto_ack=False)

def callback(ch, method, properties, body):
    try:
        process(body)
        ch.basic_ack(delivery_tag=method.delivery_tag)
    except Exception:
        ch.basic_nack(delivery_tag=method.delivery_tag, requeue=True)
```

### 4. 公平分发

```python
# 同一时间只处理1条消息
channel.basic_qos(prefetch_count=1)
```

---

## ❓ 常见问题

### Q1: 消息丢失怎么办？

**原因：** 队列或消息没有持久化

**解决：**
```python
# 1. 队列持久化
channel.queue_declare(queue='my_queue', durable=True)

# 2. 消息持久化
channel.basic_publish(
    ...,
    properties=pika.BasicProperties(
        delivery_mode=2
    )
)

# 3. 手动确认
channel.basic_consume(queue='my_queue', auto_ack=False)
```

### Q2: 消费者处理失败怎么办？

**解决：** 使用重试机制
```python
def callback(ch, method, properties, body):
    try:
        process(body)
        ch.basic_ack(delivery_tag=method.delivery_tag)
    except Exception as e:
        # 失败后重新入队
        ch.basic_nack(delivery_tag=method.delivery_tag, requeue=True)
```

### Q3: 如何监控队列？

使用管理界面：`http://localhost:15672`

```bash
# 用户名/密码：guest/guest
```

可以查看：
- 队列状态（消息数、消费者数）
- 交换机绑定
- 连接状态
- 消息吞吐量

### Q4: 性能优化？

1. **批量处理**：累积多条消息一起处理
2. **连接池**：使用连接池复用连接
3. **预取数量**：适当调整 prefetch_count
4. **消息压缩**：大消息可以压缩后发送

---

## 📚 学习路径

```
基础 → 进阶 → 高级
  ↓      ↓       ↓
连接    工作队列   事务
简单    交换机    集群
消息    路由     监控
```

### 推荐学习资源

1. **官方文档**: https://www.rabbitmq.com/tutorials
2. **pika 文档**: https://pika.readthedocs.io
3. **RabbitMQ in Action**: 经典书籍

---

## 🎉 总结

你学会了：

- ✅ 什么是消息队列，为什么需要它
- ✅ RabbitMQ 核心概念（生产者、消费者、队列、交换机）
- ✅ 连接管理和消息发送/接收
- ✅ 工作队列实现负载均衡
- ✅ 四种交换机类型及使用场景
- ✅ 主题交换机和通配符匹配
- ✅ 构建完整的订单处理系统
- ✅ 最佳实践和常见问题解决

---

*📝 本教程由 MiniMax Agent 编写*
