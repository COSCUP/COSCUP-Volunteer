# 專案簡介

如果您想要開始貢獻此專案，這裡有引導說明讓您知道如何進行。

## 哪些服務在 COSCUP 志工平台中？

<figure markdown>
  <a href="https://volunteer.coscup.org/doc/wiki_coscup_volunteer_services.svg">
    <img alt="coscup_volunteer_infra" src="https://volunteer.coscup.org/doc/wiki_coscup_volunteer_services.svg">
  </a>
  <figcaption>Services, <small><a href="https://volunteer.coscup.org/doc/wiki_coscup_volunteer_services.svg">[original]</a></small></figcaption>
</figure>

這些服務已經實作在志工服務平台中，而這些服務是由 COSCUP 行政組維護。

## 如何建構 COSCUP 志工服務平台？

<figure markdown>
  <a href="https://volunteer.coscup.org/doc/wiki_coscup_volunteer_infra.svg">
    <img alt="coscup_volunteer_infra" src="https://volunteer.coscup.org/doc/wiki_coscup_volunteer_infra.svg">
  </a>
  <figcaption>Infrastructure, <small><a href="https://volunteer.coscup.org/doc/wiki_coscup_volunteer_infra.svg">[original]</a></small></figcaption>
</figure>

此圖表是關於志工平台在正式機上的架構。

我們將平台建構在 AWS EC2 並使用 `t3a.large` 的執行個體，其作業系統為 Ubuntu 20.04 LTE，其應用程序則在 Docker 容器中運行。

此外我們還有一台 `t3a.nano` 的執行個體，主要負責進出流量時的連線加解密與負載平衡。

## 路線圖

<figure markdown>
  <a href="https://volunteer.coscup.org/doc/wiki_coscup_volunteer_roadmap.svg">
    <img alt="coscup_volunteer_roadmap" src="https://volunteer.coscup.org/doc/wiki_coscup_volunteer_roadmap.svg">
  </a>
  <figcaption>Roadmap, <small><a href="https://volunteer.coscup.org/doc/wiki_coscup_volunteer_roadmap.svg">[original]</a></small></figcaption>
</figure>
