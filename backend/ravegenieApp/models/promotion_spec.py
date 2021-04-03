from django.db import models
from utils.models import ModelMixin

class PromotionSpec(models.Model, ModelMixin):
	FACEBOOK = 'FB'
	YOUTUBE = 'YT'
	INSTAGRAM = 'IG'
	TWITTER = 'TW'
	WHATSAPP = 'WA'
	PLAYSTORE = 'PS'
	APPSTORE = 'AS'

	PLATFORMS = (
		(FACEBOOK, 'facebook'),
		(TWITTER, 'twitter'),
		(INSTAGRAM, 'instagram'),
		(YOUTUBE, 'youtube'),
		(WHATSAPP, 'whatsapp'),
		(PLAYSTORE, 'playstore'),
		(APPSTORE, 'appstore')
	)

	LIKE_POST = 'LPO'
	COMMENT = 'CO'
	LIKE_PAGE = 'LPG'
	MENTION = 'MNN'
	VIEW_POST = 'VPO'
	PROMOTE = 'PRO'
	FOLLOW = 'FLW'
	LIKE_VIDEO = 'LVO'
	WATCH_VIDEO = 'WVO'
	SUBSCRIBE = 'SUB'
	POST_STATUS = 'PST'
	RATE_APP = 'RTA'
	REVIEW_APP = 'RVA'
	DOWNLOAD_APP = 'DWA'

	ACTIONS = (
		(LIKE_POST, 'like post'),
		(COMMENT, 'comment'),
		(LIKE_PAGE, 'like page'),
		(MENTION, 'mention'),
		(VIEW_POST, 'view post'),
		(PROMOTE, 'promote'),
		(FOLLOW, 'follow'),
		(LIKE_VIDEO, 'like video'),
		(WATCH_VIDEO, 'watch video'),
		(SUBSCRIBE, 'subscribe'),
		(POST_STATUS, 'post status'),
		(RATE_APP, 'rate app'),
		(REVIEW_APP, 'review app'),
		(DOWNLOAD_APP, 'download app')
	)
	platform = models.CharField(max_length=3, choices=PLATFORMS)
	action = models.CharField(max_length=3, choices=ACTIONS)
	platform_cost = models.DecimalField(decimal_places=2, max_digits=10)
	publisher_cost = models.DecimalField(decimal_places=2, max_digits=10)
	publisher_unit_compensation = models.DecimalField(decimal_places=2, max_digits=5)

	def get_dict(self):
		return {
			'price': self.cost(),
			'platform': self.platform,
			'action': self.action
		}
	def cost(self):
		return  self.platform_cost + self.publisher_cost