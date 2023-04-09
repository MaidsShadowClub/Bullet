# Bullet
Tool for scraping CVEs for vulnerability research purposes

## Instruction
### Instalation
1. `pip3 install scrapy`
2. `git clone https://github.com/MaidsShadowClub/Bullet`

### Commands
`scrapy crawl SamsungCVE` - scrap Samsung's CVEs<br>
`scrapy crawl HuaweiCVE` - scrap Huawei's CVEs<br>
`scrapy crawl LgCVE` - scrap Lg's CVEs<br>
To reduce debug logs add `-s LOG_LEVEL='INFO'` at end of the command<br>

## Todo
### To add
- Database
- Export scraped info as PDF
- Use telegram bot to send bulletin

### Planned scrapers
- AppleCVE (https://support.apple.com/en-us/HT201222)
- QualcommCVE (https://docs.qualcomm.com/product/publicresources/securitybulletin/april-2023-bulletin.html)
- AndroidCVE (https://source.android.com/docs/security/bulletin/asb-overview)
- MicrosoftCVE (https://www.microsoft.com/en-us/download/confirmation.aspx?id=36982)
- NvdCVE (https://nvd.nist.gov/)
- GPZArticles
- Conferences?
