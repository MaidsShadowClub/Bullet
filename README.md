# Bullet
Tool for scraping CVEs for vulnerability research purposes

## Instruction
### Instalation
1. `git clone https://github.com/MaidsShadowClub/Bullet`
2. `cd Bullet`
3. `pip3 install -r requirements.txt`

### Commands
`scrapy crawl SamsungCVE` - scrap Samsung's CVEs<br>
`scrapy crawl HuaweiCVE` - scrap Huawei's CVEs<br>
`scrapy crawl LgCVE` - scrap Lg's CVEs<br>
`scrapy crawl GPZArticles` - scrap articles from Google Project Zero for current year<br>
To reduce debug logs add `-s LOG_LEVEL='INFO'` at end of the command<br>

## Todo
### To add
- Export scraped info as PDF
- Use telegram bot to send bulletin

### Planned scrapers
- AppleCVE (https://support.apple.com/en-us/HT201222)
- QualcommCVE (https://docs.qualcomm.com/product/publicresources/securitybulletin/april-2023-bulletin.html)
- AndroidCVE (https://source.android.com/docs/security/bulletin/asb-overview)
- MicrosoftCVE (https://www.microsoft.com/en-us/download/confirmation.aspx?id=36982)
- NvdCVE (https://nvd.nist.gov/)
- Conferences?
