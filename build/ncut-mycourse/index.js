// ==UserScript==
// @name          平安毓秀
// @namespace     bid.yuanlu
// @version       1.0.20231013.1858457
// @description   自动完成平安毓秀学习（打开课程列表，全自动完成）
// @author        yuanlu
// @grant         none
// @icon          https://www.google.com/s2/favicons?domain=mycourse.cn
// @match         http*://*.mycourse.cn/*
// ==/UserScript==


(() => {
    /**是否运行流程? (正在运行时不再重复触发) */
    let running = false;

    /**自动完成学习 */
    function auto_finish() {
        if (!window.location.origin.includes('mcwk.mycourse.cn')) {
            return;
        }
        const start = Date.now();
        const rand = 1000 * 60 * 1 + Math.random() * 1000 * 20 - 1000 * 10;
        const real_alert = window.alert;
        window.alert = (msg) => {
            if (msg === '恭喜，您已完成本微课的学习') {
                window.history.back();
                // window.location.reload();
            } else {
                real_alert(msg);
            }
        };
        console.log('已经开始监听, 准备', rand / 1e3, window.finishWxCourse);
        console.log('alert', real_alert, window.alert, alert);
        running = true;
        setTimeout(() => {
            const end = Date.now();
            console.log('准备完成,耗时', (end - start) / 1e3, window.finishWxCourse);
            window.finishWxCourse();
            running = false;
        }, rand);
    }

    /**自动寻找未进行的课程 */
    function auto_go() {
        //#app > div > div.viewport > div.tabs-container > div:nth-child(2) > div > div:nth-child(1) > div.van-collapse-item__wrapper > div > ul > li:nth-child(1)
        if (!window.location.hash.startsWith('#/course?')) return;
        const boxs = document.querySelectorAll('#app .van-collapse-item__title');
        if (boxs.length <= 0) return;
        running = true;
        console.log(boxs);
        let i = 0,
            j = 0,
            k = false;
        const inter = setInterval(() => {
            k = !k;
            if (k) {
                const nopass = document.querySelectorAll('#app .img-texts-item.van-hairline--top:not(.passed)');
                if (nopass.length) {
                    clearInterval(inter);
                    nopass.item(0).click();
                    running = false;
                }
            } else {
                if (i < boxs.length) {
                    boxs.item(i).click();
                    i++;
                } else {
                    i = 0;
                    j++;
                }
                if (j > 1) {
                    clearInterval(inter);
                    running = false;
                    alert('已完成! [yuanlu]');
                }
            }
        }, 1500);
    }
    /**考试页面自动停止 */
    function auto_stop() {
        running = window.location.href.includes('#/courses/exam-page?');
    }

    const funcs = [auto_stop, auto_finish, auto_go];
    const timer = setInterval(() => {
        funcs.forEach((f) => {
            if (!running) f();
        });
    }, 1000);
})();

