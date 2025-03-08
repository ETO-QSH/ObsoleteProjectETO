// ==UserScript==
// @name         改B站全站数据
// @namespace    http://tampermonkey.net/
// @version      1.3
// @description  ETO
// @author       ETO
// @match        *://*.bilibili.com/*
// ==/UserScript==

(function() {
    'use strict';

    const config = {
        // 特定页面配置
        specialPages: {
            'space.bilibili.com': {
                'nav-statistics__item-num': {
                    0: '88', // 关注数
                    1: '2486.5万', // 粉丝数
                    2: '2.4亿',   // 获赞数
                    3: '48.6亿'   // 播放数
                }
            }
        },
        // 全局通用配置（支持按索引设置不同值）
        global: {
            'coin-item__num': {
                0: '16.8万',  // 硬币
                1: '4096'   // B币
            },
            'count-num': {
                0: '88',  // 关注
                1: '2486.5万',  // 粉丝
                2: '42'   // 动态
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
        const hostname = location.hostname;

        // 处理特定页面配置
        if (config.specialPages[hostname]) {
            Object.entries(config.specialPages[hostname]).forEach(([className, rules]) => {
                processElements(className, rules);
            });
        }

        // 处理全局配置
        Object.entries(config.global).forEach(([className, rules]) => {
            processElements(className, rules);
        });
    });

    observer.observe(document.body, {
        childList: true,
        subtree: true,
        attributes: false,
        characterData: false
    });

    // 立即执行一次检查
    observer.takeRecords();
})();
