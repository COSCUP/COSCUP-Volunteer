---
title: 開發設定頁面
summary: 設定開發時需要的參數或測試帳號
description: 設定開發時需要的參數或測試帳號
---
# 開發設定頁面

!!! info

    這個頁面適用於開發環境，你可以在開發設定頁面建立專案與切換工作階段帳號。

## 進入頁面

進入以下設定網址位置：

    http://127.0.0.1:80/dev/

## 指定擁有者（owner）

在進行以下設定前，你需要設定指定一個 `uid` 為擁有者於 `setting.py`。

``` python title="setting.py"
API_DEFAULT_OWNERS = ['00000000', ]  # replace `00000000` to your uid.
```

## 帳號

預設將會建立 10 組測試帳號。

<figure markdown>
  <a href="https://volunteer.coscup.org/doc/docs_dev_account_lists.png">
    <img alt="docs_dev_account_lists"
         src="https://volunteer.coscup.org/doc/docs_dev_account_lists.png"
         style="border: 1px #ececec solid; border-radius: 0.4rem;"
    >
  </a>
</figure>

## 工作階段

在 `Session` 段落，預設會有 10 組帳號，你可以任意切換帳號透過切換按鈕來操作。

## 專案

你需要建立第一個專案來開發。請點擊 `To create a project` 來開啟建立表單頁面。

<figure markdown>
  <a href="https://volunteer.coscup.org/doc/docs_create_project.png">
    <img alt="docs_create_project"
         src="https://volunteer.coscup.org/doc/docs_create_project.png"
         style="border: 1px #ececec solid; border-radius: 0.4rem;"
    >
  </a>
</figure>

可依以下範例來設定：

- `pid` 設定為 `2022`
- `name` 設定為 `One Project`
- `action date` 可為任何時間。

... 之後點擊 `Create Project`.

建立後的專案將會顯示在專案列表。點擊 `Setting` 進入專案設定頁面。

## 編輯專案

在這一階段，你可以學會建立「組（Team）」於專案中。

前往專案頁面，如：`http://127.0.0.1/project/{pid}/edit`

點擊 `編輯組別`，點擊 `建立` 開啟介面，可依以下範例來建立：

- name 設定為 `One Team`
- tid 設定為 `one`

... 然後點擊 `update`

### 加入組長與組員

點擊於列表後方的 `編輯`。輸入使用者 ID (`uid`) 到 `chiefs`、`members`欄位中。

<figure markdown>
  <a href="https://volunteer.coscup.org/doc/docs_edit_team_setting.png">
    <img alt="docs_edit_team_setting"
         src="https://volunteer.coscup.org/doc/docs_edit_team_setting.png"
         style="border: 1px #ececec solid; border-radius: 0.4rem;"
    >
  </a>
</figure>

!!! note

    如果你正在開發財務相關的功能，請建立一個組 `tid` 為 `finance` 與設定一個組長的 `uid` 於組中。

## 開發小抄

如要取得更多開發小抄內容，可以參考這份來自行政組開發小組[整理的內容](https://hackmd.io/ejN7azuSQMym8p5SZEKJQw)。（感謝 [@ddio](https://github.com/ddio)）。
