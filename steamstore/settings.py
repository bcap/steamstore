# -*- coding: utf-8 -*-

# Scrapy settings for steamstore project
#
# For simplicity, this file contains only the most important settings by
# default. All the other settings are documented here:
#
#     http://doc.scrapy.org/en/latest/topics/settings.html
#

BOT_NAME = 'steamstore'

SPIDER_MODULES = ['steamstore.spiders']
NEWSPIDER_MODULE = 'steamstore.spiders'

ROBOTSTXT_OBEY = True

LOG_ENABLED = True
LOG_FILE = 'steamstore.log'

# Crawl responsibly by identifying yourself (and your website) on the user-agent
#USER_AGENT = 'steamstore (+http://www.yourdomain.com)'
