---
title: Milking Settings Optimization Landing Page
space: MSO (Milking Settings Optimization)
breadcrumbs: []
author: Jakub Maléř
editor: Petr Svarny
last_modified: '2026-02-23'
---

A space shared with Lely for the “MSO” project.

## Project Description

**Milking Settings Optimization (MSO)** is an AI project that aims to set optimal milking settings for each animal milked with **Lely’s Astronaut milking robot** in order to maximize cow health and comfort as well as milk yield and milking speed. With Milking Settings Optimization, the farmers can set performance objectives according to their preferences without having to worry about the needs of each individual animal, which is not possible in the world of robotic milking, where millions of animals are milked each day.

MSO is an umbrella project containing sub-projects that focus on different setting categories:

- Settings set before the milking

  - Pretreatment (brushing) - **Pretreatment Optimization (PTO)** **[IN PRODUCTION]**
  - Milking interval - **Milking Interval Optimization (MIO)** **[IN DEVELOPMENT]**
- Settings set adaptively during the milking

  - **Pulsation** **[IN DEVELOPMENT]**
  - Vacuum
  - Take-off
- Providing advice about milking via the [Chameleon pipeline](https://datamole.atlassian.net/wiki/spaces/CHMEL) **[IN PRODUCTION]**

## Team

### Datamole

|  |  |
| --- | --- |
| **Team Member** | **Role & Responsibility** |
| Petr Svarny | MFPC and MSO Project Lead |
| Adam Skluzáček | Lead Data Scientist |
| Jiří Vošmik | Former Lead Engineer, Data Scientist, responsible for models |
| Jan Lukány | Lead Data Engineer (in progress handover to Michal Belák), Hellen Data Engineering PRG Team Lead |
| Michal Belák | Lead Data Engineer (in progress handover from Jan Lukány ) |
| Ondrej Profant | Data Engineer |
| Jana Košlabová | Data Engineer |
| Antonín Hruška | Data Scientist (MIO) |
| Tomáš Kovářík | Data Scientist (Pulsation) |
| Tomáš Klas | Lead SRE engineer of PTO/MSO |

### Lely

|  |  |  |
| --- | --- | --- |
| **Customer’s Contact Name** | **E-mail** | **Role & Responsibility** |
| Frenk van Mil | [fvanmil@lely.com](mailto:fvanmil@lely.com) | Data Analyst, responsible for MSO initiatives |
| Marit van Dijk | [mvandijk1@lely.com](mailto:mvandijk1@lely.com) | Product Owner of MSO, MFPC |
| Heleen ten Have | [htenhave@lely.com](mailto:HtenHave@lely.com ) | Subject Matter Expert, Data Analyst |
| Yvet Renkema | [yrenkema@lely.com](mailto:yrenkema@lely.com) | Data Analyst, working also on MSO |
| Kimberlee Mesu | [kmesu@lely.com](mailto:kmesu@lely.com) | Contact person forintegration of MSO in Horizon |
| DOC Cloud Team | [doc.cloudoperations@lely.com](mailto:doc.cloudoperations@lely.com) | Mail group of Lely DOC Cloud team |
| Astronaut CD team |  | Responsible for MFP data |
| Nicole Kuijs | nkuijs@lely.com | Junior Business Analyst in Horizon   - Responsible for planning and coordination of the work for Horizon team. E.g. she planned and coordinated adding support of cloud2device at Horizon side. |
| Erik Hoogeveen | ehoogeveen@lely.com | Horizon architect |
| Berkay Engin | bengin@lely.com | Horizon developer, disipline architect |
| Hakan Doker | hdoker@lely.com | Horizon developer |

## Repository URL

| **Repository** | **Description** | **Maintainers** |
| --- | --- | --- |
| [PTO](https://github.com/datamole-ai/lely-mso-pto) | Jobs and packages related to the PTO pipeline | [Hellen Data Engineering PRG Team](https://datamole.atlassian.net/people/team/og-0c0e38cd-d6de-41f5-83d6-9dc79e6a8625) |
| [PTO Gitops](https://github.com/datamole-ai/lely-mso-pto-gitops) | Gitops repository for the PTO pipeline | [Hellen Data Engineering PRG Team](https://datamole.atlassian.net/people/team/og-0c0e38cd-d6de-41f5-83d6-9dc79e6a8625) |
| [PTO Data Science](https://github.com/datamole-ai/lely-mso-pto-data-science) | DS experiments and packages maintained by data scientists (notably pto-models) | Apollo |
| [PTO Model Monitoring](https://github.com/datamole-ai/lely-mso-pto-model-monitoring) | Jobs and packages related to the model monitoring dashboard | Apollo |
| [MSO](https://github.com/datamole-ai/lely-mso) | Implementation of MSO projects in Databricks | [Hellen Data Engineering PRG Team](https://datamole.atlassian.net/people/team/og-0c0e38cd-d6de-41f5-83d6-9dc79e6a8625) |
| MSO IaaC   - [rg-mso-dev](https://gitlab.lelyonline.com/dvit1/cloud/infrastructure/development/databricks/rg-mso-dev) | Infrastructure as a Code for MSO in Databricks |  |

## Literature

The papers related to this project and those pertaining to domain knowledge are collected in shared Zotero library. Access to the library can be granted by Iveta Šárfyová (Unlicensed) .

## Project Status

**[IN PRODUCTION]**

## Recent updates

- [Draft: PTO Setting Recommender Monitoring Requirements](Milking-Settings-Optimization-Landing-Page - Documentation - PTO-Requirements - Draft-PTO-Setting-Recommender-Monitoring-Requirements.md "data-linked-resource-id=")

  30 minutes ago • contributed by Jiří Vošmik
- [Draft: PTO Setting Recommender Monitoring Requirements](/wiki/spaces/MSO/pages/2447507530/Draft+PTO+Setting+Recommender+Monitoring+Requirements?focusedCommentId=2479882296)

  31 minutes ago • commented by Jan Lukány
- [Draft: PTO Setting Recommender Monitoring Requirements](/wiki/spaces/MSO/pages/2447507530/Draft+PTO+Setting+Recommender+Monitoring+Requirements?focusedCommentId=2478932041)

  33 minutes ago • commented by Jan Lukány
- [2026 Q2 Roadmap](Milking-Settings-Optimization-Landing-Page - Data-Engineering - Misc - 2026-Q2-Roadmap.md "data-linked-resource-id=")

  38 minutes ago • contributed by Jan Lukány
- [2026-03 - PoC: Incremental data collection](Milking-Settings-Optimization-Landing-Page - Data-Engineering - Misc - 2026-03-PoC-Incremental-data-collection.md "data-linked-resource-id=")

  about an hour ago • contributed by Michal Belák
- [2026 Q2 Roadmap](/wiki/spaces/MSO/pages/2476278470/2026+Q2+Roadmap?focusedCommentId=2479259693)

  about an hour ago • commented by Jan Lukány
- [2026 Q2 Roadmap](/wiki/spaces/MSO/pages/2476278470/2026+Q2+Roadmap?focusedCommentId=2479980557)

  about an hour ago • commented by Jan Lukány
- [WIP ADR: Repository Strategy for MSO Project (DS & DE Collaboration)](/wiki/spaces/MSO/pages/2297856007/WIP+ADR+Repository+Strategy+for+MSO+Project+DS+DE+Collaboration?focusedCommentId=2479685634)

  about 3 hours ago • commented by Jan Lukány
- [2026 Q2 Roadmap](/wiki/spaces/MSO/pages/2476278470/2026+Q2+Roadmap?focusedCommentId=2477916221)

  yesterday at 08:41 • commented by Jan Lukány
- [Pulsation meeting notes thread](Milking-Settings-Optimization-Landing-Page - Meeting-notes - Pulsation-meeting-notes-thread.md "data-linked-resource-id=")

  yesterday at 08:22 • contributed by Petr Svarny
- [MIO meeting notes thread](Milking-Settings-Optimization-Landing-Page - Meeting-notes - MIO-meeting-notes-thread.md "data-linked-resource-id=")

  yesterday at 07:59 • contributed by Petr Svarny
- [MIO (Beaver) Requirements](Milking-Settings-Optimization-Landing-Page - Documentation - MIO-Beaver-Requirements.md "data-linked-resource-id=")

  yesterday at 07:28 • contributed by Adam Skluzáček
- [WIP: MSO Databricks Core Layer & Optimization Container Blueprints](Milking-Settings-Optimization-Landing-Page - Data-Engineering - Design-docs - WIP-MSO-Databricks-Core-Layer-Optimization-Container-Blueprints.md "data-linked-resource-id=")

  28/03/2026 • contributed by Jan Lukány
- [WIP: MSO Databricks Architecture](Milking-Settings-Optimization-Landing-Page - Data-Engineering - Design-docs - WIP-MSO-Databricks-Architecture.md "data-linked-resource-id=")

  28/03/2026 • contributed by Jan Lukány
- [mermaid\_1774695370281.png](/wiki/pages/viewpageattachments.action?pageId=2475688504&preview=%2F2475688504%2F2475688533%2Fmermaid_1774695370281.png)

  28/03/2026 • attached by Jan Lukány

[Show More](/wiki/plugins/recently-updated/changes.action?theme=concise&startIndex=15&searchToken=1&spaceKeys=MSO&contentType=-mail,page,whiteboard,database,slide,embed,comment,blogpost,attachment,userinfo,spacedesc,personalspacedesc,space,draft,folder,custom&cursor=_t_WzE3NzQ2OTUzNzEwMDAsIlx0MjQ3NTY4ODUzMyBYVS9UW1l0SV9lTEhOQ2hrViZSNiBjYSJd_h_W10%3D)

## Google Drive Folder

## Jira Issues

|
|  |
| Key | Summary | T | Updated | Assignee | Status | Resolution |
| [PTO-1446](https://datamole.atlassian.net/browse/PTO-1446) | [Make device-checker independent from PTO data](https://datamole.atlassian.net/browse/PTO-1446) |  | Fri 08:13 | Marek Pavelka | Done | Done |
| [PTO-2019](https://datamole.atlassian.net/browse/PTO-2019) | [Route MILKING-DATA-LOW-AVAILABILITY to SRE or Lely](https://datamole.atlassian.net/browse/PTO-2019) |  | Fri 08:13 | Unassigned | Backlog | Unresolved |
| [PTO-1607](https://datamole.atlassian.net/browse/PTO-1607) | [Move missing robot free time alert to DOC](https://datamole.atlassian.net/browse/PTO-1607) |  | Fri 08:13 | Lukáš Folwarczný | Done | Done |
| [PTO-1457](https://datamole.atlassian.net/browse/PTO-1457) | [Migrate MFP stream](https://datamole.atlassian.net/browse/PTO-1457) |  | Fri 08:13 | Marek Pavelka | Done | Done |
| [PTO-2264](https://datamole.atlassian.net/browse/PTO-2264) | [EXPIRED\_SETTINGS alert is not resolved when there are too few samples](https://datamole.atlassian.net/browse/PTO-2264) |  | Fri 08:13 | Jan Lukány | Done | Done |
| [PTO-2143](https://datamole.atlassian.net/browse/PTO-2143) | [Investigate setting propagation monitoring](https://datamole.atlassian.net/browse/PTO-2143) |  | Fri 08:13 | Jan Lukány | Done | Done |
| [PTO-1978](https://datamole.atlassian.net/browse/PTO-1978) | [MFPC-DATA-MISSING: Change semantics](https://datamole.atlassian.net/browse/PTO-1978) |  | Fri 08:13 | Unassigned | Backlog | Unresolved |
| [PTO-1212](https://datamole.atlassian.net/browse/PTO-1212) | [Create mapping of Jira components to abbreviations in TOPdesk integration](https://datamole.atlassian.net/browse/PTO-1212) |  | Fri 08:13 | Jan Lukány | Done | Done |
| [PTO-2270](https://datamole.atlassian.net/browse/PTO-2270) | [Estimate the effects of missing data coming from streaming sources from AADP on PTO](https://datamole.atlassian.net/browse/PTO-2270) |  | Fri 08:13 | Ondrej Profant | Done | Done |
| [PTO-1424](https://datamole.atlassian.net/browse/PTO-1424) | [Extend TIA so it adds Lely Center & Farm Name to Jira Tickets](https://datamole.atlassian.net/browse/PTO-1424) |  | Fri 08:13 | Marek Pavelka | Done | Done |

Showing 10 out of
[2583 issues](https://datamole.atlassian.net/issues/?jql=filter+%3D+%22Filter+for+MSO+scrum%22+order+by+updated+desc+++++++&src=confmacro "View all matching issues in JIRA.")
