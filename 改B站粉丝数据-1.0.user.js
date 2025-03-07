// ==UserScript==
// @name         改B站粉丝数据
// @namespace    http://tampermonkey.net/
// @version      1.0
// @description  ETO
// @author       ETO
// @match        https://space.bilibili.com/*
// ==/UserScript==

(function() {
    'use strict';
    const observer = new MutationObserver((mutationList, observer) => {
        if (window.location.href.startsWith('https://space.bilibili.com/487284802')) {
            if (document.getElementsByClassName('nav-statistics__item-num') && document.getElementsByClassName('nav-statistics__item-num')[1]) {
                document.getElementsByClassName('nav-statistics__item-num')[1].innerText = '3000.0万'; // 粉丝数
                document.getElementsByClassName('nav-statistics__item-num')[2].innerText = '22.4亿'; // 获赞数
                document.getElementsByClassName('nav-statistics__item-num')[3].innerText = '486.9亿'; // 播放数
                observer.disconnect();
            }
        }
    });

    observer.observe(document.body, {
        childList: true,
        subtree: true
    });
})();