// ==UserScript==
// @name         改B站数据(全页面覆盖版)
// @namespace    http://tampermonkey.net/
// @version      1.6
// @description  ETO
// @author       ETO
// @match        *://*.bilibili.com/*
// ==/UserScript==

(function() {
    'use strict';

    // 配置系统
    const config = {
        // 个人空间专属配置
        mySpace: {
            uid: '487284802',
            stats: {
                0: '88', // 关注数
                1: '2486.5万', // 粉丝数
                2: '4.2亿', // 获赞数
                3: '486.0亿' // 播放数
            }
        },
        // 全局通用配置
        global: {
            'coin-item__num': {
                0: '16.8万', // 硬币
                1: '4096' // B币
            },
            'count-num': {
                0: '88', // 关注
                1: '2486.5万', // 粉丝
                2: '42' // 动态
            },
            'item-num': {
                0: '88', // 关注
                1: '2486.5万', // 粉丝
                2: '42' // 动态
            }
        }
    };

    const processElements = (className, rules) => {
        const elements = document.getElementsByClassName(className);
        Array.from(elements).forEach((el, index) => {
            if (rules.hasOwnProperty(index)) {
                el.textContent = rules[index];
            }
        });
    };

    const observer = new MutationObserver(() => {
        const isMySpace = window.location.href.startsWith(`https://space.bilibili.com/${config.mySpace.uid}`);

        // 处理个人空间统计数据 (只修改一次)
        if (isMySpace) {
            const stats = document.getElementsByClassName('nav-statistics__item-num');
            if (stats.length > 3) {
                stats[1].textContent = config.mySpace.stats[1];
                stats[2].textContent = config.mySpace.stats[2];
                stats[3].textContent = config.mySpace.stats[3];
            }
        }

        // 处理全局元素 (所有页面包括个人空间)
        Object.entries(config.global).forEach(([className, rules]) => {
            processElements(className, rules);
        });
    });

    observer.observe(document.body, {
        childList: true,
        subtree: true
    });

    // 立即执行初始检查
    observer.takeRecords();
})();
