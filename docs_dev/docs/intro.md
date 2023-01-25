# Introduction

If you want to start contributing to the project, here is the path you can take step by step to arrive.

- [Introduction](#introduction)
  - [What Service is in the COSCUP Volunteer?](#what-service-is-in-the-coscup-volunteer)
  - [How to Make COSCUP Volunteer?](#how-to-make-coscup-volunteer)
  - [Roadmap](#roadmap)

## What Service is in the COSCUP Volunteer?

<figure markdown>
  <a href="https://volunteer.coscup.org/doc/wiki_coscup_volunteer_services.svg">
    <img alt="coscup_volunteer_infra" src="https://volunteer.coscup.org/doc/wiki_coscup_volunteer_services.svg">
  </a>
  <figcaption>Services, <small><a href="https://volunteer.coscup.org/doc/wiki_coscup_volunteer_services.svg">[original]</a></small></figcaption>
</figure>

Those services have been implemented in the volunteer platform. Those services are
served by the **Secretary Team<small>（行政組）</small>** in the COSCUP.

## How to Make COSCUP Volunteer?

<figure markdown>
  <a href="https://volunteer.coscup.org/doc/wiki_coscup_volunteer_infra.svg">
    <img alt="coscup_volunteer_infra" src="https://volunteer.coscup.org/doc/wiki_coscup_volunteer_infra.svg">
  </a>
  <figcaption>Infrastructure, <small><a href="https://volunteer.coscup.org/doc/wiki_coscup_volunteer_infra.svg">[original]</a></small></figcaption>
</figure>

This figure is the whole picture about the infrastructure of the volunteer platform on the production.

We set up the platform on AWS EC2 with Ubuntu 20.04 in `t3a.large` instance. Running those applications
into containers by using upstream to round robin the containers. And we also have an instance in
`t3a.nano` placed at the front of them, this instance will do the job of encrypting / decrypting
the connections from requests and to responses.


## Roadmap

<figure markdown>
  <a href="https://volunteer.coscup.org/doc/wiki_coscup_volunteer_roadmap.svg">
    <img alt="coscup_volunteer_roadmap" src="https://volunteer.coscup.org/doc/wiki_coscup_volunteer_roadmap.svg">
  </a>
  <figcaption>Roadmap, <small><a href="https://volunteer.coscup.org/doc/wiki_coscup_volunteer_roadmap.svg">[original]</a></small></figcaption>
</figure>
