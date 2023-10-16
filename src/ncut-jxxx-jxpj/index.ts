// ==UserScript==
// @include      https://jxxx.ncut.edu.cn/xs/grxx.asp?id=12*
// @include      https://jxxx.webvpn.ncut.edu.cn/xs/grxx.asp?id=12*
// @include      http://jxxx.ncut.edu.cn/xs/grxx.asp?id=12*
// @include      http://jxxx.webvpn.ncut.edu.cn/xs/grxx.asp?id=12*
// @icon         https://www.google.com/s2/favicons?sz=64&domain=ncut.edu.cn
// @grant        none
// @run-at       document-end
// ==/UserScript==

(function () {
    'use strict';

    const $ = (window as any).jQuery as JQueryStatic;
    const id = 'yuanlu_ncut_jxpj_loaded';
    if ($(`#${id}`).length) return;
    $('body').append(`<div id="${id}" />`); //标识

    function getSelecter() {
        return document.getElementsByName('kcxuanze')[0] as HTMLSelectElement;
    }
    const autoSelect = function () {
        const list = $('option') as JQuery<HTMLOptionElement>;
        for (let i = 0; i < list.length; i++) {
            let ele = list[i];
            if (ele.value === 'all') continue;
            if (ele.text.indexOf('(未评)') < 0) continue;
            console.log('自动选择:', ele.text);
            ele.selected = true;
            $('#submit3').click();
            return;
        }
        if (getSelecter().selectedIndex) {
            list[0].selected = true;
            $('#submit3').click();
        }
    };
    if (getSelecter().selectedOptions[0].text.indexOf('(未评)') < 0) autoSelect();

    $('body').prepend('教学评价自动填充已加载 - yuanlu.');

    const allOption = $('input[value=E]');
    if (!allOption.length) return;
    setTimeout(() => allOption.click(), 500); //自动选择"完全赞同"
    $('#submit01').click(() => setTimeout(autoSelect, 500));
})();
