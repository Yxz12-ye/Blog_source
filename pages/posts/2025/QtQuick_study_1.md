---
title: Qml与C++后端简单交互
date: 2025-11-26 21:10:00
updated: 2025-11-27 19:02:00
categories:
 - 技术
tags:
 - C/C++
 - Qt
 - Qml
---

## 全局暴露

这里用CPP创建一个类

`MyQmlClass.h`

```c++
#pragma once

#include <QObject>

class MyQmlClass : public QObject {
    Q_OBJECT
private:
    int m_value;

public:
    explicit MyQmlClass(QObject* parent = nullptr) : QObject(parent) {};
    ~MyQmlClass() {};

    Q_INVOKABLE void setValue(int value);
    Q_INVOKABLE int getValue();
};

```
<!-- more -->

`MyQmlClass.cpp`

```C++
#include "MyQmlClass.h"

Q_INVOKABLE void MyQmlClass::setValue(int value) {
    m_value = value;
}

Q_INVOKABLE int MyQmlClass::getValue() {
    return m_value;
}

```

`main.cpp`

```c++
#include <QGuiApplication>
#include <QQmlApplicationEngine>
#include <QTimer>
#include <QDebug>
#include "MyQmlClass.h"
#include <QQmlContext>

int main(int argc, char* argv[]) {
    QGuiApplication app(argc, argv);

    qDebug() << "应用程序启动...";

    QQmlApplicationEngine engine;

    MyQmlClass myQmlClass;

    engine.rootContext()->setContextProperty("myQmlClass", &myQmlClass);

    QObject::connect(
        &engine, &QQmlApplicationEngine::objectCreated, &app,
        [](QObject* obj, const QUrl& objUrl) {
            if (obj) {
                qDebug() << "QML 加载成功！";
            } else {
                qDebug() << "QML 加载失败：" << objUrl;
            }
        },
        Qt::QueuedConnection);

    qDebug() << "开始加载 QML...";
    engine.load(QUrl("qrc:/ui/interactWithCPP.qml"));

    qDebug() << "进入事件循环...";
    return app.exec();
}
```

`interactWithCPP.qml`

```qml
import QtQuick
import QtQuick.Controls

Window {
    width: 400
    height: 300
    visible: true
    title: "与C++交互示例"

    Label {
        id: myLabel
        text: "欢迎使用Qt与C++交互示例！"
        anchors.top: parent.top
        anchors.horizontalCenter: parent.horizontalCenter
        anchors.topMargin: 20
    }

    Button {
        id: myButton
        text: "点击我"
        anchors.centerIn: parent
        onClicked: {
            console.log("按钮被点击了！");
            // 这里可以调用C++暴露的方法
            myLabel.text = myQmlClass.getValue();
        }
    }
}

```

OK, 那么拿到代码先看`QQmlApplicationEngine`

| 头文件： | `#include <QQmlApplicationEngine>`                           |
| -------- | ------------------------------------------------------------ |
| CMake：  | `find_package(Qt6 REQUIRED COMPONENTS Qml)` `target_link_libraries(mytarget PRIVATE Qt6::Qml)` |
| qmake：  | `QT += qml`                                                  |
| 继承：   | [QQmlEngine](https://doc.qt.io/qt-6/zh/qqmlengine.html)      |

继承自`QQmlEngine`, 类似`QMainWindow`继承`QWidget`吧(我猜测)

`rootContext`方法在`QQmlEngine`中定义, 官网这么说的:

> ### [QQmlContext](https://doc.qt.io/qt-6/zh/qqmlcontext.html) *QQmlEngine::rootContext() const
> 返回引擎的根上下文（root context）。
> 根上下文由[QQmlEngine](https://doc.qt.io/qt-6/zh/qqmlengine.html) 自动创建。引擎实例化的所有 QML 组件实例都应使用的数据应放在根上下文中。
> 只应提供给组件实例子集的其他数据，应添加到根上下文的子上下文中。

继续查询`QQmlContext`的`setContextProperty`方法

> ### void QQmlContext::setContextProperty(const [QString](https://doc.qt.io/qt-6/zh/qstring.html) &*name*, [QObject](https://doc.qt.io/qt-6/zh/qobject.html) **value*)
>设置此上下文中*name* 属性的*value* 。
>[QQmlContext](https://doc.qt.io/qt-6/zh/qqmlcontext.html) **不**拥有*value* 的所有权。
>**注意：** 您不应使用上下文属性将值注入 QML 组件。请使用 singletons 或常规对象属性。

可以看到这样写有个问题就是没有所有权, 所有权是什么意思呢? 参考`QWidget`, 拥有所有权, 那么该对象的声明周期就会由持有者管理, 没有所有权就导致`QQmlContext`不会去销毁传入的`QObject`, 然后就要自己管理对象的内存生命周期

并且这样编写会导致此对象对所有的qml暴露(不引入也能使用, 污染函数)

# 施工中, 最近是真没时间写博客qwq
