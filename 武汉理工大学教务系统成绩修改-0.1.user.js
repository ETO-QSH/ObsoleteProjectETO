// ==UserScript==
// @name         武汉理工大学教务系统成绩修改
// @namespace    http://tampermonkey.net/
// @version      0.1
// @description  将“教学空间-我的成绩”修改为“100”
// @author       ETO
// @match        https://jwxt.whut.edu.cn/jwapp/sys/homeapp/home/index.html*
// @grant        none
// ==/UserScript==

(function() {
    'use strict';

    // 定义一个函数，用于修改成绩显示
    function modifyGrades() {
        // 查找所有符合选择器路径的元素
        const gradeElements = document.querySelectorAll(
            '#root > div > div > div.tabPagesRoot___3EQoJ.tabPages___3232i > div.tabPanelRoot___MzXA2 > div > div > div.container___1qOJG > div > div.leftPart___2bI2f > div.container___3Vw9C > div.tabContentContainer___151Dp > div > div > div > div > div > div.main___1likm > div.bigLine___G9eW9'
        );

        // 遍历找到的元素并修改文本内容
        gradeElements.forEach(element => {
            const text = element.textContent;
            if (text !== '成绩: 100') {
                element.textContent = '成绩: 100';
            }
        });
    }

    // 立即执行一次，处理已经加载的元素
    modifyGrades();

    // 设置一个定时器，每秒检查一次新加载的元素
    setInterval(modifyGrades, 1000);

    // 监听 MutationObserver，当DOM发生变化时执行修改
    const observer = new MutationObserver(modifyGrades);
    observer.observe(document.body, {
        childList: true,
        subtree: true
    });
})();