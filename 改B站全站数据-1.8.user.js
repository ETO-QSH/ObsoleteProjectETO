// ==UserScript==
// @name         B站数据修改(精准版)
// @namespace    https://github.com/ETO-QSH/
// @version      1.9
// @description  精准修改个人空间数据及标题
// @author       ETO
// @match        *://*.bilibili.com/*
// ==/UserScript==

(function() {
    'use strict';

    // 配置系统
    const config = {
        mySpace: {
            uid: '487284802',
            stats: {
                0: { display: '84', title: '84' }, // 关注
                1: { display: '2486.5万', title: '24,865,404' }, // 粉丝
                2: { display: '8.6亿', title: '861,415,926' }, // 获赞
                3: { display: '48.6亿', title: '4,860,192,120' } // 播放
            }
        },
        global: {
            'coin-item__num': {
                0: '16.8万', // 硬币
                1: '4096' // B币
            },
            'count-num': {
                0: '84', // 关注
                1: '2486.5万', // 粉丝
                2: '648' // 动态
            },
            'item-num': {
                0: '84', // 关注
                1: '2486.5万', // 粉丝
                2: '648' // 动态
            }
        }
    };

    // 智能修改个人空间标题
    const modifySpaceTitle = (element, newValue) => {
        // 修改显示内容
        element.textContent = newValue.display;

        // 精准修改标题数字
        if (element.title) {
            // 匹配最后一个连续数字部分（支持中文单位）
            element.title = element.title.replace(
                /(\d[\d,.]*)([万|亿]?)([\u4e00-\u9fa5]*)$/, `${newValue.title}$3`
            );
        }
    };

    // 通用元素处理器
    const processElements = (className, rules) => {
        document.querySelectorAll(`.${className}`).forEach((el, index) => {
            if (rules[index]) {
                el.textContent = rules[index];
            }
        });
    };

    // 优化后的观察器
    const observer = new MutationObserver(() => {
        // 避免频繁触发
        setTimeout(() => {
            const isMySpace = window.location.href.includes(
                `https://space.bilibili.com/${config.mySpace.uid}`
            );

            // 处理个人空间专属修改
            if (isMySpace) {
                const stats = document.querySelectorAll('.nav-statistics__item-num');
                if (stats.length > 3) {
                    stats.forEach((el, index) => {
                        if (config.mySpace.stats[index]) {
                            modifySpaceTitle(el, config.mySpace.stats[index]);
                        }
                    });
                }
            }

            // 处理全局修改
            Object.entries(config.global).forEach(([className, rules]) => {
                processElements(className, rules);
            });
        }, 100); // 延迟 100ms 避免冲突
    });

    // 限制观察范围，只观察需要的元素
    observer.observe(document.body, {
        childList: true,
        subtree: true
    });

    // 立即生效
    observer.takeRecords();
})();
