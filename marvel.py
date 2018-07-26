import asyncio
import aiohttp

from random import randint
from hashlib import md5

uri         = "?ts={}&apikey={}&hash={}"
publik_key  = 'ffa0bb02c7ece0999803af25210e8b9c'
private_key = 'c6c3d24659cdf5b0dcd9d17e4ec854eac63c847f'
url         = "http://gateway.marvel.com/v1/public/characters"

'''
class AsyncIter:
	def __init__(self, it):
		self._iter = iter(it)

	async def __aiter__(self):
		return self

	async def __anext__(self):
		await asyncio.sleep(1)
		try:
			value = next(self._iter)
		except StopIteration:
			raise StopAsyncIteration
		return value
'''

class AsyncCrawler:
	def __init__(self, loop=None):
		self.loop = loop if loop else asyncio.get_event_loop()
		self.uri  = uri
		self.publik_key  = publik_key
		self.private_key = private_key
		self.url = url

		self._name       = list()
		self._characters = list()
		self._comics     = list()
		self._events     = list()
		self._creators   = list()
		self._modified   = list()

	def make_md5(self, url):
		ts = str(randint(1, 100))
		u = url + self.uri
		dgst = ts + self.private_key + self.publik_key
		hs = md5(dgst.encode('utf-8')).hexdigest()
		return u.format(ts, self.publik_key, hs)


	async def characters(self, data):
		for js in data:
			for _ in js['comics'].get('items'):
				name = _.get('name')
				mod = js.get('modified').split('T1')[0]
				self._name.append(name)
				self._modified.append(mod)
				url = _.get('resourceURI')
				await self.comics(url)



	async def crawler_comics(self, data):
		for js in data:
			title = js.get('title')
			self._comics.append(title)
			await self.crawler_events(js)


	async def comics(self, url):
		u = self.make_md5(url)
		async with aiohttp.ClientSession() as session:
			async with session.get(u) as resp:
				data = await resp.json()
				await self.crawler_comics(data['data'].get('results'))


	async def crawler_events(self, data):
		for js in data.get('events')['items']:
			if js.get('resourceURI'):
				url = js.get('resourceURI')
				if url and 'events' in url:
					await self.events(url)
				else:
					self._events.append("events not found")
			else:
				self._events.append("events not found")



	async def crawler_events_end(self, data):
		for js in data:
			description = js.get('description')
			if description:
				self._events.append(description)
			else:
				self._events.append("events not found")
			await self.crawler_creators(js)


	async def events(self, url):
		u = self.make_md5(url)
		async with aiohttp.ClientSession() as session:
			async with session.get(u) as resp:
				data = await resp.json()
				await self.crawler_events_end(data['data'].get('results'))
     

	async def crawler_creators(self, data):
		data = data.get('creators').get('items')
		for js in data:
			cre = js.get('name')
			self._creators.append(cre)


	async def go(self, url):
		print("go")
		u = self.make_md5(url)
		async with aiohttp.ClientSession() as session:
			async with session.get(u) as resp:
				data = await resp.json()
				await self.characters(data['data'].get('results'))


	def start(self):
		obj = []
		loop = asyncio.get_event_loop()
		try:
			loop.run_until_complete(self.go(self.url))
		except KeyboardInterrupt:
			pass
		finally:
			loop.close()

		#old = [self._name, self._comics, self._events, self._creators, self._modified]
		#old.sort(key=lambda i: 4)
		#self._name, self._comics, self._events, self._creators, self._modified = old
		
		for x in  zip(self._name, self._comics, self._events, self._creators, self._modified)[:20]:
			obj.append(x)
		
		for x in obj:
			_ = " ".join(x)
			print(_, end='\n\n\n\n')



def main():
	crawler = AsyncCrawler()
	crawler.start()

if __name__ == '__main__':
	main()